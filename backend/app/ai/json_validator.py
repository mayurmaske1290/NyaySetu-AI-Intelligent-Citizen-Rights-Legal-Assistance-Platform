import json
import logging
import re
from typing import Optional

from pydantic import ValidationError

from app.schemas.analysis import AnalysisResponse

logger = logging.getLogger(__name__)


def extract_json_object(raw: str) -> Optional[str]:
    """
    Extract the first valid JSON object from an LLM response.

    Handles:
    - plain JSON
    - ```json ... ```
    - extra text before/after JSON
    """

    if not raw:
        return None

    raw = raw.strip()

    # Remove markdown code fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)

    # First try the entire response
    try:
        parsed = json.loads(raw)

        if isinstance(parsed, dict):
            return json.dumps(parsed, ensure_ascii=False)

    except json.JSONDecodeError:
        pass

    # Find JSON object boundaries
    start = raw.find("{")

    if start == -1:
        return None

    # Try every closing brace from the end backwards.
    # This is more reliable than simply using rfind().
    for end in range(len(raw) - 1, start, -1):

        if raw[end] != "}":
            continue

        candidate = raw[start:end + 1]

        try:
            parsed = json.loads(candidate)

            if isinstance(parsed, dict):
                return json.dumps(parsed, ensure_ascii=False)

        except json.JSONDecodeError:
            continue

    return None


def _normalise_analysis_data(data: dict) -> dict:
    """
    Safely normalise common LLM formatting mistakes before
    Pydantic validation.
    """

    # Required list fields
    list_fields = [
        "secondary_categories",
        "rights",
        "what_not_to_do",
        "action_steps",
        "evidence_to_preserve",
        "evidence_gaps",
        "sources",
    ]

    for field in list_fields:
        value = data.get(field)

        if value is None:
            data[field] = []

        elif not isinstance(value, list):
            data[field] = [value]

    # Required strings
    string_fields = [
        "primary_category",
        "severity",
        "confidence_label",
        "summary",
        "safety_notes",
        "language",
    ]

    for field in string_fields:
        value = data.get(field)

        if value is None:
            data[field] = ""

        elif not isinstance(value, str):
            data[field] = str(value)

    # Confidence
    confidence = data.get("confidence", 0.5)

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.5

    data["confidence"] = max(0.0, min(1.0, confidence))

    # Booleans
    for field in ["requires_human_help", "demo_mode"]:
        value = data.get(field)

        if isinstance(value, str):
            data[field] = value.lower() in {
                "true",
                "1",
                "yes",
            }
        elif value is None:
            data[field] = False

    # Disclaimer
    if not data.get("disclaimer"):
        data["disclaimer"] = (
            "This is informational assistance, not legal advice. "
            "NyaySetu AI is not a replacement for a lawyer. "
            "Verify uncertain points with a legal professional or "
            "a legitimate authority."
        )

    return data


def parse_analysis_json(raw: str) -> Optional[AnalysisResponse]:
    """
    Convert an LLM response into a validated AnalysisResponse.
    """

    blob = extract_json_object(raw)

    if not blob:
        logger.warning("LLM response did not contain valid JSON.")
        logger.warning("RAW RESPONSE: %r", raw[:2000] if raw else raw)
        return None

    try:
        data = json.loads(blob)

        if not isinstance(data, dict):
            logger.warning("LLM JSON root is not an object.")
            return None

        data = _normalise_analysis_data(data)

        return AnalysisResponse.model_validate(data)

    except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        logger.warning("Invalid analysis JSON: %s", exc)
        logger.warning("PARSED DATA: %s", blob[:4000])
        return None