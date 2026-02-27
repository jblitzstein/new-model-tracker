# AI Model Release Tracker

A personal dashboard that tracks frontier AI model releases — LLMs, image/video/audio generators, coding models, and notable SLMs.

Data is collected automatically every 4 hours via GitHub Actions and served as a static dashboard on GitHub Pages.

## Data Sources

- **OpenRouter API** — ~300+ commercial/frontier models (no auth required)
- **HuggingFace API** — open-source/open-weight models from notable orgs (no auth required)
- **Direct provider APIs** (optional) — OpenAI, Anthropic, Google Gemini, Mistral for faster detection

## How It Works

1. A GitHub Actions cron job runs the Python collector every 4 hours
2. The collector fetches model listings from all configured sources
3. New models are merged, deduplicated, and appended to `data/models.json`
4. The static dashboard in `docs/` reads the JSON and renders an interactive view

## Local Development

```bash
pip install -r requirements.txt
python -m collector.main
```

## Dashboard

Visit the GitHub Pages URL for this repo to see the live dashboard.
