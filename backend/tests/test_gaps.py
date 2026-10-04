from app.evidence.gap_detector import detect_gaps
from app.schemas.evidence import EvidenceItem


def test_gaps_scam():
    res = detect_gaps(
        "UPI scam message",
        "SCAM",
        [EvidenceItem(file_name="shot.png", file_type="image/png", source_type="screenshot", has_timestamp=True)],
    )
    assert res.available
    assert res.potentially_useful
    assert "not a statement that you legally need" in res.language_note.lower()
