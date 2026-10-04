from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "nyaysetu-ai",
        "demo_mode": settings.use_demo_llm,
        "disclaimer": "Informational assistance only. Not legal advice.",
    }
