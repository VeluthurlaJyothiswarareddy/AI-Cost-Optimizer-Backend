import time
from typing import Any

import httpx

from app.config import settings
from app.services.cost_calculator import calculate_cost


class OpenRouterError(Exception):
    """Raised when OpenRouter API returns an error."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _build_budget_system_prompt(max_tokens: int) -> str:
    """Build a system instruction that guides the model to produce a complete,
    self-contained answer within the requested token budget instead of being
    hard-truncated mid-sentence.

    ~1 token is roughly 0.75 words. We target slightly under the budget so the
    model has room to finish on a complete sentence before hitting the cap.
    """
    target_words = max(1, int(max_tokens * 0.6))
    return (
        "You are a concise assistant. You have a strict output budget of about "
        f"{max_tokens} tokens (roughly {target_words} words). "
        "Plan your reply so it is a COMPLETE, self-contained answer that fits "
        "within this budget. Prioritize the most important information, be "
        "concise, and ALWAYS finish on a complete sentence. Do not get cut off "
        "mid-thought. If the topic is large, briefly summarize rather than "
        "starting a detailed explanation you cannot finish."
    )


class OpenRouterService:
    def __init__(self) -> None:
        self.base_url = settings.openrouter_base_url.rstrip("/")
        self.api_key = settings.openrouter_api_key

    async def chat_completion(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise OpenRouterError(
                "OPENROUTER_API_KEY is not configured. Set it in your .env file.",
                status_code=500,
            )

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": _build_budget_system_prompt(max_tokens)},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "AI Cost Optimizer POC",
        }

        start = time.perf_counter()

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
            except httpx.RequestError as exc:
                raise OpenRouterError(
                    f"Failed to connect to OpenRouter: {exc}",
                    status_code=503,
                ) from exc

        elapsed_ms = int((time.perf_counter() - start) * 1000)

        if response.status_code != 200:
            detail = response.text
            try:
                error_body = response.json()
                detail = error_body.get("error", {}).get("message", detail)
            except Exception:
                pass
            raise OpenRouterError(
                f"OpenRouter API error: {detail}",
                status_code=response.status_code,
            )

        data = response.json()
        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", input_tokens + output_tokens)

        content = ""
        choices = data.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "") or ""

        estimated_cost = calculate_cost(model, input_tokens, output_tokens)

        return {
            "response": content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost": estimated_cost,
            "response_time_ms": elapsed_ms,
        }

    async def chat_completion_with_messages(
        self,
        messages: list[dict[str, str]],
        model: str,
        max_tokens: int,
    ) -> dict[str, Any]:
        """Chat completion with custom messages (used by prefix cache feature)."""
        if not self.api_key:
            raise OpenRouterError(
                "OPENROUTER_API_KEY is not configured. Set it in your .env file.",
                status_code=500,
            )

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "AI Cost Optimizer POC",
        }

        start = time.perf_counter()

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
            except httpx.RequestError as exc:
                raise OpenRouterError(
                    f"Failed to connect to OpenRouter: {exc}",
                    status_code=503,
                ) from exc

        elapsed_ms = int((time.perf_counter() - start) * 1000)

        if response.status_code != 200:
            detail = response.text
            try:
                error_body = response.json()
                detail = error_body.get("error", {}).get("message", detail)
            except Exception:
                pass
            raise OpenRouterError(
                f"OpenRouter API error: {detail}",
                status_code=response.status_code,
            )

        data = response.json()
        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", input_tokens + output_tokens)

        content = ""
        choices = data.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "") or ""

        estimated_cost = calculate_cost(model, input_tokens, output_tokens)

        return {
            "response": content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost": estimated_cost,
            "response_time_ms": elapsed_ms,
        }


openrouter_service = OpenRouterService()
