from fastapi import APIRouter

from app.rag.retriever import retriever

router = APIRouter(prefix="/legal", tags=["legal"])


@router.get("/sources")
async def legal_sources():
    return {"demo_mode": True, "sources": retriever.sources()}
