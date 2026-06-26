from fastapi import APIRouter, HTTPException

from app.schemas.model_tiering import (
    ModelTieringChatRequest,
    ModelTieringChatResponse,
    ModelTieringHistoryItem,
    ModelTieringMetricsResponse,
)
from app.services.model_router import model_router_service
from app.services.model_tiering_metrics import get_history, get_metrics
from app.services.openrouter_service import OpenRouterError

router = APIRouter(prefix="/api/model-tiering", tags=["model-tiering"])


@router.post("/chat", response_model=ModelTieringChatResponse)
async def model_tiering_chat(request: ModelTieringChatRequest) -> ModelTieringChatResponse:
    try:
        result = await model_router_service.route_and_chat(prompt=request.prompt)
    except OpenRouterError as exc:
        status = exc.status_code if exc.status_code and exc.status_code < 500 else 502
        if exc.status_code == 500:
            status = 500
        raise HTTPException(status_code=status, detail=str(exc)) from exc

    return ModelTieringChatResponse(
        selected_model=result["selected_model"],
        tier=result["tier"],
        routing_reason=result["routing_reason"],
        input_tokens=result["input_tokens"],
        output_tokens=result["output_tokens"],
        total_tokens=result["total_tokens"],
        actual_cost=result["actual_cost"],
        premium_model_cost=result["premium_model_cost"],
        savings=result["savings"],
        response_time_ms=result["response_time_ms"],
        response=result["response"],
    )


@router.get("/history", response_model=list[ModelTieringHistoryItem])
async def model_tiering_history(limit: int = 50) -> list[ModelTieringHistoryItem]:
    items = await get_history(limit=limit)
    return [ModelTieringHistoryItem(**item) for item in items]


@router.get("/metrics", response_model=ModelTieringMetricsResponse)
async def model_tiering_metrics() -> ModelTieringMetricsResponse:
    result = await get_metrics()
    return ModelTieringMetricsResponse(**result)
