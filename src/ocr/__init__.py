# Backward-compatibility alias redirecting to new ai package
from ai.base import BaseAIProvider as BaseOCRProvider
from ai.gemini import GeminiAIProvider as GeminiProvider
from ai.openai import OpenAIProvider
from ai.service import AIService as OCRService

__all__ = ["BaseOCRProvider", "GeminiProvider", "OpenAIProvider", "OCRService"]
