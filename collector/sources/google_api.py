"""Google Gemini direct API client — detects new Gemini models."""

from __future__ import annotations

import logging
import os

import httpx

from collector.models import Model

logger = logging.getLogger(__name__)

API_URL = "https://generativelanguage.googleapis.com/v1beta/models"


def fetch_models() -> list[Model]:
    """Fetch models from Google Gemini API. Requires GEMINI_API_KEY env var."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.info("GEMINI_API_KEY not set, skipping Google Gemini source")
        return []

    logger.info("Fetching models from Google Gemini...")
    all_models: list[Model] = []
    page_token = None

    while True:
        params: dict = {"key": api_key}
        if page_token:
            params["pageToken"] = page_token

        try:
            resp = httpx.get(API_URL, params=params, timeout=30)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.error("Google Gemini API error: %s", e)
            break

        body = resp.json()
        items = body.get("models", [])

        for item in items:
            name = item.get("name", "")
            if not name:
                continue
            # name is like "models/gemini-2.5-pro" — extract the model slug
            model_slug = name.replace("models/", "")
            display = item.get("displayName", model_slug)
            actions = item.get("supportedGenerationMethods") or item.get(
                "supportedActions", []
            )

            # Determine modalities from supported methods
            output_mods = ["text"]
            if any("image" in a.lower() for a in actions):
                output_mods.append("image")

            model = Model(
                id=f"google:{model_slug}",
                name=display,
                provider="Google",
                source="google",
                modality=sorted(set(["text"] + output_mods)),
                input_modalities=["text"],
                output_modalities=output_mods,
                release_date=None,  # Gemini API doesn't expose created_at
                url=f"https://ai.google.dev/gemini-api/docs/models#{model_slug}",
                tags=actions[:5] if actions else [],
                source_ids=[model_slug],
            )
            all_models.append(model)

        page_token = body.get("nextPageToken")
        if not page_token:
            break

    logger.info("Fetched %d models from Google Gemini", len(all_models))
    return all_models
