from datetime import datetime
from typing import Any


class ModelRoutingDocument:
    """Represents a document in the model_routing_requests MongoDB collection."""

    COLLECTION_NAME = "model_routing_requests"

    @staticmethod
    def to_document(
        user_id: str,
        prompt: str,
        selected_model: str,
        tier: str,
        routing_reason: str,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        actual_cost: float,
        premium_model_cost: float,
        savings: float,
        response_time_ms: int,
        response: str,
    ) -> dict[str, Any]:
        return {
            "user_id": user_id,
            "prompt": prompt,
            "selected_model": selected_model,
            "tier": tier,
            "routing_reason": routing_reason,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "actual_cost": actual_cost,
            "premium_model_cost": premium_model_cost,
            "savings": savings,
            "response_time_ms": response_time_ms,
            "response": response,
            "created_at": datetime.utcnow(),
        }

    @staticmethod
    def serialize(doc: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(doc["_id"]),
            "prompt": doc.get("prompt", ""),
            "selected_model": doc.get("selected_model", ""),
            "tier": doc.get("tier", ""),
            "routing_reason": doc.get("routing_reason", ""),
            "input_tokens": doc.get("input_tokens", 0),
            "output_tokens": doc.get("output_tokens", 0),
            "total_tokens": doc.get("total_tokens", 0),
            "actual_cost": doc.get("actual_cost", 0.0),
            "premium_model_cost": doc.get("premium_model_cost", 0.0),
            "savings": doc.get("savings", 0.0),
            "response_time_ms": doc.get("response_time_ms", 0),
            "response": doc.get("response", ""),
            "created_at": doc.get("created_at"),
        }
