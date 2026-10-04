from app.services.confidence import label_from_score
from app.schemas.analysis import ConfidenceLabel


def test_uncertain():
    assert label_from_score(0.4, True) == ConfidenceLabel.UNCERTAIN


def test_verify_without_retrieval():
    assert label_from_score(0.9, False) == ConfidenceLabel.VERIFY_WITH_SOURCE


def test_well_established():
    assert label_from_score(0.9, True) == ConfidenceLabel.WELL_ESTABLISHED
