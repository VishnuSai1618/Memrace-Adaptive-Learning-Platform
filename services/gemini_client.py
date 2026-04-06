"""
Gemini API Client Utility
=========================
Centralised wrapper around google-generativeai that supports multiple API keys
with automatic quota-error retry using a different key.

Usage
-----
    from services.gemini_client import call_gemini

    response = call_gemini(prompt="Explain quantum computing")
    text = response.text

Configuration (in .env)
-----------------------
    # Single key (original behaviour – fully backward compatible):
    GEMINI_API_KEY=your_key_here

    # Multiple keys (comma-separated):
    GEMINI_API_KEYS=key1,key2,key3
"""

import os
import random
import logging

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ── Key Loading ────────────────────────────────────────────────────────────────

def get_gemini_api_keys() -> list[str]:
    """
    Return an ordered list of available Gemini API keys.

    Priority:
      1. GEMINI_API_KEYS  – comma-separated multi-key string
      2. GEMINI_API_KEY   – single legacy key (backward-compatible)

    Returns:
        List of non-empty key strings.

    Raises:
        ValueError: If no keys are found in the environment.
    """
    multi = os.getenv("GEMINI_API_KEYS", "").strip()
    if multi:
        keys = [k.strip() for k in multi.split(",") if k.strip()]
        if keys:
            logger.info(f"[gemini_client] Loaded {len(keys)} API key(s) from GEMINI_API_KEYS")
            return keys

    single = os.getenv("GEMINI_API_KEY", "").strip()
    if single:
        logger.info("[gemini_client] Loaded 1 API key from GEMINI_API_KEY")
        return [single]

    raise ValueError(
        "No Gemini API key found. Set GEMINI_API_KEY or GEMINI_API_KEYS in your .env file."
    )


# ── Key Selection ──────────────────────────────────────────────────────────────

def _pick_key(exclude: str | None = None) -> str:
    """
    Randomly select an API key, optionally excluding one (for retry logic).

    Args:
        exclude: A key string to exclude from selection (used during retry).

    Returns:
        A selected API key string.

    Raises:
        ValueError: If no alternative key is available after exclusion.
    """
    keys = get_gemini_api_keys()

    if exclude:
        alternatives = [k for k in keys if k != exclude]
        if alternatives:
            return random.choice(alternatives)
        # Only one key available; must reuse it
        logger.warning("[gemini_client] Only one API key available — cannot rotate for retry.")
        return keys[0]

    return random.choice(keys)


# ── Core Call ──────────────────────────────────────────────────────────────────

def call_gemini(
    prompt: str,
    model_name: str = "gemini-2.5-flash",
    generation_config: dict | None = None,
) -> genai.types.GenerateContentResponse:
    """
    Call the Gemini API with automatic quota-error retry using a different key.

    Retry policy:
      - On a 429 / ResourceExhausted error, select a different key and retry once.
      - All other errors propagate immediately.
      - No infinite retry loops.

    Args:
        prompt:            The text prompt to send.
        model_name:        Gemini model to use (default: gemini-2.5-flash).
        generation_config: Optional GenerationConfig dict passed to the model.

    Returns:
        A GenerateContentResponse from the Gemini API.

    Raises:
        Exception: Propagated from the Gemini SDK after retries are exhausted.
    """
    first_key = _pick_key()
    return _call_with_key(prompt, first_key, model_name, generation_config, attempt=1)


def _call_with_key(
    prompt: str,
    api_key: str,
    model_name: str,
    generation_config: dict | None,
    attempt: int,
) -> genai.types.GenerateContentResponse:
    """Internal call that handles the single-retry fallback."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)

        kwargs = {}
        if generation_config:
            kwargs["generation_config"] = generation_config

        return model.generate_content(prompt, **kwargs)

    except Exception as exc:
        error_str = str(exc).lower()
        is_quota_error = (
            "429" in error_str
            or "resource_exhausted" in error_str
            or "quota" in error_str
            or "rate limit" in error_str
        )

        if is_quota_error and attempt == 1:
            fallback_key = _pick_key(exclude=api_key)
            logger.warning(
                f"[gemini_client] Quota error on attempt 1. "
                f"Retrying with {'a different' if fallback_key != api_key else 'the same (only)'} key."
            )
            return _call_with_key(prompt, fallback_key, model_name, generation_config, attempt=2)

        # Not a quota error, or this was already the retry — propagate
        raise
