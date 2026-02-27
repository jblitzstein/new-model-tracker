"""Main entry point for the model tracker collector."""

from __future__ import annotations

import logging
import os
import sys

from collector.dedup import filter_latest, merge_models
from collector.models import load_models, save_models
from collector.sources import (
    anthropic_api,
    google_api,
    huggingface,
    mistral_api,
    openai_api,
    openrouter,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
MODELS_PATH = os.path.join(DATA_DIR, "models.json")
LATEST_PATH = os.path.join(DATA_DIR, "latest.json")


def collect() -> None:
    """Run all collectors and merge results."""
    logger.info("Starting model collection...")

    # Phase 1 sources (no auth required)
    all_new = []
    all_new.extend(openrouter.fetch_models())
    all_new.extend(huggingface.fetch_models())

    # Phase 2 sources (optional, need API keys)
    all_new.extend(openai_api.fetch_models())
    all_new.extend(anthropic_api.fetch_models())
    all_new.extend(google_api.fetch_models())
    all_new.extend(mistral_api.fetch_models())

    logger.info("Total models fetched from all sources: %d", len(all_new))

    # Load existing catalog and merge
    existing = load_models(MODELS_PATH)
    existing_count = len(existing)

    merged = merge_models(all_new, existing)
    new_count = len(merged) - existing_count

    # Save full catalog
    save_models(MODELS_PATH, merged)
    logger.info("Catalog: %d total models (%d new)", len(merged), new_count)

    # Save latest (last 30 days)
    latest = filter_latest(merged)
    save_models(LATEST_PATH, latest)
    logger.info("Latest: %d models in last 30 days", len(latest))

    # Summary for GitHub Actions
    if new_count > 0:
        print(f"\n✨ {new_count} new model(s) detected!")
        for m in merged[-new_count:]:
            print(f"  → {m.get('name', '?')} ({m.get('provider', '?')})")
    else:
        print("\n✅ No new models detected.")


def main() -> None:
    try:
        collect()
    except Exception:
        logger.exception("Collection failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
