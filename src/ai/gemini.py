import base64
import http.client
import io
import json
import mimetypes
import os
import threading
from PIL import Image
from .base import BaseAIProvider
from .prompt import EXTRACTION_PROMPT


class GeminiAIProvider(BaseAIProvider):
    """AI Vision provider using Google Gemini REST API with high-speed payload and connection optimizations."""

    DEFAULT_MODEL = "gemini-3.1-flash-lite"
    HOST = "generativelanguage.googleapis.com"

    MAX_PARALLEL_REQUESTS = 3
    _request_semaphore = threading.Semaphore(MAX_PARALLEL_REQUESTS)

    def __init__(self, api_key: str, model: str = None):
        self.api_key = (api_key or "").strip()
        m = (model or "").strip() or self.DEFAULT_MODEL
        if m.endswith("flast"):
            m = m[:-5] + "flash"
        self.model = m

    @staticmethod
    def _prepare_image(image_path: str, max_dimension: int = 1200, quality: int = 80) -> tuple[bytes, str]:
        """
        Downscale and compress image to optimal tile dimensions (<= 1200px)
        to minimize Gemini vision tokens and network transmission time.
        """
        try:
            with Image.open(image_path) as img:
                orig_w, orig_h = img.size

                resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.LANCZOS)
                if max(orig_w, orig_h) > max_dimension:
                    scale = max_dimension / float(max(orig_w, orig_h))
                    new_w = max(1, int(orig_w * scale))
                    new_h = max(1, int(orig_h * scale))
                    img = img.resize((new_w, new_h), resample)

                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    rgba = img.convert("RGBA")
                    bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
                    img = Image.alpha_composite(bg, rgba).convert("RGB")
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=quality, optimize=True)
                return buf.getvalue(), "image/jpeg"
        except Exception as e:
            print(f"[Klipr AI Warning] Image optimization failed ({e}), falling back to raw image file")
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type:
                mime_type = "image/png"
            with open(image_path, "rb") as f:
                return f.read(), mime_type

    def extract_text(self, image_path: str) -> str:
        if not self.api_key:
            raise ValueError("Gemini API Key not set")

        if not os.path.isfile(image_path):
            raise FileNotFoundError("Image file not found")

        raw_bytes, mime_type = self._prepare_image(image_path)
        encoded_image = base64.b64encode(raw_bytes).decode("utf-8")

        print(f"[Klipr AI] Calling Gemini API (model: {self.model}, image: {os.path.basename(image_path)}, size: {len(raw_bytes)/1024:.1f}KB, mime: {mime_type})...")

        # System instruction separates extractor persona from user payload,
        # and thinkingBudget: 0 disables hidden reasoning tokens for instant output.
        payload = {
            "systemInstruction": {
                "parts": [
                    {
                        "text": EXTRACTION_PROMPT
                    }
                ]
            },

            "contents": [
                {
                    "parts": [
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
                "temperature": 0.0,
                "thinkingConfig": {
                    "thinkingBudget": 0
                }
            }
        }

        body = json.dumps(payload).encode("utf-8")
        path = f"/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
            "User-Agent": "Klipr/1.2.8",
            "Connection": "keep-alive",
        }

        # Each call opens its own connection (no shared socket state across threads),
        # gated by a semaphore so at most MAX_PARALLEL_REQUESTS run concurrently.
        data = None
        with self._request_semaphore:
            for attempt in range(2):
                conn = http.client.HTTPSConnection(self.HOST, timeout=30)
                try:
                    conn.request("POST", path, body=body, headers=headers)
                    resp = conn.getresponse()
                    raw_resp = resp.read().decode("utf-8")

                    if resp.status >= 400:
                        try:
                            err_json = json.loads(raw_resp)
                            msg = err_json.get("error", {}).get("message", raw_resp)
                        except Exception:
                            msg = raw_resp
                        print(f"[Klipr AI Error] Gemini HTTP {resp.status}: {msg}")
                        if resp.status == 429:
                            raise RuntimeError("Rate limit exceeded")
                        elif resp.status in (401, 403):
                            raise RuntimeError("Invalid Gemini API key")
                        raise RuntimeError(f"Gemini error ({resp.status})")

                    data = json.loads(raw_resp)
                    break
                except (http.client.RemoteDisconnected, BrokenPipeError, ConnectionResetError) as e:
                    if attempt == 1:
                        print(f"[Klipr AI Error] Gemini connection error: {e}")
                        raise RuntimeError("Connection failed")
                except Exception as e:
                    if "Gemini" in str(e) or "Rate limit" in str(e) or "API key" in str(e):
                        raise
                    print(f"[Klipr AI Error] Gemini request failed: {e}")
                    raise RuntimeError("Request failed")
                finally:
                    try:
                        conn.close()
                    except Exception:
                        pass

        try:
            candidates = data.get("candidates", [])
            if not candidates:
                feedback = data.get("promptFeedback", {})
                block_reason = feedback.get("blockReason")
                if block_reason:
                    print(f"[Klipr AI Error] Gemini blocked content: {block_reason}")
                    raise RuntimeError("Content blocked")
                return ""

            parts = candidates[0].get("content", {}).get("parts", [])
            text_parts = [p.get("text", "") for p in parts if isinstance(p, dict) and "text" in p]
            result = "".join(text_parts).strip()
            print(f"[Klipr AI] Gemini extraction completed ({len(result)} chars)")
            return result
        except Exception as e:
            if "Content blocked" in str(e):
                raise
            print(f"[Klipr AI Error] Failed to parse Gemini response: {e}")
            raise RuntimeError("Response parse error")
