from fastapi import APIRouter

from app.complaints.generator import generate_complaint
from app.schemas.complaint import ComplaintDraft, ComplaintRequest

router = APIRouter(prefix="/complaints", tags=["complaints"])


@router.post("/generate", response_model=ComplaintDraft)
async def complaints(body: ComplaintRequest):
    return generate_complaint(body)
