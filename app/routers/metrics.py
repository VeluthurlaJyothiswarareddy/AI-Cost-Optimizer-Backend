from fastapi import APIRouter

from app.database import get_collection
from app.schemas.metrics import MetricsResponse

router = APIRouter(prefix="/api", tags=["metrics"])


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    collection = get_collection()

    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_requests": {"$sum": 1},
                "total_tokens": {"$sum": "$total_tokens"},
                "total_cost": {"$sum": "$estimated_cost"},
            }
        }
    ]

    result = await collection.aggregate(pipeline).to_list(length=1)

    if not result:
        return MetricsResponse(
            total_requests=0,
            total_tokens=0,
            average_tokens=0.0,
            total_cost=0.0,
        )

    stats = result[0]
    total_requests = stats.get("total_requests", 0)
    total_tokens = stats.get("total_tokens", 0)
    total_cost = round(stats.get("total_cost", 0.0), 6)
    average_tokens = round(total_tokens / total_requests, 2) if total_requests else 0.0

    return MetricsResponse(
        total_requests=total_requests,
        total_tokens=total_tokens,
        average_tokens=average_tokens,
        total_cost=total_cost,
    )
