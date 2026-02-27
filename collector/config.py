"""Configuration for the model tracker collector."""

# Notable orgs to track on HuggingFace (slug format)
HUGGINGFACE_WHITELISTED_ORGS = [
    "meta-llama",
    "google",
    "mistralai",
    "microsoft",
    "Qwen",
    "deepseek-ai",
    "stabilityai",
    "black-forest-labs",
    "openai",
    "nvidia",
    "apple",
    "alibaba-nlp",
    "01-ai",
    "CohereForAI",
    "xai-org",
    "tencent",
    "baidu",
    "ByteDance",
    "amazon",
    "Salesforce",
    "bigscience",
    "EleutherAI",
    "allenai",
    "HuggingFaceH4",
    "NousResearch",
    "teknium",
    "lmsys",
    "THUDM",
    "internlm",
]

# Pipeline tags that indicate frontier/generative models
HUGGINGFACE_PIPELINE_TAGS = [
    "text-generation",
    "text-to-image",
    "image-to-text",
    "text-to-video",
    "text-to-audio",
    "text-to-speech",
    "automatic-speech-recognition",
    "image-text-to-text",
    "visual-question-answering",
]

# Minimum downloads for non-whitelisted orgs to be included
HUGGINGFACE_MIN_DOWNLOADS = 1000

# Number of models to fetch per HuggingFace query
HUGGINGFACE_FETCH_LIMIT = 50

# Provider display name mapping
PROVIDER_NAMES = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "google": "Google",
    "meta-llama": "Meta",
    "meta": "Meta",
    "mistralai": "Mistral",
    "mistral": "Mistral",
    "deepseek-ai": "DeepSeek",
    "deepseek": "DeepSeek",
    "cohere": "Cohere",
    "cohereforai": "Cohere",
    "xai": "xAI",
    "xai-org": "xAI",
    "nvidia": "NVIDIA",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "qwen": "Qwen",
    "stabilityai": "Stability AI",
    "black-forest-labs": "Black Forest Labs",
    "bytedance": "ByteDance",
    "apple": "Apple",
    "alibaba-nlp": "Alibaba",
    "01-ai": "01.AI",
    "salesforce": "Salesforce",
    "eleutherai": "EleutherAI",
    "allenai": "Allen AI",
    "nousresearch": "Nous Research",
    "thudm": "Tsinghua",
    "internlm": "InternLM",
    "lmsys": "LMSYS",
}


def resolve_provider_name(raw: str) -> str:
    """Resolve a raw provider string to a display name."""
    key = raw.lower().strip().replace(" ", "")
    return PROVIDER_NAMES.get(key, raw)
