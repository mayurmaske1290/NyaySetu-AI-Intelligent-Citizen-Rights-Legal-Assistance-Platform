from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Category:
    TRAFFIC_STOP = "TRAFFIC_STOP"
    BRIBE_DEMAND = "BRIBE_DEMAND"
    SCAM = "SCAM"
    THREAT_HARASSMENT = "THREAT_HARASSMENT"
    LEGAL_NOTICE = "LEGAL_NOTICE"
    OTHER = "OTHER"
    ALL = {
        TRAFFIC_STOP,
        BRIBE_DEMAND,
        SCAM,
        THREAT_HARASSMENT,
        LEGAL_NOTICE,
        OTHER,
    }


class Severity:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    ALL = {LOW, MEDIUM, HIGH}


class ConfidenceLabel:
    WELL_ESTABLISHED = "WELL_ESTABLISHED"
    VERIFY_WITH_SOURCE = "VERIFY_WITH_SOURCE"
    UNCERTAIN = "UNCERTAIN"
    ALL = {WELL_ESTABLISHED, VERIFY_WITH_SOURCE, UNCERTAIN}


class RightItem(BaseModel):
    title: str
    explanation: str
    why: str
    source_title: Optional[str] = None
    source_url: Optional[str] = None


class WarningItem(BaseModel):
    warning: str
    reason: str


class ActionStep(BaseModel):
    order: int
    text: str
    kind: str

    @field_validator("kind")
    @classmethod
    def kind_ok(cls, v: str) -> str:
        allowed = {"immediate", "evidence", "verification", "escalation", "professional"}
        if v not in allowed:
            raise ValueError("invalid action kind")
        return v


class EvidenceHint(BaseModel):
    item: str
    reason: str


class EvidenceGap(BaseModel):
    item: str
    why_useful: str
    status: str = "potentially_useful"


class SourceRef(BaseModel):
    title: str
    url: Optional[str] = None
    source_type: str = "demo"
    verified: bool = False
    demo: bool = True


class AnalysisResponse(BaseModel):
    primary_category: str
    secondary_categories: List[str] = Field(default_factory=list)
    severity: str
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_label: str
    summary: str
    rights: List[RightItem] = Field(default_factory=list)
    what_not_to_do: List[WarningItem] = Field(default_factory=list)
    action_steps: List[ActionStep] = Field(default_factory=list)
    evidence_to_preserve: List[EvidenceHint] = Field(default_factory=list)
    evidence_gaps: List[EvidenceGap] = Field(default_factory=list)
    sources: List[SourceRef] = Field(default_factory=list)
    requires_human_help: bool = False
    safety_notes: str = ""
    disclaimer: str = (
        "This is informational assistance, not legal advice. "
        "NyaySetu AI is not a replacement for a lawyer. "
        "Verify uncertain points with a legal professional or a legitimate authority."
    )
    demo_mode: bool = True
    language: str = "en"

    @field_validator("primary_category")
    @classmethod
    def cat_ok(cls, v: str) -> str:
        if v not in Category.ALL:
            raise ValueError("invalid category")
        return v

    @field_validator("severity")
    @classmethod
    def sev_ok(cls, v: str) -> str:
        if v not in Severity.ALL:
            raise ValueError("invalid severity")
        return v

    @field_validator("confidence_label")
    @classmethod
    def conf_ok(cls, v: str) -> str:
        if v not in ConfidenceLabel.ALL:
            raise ValueError("invalid confidence")
        return v


class AnalyzeTextRequest(BaseModel):
    text: str
    language: str = "en"
    category_hint: Optional[str] = None
    incident_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AnalyzeMediaRequest(BaseModel):
    extracted_text: str = ""
    user_notes: str = ""
    language: str = "en"
    source_type: str = "image"
    incident_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AnalyzeVoiceRequest(BaseModel):
    transcript: str
    language: str = "en"
    incident_id: Optional[str] = None
