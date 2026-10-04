from app.complaints.generator import generate_complaint
from app.schemas.complaint import ComplaintRequest


def test_complaint_is_draft():
    draft = generate_complaint(
        ComplaintRequest(
            user_statement="Asked for cash without receipt at a traffic stop.",
            category="BRIBE_DEMAND",
            evidence_names=["note.txt"],
        )
    )
    assert draft.must_review is True
    assert draft.never_auto_submit is True
    assert "DO NOT SUBMIT AUTOMATICALLY" in draft.body
