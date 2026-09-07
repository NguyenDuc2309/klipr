import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
from .base import BaseOCRProvider


class OpenAIProvider(BaseOCRProvider):
    """OCR provider using OpenAI Vision REST API via pure Python urllib."""

    DEFAULT_MODEL = "gpt-4o-mini"
    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    def __init__(self, api_key: str, model: str = None, base_url: str = None):
        self.api_key = (api_key or "").strip()
        self.model = (model or "").strip() or self.DEFAULT_MODEL
        url_input = (base_url or "").strip() or self.DEFAULT_BASE_URL
        self.base_url = url_input.rstrip("/")

    def _send_request(self, payload: dict, url: str) -> dict:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "Klipr/1.2.5",
            },
            method="POST",
        )

        is_local = "127.0.0.1" in url or "localhost" in url
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({})) if is_local else urllib.request.build_opener()

        with opener.open(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def extract_text(self, image_path: str) -> str:
        if not self.api_key:
            raise ValueError("OpenAI API Key is not set. Configure it in Klipr Settings -> AI OCR.")

        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image not found at: {image_path}")

        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/png"

        with open(image_path, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode("utf-8")

        # Normalize endpoint (avoid duplicating /chat/completions if user included it)
        if self.base_url.endswith("/chat/completions"):
            url = self.base_url
        else:
            url = f"{self.base_url}/chat/completions"

        print(f"[Klipr OCR] Calling OpenAI API (endpoint: {url}, model: {self.model}, image: {os.path.basename(image_path)}, mime: {mime_type})...")

        prompt_text = (
            "Extract all text from this image accurately. "
            "Output only the raw extracted text without any markdown formatting, "
            "preamble, or explanations."
        )

        # Format 1: Standard OpenAI Vision payload (content as array of parts)
        standard_payload = {
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
                                "url": f"data:{mime_type};base64,{encoded_image}",
                                "detail": "auto",
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 4096,
            "temperature": 0.1,
        }

        try:
            data = self._send_request(standard_payload, url)
        except urllib.error.HTTPError as e:
            raw_err = e.read().decode("utf-8", errors="replace")
            # If the backend is a Go struct (e.g. Ollama/Go proxy) expecting content as string
            if "cannot unmarshal array into" in raw_err and "content of type string" in raw_err:
                print("[Klipr OCR] Backend Go struct expects string content. Retrying with content: string + images: [...] format...")
                go_payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt_text,
                            "images": [encoded_image],
                        }
                    ],
                    "max_tokens": 4096,
                    "temperature": 0.1,
                }
                try:
                    data = self._send_request(go_payload, url)
                except urllib.error.HTTPError as e2:
                    raw_err2 = e2.read().decode("utf-8", errors="replace")
                    print(f"[Klipr OCR Error] Go format retry HTTP {e2.code}: {raw_err2}")
                    raise RuntimeError(f"OpenAI gateway error ({e2.code}): {raw_err2}")
                except Exception as e2:
                    print(f"[Klipr OCR Error] Go format retry error: {e2}")
                    raise RuntimeError(f"OpenAI gateway error: {e2}")
            else:
                try:
                    err_data = json.loads(raw_err)
                    msg = err_data.get("error", {}).get("message", raw_err)
                except Exception:
                    msg = raw_err
                print(f"[Klipr OCR Error] OpenAI HTTP {e.code}: {msg}")
                raise RuntimeError(f"OpenAI error ({e.code}): {msg}")
        except urllib.error.URLError as e:
            print(f"[Klipr OCR Error] OpenAI connection error ({url}): {e.reason}")
            raise RuntimeError(f"Cannot connect to OpenAI ({url}): {e.reason}")

        # Check for error object returned inside JSON with 200 OK
        if "error" in data:
            err_obj = data["error"]
            err_msg = err_obj.get("message", str(err_obj)) if isinstance(err_obj, dict) else str(err_obj)
            print(f"[Klipr OCR Error] OpenAI server returned error: {err_msg}")
            raise RuntimeError(f"OpenAI error: {err_msg}")

        try:
            choices = data.get("choices", [])
            if not choices:
                return ""
            msg = choices[0].get("message", {})
            content = msg.get("content", "")

            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text_parts.append(part.get("text", ""))
                    elif isinstance(part, str):
                        text_parts.append(part)
                result = "".join(text_parts).strip()
            else:
                result = (content or "").strip()

            print(f"[Klipr OCR] OpenAI extraction completed ({len(result)} chars)")
            return result
        except Exception as e:
            print(f"[Klipr OCR Error] Failed to parse OpenAI response: {e}")
            raise RuntimeError(f"Failed to parse OpenAI response: {e}")
