import settings
from .gemini import GeminiProvider
from .openai import OpenAIProvider


class OCRService:
    """Service to coordinate OCR text extraction based on Klipr settings."""

    @staticmethod
    def get_provider():
        conf = settings.load()
        provider_name = conf.get("ocrProvider", "gemini").strip().lower()

        if provider_name == "openai":
            api_key = conf.get("ocrOpenAIKey", "")
            model = conf.get("ocrOpenAIModel", "gpt-4o-mini")
            base_url = conf.get("ocrOpenAIBaseUrl", "https://api.openai.com/v1")
            return OpenAIProvider(api_key=api_key, model=model, base_url=base_url)
        else:
            api_key = conf.get("ocrGeminiKey", "")
            model = conf.get("ocrGeminiModel", "gemini-3.1-flash-lite")
            return GeminiProvider(api_key=api_key, model=model)

    @classmethod
    def extract(cls, image_path: str) -> str:
        provider = cls.get_provider()
        return provider.extract_text(image_path)
