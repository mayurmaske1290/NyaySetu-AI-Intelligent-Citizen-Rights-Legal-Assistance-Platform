from fastapi import APIRouter

from app.core.security import sha256_text
from app.evidence.gap_detector import detect_gaps
from app.schemas.evidence import EvidenceItem, GapRequest, GapResponse

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.post("/analyze")
async def analyze_evidence_meta(item: EvidenceItem):
    digest = item.sha256_hash or sha256_text(f"{item.file_name}:{item.description}")
    return {
        "file_name": item.file_name,
        "sha256_hash": digest,
        "note": "Integrity hash only. Hashing does not make evidence legally admissible.",
        "demo_mode": True,
    }


@router.post("/gaps", response_model=GapResponse)
async def evidence_gaps(body: GapRequest):
    return detect_gaps(body.description, body.category, body.evidence)
