"""Token cost calculator using per-model pricing (USD per 1M tokens)."""

from typing import TypedDict


class ModelPricing(TypedDict):
    input: float
    output: float


# Pricing per 1 million tokens (USD)
PRICING_TABLE: dict[str, ModelPricing] = {
    "openai/gpt-4o-mini": {
        "input": 0.15,
        "output": 0.60,
    },
    "anthropic/claude-3-haiku": {
        "input": 0.25,
        "output": 1.25,
    },
    "google/gemini-2.5-flash": {
        "input": 0.30,
        "output": 2.50,
    },
}

DEFAULT_PRICING: ModelPricing = {"input": 0.50, "output": 1.50}


def get_model_pricing(model: str) -> ModelPricing:
    return PRICING_TABLE.get(model, DEFAULT_PRICING)


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated request cost in USD."""
    pricing = get_model_pricing(model)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return round(input_cost + output_cost, 6)
