from typing import List, Optional

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    id: Optional[str] = None
    file_name: str
    file_type: str
    description: str = ""
    source_type: str = "note"
    sha256_hash: Optional[str] = None
    has_location: bool = False
    has_timestamp: bool = True


class GapRequest(BaseModel):
    incident_id: Optional[str] = None
    description: str
    category: Optional[str] = None
    evidence: List[EvidenceItem] = Field(default_factory=list)


class GapResponse(BaseModel):
    available: List[str]
    potentially_useful: List[str]
    recommended_preservation: List[str]
    language_note: str = (
        "These are potentially useful items to preserve. "
        "This is not a statement that you legally need this evidence."
    )
    demo_mode: bool = True


class TimelineEvent(BaseModel):
    event_time: Optional[str] = None
    label: str
    inferred: bool = False
    evidence_id: Optional[str] = None


class TimelineRequest(BaseModel):
    description: str
    evidence: List[EvidenceItem] = Field(default_factory=list)


class TimelineResponse(BaseModel):
    events: List[TimelineEvent]
    note: str = "Times are shown only when provided. Inferred events are marked and are not invented clock times."
    demo_mode: bool = True


class ClaimMapRequest(BaseModel):
    description: str
    claims: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)


class ClaimLink(BaseModel):
    claim: str
    evidence_names: List[str]
    status: str
    note: str = "Supports the described event. This does not prove a legal conclusion."


class ClaimMapResponse(BaseModel):
    mappings: List[ClaimLink]
    demo_mode: bool = True


class ActionSafetyRequest(BaseModel):
    planned_action: str
    situation: str = ""
    category: Optional[str] = None


class ActionSafetyResponse(BaseModel):
    title: str = "Pause & Verify"
    appears_to_plan: str
    risk_why: str
    safer_step: str
    demo_mode: bool = True
