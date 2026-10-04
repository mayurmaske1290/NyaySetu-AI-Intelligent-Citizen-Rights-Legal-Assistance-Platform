from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    title: Optional[str] = None
    category: str = "OTHER"
    secondary_categories: List[str] = Field(default_factory=list)
    user_statement: str = ""
    severity: str = "MEDIUM"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    analysis: Optional[Dict[str, Any]] = None


class IncidentOut(BaseModel):
    id: str
    title: str
    category: str
    secondary_categories: List[str]
    summary: Optional[str] = None
    severity: str
    status: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    analysis: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    evidence_count: int = 0


class IncidentStatusUpdate(BaseModel):
    status: str
