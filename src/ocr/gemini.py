import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
from .base import BaseOCRProvider


class GeminiProvider(BaseOCRProvider):
    """OCR provider using Google Gemini Vision REST API via pure Python urllib."""

    DEFAULT_MODEL = "gemini-3.1-flash-lite"

    def __init__(self, api_key: str, model: str = None):
        self.api_key = (api_key or "").strip()
        m = (model or "").strip() or self.DEFAULT_MODEL
        # Auto-correct common typo 'flast' -> 'flash'
        if m.endswith("flast"):
            m = m[:-5] + "flash"
        self.model = m

    def extract_text(self, image_path: str) -> str:
        if not self.api_key:
            raise ValueError("Gemini API Key is not set. Configure it in Klipr Settings -> AI OCR.")

        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image not found at: {image_path}")

        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/png"

        with open(image_path, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode("utf-8")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        print(f"[Klipr OCR] Calling Gemini API (model: {self.model}, image: {os.path.basename(image_path)}, mime: {mime_type})...")

        # Standard Google Gemini REST API format uses camelCase: inlineData and mimeType
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "Extract all text from this image accurately. "
                                "Output only the raw extracted text without any markdown formatting, "
                                "preamble, or explanations."
                            )
                        },
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": encoded_image,
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
                "User-Agent": "Klipr/1.2.5",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raw_err = e.read().decode("utf-8", errors="replace")
            try:
                err_data = json.loads(raw_err)
                msg = err_data.get("error", {}).get("message", raw_err)
            except Exception:
                msg = raw_err
            print(f"[Klipr OCR Error] Gemini HTTP {e.code}: {msg}")
            raise RuntimeError(f"Gemini error ({e.code}): {msg}")
        except urllib.error.URLError as e:
            print(f"[Klipr OCR Error] Gemini connection error: {e.reason}")
            raise RuntimeError(f"Cannot connect to Gemini: {e.reason}")

        try:
            candidates = data.get("candidates", [])
            if not candidates:
                feedback = data.get("promptFeedback", {})
                block_reason = feedback.get("blockReason")
                if block_reason:
                    print(f"[Klipr OCR Error] Gemini blocked content: {block_reason}")
                    raise RuntimeError(f"Content blocked by Gemini: {block_reason}")
                return ""

            parts = candidates[0].get("content", {}).get("parts", [])
            text_parts = [p.get("text", "") for p in parts if isinstance(p, dict) and "text" in p]
            result = "".join(text_parts).strip()
            print(f"[Klipr OCR] Gemini extraction completed ({len(result)} chars)")
            return result
        except Exception as e:
            print(f"[Klipr OCR Error] Failed to parse Gemini response: {e}")
            raise RuntimeError(f"Failed to parse Gemini response: {e}")
