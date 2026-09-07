from abc import ABC, abstractmethod


class BaseOCRProvider(ABC):
    """Abstract base class for OCR providers."""

    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        """Extract text from the given image file path.

        Args:
            image_path: Absolute filesystem path to the image.

        Returns:
            Extracted text as a string.

        Raises:
            Exception: If API call fails or text extraction errors.
        """
        pass
