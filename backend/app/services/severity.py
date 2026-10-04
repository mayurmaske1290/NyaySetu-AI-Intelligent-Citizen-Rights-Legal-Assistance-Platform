from app.schemas.analysis import Category, Severity


def fuse_severity(categories: list[str], text: str) -> str:
    t = text.lower()
    high_words = ("kill", "weapon", "hurt you", "don't tell anyone", "now or", "last warning")
    if any(w in t for w in high_words) or Category.THREAT_HARASSMENT in categories:
        if Category.THREAT_HARASSMENT in categories:
            return Severity.HIGH
    if Category.BRIBE_DEMAND in categories:
        return Severity.HIGH
    if Category.SCAM in categories:
        if any(k in t for k in ("otp", "transfer", "paid", "sent money", "remote")):
            return Severity.HIGH
        return Severity.MEDIUM
    if Category.LEGAL_NOTICE in categories:
        return Severity.MEDIUM
    if Category.TRAFFIC_STOP in categories:
        return Severity.MEDIUM
    return Severity.LOW
