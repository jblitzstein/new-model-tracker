"""Deduplication and merge logic for combining models from multiple sources."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone

from collector.models import Model

logger = logging.getLogger(__name__)


def _normalize_name(name: str) -> str:
    """Normalize a model name for fuzzy matching."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]", "", s)
    return s


def _model_match_key(model: Model) -> str:
    """Generate a match key from model name + provider for cross-source dedup."""
    provider = model.provider.lower().replace(" ", "")
    name = _normalize_name(model.name)
    return f"{provider}:{name}"


def merge_models(
    new_models: list[Model], existing_data: list[dict]
) -> list[dict]:
    """Merge new models into existing catalog.

    - Existing models are preserved as-is
    - New models not already in the catalog are appended
    - Cross-source matches update source_ids and use earliest release_date
    """
    # Index existing by id and by match key
    by_id: dict[str, dict] = {m["id"]: m for m in existing_data}
    by_key: dict[str, dict] = {}
    for m in existing_data:
        try:
            model_obj = Model.from_dict(m)
            key = _model_match_key(model_obj)
            by_key[key] = m
        except Exception:
            continue

    added = 0
    updated = 0

    for model in new_models:
        model_dict = model.to_dict()

        # Exact ID match — already tracked
        if model.id in by_id:
            existing = by_id[model.id]
            # Update source_ids if new source info
            existing_sources = set(existing.get("source_ids", []))
            new_sources = set(model.source_ids)
            if new_sources - existing_sources:
                existing["source_ids"] = sorted(existing_sources | new_sources)
                updated += 1
            continue

        # Fuzzy match — same model from different source
        key = _model_match_key(model)
        if key in by_key:
            existing = by_key[key]
            # Merge source IDs
            existing_sources = set(existing.get("source_ids", []))
            new_sources = set(model.source_ids)
            existing["source_ids"] = sorted(existing_sources | new_sources)

            # Use earliest release date
            if model.release_date and existing.get("release_date"):
                if model.release_date < existing["release_date"]:
                    existing["release_date"] = model.release_date
            elif model.release_date and not existing.get("release_date"):
                existing["release_date"] = model.release_date

            # Use earliest first_seen
            if model.first_seen < existing.get("first_seen", model.first_seen):
                existing["first_seen"] = model.first_seen

            # Enrich missing fields
            if not existing.get("context_length") and model.context_length:
                existing["context_length"] = model.context_length
            if not existing.get("pricing") and model.pricing:
                existing["pricing"] = model.pricing
            if not existing.get("description") and model.description:
                existing["description"] = model.description

            updated += 1
            continue

        # Genuinely new model
        by_id[model.id] = model_dict
        by_key[key] = model_dict
        existing_data.append(model_dict)
        added += 1

    logger.info("Merge complete: %d added, %d updated", added, updated)
    return existing_data


def filter_latest(models: list[dict], days: int = 30) -> list[dict]:
    """Filter models to only those first seen within the last N days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    latest = []
    for m in models:
        first_seen = m.get("first_seen", "")
        release_date = m.get("release_date", "")
        ref_date = first_seen or release_date
        if ref_date and ref_date >= cutoff:
            latest.append(m)
    # Sort by release date descending
    latest.sort(key=lambda m: m.get("release_date") or m.get("first_seen", ""), reverse=True)
    return latest
