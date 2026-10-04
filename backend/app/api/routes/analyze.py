from fastapi import APIRouter

from app.ai.factory import get_llm_provider
from app.core.security import sanitize_text
from app.rag.retriever import format_context
from app.schemas.analysis import (
    AnalysisResponse,
    AnalyzeMediaRequest,
    AnalyzeTextRequest,
    AnalyzeVoiceRequest,
)
from app.services.incident_service import incident_store

router = APIRouter(prefix="/analyze", tags=["analyze"])


async def _run(
    text: str,
    language: str = "en",
    hint: str | None = None,
) -> AnalysisResponse:
    cleaned_text = sanitize_text(text or "")

    if not cleaned_text:
        from app.core.errors import ControlledError

        raise ControlledError(
            400,
            "Please describe what is happening, or review OCR text first.",
            "EMPTY_INPUT",
            False,
        )

    context = format_context(cleaned_text)

    provider = get_llm_provider()

    result = await provider.analyze_situation(
        cleaned_text,
        language=language or "en",
        category_hint=hint,
        retrieved_context=context,
    )

    title = (result.summary or "Legal incident")[:72]

    incident_store.create(
        title=title,
        category=result.primary_category,
        secondary=result.secondary_categories,
        severity=result.severity,
        summary=result.summary,
        analysis=result.model_dump(),
        lat=None,
        lng=None,
    )

    return result


@router.post("/text", response_model=AnalysisResponse)
async def analyze_text(body: AnalyzeTextRequest):
    return await _run(
        text=body.text,
        language=body.language,
        hint=body.category_hint,
    )


@router.post("/image", response_model=AnalysisResponse)
async def analyze_image(body: AnalyzeMediaRequest):
    extracted = body.extracted_text or ""
    notes = body.user_notes or ""

    combined = " ".join(
        part.strip()
        for part in (extracted, notes)
        if part and part.strip()
    )

    return await _run(
        text=combined,
        language=body.language,
        hint=None,
    )


@router.post("/document", response_model=AnalysisResponse)
async def analyze_document(body: AnalyzeMediaRequest):
    extracted = body.extracted_text or ""
    notes = body.user_notes or ""

    combined = " ".join(
        part.strip()
        for part in (extracted, notes)
        if part and part.strip()
    )

    hint = None

    if "notice" in combined.lower():
        hint = "LEGAL_NOTICE"

    return await _run(
        text=combined,
        language=body.language,
        hint=hint,
    )


@router.post("/voice-text", response_model=AnalysisResponse)
async def analyze_voice(body: AnalyzeVoiceRequest):
    return await _run(
        text=body.transcript,
        language=body.language,
        hint=None,
    )