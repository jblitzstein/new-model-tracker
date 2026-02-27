"""HuggingFace API client — fetches open-source/open-weight models."""

from __future__ import annotations

import logging

import httpx

from collector.config import (
    HUGGINGFACE_FETCH_LIMIT,
    HUGGINGFACE_MIN_DOWNLOADS,
    HUGGINGFACE_PIPELINE_TAGS,
    HUGGINGFACE_WHITELISTED_ORGS,
    resolve_provider_name,
)
from collector.models import Model

logger = logging.getLogger(__name__)

API_URL = "https://huggingface.co/api/models"


def _is_notable(item: dict) -> bool:
    """Check if a model is notable enough to track."""
    author = (item.get("author") or item.get("modelId", "").split("/")[0]).lower()
    # Whitelisted org?
    for org in HUGGINGFACE_WHITELISTED_ORGS:
        if org.lower() == author:
            return True
    # High enough downloads?
    downloads = item.get("downloads", 0) or 0
    return downloads >= HUGGINGFACE_MIN_DOWNLOADS


def _pipeline_to_modalities(tag: str) -> tuple[list[str], list[str]]:
    """Map HuggingFace pipeline tags to input/output modalities."""
    mapping = {
        "text-generation": (["text"], ["text"]),
        "text-to-image": (["text"], ["image"]),
        "image-to-text": (["image"], ["text"]),
        "image-text-to-text": (["image", "text"], ["text"]),
        "text-to-video": (["text"], ["video"]),
        "text-to-audio": (["text"], ["audio"]),
        "text-to-speech": (["text"], ["audio"]),
        "automatic-speech-recognition": (["audio"], ["text"]),
        "visual-question-answering": (["image", "text"], ["text"]),
    }
    return mapping.get(tag, (["text"], ["text"]))


def fetch_models() -> list[Model]:
    """Fetch notable models from HuggingFace API."""
    logger.info("Fetching models from HuggingFace...")
    all_models: list[Model] = []
    seen_ids: set[str] = set()

    for tag in HUGGINGFACE_PIPELINE_TAGS:
        try:
            resp = httpx.get(
                API_URL,
                params={
                    "pipeline_tag": tag,
                    "sort": "lastModified",
                    "direction": "-1",
                    "limit": HUGGINGFACE_FETCH_LIMIT,
                },
                timeout=30,
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.error("HuggingFace API error for tag %s: %s", tag, e)
            continue

        items = resp.json()
        for item in items:
            model_id = item.get("modelId") or item.get("id", "")
            if not model_id or model_id in seen_ids:
                continue
            if not _is_notable(item):
                continue

            seen_ids.add(model_id)
            author = model_id.split("/")[0] if "/" in model_id else "unknown"
            input_mods, output_mods = _pipeline_to_modalities(tag)
            all_mods = sorted(set(input_mods + output_mods))

            model = Model(
                id=f"huggingface:{model_id}",
                name=model_id.split("/")[-1] if "/" in model_id else model_id,
                provider=resolve_provider_name(author),
                source="huggingface",
                modality=all_mods,
                input_modalities=input_mods,
                output_modalities=output_mods,
                release_date=item.get("createdAt") or item.get("lastModified"),
                description=item.get("description", ""),
                url=f"https://huggingface.co/{model_id}",
                tags=[tag] + (item.get("tags") or [])[:5],
                source_ids=[model_id],
            )
            all_models.append(model)

    logger.info("Fetched %d notable models from HuggingFace", len(all_models))
    return all_models
