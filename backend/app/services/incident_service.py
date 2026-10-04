import random
import string
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.schemas.incident import IncidentOut


def new_incident_id(now: Optional[datetime] = None) -> str:
    now = now or datetime.now(timezone.utc)
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"NYA-{now.year}-{suffix}"


class IncidentStore:
    def __init__(self) -> None:
        self._items: Dict[str, IncidentOut] = {}
        self._evidence_counts: Dict[str, int] = {}

    def create(
        self,
        title: str,
        category: str,
        secondary: List[str],
        severity: str,
        summary: Optional[str],
        analysis: Optional[Dict[str, Any]],
        lat: Optional[float],
        lng: Optional[float],
        status: str = "ACTIVE",
    ) -> IncidentOut:
        now = datetime.now(timezone.utc)
        item = IncidentOut(
            id=new_incident_id(now),
            title=title[:80] or "Untitled incident",
            category=category,
            secondary_categories=secondary,
            summary=summary,
            severity=severity,
            status=status,
            latitude=lat,
            longitude=lng,
            analysis=analysis,
            created_at=now,
            updated_at=now,
            evidence_count=0,
        )
        self._items[item.id] = item
        return item

    def get(self, incident_id: str) -> Optional[IncidentOut]:
        return self._items.get(incident_id)

    def list(self) -> List[IncidentOut]:
        return sorted(self._items.values(), key=lambda i: i.updated_at, reverse=True)

    def update_status(self, incident_id: str, status: str) -> Optional[IncidentOut]:
        item = self._items.get(incident_id)
        if not item:
            return None
        updated = item.model_copy(update={"status": status, "updated_at": datetime.now(timezone.utc)})
        self._items[incident_id] = updated
        return updated

    def bump_evidence(self, incident_id: str) -> None:
        item = self._items.get(incident_id)
        if not item:
            return
        self._items[incident_id] = item.model_copy(
            update={"evidence_count": item.evidence_count + 1, "updated_at": datetime.now(timezone.utc)}
        )


incident_store = IncidentStore()
