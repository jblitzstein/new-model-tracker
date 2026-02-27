"""OpenRouter API client — fetches commercial/frontier models."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import httpx

from collector.config import resolve_provider_name
from collector.models import Model

logger = logging.getLogger(__name__)

API_URL = "https://openrouter.ai/api/v1/models"


def _parse_modalities(arch: dict | None) -> tuple[list[str], list[str]]:
    if not arch:
        return ["text"], ["text"]
    input_mods = arch.get("input_modalities") or ["text"]
    output_mods = arch.get("output_modalities") or ["text"]
    return input_mods, output_mods


def _extract_provider(model_id: str) -> str:
    """Extract provider slug from OpenRouter model ID like 'openai/gpt-5'."""
    parts = model_id.split("/")
    return parts[0] if len(parts) >= 2 else "unknown"


def _parse_pricing(pricing: dict | None) -> dict | None:
    if not pricing:
        return None
    try:
        prompt = float(pricing.get("prompt", 0)) * 1_000_000
        completion = float(pricing.get("completion", 0)) * 1_000_000
        if prompt == 0 and completion == 0:
            return None
        return {
            "prompt_per_million": round(prompt, 4),
            "completion_per_million": round(completion, 4),
        }
    except (ValueError, TypeError):
        return None


def fetch_models() -> list[Model]:
    """Fetch all models from OpenRouter API."""
    logger.info("Fetching models from OpenRouter...")
    try:
        resp = httpx.get(API_URL, timeout=30)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error("OpenRouter API error: %s", e)
        return []

    data = resp.json().get("data", [])
    models = []

    for item in data:
        model_id = item.get("id", "")
        if not model_id:
            continue

        provider_slug = _extract_provider(model_id)
        arch = item.get("architecture")
        input_mods, output_mods = _parse_modalities(arch)
        all_mods = sorted(set(input_mods + output_mods))

        created = item.get("created")
        release_date = None
        if created:
            try:
                release_date = datetime.fromtimestamp(
                    created, tz=timezone.utc
                ).isoformat()
            except (ValueError, TypeError, OSError):
                pass

        model = Model(
            id=f"openrouter:{model_id}",
            name=item.get("name", model_id),
            provider=resolve_provider_name(provider_slug),
            source="openrouter",
            modality=all_mods,
            input_modalities=input_mods,
            output_modalities=output_mods,
            release_date=release_date,
            context_length=item.get("context_length"),
            description=item.get("description", ""),
            url=f"https://openrouter.ai/{model_id}",
            pricing=_parse_pricing(item.get("pricing")),
            tags=[],
            source_ids=[model_id],
        )
        models.append(model)

    logger.info("Fetched %d models from OpenRouter", len(models))
    return models
