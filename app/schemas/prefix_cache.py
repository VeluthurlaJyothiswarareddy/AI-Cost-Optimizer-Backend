from pydantic import BaseModel, Field


class PrefixCacheChatRequest(BaseModel):
    system_prompt: str = Field(..., min_length=1, max_length=10000)
    user_prompt: str = Field(..., min_length=1, max_length=10000)
    model: str = Field(..., min_length=1)
    max_tokens: int = Field(..., ge=1, le=4096)


class PrefixCacheChatResponse(BaseModel):
    response: str
    cache_hit: bool
    prompt_hash: str
    prefix_tokens: int
    tokens_saved: int
    cost_saved: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    response_time_ms: int


class PrefixCacheMetricsResponse(BaseModel):
    cache_hits: int
    cache_misses: int
    hit_rate: float
    tokens_saved: int
    cost_saved: float
