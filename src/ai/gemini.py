import base64
import http.client
import io
import json
import mimetypes
import os
import threading
from PIL import Image
from .base import BaseAIProvider


class GeminiAIProvider(BaseAIProvider):
    """AI Vision provider using Google Gemini REST API with high-speed payload and connection optimizations."""

    DEFAULT_MODEL = "gemini-3.1-flash-lite"
    HOST = "generativelanguage.googleapis.com"

    _conn_lock = threading.Lock()
    _shared_conn = None

    def __init__(self, api_key: str, model: str = None):
        self.api_key = (api_key or "").strip()
        m = (model or "").strip() or self.DEFAULT_MODEL
        if m.endswith("flast"):
            m = m[:-5] + "flash"
        self.model = m

    @classmethod
    def _get_connection(cls) -> http.client.HTTPSConnection:
        with cls._conn_lock:
            if cls._shared_conn is None:
                cls._shared_conn = http.client.HTTPSConnection(cls.HOST, timeout=30)
            return cls._shared_conn

    @classmethod
    def _reset_connection(cls):
        with cls._conn_lock:
            if cls._shared_conn is not None:
                try:
                    cls._shared_conn.close()
                except Exception:
                    pass
                cls._shared_conn = None

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
            raise ValueError("Gemini API Key is not set. Configure it in Klipr Settings -> AI Features.")

        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image not found at: {image_path}")

        raw_bytes, mime_type = self._prepare_image(image_path)
        encoded_image = base64.b64encode(raw_bytes).decode("utf-8")

        print(f"[Klipr AI] Calling Gemini API (model: {self.model}, image: {os.path.basename(image_path)}, size: {len(raw_bytes)/1024:.1f}KB, mime: {mime_type})...")

        # System instruction separates extractor persona from user payload,
        # and thinkingBudget: 0 disables hidden reasoning tokens for instant output.
        payload = {
            "systemInstruction": {
                "parts": [
                    {
                        "text": (
                            "You are an intelligent document text extraction engine.\n"
                            "Extract all text accurately while preserving the natural visual layout, line breaks, and spatial alignment.\n"
                            "FORMATTING RULES:\n"
                            "- Never use markdown table syntax (do NOT use vertical pipes '|' or '---' dividers). "
                            "Instead, align columns cleanly using natural spacing so tables read legibly in plain text.\n"
                            "- Maintain clean paragraph and section breaks between different information blocks.\n"
                            "- Output ONLY the clean plain text verbatim without markdown code fences, notes, or explanations."
                        )
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

        # Send request with automatic reconnect on stale socket
        data = None
        for attempt in range(2):
            conn = self._get_connection()
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
                    raise RuntimeError(f"Gemini error ({resp.status}): {msg}")

                data = json.loads(raw_resp)
                break
            except (http.client.RemoteDisconnected, BrokenPipeError, ConnectionResetError) as e:
                self._reset_connection()
                if attempt == 1:
                    print(f"[Klipr AI Error] Gemini connection error: {e}")
                    raise RuntimeError(f"Cannot connect to Gemini: {e}")
            except Exception as e:
                self._reset_connection()
                if "Gemini error" in str(e):
                    raise
                print(f"[Klipr AI Error] Gemini request failed: {e}")
                raise RuntimeError(f"Gemini request failed: {e}")

        try:
            candidates = data.get("candidates", [])
            if not candidates:
                feedback = data.get("promptFeedback", {})
                block_reason = feedback.get("blockReason")
                if block_reason:
                    print(f"[Klipr AI Error] Gemini blocked content: {block_reason}")
                    raise RuntimeError(f"Content blocked by Gemini: {block_reason}")
                return ""

            parts = candidates[0].get("content", {}).get("parts", [])
            text_parts = [p.get("text", "") for p in parts if isinstance(p, dict) and "text" in p]
            result = "".join(text_parts).strip()
            print(f"[Klipr AI] Gemini extraction completed ({len(result)} chars)")
            return result
        except Exception as e:
            if "blocked by Gemini" in str(e):
                raise
            print(f"[Klipr AI Error] Failed to parse Gemini response: {e}")
            raise RuntimeError(f"Failed to parse Gemini response: {e}")
