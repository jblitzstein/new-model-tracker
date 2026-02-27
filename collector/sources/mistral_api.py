"""Mistral direct API client — faster detection of new Mistral/Codestral models."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

import httpx

from collector.models import Model

logger = logging.getLogger(__name__)

API_URL = "https://api.mistral.ai/v1/models"


def fetch_models() -> list[Model]:
    """Fetch models from Mistral API. Requires MISTRAL_API_KEY env var."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        logger.info("MISTRAL_API_KEY not set, skipping Mistral source")
        return []

    logger.info("Fetching models from Mistral...")
    try:
        resp = httpx.get(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error("Mistral API error: %s", e)
        return []

    data = resp.json().get("data", [])
    models = []

    for item in data:
        model_id = item.get("id", "")
        if not model_id:
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
            id=f"mistral:{model_id}",
            name=model_id,
            provider="Mistral",
            source="mistral",
            modality=["text"],
            input_modalities=["text"],
            output_modalities=["text"],
            release_date=release_date,
            url=f"https://docs.mistral.ai/getting-started/models/",
            source_ids=[model_id],
        )
        models.append(model)

    logger.info("Fetched %d models from Mistral", len(models))
    return models
