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
    "x-ai": "xAI",
    "nvidia": "NVIDIA",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "qwen": "Qwen",
    "stabilityai": "Stability AI",
    "black-forest-labs": "Black Forest Labs",
    "bytedance": "ByteDance",
    "bytedanceseed": "ByteDance",
    "bytedance-seed": "ByteDance",
    "apple": "Apple",
    "alibaba-nlp": "Alibaba",
    "alibaba": "Alibaba",
    "01-ai": "01.AI",
    "01ai": "01.AI",
    "salesforce": "Salesforce",
    "eleutherai": "EleutherAI",
    "allenai": "Allen AI",
    "nousresearch": "Nous Research",
    "thudm": "Tsinghua",
    "internlm": "InternLM",
    "lmsys": "LMSYS",
    "perplexity": "Perplexity",
    "minimax": "MiniMax",
    "z-ai": "Zhipu AI",
    "zai": "Zhipu AI",
    "inflection": "Inflection",
    "ai21": "AI21 Labs",
    "liquid": "Liquid AI",
    "moonshotai": "Moonshot AI",
    "arceeai": "Arcee AI",
    "arcee-ai": "Arcee AI",
    "baidu": "Baidu",
    "inception": "Inception",
    "ibmgranite": "IBM",
    "ibm-granite": "IBM",
    "writer": "Writer",
    "stepfun": "StepFun",
    "tencent": "Tencent",
    "xiaomi": "Xiaomi",
    "deepcogito": "Deep Cogito",
    "essentialai": "Essential AI",
    "morph": "Morph",
    "upstage": "Upstage",
    "aionlabs": "Aion Labs",
    "aion-labs": "Aion Labs",
    "primeintellect": "Prime Intellect",
    "prime-intellect": "Prime Intellect",
    "meituan": "Meituan",
    "relace": "Relace",
    "kwaipilot": "Kwaipilot",
    "nexagi": "Nex AGI",
    "nex-agi": "Nex AGI",
}


def resolve_provider_name(raw: str) -> str:
    """Resolve a raw provider string to a display name."""
    key = raw.lower().strip().replace(" ", "")
    if key in PROVIDER_NAMES:
        return PROVIDER_NAMES[key]
    # Also try with hyphens removed
    key_no_hyphen = key.replace("-", "")
    return PROVIDER_NAMES.get(key_no_hyphen, raw)
