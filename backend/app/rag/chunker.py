from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LegalChunk:
    id: str
    document_id: str
    title: str
    section: str
    content: str
    source_name: str
    source_url: Optional[str]
    source_type: str
    verified_at: Optional[str]
    is_demo: bool = True
    embedding: Optional[List[float]] = field(default=None)
