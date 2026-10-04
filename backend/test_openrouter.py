import asyncio
import httpx
from app.core.config import settings

async def test():
    print("=== OPENROUTER TEST ===")
    print("API key loaded:", bool(settings.llm_api_key))
    print("Model:", settings.llm_model)
    print("URL:", settings.llm_base_url)

    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.llm_model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": "Return valid JSON only."
            },
            {
                "role": "user",
                "content": "Return a JSON object saying hello."
            }
        ],
    }

    print("Sending request...")

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                f"{settings.llm_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )

        print("STATUS:", response.status_code)
        print("RESPONSE:")
        print(response.text)

    except Exception as e:
        print("ERROR:", type(e).__name__)
        print("DETAIL:", str(e))

if __name__ == "__main__":
    asyncio.run(test())
