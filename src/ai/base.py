from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        """Extract text from the given image path."""
        pass
