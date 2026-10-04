from fastapi import APIRouter

from app.core.errors import ControlledError
from app.schemas.incident import IncidentCreate, IncidentOut, IncidentStatusUpdate
from app.services.incident_service import incident_store

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentOut)
async def create_incident(body: IncidentCreate):
    title = body.title or (body.user_statement[:72] if body.user_statement else "Untitled incident")
    return incident_store.create(
        title=title,
        category=body.category,
        secondary=body.secondary_categories,
        severity=body.severity,
        summary=body.user_statement[:400] if body.user_statement else None,
        analysis=body.analysis,
        lat=body.latitude,
        lng=body.longitude,
        status="ACTIVE",
    )


@router.get("", response_model=list[IncidentOut])
async def list_incidents():
    return incident_store.list()


@router.get("/{incident_id}", response_model=IncidentOut)
async def get_incident(incident_id: str):
    item = incident_store.get(incident_id)
    if not item:
        raise ControlledError(404, "Incident not found.", "NOT_FOUND", False)
    return item


@router.patch("/{incident_id}", response_model=IncidentOut)
async def patch_incident(incident_id: str, body: IncidentStatusUpdate):
    if body.status not in {"ACTIVE", "DRAFT", "RESOLVED", "ARCHIVED"}:
        raise ControlledError(400, "Invalid status.", "INVALID_STATUS", False)
    item = incident_store.update_status(incident_id, body.status)
    if not item:
        raise ControlledError(404, "Incident not found.", "NOT_FOUND", False)
    return item
