from typing import List, Tuple

from app.rag.chunker import LegalChunk
from app.rag.demo_knowledge import DEMO_CHUNKS
from app.rag.embeddings import cosine, embed_text


class DemoLegalKnowledgeProvider:
    def __init__(self) -> None:
        self.chunks: List[LegalChunk] = []
        for c in DEMO_CHUNKS:
            c.embedding = embed_text(f"{c.title} {c.content}")
            self.chunks.append(c)

    def search(self, query: str, k: int = 5) -> List[Tuple[LegalChunk, float]]:
        q = embed_text(query)
        scored = [(c, cosine(q, c.embedding or [])) for c in self.chunks]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def sources(self) -> List[dict]:
        docs = {}
        for c in self.chunks:
            docs[c.document_id] = {
                "id": c.document_id,
                "title": c.title,
                "source_name": c.source_name,
                "source_url": c.source_url,
                "source_type": c.source_type,
                "is_demo": c.is_demo,
            }
        return list(docs.values())


retriever = DemoLegalKnowledgeProvider()


def format_context(query: str, k: int = 4) -> str:
    hits = retriever.search(query, k=k)
    lines = ["DEMO RETRIEVED KNOWLEDGE — not verified statutory text:"]
    for chunk, score in hits:
        lines.append(f"[{chunk.id} score={score:.2f} DEMO] {chunk.title}: {chunk.content}")
    return "\n".join(lines)
