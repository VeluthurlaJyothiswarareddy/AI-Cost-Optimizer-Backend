from fastapi import APIRouter

from app.database import get_collection
from app.models.llm_request import LLMRequestDocument
from app.schemas.history import HistoryItem

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history", response_model=list[HistoryItem])
async def get_history(limit: int = 50) -> list[HistoryItem]:
    collection = get_collection()
    cursor = collection.find().sort("created_at", -1).limit(min(limit, 200))
    documents = await cursor.to_list(length=limit)

    return [HistoryItem(**LLMRequestDocument.serialize(doc)) for doc in documents]
