from abc import ABC, abstractmethod
from typing import List, Optional

from app.schemas.analysis import AnalysisResponse


class LLMProvider(ABC):
    """Provider-agnostic LLM interface. Do not couple the app to a single vendor."""

    name: str = "base"

    @abstractmethod
    async def analyze_situation(
        self,
        text: str,
        language: str = "en",
        category_hint: Optional[str] = None,
        retrieved_context: str = "",
    ) -> AnalysisResponse:
        raise NotImplementedError

    async def complete_json(self, system: str, user: str) -> str:
        raise NotImplementedError
