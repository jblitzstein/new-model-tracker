"""OpenAI direct API client — faster detection of new GPT/o-series models."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

import httpx

from collector.models import Model

logger = logging.getLogger(__name__)

API_URL = "https://api.openai.com/v1/models"


def fetch_models() -> list[Model]:
    """Fetch models from OpenAI API. Requires OPENAI_API_KEY env var."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.info("OPENAI_API_KEY not set, skipping OpenAI source")
        return []

    logger.info("Fetching models from OpenAI...")
    try:
        resp = httpx.get(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error("OpenAI API error: %s", e)
        return []

    data = resp.json().get("data", [])
    models = []

    for item in data:
        model_id = item.get("id", "")
        if not model_id:
            continue
        # Skip fine-tuned models and internal variants
        if model_id.startswith("ft:") or model_id.startswith("user-"):
            continue

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
            id=f"openai:{model_id}",
            name=model_id,
            provider="OpenAI",
            source="openai",
            modality=["text"],
            input_modalities=["text"],
            output_modalities=["text"],
            release_date=release_date,
            url=f"https://platform.openai.com/docs/models/{model_id}",
            source_ids=[model_id],
        )
        models.append(model)

    logger.info("Fetched %d models from OpenAI", len(models))
    return models
