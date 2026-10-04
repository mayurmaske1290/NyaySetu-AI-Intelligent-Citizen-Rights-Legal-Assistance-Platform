from fastapi import APIRouter

from app.evidence.claims import map_claims
from app.schemas.evidence import ClaimMapRequest, ClaimMapResponse

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post("/map", response_model=ClaimMapResponse)
async def claims_map(body: ClaimMapRequest):
    return map_claims(body)
