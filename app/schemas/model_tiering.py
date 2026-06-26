from datetime import datetime

from pydantic import BaseModel, Field


class ModelTieringChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)


class ModelTieringChatResponse(BaseModel):
    selected_model: str
    tier: str
    routing_reason: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    actual_cost: float
    premium_model_cost: float
    savings: float
    response_time_ms: int
    response: str


class ModelTieringHistoryItem(BaseModel):
    id: str
    prompt: str
    selected_model: str
    tier: str
    routing_reason: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    actual_cost: float
    premium_model_cost: float
    savings: float
    response_time_ms: int
    response: str
    created_at: datetime


class ModelTieringMetricsResponse(BaseModel):
    total_requests: int
    small_tier_requests: int
    medium_tier_requests: int
    large_tier_requests: int
    actual_total_cost: float
    premium_model_total_cost: float
    total_savings: float
