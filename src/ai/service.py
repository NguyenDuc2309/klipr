import hashlib
import os
import settings
from .gemini import GeminiAIProvider
from .openai import OpenAIProvider


class AIService:
    """Service coordinating AI vision and text extraction based on Klipr settings."""

    _cache: dict[str, str] = {}

    @staticmethod
    def get_provider():
        conf = settings.load()
        provider_name = (conf.get("aiProvider") or conf.get("ocrProvider") or "gemini").strip().lower()

        if provider_name == "openai":
            api_key = conf.get("aiOpenAIKey") or conf.get("ocrOpenAIKey") or ""
            model = conf.get("aiOpenAIModel") or conf.get("ocrOpenAIModel") or "gpt-4o-mini"
            base_url = conf.get("aiOpenAIBaseUrl") or conf.get("ocrOpenAIBaseUrl") or "https://api.openai.com/v1"
            return OpenAIProvider(api_key=api_key, model=model, base_url=base_url)
        else:
            api_key = conf.get("aiGeminiKey") or conf.get("ocrGeminiKey") or ""
            model = conf.get("aiGeminiModel") or conf.get("ocrGeminiModel") or "gemini-3.1-flash-lite"
            return GeminiAIProvider(api_key=api_key, model=model)

    @classmethod
    def _compute_file_key(cls, image_path: str) -> str:
        try:
            stat = os.stat(image_path)
            raw = f"{image_path}:{stat.st_size}:{stat.st_mtime}"
            return hashlib.md5(raw.encode("utf-8")).hexdigest()
        except Exception:
            return image_path

    @classmethod
    def extract(cls, image_path: str) -> str:
        cache_key = cls._compute_file_key(image_path)
        if cache_key in cls._cache:
            cached = cls._cache[cache_key]
            print(f"[Klipr AI Cache Hit] Returning cached result for {os.path.basename(image_path)} ({len(cached)} chars)")
            return cached

        provider = cls.get_provider()
        result = provider.extract_text(image_path)
        if result and result.strip():
            # Keep cache bounded
            if len(cls._cache) > 100:
                cls._cache.clear()
            cls._cache[cache_key] = result
        return result
