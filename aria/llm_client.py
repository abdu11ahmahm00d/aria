import json
import re
import os
import time
from typing import Optional
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
MAX_RETRIES = 10


def call_llm(
    prompt: str,
    model: str = "gemini-2.5-flash",
    temperature: float = 0.1,
    max_tokens: int = 2000,
) -> str:
    if os.getenv("ARIA_USE_MOCK_LLM") == "1":
        return "This is a mock LLM response for testing."

    if not GOOGLE_API_KEY:
        raise Exception("GOOGLE_API_KEY is not set")

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
            "responseMimeType": "application/json"
            if "JSON" in prompt.upper()
            else "text/plain",
        },
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                f"{MODEL_URL}?key={GOOGLE_API_KEY}", json=payload, timeout=30
            )

            if response.status_code == 200:
                candidates = response.json().get("candidates", [])
                if candidates:
                    content = (
                        candidates[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text")
                    )
                    if content is None:
                        raise Exception("API returned empty content")
                    return content.strip()
                else:
                    raise Exception("API returned no candidates")

            elif response.status_code == 429:
                wait_time = 2 ** attempt
                print(
                    f"Rate limit (429). Retry {attempt}/{MAX_RETRIES} in {wait_time}s..."
                )
                time.sleep(wait_time)

            else:
                wait_time = 2 ** attempt
                print(
                    f"API error {response.status_code}. Retry {attempt}/{MAX_RETRIES} in {wait_time}s..."
                )
                time.sleep(wait_time)

        except (requests.exceptions.RequestException, Exception) as e:
            wait_time = 2 ** attempt
            print(
                f"Connection issue: {e}. Retry {attempt}/{MAX_RETRIES} in {wait_time}s..."
            )
            time.sleep(wait_time)

    raise Exception(
        f"Google AI Studio API failed after {MAX_RETRIES} attempts."
    )


def call_llm_json(
    prompt: str,
    model: str = "gemini-2.5-flash",
    retries: int = 2,
) -> Optional[dict]:
    if os.getenv("ARIA_USE_MOCK_LLM") == "1":
        return {"mock": "response"}

    for attempt in range(retries + 1):
        raw = call_llm(prompt, model=model)
        cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            if attempt == retries:
                return None
    return None
