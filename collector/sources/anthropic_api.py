"""Anthropic direct API client — faster detection of new Claude models."""

from __future__ import annotations

import logging
import os

import httpx

from collector.models import Model

logger = logging.getLogger(__name__)

API_URL = "https://api.anthropic.com/v1/models"


def fetch_models() -> list[Model]:
    """Fetch models from Anthropic API. Requires ANTHROPIC_API_KEY env var."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.info("ANTHROPIC_API_KEY not set, skipping Anthropic source")
        return []

    logger.info("Fetching models from Anthropic...")
    all_models: list[Model] = []
    after_id = None

    while True:
        params: dict = {"limit": 100}
        if after_id:
            params["after_id"] = after_id

        try:
            resp = httpx.get(
                API_URL,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
                params=params,
                timeout=30,
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.error("Anthropic API error: %s", e)
            break

        body = resp.json()
        items = body.get("data", [])

        for item in items:
            model_id = item.get("id", "")
            if not model_id:
                continue

            model = Model(
                id=f"anthropic:{model_id}",
                name=item.get("display_name", model_id),
                provider="Anthropic",
                source="anthropic",
                modality=["text"],
                input_modalities=["text"],
                output_modalities=["text"],
                release_date=item.get("created_at"),
                url=f"https://docs.anthropic.com/en/docs/about-claude/models",
                source_ids=[model_id],
            )
            all_models.append(model)

        if body.get("has_more") and items:
            after_id = body.get("last_id")
        else:
            break

    logger.info("Fetched %d models from Anthropic", len(all_models))
    return all_models
