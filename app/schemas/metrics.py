from pydantic import BaseModel


class MetricsResponse(BaseModel):
    total_requests: int
    total_tokens: int
    average_tokens: float
    total_cost: float
