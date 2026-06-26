from datetime import datetime
from typing import Any


class PromptCacheDocument:
    """Represents a document in the prompt_cache MongoDB collection."""

    COLLECTION_NAME = "prompt_cache"

    @staticmethod
    def to_document(
        prompt_hash: str,
        system_prompt: str,
        user_prompt: str,
        model: str,
        max_tokens: int,
        cache_hit: bool,
        prefix_tokens: int,
        tokens_saved: int,
        cost_saved: float,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        estimated_cost: float,
        response_time_ms: int,
        response: str,
    ) -> dict[str, Any]:
        return {
            "prompt_hash": prompt_hash,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "model": model,
            "max_tokens": max_tokens,
            "cache_hit": cache_hit,
            "prefix_tokens": prefix_tokens,
            "tokens_saved": tokens_saved,
            "cost_saved": cost_saved,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost": estimated_cost,
            "response_time_ms": response_time_ms,
            "response": response,
            "created_at": datetime.utcnow(),
        }
