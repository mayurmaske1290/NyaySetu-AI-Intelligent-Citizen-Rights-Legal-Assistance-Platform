from app.schemas.analysis import ConfidenceLabel


def label_from_score(score: float, has_retrieved: bool) -> str:
    if score < 0.55:
        return ConfidenceLabel.UNCERTAIN
    if score < 0.75 or not has_retrieved:
        return ConfidenceLabel.VERIFY_WITH_SOURCE
    return ConfidenceLabel.WELL_ESTABLISHED
