import hashlib
from typing import Any

from app.database import get_prompt_cache_collection
from app.models.prompt_cache import PromptCacheDocument
from app.services.cost_calculator import calculate_cost
from app.services.openrouter_service import OpenRouterError, openrouter_service


def hash_system_prompt(system_prompt: str) -> str:
    """Generate SHA256 hash of a system prompt for cache lookup."""
    return hashlib.sha256(system_prompt.encode("utf-8")).hexdigest()


def estimate_prefix_tokens(system_prompt: str) -> int:
    """Estimate system-prompt token count (~4 chars per token)."""
    return max(1, len(system_prompt.encode("utf-8")) // 4)


class PromptCacheService:
    async def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        max_tokens: int,
    ) -> dict[str, Any]:
        prompt_hash = hash_system_prompt(system_prompt)
        collection = get_prompt_cache_collection()

        prior = await collection.find_one(
            {"prompt_hash": prompt_hash, "model": model},
            sort=[("created_at", 1)],
        )

        cache_hit = prior is not None
        prefix_tokens = (
            prior.get("prefix_tokens", estimate_prefix_tokens(system_prompt))
            if prior
            else estimate_prefix_tokens(system_prompt)
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        result = await openrouter_service.chat_completion_with_messages(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
        )

        tokens_saved = prefix_tokens if cache_hit else 0
        cost_saved = calculate_cost(model, tokens_saved, 0) if cache_hit else 0.0

        document = PromptCacheDocument.to_document(
            prompt_hash=prompt_hash,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            max_tokens=max_tokens,
            cache_hit=cache_hit,
            prefix_tokens=prefix_tokens,
            tokens_saved=tokens_saved,
            cost_saved=cost_saved,
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            total_tokens=result["total_tokens"],
            estimated_cost=result["estimated_cost"],
            response_time_ms=result["response_time_ms"],
            response=result["response"],
        )
        await collection.insert_one(document)

        return {
            "response": result["response"],
            "cache_hit": cache_hit,
            "prompt_hash": prompt_hash,
            "prefix_tokens": prefix_tokens,
            "tokens_saved": tokens_saved,
            "cost_saved": cost_saved,
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "total_tokens": result["total_tokens"],
            "estimated_cost": result["estimated_cost"],
            "response_time_ms": result["response_time_ms"],
        }

    async def get_metrics(self) -> dict[str, Any]:
        collection = get_prompt_cache_collection()

        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "cache_hits": {
                        "$sum": {"$cond": [{"$eq": ["$cache_hit", True]}, 1, 0]}
                    },
                    "cache_misses": {
                        "$sum": {"$cond": [{"$eq": ["$cache_hit", False]}, 1, 0]}
                    },
                    "tokens_saved": {"$sum": "$tokens_saved"},
                    "cost_saved": {"$sum": "$cost_saved"},
                }
            }
        ]

        result = await collection.aggregate(pipeline).to_list(length=1)

        if not result:
            return {
                "cache_hits": 0,
                "cache_misses": 0,
                "hit_rate": 0.0,
                "tokens_saved": 0,
                "cost_saved": 0.0,
            }

        stats = result[0]
        cache_hits = stats.get("cache_hits", 0)
        cache_misses = stats.get("cache_misses", 0)
        total = cache_hits + cache_misses
        hit_rate = round((cache_hits / total) * 100, 2) if total else 0.0

        return {
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "hit_rate": hit_rate,
            "tokens_saved": stats.get("tokens_saved", 0),
            "cost_saved": round(stats.get("cost_saved", 0.0), 6),
        }


prompt_cache_service = PromptCacheService()
