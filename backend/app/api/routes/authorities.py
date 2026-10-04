from fastapi import APIRouter, Query

from app.schemas.authority import NearbyAuthoritiesResponse
from app.services.escalation import nearby

router = APIRouter(prefix="/authorities", tags=["authorities"])


@router.get("/nearby", response_model=NearbyAuthoritiesResponse)
async def authorities_nearby(
    lat: float | None = Query(default=None),
    lng: float | None = Query(default=None),
    category: str | None = Query(default=None),
):
    return nearby(lat, lng, category)
