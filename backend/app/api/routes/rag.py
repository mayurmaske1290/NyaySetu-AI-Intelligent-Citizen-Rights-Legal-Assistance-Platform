from pydantic import BaseModel
from fastapi import APIRouter

from app.rag.retriever import retriever

router = APIRouter(prefix="/rag", tags=["rag"])


class SearchBody(BaseModel):
    query: str
    k: int = 5


@router.post("/search")
async def rag_search(body: SearchBody):
    hits = retriever.search(body.query, k=min(body.k, 8))
    return {
        "demo_mode": True,
        "warning": "Retrieved chunks are DEMO DATA unless replaced with verified sources.",
        "results": [
            {
                "id": c.id,
                "title": c.title,
                "content": c.content,
                "score": round(score, 4),
                "is_demo": c.is_demo,
                "source_name": c.source_name,
                "source_url": c.source_url,
            }
            for c, score in hits
        ],
    }
