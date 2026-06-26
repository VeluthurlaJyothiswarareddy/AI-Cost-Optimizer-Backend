from datetime import datetime

from pydantic import BaseModel


class HistoryItem(BaseModel):
    id: str
    prompt: str
    model: str
    max_tokens: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    response_time_ms: int
    response: str
    created_at: datetime
