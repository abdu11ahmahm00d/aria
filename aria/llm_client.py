import json
import re
import os
import time
from typing import Optional, Tuple
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
MAX_RETRIES = 5

GROQ_MODEL = "llama-3.1-8b-instant"


class ProviderError(Exception):
    def __init__(self, message: str, is_rate_limit: bool = False):
        super().__init__(message)
        self.is_rate_limit = is_rate_limit


def call_llm(
    prompt: str,
    model: str = "groq",
    temperature: float = 0.1,
    max_tokens: int = 2000,
) -> str:
    if os.getenv("ARIA_USE_MOCK_LLM") == "1":
        return "This is a mock LLM response for testing."

    provider = os.getenv("ARIA_LLM_PROVIDER", "groq")

    if provider == "groq" and GROQ_API_KEY:
        try:
            return _call_groq(prompt, temperature, max_tokens)
        except ProviderError as e:
            if e.is_rate_limit and GOOGLE_API_KEY:
                print(f"[ARIA] Groq rate limited, falling back to Gemini: {e}")
                return _call_gemini(prompt, temperature, max_tokens)
            raise

    if GOOGLE_API_KEY:
        return _call_gemini(prompt, temperature, max_tokens)

    if GROQ_API_KEY:
        return _call_groq(prompt, temperature, max_tokens)

    raise Exception("No LLM provider configured. Set GROQ_API_KEY or GOOGLE_API_KEY.")


def _parse_retry_after(msg: str) -> Optional[float]:
    m = re.search(r"retry in ([\d.]+)s", msg, re.IGNORECASE)
    if m:
        return float(m.group(1))
    m = re.search(r"retry in ([\d.]+) second", msg, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


def _call_groq(prompt: str, temperature: float, max_tokens: int) -> str:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                GROQ_URL,
                json={
                    "model": GROQ_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                timeout=120,
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()

            err_body = response.json().get("error", {})
            err_msg = err_body.get("message", str(response.status_code))
            is_rate_limit = response.status_code == 429
            is_tpm = "tokens per minute" in err_msg
            is_tpd = "tokens per day" in err_msg

            if is_rate_limit and not is_tpm:
                raise ProviderError(err_msg, is_rate_limit=True)

            wait = _parse_retry_after(err_msg) or float(2**attempt)
            wait = min(wait + 1, 120)
            print(
                f"Groq error {response.status_code} ({err_msg[:80]}). "
                f"Retry {attempt}/{MAX_RETRIES} in {wait:.0f}s..."
            )
            time.sleep(wait)

        except ProviderError:
            raise
        except Exception as e:
            wait = 2**attempt
            print(f"Groq error: {e}. Retry {attempt}/{MAX_RETRIES} in {wait}s...")
            time.sleep(wait)

    raise ProviderError(f"Groq API failed after {MAX_RETRIES} attempts.")


def _call_gemini(prompt: str, temperature: float, max_tokens: int) -> str:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                },
            }

            response = requests.post(
                f"{GEMINI_URL}?key={GOOGLE_API_KEY}", json=payload, timeout=120
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
                raise Exception("API returned no candidates")

            wait = 2**attempt
            print(
                f"Gemini error {response.status_code}. Retry {attempt}/{MAX_RETRIES} in {wait}s..."
            )
            time.sleep(wait)

        except Exception as e:
            wait = 2**attempt
            print(f"Gemini error: {e}. Retry {attempt}/{MAX_RETRIES} in {wait}s...")
            time.sleep(wait)

    raise Exception(f"Gemini API failed after {MAX_RETRIES} attempts.")


def _clean_json(raw: str) -> str:
    return re.sub(r"```(?:json)?\s*|\s*```", "", raw).strip()


def call_llm_json(
    prompt: str,
    model: str = "groq",
    retries: int = 2,
) -> Optional[dict]:
    if os.getenv("ARIA_USE_MOCK_LLM") == "1":
        return {"mock": "response"}

    for attempt in range(retries + 1):
        raw = call_llm(prompt, model=model)
        cleaned = _clean_json(raw)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            if attempt == retries:
                return None
    return None


def call_llm_json_array(
    prompt: str,
    model: str = "groq",
    retries: int = 2,
) -> list:
    if os.getenv("ARIA_USE_MOCK_LLM") == "1":
        return []

    for attempt in range(retries + 1):
        raw = call_llm(prompt, model=model)
        cleaned = _clean_json(raw)
        try:
            result = json.loads(cleaned)
            if isinstance(result, list):
                return result
            if isinstance(result, dict):
                return [result]
            return []
        except json.JSONDecodeError:
            if attempt == retries:
                return []
    return []
