import re
from typing import List

from app.schemas.evidence import ClaimLink, ClaimMapRequest, ClaimMapResponse, EvidenceItem


def map_claims(req: ClaimMapRequest) -> ClaimMapResponse:
    claims = req.claims or _split_claims(req.description)
    mappings: List[ClaimLink] = []
    for claim in claims:
        tokens = set(re.findall(r"[a-z0-9₹]+", claim.lower()))
        matched: List[str] = []
        for e in req.evidence:
            hay = f"{e.file_name} {e.description} {e.source_type}".lower()
            if any(tok in hay for tok in tokens if len(tok) > 3):
                matched.append(e.file_name)
            elif e.source_type in ("screenshot", "image", "document") and any(
                w in claim.lower() for w in ("message", "notice", "photo", "screenshot", "chat")
            ):
                matched.append(e.file_name)
        if len(matched) >= 2:
            status = "SUPPORTED"
        elif len(matched) == 1:
            status = "PARTIALLY_SUPPORTED"
        else:
            status = "NO_SUPPORTING_EVIDENCE_FOUND"
        mappings.append(
            ClaimLink(
                claim=claim,
                evidence_names=list(dict.fromkeys(matched)),
                status=status,
            )
        )
    return ClaimMapResponse(mappings=mappings, demo_mode=True)


def _split_claims(description: str) -> List[str]:
    parts = re.split(r"[.!?]\s+", description.strip())
    parts = [p.strip() for p in parts if len(p.strip()) > 12]
    return parts[:6] or [description.strip()[:200]]
