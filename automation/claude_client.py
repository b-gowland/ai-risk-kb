"""
Shared Claude API settings for the automation (monthly engine + weekly classifier).

Model routing:
  MODEL_OPUS   — accuracy-critical judgement (claim verification)
  MODEL_SONNET — extraction, classification, drafting

Both models always think (adaptive); thinking tokens count against max_tokens,
so budgets are generous (only tokens actually generated are billed) and depth
is controlled with `effort` instead.
"""

from __future__ import annotations

MODEL_OPUS = "claude-opus-5-5"
MODEL_SONNET = "claude-sonnet-5-5"

DEFAULT_MAX_TOKENS = 16000

# On a safety-classifier refusal, the API re-runs the request on a fallback
# model inside the same call. The installed SDK predates the `fallbacks`
# parameter, so it is sent via extra_body.
FALLBACK_BETA = "server-side-fallback-2026-07-01"


def message_kwargs(
    model: str,
    prompt: str,
    effort: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    system: str | None = None,
) -> dict:
    """Keyword arguments for client.beta.messages.create."""
    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        "output_config": {"effort": effort},
        "betas": [FALLBACK_BETA],
        "extra_body": {"fallbacks": "default"},
    }
    if system:
        kwargs["system"] = system
    return kwargs


def check_stop_reason(response) -> None:
    """Raise on responses whose text is unusable (refused or truncated)."""
    if response.stop_reason == "refusal":
        details = getattr(response, "stop_details", None)
        category = getattr(details, "category", None) if details else None
        raise RuntimeError(f"request refused by safety classifier (category={category})")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("response truncated at max_tokens")


def response_text(response) -> str:
    """Concatenate text blocks (responses may lead with thinking blocks)."""
    return "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )
