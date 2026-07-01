from datetime import datetime
from typing import Any


class UserDocument:
    """Represents a document in the users MongoDB collection."""

    COLLECTION_NAME = "users"

    @staticmethod
    def to_document(email: str, hashed_password: str) -> dict[str, Any]:
        return {
            "email": email.lower(),
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
        }

    @staticmethod
    def serialize(doc: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(doc["_id"]),
            "email": doc.get("email", ""),
            "created_at": doc.get("created_at"),
        }
