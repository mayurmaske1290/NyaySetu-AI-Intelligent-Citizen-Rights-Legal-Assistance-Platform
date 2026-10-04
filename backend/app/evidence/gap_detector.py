from typing import List

from app.schemas.evidence import EvidenceItem, GapResponse


CATEGORY_HINTS = {
    "TRAFFIC_STOP": ["Written challan or e-challan screenshot", "Dashboard/location photo if safe", "Note of officer identifiers if visible"],
    "BRIBE_DEMAND": ["Contemporaneous written note of the amount and words used", "Any receipt that was offered or refused"],
    "SCAM": ["Full message screenshot", "UPI ID / phone / URL", "Bank or UPI transaction SMS if money moved"],
    "THREAT_HARASSMENT": ["Complete chat export or screenshots with timestamps", "Witness names if any"],
    "LEGAL_NOTICE": ["Every page of the document", "Envelope or email headers", "Sender identity details if printed"],
    "OTHER": ["Photos of relevant documents", "A dated written narrative"],
}


def detect_gaps(description: str, category: str | None, evidence: List[EvidenceItem]) -> GapResponse:
    available: List[str] = []
    names = {e.file_name.lower() + " " + e.source_type.lower() + " " + e.description.lower() for e in evidence}
    blob = " ".join(names)
    for e in evidence:
        label = e.file_name or e.source_type
        extra = []
        if e.has_timestamp:
            extra.append("timestamp")
        if e.has_location:
            extra.append("location")
        if e.sha256_hash:
            extra.append("integrity hash")
        available.append(label + (f" ({', '.join(extra)})" if extra else ""))

    hints = list(CATEGORY_HINTS.get(category or "OTHER", CATEGORY_HINTS["OTHER"]))
    if "screenshot" not in blob and "image" not in blob:
        hints.insert(0, "Screenshot or photo of the original message/document")
    if "transaction" not in blob and ("upi" in description.lower() or "paid" in description.lower()):
        hints.append("Transaction record or bank SMS")

    already = blob
    potentially = [h for h in hints if h.split()[0].lower() not in already]
    if not potentially:
        potentially = ["A short dated written summary in your own words"]

    preserve = [
        "Keep originals. Do not crop out headers, numbers, or timestamps if you can avoid it.",
        "Compute and store an integrity hash in the vault (integrity aid, not a guarantee of legal admissibility).",
        "If location permission is on, attach it; if not, write the place in a note.",
    ]
    return GapResponse(
        available=available or ["No evidence items listed yet"],
        potentially_useful=potentially[:6],
        recommended_preservation=preserve,
        demo_mode=True,
    )
