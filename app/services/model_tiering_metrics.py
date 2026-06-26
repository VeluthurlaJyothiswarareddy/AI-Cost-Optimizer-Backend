"""Cost calculation and metrics for the Model Tiering optimization module."""

from typing import Any, TypedDict

from app.database import get_model_routing_collection
from app.models.model_routing_request import ModelRoutingDocument

PREMIUM_MODEL = "anthropic/claude-sonnet-4.6"


class ModelPricing(TypedDict):
    input: float
    output: float


# Pricing per 1 million tokens (USD) — tiering module only
TIERING_PRICING: dict[str, ModelPricing] = {
    "google/gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40},
    "google/gemini-2.5-flash": {"input": 0.30, "output": 2.50},
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
    "anthropic/claude-sonnet-4.6": {"input": 3.00, "output": 15.00},
}

DEFAULT_PRICING: ModelPricing = {"input": 0.50, "output": 1.50}


def calculate_tiering_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated request cost in USD for tiering models."""
    pricing = TIERING_PRICING.get(model, DEFAULT_PRICING)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return round(input_cost + output_cost, 6)


def calculate_premium_cost(input_tokens: int, output_tokens: int) -> float:
    return calculate_tiering_cost(PREMIUM_MODEL, input_tokens, output_tokens)


async def get_metrics() -> dict[str, Any]:
    collection = get_model_routing_collection()

    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_requests": {"$sum": 1},
                "small_tier_requests": {
                    "$sum": {"$cond": [{"$eq": ["$tier", "SMALL"]}, 1, 0]}
                },
                "medium_tier_requests": {
                    "$sum": {"$cond": [{"$eq": ["$tier", "MEDIUM"]}, 1, 0]}
                },
                "large_tier_requests": {
                    "$sum": {"$cond": [{"$eq": ["$tier", "LARGE"]}, 1, 0]}
                },
                "actual_total_cost": {"$sum": "$actual_cost"},
                "premium_model_total_cost": {"$sum": "$premium_model_cost"},
                "total_savings": {"$sum": "$savings"},
            }
        }
    ]

    result = await collection.aggregate(pipeline).to_list(length=1)

    if not result:
        return {
            "total_requests": 0,
            "small_tier_requests": 0,
            "medium_tier_requests": 0,
            "large_tier_requests": 0,
            "actual_total_cost": 0.0,
            "premium_model_total_cost": 0.0,
            "total_savings": 0.0,
        }

    stats = result[0]
    return {
        "total_requests": stats.get("total_requests", 0),
        "small_tier_requests": stats.get("small_tier_requests", 0),
        "medium_tier_requests": stats.get("medium_tier_requests", 0),
        "large_tier_requests": stats.get("large_tier_requests", 0),
        "actual_total_cost": round(stats.get("actual_total_cost", 0.0), 6),
        "premium_model_total_cost": round(stats.get("premium_model_total_cost", 0.0), 6),
        "total_savings": round(stats.get("total_savings", 0.0), 6),
    }


async def get_history(limit: int = 50) -> list[dict[str, Any]]:
    collection = get_model_routing_collection()
    capped_limit = min(limit, 200)
    cursor = collection.find().sort("created_at", -1).limit(capped_limit)
    documents = await cursor.to_list(length=capped_limit)
    return [ModelRoutingDocument.serialize(doc) for doc in documents]
