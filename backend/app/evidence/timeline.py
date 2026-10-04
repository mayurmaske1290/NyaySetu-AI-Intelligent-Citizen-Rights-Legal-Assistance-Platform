import re
from typing import List

from app.schemas.evidence import TimelineEvent, TimelineRequest, TimelineResponse


TIME_RE = re.compile(r"\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b")


def generate_timeline(req: TimelineRequest) -> TimelineResponse:
    events: List[TimelineEvent] = []
    times = TIME_RE.findall(req.description)
    sentences = [s.strip() for s in re.split(r"[.!?]\n?", req.description) if s.strip()]
    for i, sentence in enumerate(sentences[:8]):
        t = times[i] if i < len(times) else None
        events.append(
            TimelineEvent(
                event_time=t,
                label=sentence[:180],
                inferred=t is None,
                evidence_id=None,
            )
        )
    for e in req.evidence:
        events.append(
            TimelineEvent(
                event_time=None,
                label=f"Evidence saved: {e.file_name}",
                inferred=True,
                evidence_id=e.id,
            )
        )
    if not events:
        events.append(TimelineEvent(event_time=None, label="Incident described; exact times were not provided.", inferred=True))
    return TimelineResponse(events=events, demo_mode=True)
