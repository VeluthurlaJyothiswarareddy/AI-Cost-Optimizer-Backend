"""Rule-based model routing for the Model Tiering optimization module."""

from typing import Any

from app.database import get_model_routing_collection
from app.models.model_routing_request import ModelRoutingDocument
from app.services.model_tiering_metrics import (
    PREMIUM_MODEL,
    calculate_premium_cost,
    calculate_tiering_cost,
)
from app.services.openrouter_service import openrouter_service

DEFAULT_MAX_TOKENS = 500

LARGE_KEYWORDS = [
    "architecture",
    "microservice",
    "authentication",
    "kubernetes",
    "system design",
    "distributed system",
]

MEDIUM_KEYWORDS = [
    "summarize",
    "rewrite",
    "email",
    "translate",
    "improve",
]

SMALL_KEYWORDS = [
    "what is",
    "explain",
    "define",
    "meaning",
    "overview",
]

DEFAULT_MODEL = "openai/gpt-4o-mini"
DEFAULT_TIER = "MEDIUM"
DEFAULT_REASON = "Default routing — no keyword match"


def route_prompt(prompt: str) -> tuple[str, str, str]:
    """
    Route a prompt to the appropriate model tier using keyword rules.
    Priority: LARGE > MEDIUM > SMALL > DEFAULT.
    """
    normalized = prompt.lower().strip()

    for keyword in LARGE_KEYWORDS:
        if keyword in normalized:
            return "anthropic/claude-sonnet-4.6", "LARGE", "Complex engineering request"

    for keyword in MEDIUM_KEYWORDS:
        if keyword in normalized:
            return "anthropic/claude-3-haiku", "MEDIUM", "Content transformation task"

    for keyword in SMALL_KEYWORDS:
        if keyword in normalized:
            return "google/gemini-2.5-flash-lite", "SMALL", "Simple informational request"

    return DEFAULT_MODEL, DEFAULT_TIER, DEFAULT_REASON


class ModelRouterService:
    async def route_and_chat(self, prompt: str) -> dict[str, Any]:
        selected_model, tier, routing_reason = route_prompt(prompt)

        result = await openrouter_service.chat_completion(
            prompt=prompt,
            model=selected_model,
            max_tokens=DEFAULT_MAX_TOKENS,
        )

        actual_cost = calculate_tiering_cost(
            selected_model,
            result["input_tokens"],
            result["output_tokens"],
        )
        premium_model_cost = calculate_premium_cost(
            result["input_tokens"],
            result["output_tokens"],
        )
        savings = max(0.0, round(premium_model_cost - actual_cost, 6))

        document = ModelRoutingDocument.to_document(
            prompt=prompt,
            selected_model=selected_model,
            tier=tier,
            routing_reason=routing_reason,
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            total_tokens=result["total_tokens"],
            actual_cost=actual_cost,
            premium_model_cost=premium_model_cost,
            savings=savings,
            response_time_ms=result["response_time_ms"],
            response=result["response"],
        )

        collection = get_model_routing_collection()
        await collection.insert_one(document)

        return {
            "selected_model": selected_model,
            "tier": tier,
            "routing_reason": routing_reason,
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "total_tokens": result["total_tokens"],
            "actual_cost": actual_cost,
            "premium_model_cost": premium_model_cost,
            "savings": savings,
            "response_time_ms": result["response_time_ms"],
            "response": result["response"],
            "premium_model": PREMIUM_MODEL,
        }


model_router_service = ModelRouterService()
