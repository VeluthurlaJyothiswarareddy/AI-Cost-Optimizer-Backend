from datetime import datetime
from typing import Any

from bson import ObjectId


class LLMRequestDocument:
    """Represents a document in the llm_requests MongoDB collection."""

    COLLECTION_NAME = "llm_requests"

    @staticmethod
    def to_document(
        user_id: str,
        prompt: str,
        model: str,
        max_tokens: int,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        estimated_cost: float,
        response_time_ms: int,
        response: str,
    ) -> dict[str, Any]:
        return {
            "user_id": user_id,
            "prompt": prompt,
            "model": model,
            "max_tokens": max_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost": estimated_cost,
            "response_time_ms": response_time_ms,
            "response": response,
            "created_at": datetime.utcnow(),
        }

    @staticmethod
    def serialize(doc: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(doc["_id"]),
            "prompt": doc.get("prompt", ""),
            "model": doc.get("model", ""),
            "max_tokens": doc.get("max_tokens", 0),
            "input_tokens": doc.get("input_tokens", 0),
            "output_tokens": doc.get("output_tokens", 0),
            "total_tokens": doc.get("total_tokens", 0),
            "estimated_cost": doc.get("estimated_cost", 0.0),
            "response_time_ms": doc.get("response_time_ms", 0),
            "response": doc.get("response", ""),
            "created_at": doc.get("created_at"),
        }
