"""Unified model schema for the tracker."""

from __future__ import annotations

import dataclasses
import json
import re
from datetime import datetime, timezone
from typing import Optional


def extract_family(name: str) -> str:
    """Extract model family name by stripping sizes, variants, and suffixes."""
    n = re.sub(r'^[^:]+:\s*', '', name)
    n = re.sub(r'\s*\((free|exacto)\)', '', n, flags=re.I)
    n = re.sub(r'\s*\(?20\d{2}[-/]\d{2}[-/]\d{2}\)?', '', n)
    n = re.sub(r'\s+\d{4}$', '', n)
    n = re.sub(r'\s*\d+x\d+[bB]', '', n)
    n = re.sub(r'[-\s]*\d+(\.\d+)?[bB][-\s]*[aA]\d+(\.\d+)?[bB]', '', n)
    n = re.sub(r'[-\s]*\d+(\.\d+)?[bB]\b', '', n)
    n = re.sub(
        r'\s*(Instruct|Chat|Think|Thinking|Preview|Base|GGUF|GPTQ|AWQ)\b',
        '', n, flags=re.I,
    )
    n = re.sub(r'\s*\(thinking\)', '', n, flags=re.I)
    n = re.sub(r'\s+Custom Tools$', '', n)
    n = re.sub(r'\s+(older|extended)$', '', n, flags=re.I)
    n = n.strip(' -_')
    n = re.sub(r'\s*\(\s*\)\s*$', '', n)
    return n or name


@dataclasses.dataclass
class Model:
    id: str  # source-namespaced, e.g. "openrouter:openai/gpt-5"
    name: str
    provider: str  # e.g. "OpenAI", "Anthropic", "Meta"
    source: str  # "openrouter", "huggingface", "openai", "anthropic", etc.
    modality: list[str]  # e.g. ["text"], ["text", "image"]
    input_modalities: list[str]
    output_modalities: list[str]
    release_date: Optional[str] = None  # ISO 8601
    context_length: Optional[int] = None
    description: Optional[str] = None
    url: Optional[str] = None
    tags: list[str] = dataclasses.field(default_factory=list)
    pricing: Optional[dict] = None  # {"prompt_per_million": float, "completion_per_million": float}
    first_seen: str = dataclasses.field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    source_ids: list[str] = dataclasses.field(default_factory=list)
    family: str = ""

    def __post_init__(self):
        if not self.family:
            self.family = extract_family(self.name)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Model:
        known = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


def load_models(path: str) -> list[dict]:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_models(path: str, models: list[dict]) -> None:
    with open(path, "w") as f:
        json.dump(models, f, indent=2, ensure_ascii=False)
        f.write("\n")
