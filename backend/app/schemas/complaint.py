from typing import List, Optional

from pydantic import BaseModel, Field


class ComplaintRequest(BaseModel):
    incident_id: Optional[str] = None
    user_statement: str
    date: Optional[str] = None
    time: Optional[str] = None
    location_text: Optional[str] = None
    evidence_names: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    retrieved_context: Optional[str] = None


class ComplaintDraft(BaseModel):
    subject: str
    incident_summary: str
    detailed_description: str
    evidence_list: List[str]
    requested_action: str
    recipient_category: str
    body: str
    must_review: bool = True
    never_auto_submit: bool = True
    demo_mode: bool = True
