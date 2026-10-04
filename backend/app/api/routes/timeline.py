from fastapi import APIRouter

from app.evidence.timeline import generate_timeline
from app.schemas.evidence import TimelineRequest, TimelineResponse

router = APIRouter(prefix="/timeline", tags=["timeline"])


@router.post("/generate", response_model=TimelineResponse)
async def timeline(body: TimelineRequest):
    return generate_timeline(body)
