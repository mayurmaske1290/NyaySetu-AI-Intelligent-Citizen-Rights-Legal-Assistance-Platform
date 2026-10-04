from __future__ import annotations

import json
import logging
from typing import Optional

import httpx

from app.ai.json_validator import parse_analysis_json
from app.ai.provider import LLMProvider
from app.core.config import settings
from app.core.errors import ControlledError
from app.schemas.analysis import AnalysisResponse

logger = logging.getLogger(__name__)


SYSTEM = """
You are NyaySetu AI, an AI-powered rights and evidence protection assistant
for people in India.

You are NOT a lawyer.

Your job is to analyze the user's incident and return structured information.

IMPORTANT:
- Return ONLY one valid JSON object.
- Do NOT use Markdown.
- Do NOT use ```json.
- Do NOT write explanations outside JSON.
- Do NOT invent laws, sections, penalties, phone numbers, addresses,
  government URLs, or legal claims.
- If something is uncertain, say so in the appropriate field.
- Analyze the actual user input. Do NOT copy example values.
- Do not assume the category is TRAFFIC_STOP.
- Detect ALL relevant categories.

Allowed primary categories:
TRAFFIC_STOP
BRIBE_DEMAND
SCAM
THREAT_HARASSMENT
LEGAL_NOTICE
OTHER

Allowed secondary categories:
TRAFFIC_STOP
BRIBE_DEMAND
SCAM
THREAT_HARASSMENT
LEGAL_NOTICE
OTHER

Allowed severity:
LOW
MEDIUM
HIGH

Allowed confidence labels:
WELL_ESTABLISHED
VERIFY_WITH_SOURCE
UNCERTAIN

The response MUST contain these fields:

{
  "primary_category": "one allowed category",
  "secondary_categories": [],
  "severity": "LOW/MEDIUM/HIGH",
  "confidence": 0.0,
  "confidence_label": "WELL_ESTABLISHED/VERIFY_WITH_SOURCE/UNCERTAIN",
  "summary": "short summary",
  "rights": [],
  "what_not_to_do": [],
  "action_steps": [],
  "evidence_to_preserve": [],
  "evidence_gaps": [],
  "sources": [],
  "requires_human_help": false,
  "safety_notes": "",
  "disclaimer": "This is informational assistance, not legal advice. NyaySetu AI is not a replacement for a lawyer. Verify uncertain points with a legal professional or a legitimate authority.",
  "demo_mode": false,
  "language": "en"
}

rights items MUST use:

{
  "title": "",
  "explanation": "",
  "why": "",
  "source_title": "",
  "source_url": ""
}

what_not_to_do items MUST use:

{
  "warning": "",
  "reason": ""
}

action_steps items MUST use:

{
  "order": 1,
  "text": "",
  "kind": "immediate"
}

evidence_to_preserve items MUST use:

{
  "item": "",
  "reason": ""
}

evidence_gaps items MUST use:

{
  "item": "",
  "why_useful": "",
  "status": "potentially_useful"
}

sources items MUST use:

{
  "title": "",
  "url": "",
  "source_type": "ai",
  "verified": false,
  "demo": false
}

If no reliable source URL is available, use an empty string.

The user input is the source of truth.
"""


class OpenAICompatibleProvider(LLMProvider):
    name = "openai_compatible"

    def __init__(self) -> None:
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.base_url = settings.llm_base_url.rstrip("/")

    async def complete_json(self, system: str, user: str) -> str:

        if not self.api_key:
            raise ControlledError(
                500,
                "LLM API key is not configured.",
                "AI_NOT_CONFIGURED",
                False,
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        payload = {
            "model": self.model,
            "temperature": 0.0,

            # IMPORTANT:
            # This was missing from the real provider.
            # Your standalone test already proved this works.
            "response_format": {
                "type": "json_object"
            },

            "messages": [
                {
                    "role": "system",
                    "content": system,
                },
                {
                    "role": "user",
                    "content": user,
                },
            ],
        }

        logger.info(
            "Calling LLM model=%s url=%s",
            self.model,
            self.base_url,
        )

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )

                logger.info("LLM response status=%s", response.status_code)

                # Some OpenAI-compatible/free models reject response_format.
                # Retry once without it instead of making the whole analysis fail.
                if response.status_code in (400, 404, 422) and "response_format" in payload:
                    retry_payload = dict(payload)
                    retry_payload.pop("response_format", None)
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=retry_payload,
                    )
                    logger.info("LLM retry without response_format status=%s", response.status_code)

                response.raise_for_status()

        except httpx.TimeoutException as exc:

            logger.exception("LLM timeout")

            raise ControlledError(
                504,
                "The AI service timed out. Retry or continue offline.",
                "AI_TIMEOUT",
                True,
            ) from exc

        except httpx.HTTPStatusError as exc:

            logger.exception(
                "LLM HTTP error: %s",
                exc.response.text[:2000],
            )

            raise ControlledError(
                502,
                "The AI service returned an error.",
                "AI_UNAVAILABLE",
                True,
            ) from exc

        except httpx.HTTPError as exc:

            logger.exception("LLM connection error")

            raise ControlledError(
                502,
                "The AI service is unavailable. Retry or use offline guidance.",
                "AI_UNAVAILABLE",
                True,
            ) from exc

        try:
            data = response.json()

        except ValueError as exc:

            logger.exception(
                "LLM returned non-JSON HTTP response"
            )

            raise ControlledError(
                502,
                "The AI service returned an invalid response.",
                "AI_BAD_RESPONSE",
                True,
            ) from exc

        try:
            content = data["choices"][0]["message"]["content"]

        except (KeyError, IndexError, TypeError) as exc:

            logger.error(
                "Unexpected LLM response: %s",
                json.dumps(data, ensure_ascii=False)[:4000],
            )

            raise ControlledError(
                502,
                "The AI service returned an unexpected response.",
                "AI_BAD_RESPONSE",
                True,
            ) from exc

        if isinstance(content, list):
            parts = []

            for item in content:
                if isinstance(item, dict) and item.get("text"):
                    parts.append(str(item["text"]))

            content = "".join(parts)

        if not isinstance(content, str) or not content.strip():
            refusal = data.get("choices", [{}])[0].get("message", {}).get("refusal")
            detail = "The AI service returned no usable analysis."
            if refusal:
                detail = f"The AI service refused the request: {refusal}"
            raise ControlledError(502, detail, "AI_EMPTY_RESPONSE", True)

        logger.info(
            "LLM content received (%d chars)",
            len(content),
        )

        return content


    async def analyze_situation(
        self,
        text: str,
        language: str = "en",
        category_hint: Optional[str] = None,
        retrieved_context: str = "",
    ) -> AnalysisResponse:

        user = json.dumps(
            {
                "user_input": text,
                "language": language,
                "category_hint": category_hint,
                "retrieved_context": retrieved_context,
            },
            ensure_ascii=False,
        )

        # First attempt
        raw = await self.complete_json(
            SYSTEM,
            user,
        )

        logger.debug(
            "First analysis response: %s",
            raw[:4000],
        )

        parsed = parse_analysis_json(raw)

        if parsed:
            return parsed

        # Second attempt with explicit correction request
        repair_system = SYSTEM + """

Your previous response was invalid.

Return the complete analysis again.

Requirements:
- Valid JSON object only.
- No Markdown.
- Use only the allowed category values.
- Include every required field.
- Use arrays for list fields.
- confidence must be between 0 and 1.
"""

        raw2 = await self.complete_json(
            repair_system,
            user,
        )

        logger.debug(
            "Second analysis response: %s",
            raw2[:4000],
        )

        parsed2 = parse_analysis_json(raw2)

        if parsed2:
            return parsed2

        logger.error(
            "AI response could not be validated."
        )

        raise ControlledError(
            422,
            "The AI response could not be validated. Retry, or continue with offline guidance.",
            "AI_JSON_INVALID",
            True,
        )