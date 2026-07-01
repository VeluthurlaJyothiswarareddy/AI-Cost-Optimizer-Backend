from fastapi import APIRouter, Depends, HTTPException

from app.dependencies.auth import get_current_user

from app.schemas.prefix_cache import (
    PrefixCacheChatRequest,
    PrefixCacheChatResponse,
    PrefixCacheMetricsResponse,
)
from app.services.openrouter_service import OpenRouterError
from app.services.prompt_cache_service import prompt_cache_service

router = APIRouter(prefix="/api/prefix-cache", tags=["prefix-cache"])


@router.post("/chat", response_model=PrefixCacheChatResponse)
async def prefix_cache_chat(
    request: PrefixCacheChatRequest,
    _: dict = Depends(get_current_user),
) -> PrefixCacheChatResponse:
    try:
        result = await prompt_cache_service.chat(
            system_prompt=request.system_prompt,
            user_prompt=request.user_prompt,
            model=request.model,
            max_tokens=request.max_tokens,
        )
    except OpenRouterError as exc:
        status = exc.status_code if exc.status_code and exc.status_code < 500 else 502
        if exc.status_code == 500:
            status = 500
        raise HTTPException(status_code=status, detail=str(exc)) from exc

    return PrefixCacheChatResponse(**result)


@router.get("/metrics", response_model=PrefixCacheMetricsResponse)
async def prefix_cache_metrics(
    _: dict = Depends(get_current_user),
) -> PrefixCacheMetricsResponse:
    result = await prompt_cache_service.get_metrics()
    return PrefixCacheMetricsResponse(**result)
