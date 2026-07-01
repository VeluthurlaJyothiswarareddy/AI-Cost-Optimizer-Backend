from fastapi import APIRouter, Depends, HTTPException

from app.database import get_collection
from app.dependencies.auth import get_current_user
from app.models.llm_request import LLMRequestDocument
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.openrouter_service import OpenRouterError, openrouter_service

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
) -> ChatResponse:
    try:
        result = await openrouter_service.chat_completion(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
        )
    except OpenRouterError as exc:
        status = exc.status_code if exc.status_code and exc.status_code < 500 else 502
        if exc.status_code == 500:
            status = 500
        raise HTTPException(status_code=status, detail=str(exc)) from exc

    document = LLMRequestDocument.to_document(
        user_id=current_user["id"],
        prompt=request.prompt,
        model=request.model,
        max_tokens=request.max_tokens,
        input_tokens=result["input_tokens"],
        output_tokens=result["output_tokens"],
        total_tokens=result["total_tokens"],
        estimated_cost=result["estimated_cost"],
        response_time_ms=result["response_time_ms"],
        response=result["response"],
    )

    collection = get_collection()
    await collection.insert_one(document)

    return ChatResponse(**result)
