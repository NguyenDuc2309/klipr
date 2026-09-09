import base64
import io
import json
import mimetypes
import os
import threading
import urllib.error
import urllib.request
from PIL import Image
from .base import BaseAIProvider
from .prompt import EXTRACTION_PROMPT


class OpenAIProvider(BaseAIProvider):
    """AI Vision provider using OpenAI Vision REST API."""

    DEFAULT_MODEL = "gpt-4o-mini"
    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    MAX_PARALLEL_REQUESTS = 3
    _request_semaphore = threading.Semaphore(MAX_PARALLEL_REQUESTS)

    def __init__(self, api_key: str, model: str = None, base_url: str = None):
        self.api_key = (api_key or "").strip()
        self.model = (model or "").strip() or self.DEFAULT_MODEL
        url_input = (base_url or "").strip() or self.DEFAULT_BASE_URL
        self.base_url = url_input.rstrip("/")

    @staticmethod
    def _prepare_image(image_path: str, max_dimension: int = 1200, quality: int = 80) -> tuple[bytes, str]:
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

    def _send_request(self, payload: dict, url: str) -> dict:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "Klipr/1.2.8",
            },
            method="POST",
        )

        is_local = "127.0.0.1" in url or "localhost" in url
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({})) if is_local else urllib.request.build_opener()

        with opener.open(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def extract_text(self, image_path: str) -> str:
        if not self.api_key:
            raise ValueError("OpenAI API Key not set")

        if not os.path.isfile(image_path):
            raise FileNotFoundError("Image file not found")

        raw_bytes, mime_type = self._prepare_image(image_path)
        encoded_image = base64.b64encode(raw_bytes).decode("utf-8")

        if self.base_url.endswith("/chat/completions"):
            url = self.base_url
        else:
            url = f"{self.base_url}/chat/completions"

        print(f"[Klipr AI] Calling OpenAI API (endpoint: {url}, model: {self.model}, image: {os.path.basename(image_path)}, size: {len(raw_bytes)/1024:.1f}KB, mime: {mime_type})...")

        prompt_text = EXTRACTION_PROMPT

        data_url = f"data:{mime_type};base64,{encoded_image}"

        # Standard OpenAI Chat Completions payload
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.0,
            "max_tokens": 4096,
        }

        # Gated by a semaphore so at most MAX_PARALLEL_REQUESTS run concurrently.
        with self._request_semaphore:
            try:
                data = self._send_request(payload, url)
            except urllib.error.HTTPError as e:
                raw_err = e.read().decode("utf-8", errors="replace")
                # If backend expects string content instead of array
                if "json: cannot unmarshal array into Go struct" in raw_err:
                    payload["messages"][0]["content"] = prompt_text
                    payload["messages"][0]["images"] = [data_url]
                    try:
                        data = self._send_request(payload, url)
                    except urllib.error.HTTPError as e2:
                        raw_err2 = e2.read().decode("utf-8", errors="replace")
                        print(f"[Klipr AI Error] Go format retry HTTP {e2.code}: {raw_err2}")
                        raise RuntimeError(f"OpenAI error ({e2.code}): {raw_err2}")
                    except Exception as e2:
                        print(f"[Klipr AI Error] Go format retry error: {e2}")
                        raise RuntimeError(f"OpenAI error: {e2}")
                else:
                    print(f"[Klipr AI Error] OpenAI HTTP {e.code}")
                    if e.code == 429:
                        raise RuntimeError("Rate limit exceeded")
                    elif e.code in (401, 403):
                        raise RuntimeError("Invalid OpenAI API key")
                    raise RuntimeError(f"OpenAI error ({e.code})")
            except urllib.error.URLError as e:
                print(f"[Klipr AI Error] OpenAI connection error ({url}): {e.reason}")
                raise RuntimeError("Connection failed")

        if "error" in data:
            err_msg = data["error"].get("message", str(data["error"]))
            print(f"[Klipr AI Error] OpenAI server returned error: {err_msg}")
            raise RuntimeError("Request failed")

        try:
            choices = data.get("choices", [])
            if not choices:
                return ""
            msg = choices[0].get("message", {})
            content = msg.get("content", "")
            if isinstance(content, list):
                text_parts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
                result = "".join(text_parts).strip()
            else:
                result = str(content).strip()
            print(f"[Klipr AI] OpenAI extraction completed ({len(result)} chars)")
            return result
        except Exception as e:
            print(f"[Klipr AI Error] Failed to parse OpenAI response: {e}")
            raise RuntimeError("Response parse error")
