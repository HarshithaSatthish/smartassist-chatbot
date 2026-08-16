import logging
import os
import re
import string
from pathlib import Path
from typing import Optional, Tuple

import httpx
from dotenv import load_dotenv

from app.responses import (
    AI_FALLBACK_REPLY,
    FAQ_RULES,
    GREETING_FILLERS,
    GREETING_PHRASES,
    GREETING_REPLY,
    MISSING_API_KEY_REPLY,
)

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are SmartAssist, a helpful, concise AI assistant. "
    "Give clear beginner-friendly answers. Keep replies reasonably short."
)


def get_ai_settings():
    """Read AI settings from .env on every call so key changes apply after save."""
    load_dotenv(ENV_PATH, override=True)
    return {
        "api_key": os.getenv("AI_API_KEY", "").strip(),
        "base_url": os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        "model": os.getenv("AI_MODEL", "gpt-4o-mini"),
        "timeout": float(os.getenv("AI_TIMEOUT", "30")),
    }


def normalize_input(message: str) -> str:
    """Lowercase, trim, remove punctuation, and collapse extra spaces."""
    text = message.lower().strip()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text)
    return text


def contains_keyword(normalized: str, keyword: str) -> bool:
    """Match whole words for short keywords so 'hi' does not match 'this'."""
    if " " in keyword:
        return keyword in normalized
    return keyword in normalized.split()


def _is_pure_greeting(normalized: str) -> bool:
    """Match greetings like 'Hi there!' but not 'Hi, explain machine learning'."""
    if not normalized:
        return False

    has_greeting = any(contains_keyword(normalized, phrase) for phrase in GREETING_PHRASES)
    if not has_greeting:
        return False

    leftover = normalized
    # Remove longer phrases first so "good morning" is not left as leftover words.
    for phrase in sorted(GREETING_PHRASES, key=len, reverse=True):
        leftover = leftover.replace(phrase, " ")

    leftover_tokens = [
        token
        for token in leftover.split()
        if token and token not in GREETING_FILLERS
    ]
    return len(leftover_tokens) == 0


def find_predefined_response(message: str) -> Optional[str]:
    """Return a saved reply if the message matches an FAQ or greeting."""
    normalized = normalize_input(message)
    if not normalized:
        return None

    for rule in FAQ_RULES:
        for keyword in rule["keywords"]:
            if contains_keyword(normalized, keyword):
                return rule["reply"]

    if _is_pure_greeting(normalized):
        return GREETING_REPLY

    return None


async def ask_ai(message: str) -> str:
    """
    Call an OpenAI-compatible chat API.

    Change AI_BASE_URL and AI_MODEL in .env to switch providers
    (OpenAI, Groq, and similar services).
    """
    settings = get_ai_settings()
    if not settings["api_key"]:
        logger.warning("AI_API_KEY is missing. Skipping AI fallback.")
        return MISSING_API_KEY_REPLY

    url = f"{settings['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings["model"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        "max_tokens": 500,
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient(timeout=settings["timeout"]) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            if not content:
                return AI_FALLBACK_REPLY
            return content
    except httpx.TimeoutException:
        logger.error("AI API request timed out.")
        return AI_FALLBACK_REPLY
    except httpx.HTTPStatusError as error:
        logger.error(
            "AI API returned HTTP %s: %s",
            error.response.status_code,
            error.response.text[:300],
        )
        return AI_FALLBACK_REPLY
    except (httpx.RequestError, KeyError, IndexError, ValueError) as error:
        logger.error("AI API request failed: %s", error)
        return AI_FALLBACK_REPLY


async def process_message(message: str) -> Tuple[str, str]:
    """
    Main chatbot flow:
    1. Normalize input
    2. Check predefined responses
    3. Fall back to the AI API
    """
    predefined = find_predefined_response(message)
    if predefined:
        return predefined, "predefined"

    ai_reply = await ask_ai(message)
    return ai_reply, "ai"
