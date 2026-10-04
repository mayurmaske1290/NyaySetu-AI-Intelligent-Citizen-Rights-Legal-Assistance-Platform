from app.ai.demo_provider import DemoAIProvider
from app.ai.openai_compatible import OpenAICompatibleProvider
from app.ai.provider import LLMProvider
from app.core.config import settings


def get_llm_provider() -> LLMProvider:
    if settings.use_demo_llm:
        return DemoAIProvider()
    return OpenAICompatibleProvider()
