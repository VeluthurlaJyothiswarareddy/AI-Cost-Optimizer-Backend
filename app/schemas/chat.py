from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    model: str = Field(..., min_length=1)
    max_tokens: int = Field(..., ge=1, le=4096)


class ChatResponse(BaseModel):
    response: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    response_time_ms: int
