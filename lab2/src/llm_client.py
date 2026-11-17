"""Small provider-neutral client for Gemini, Ollama, and deterministic offline mode."""

import json
import os
from urllib.request import Request, urlopen

from config import LLM_BACKEND


def generate_json(prompt: str, schema: type | None = None) -> dict:
    if LLM_BACKEND == "gemini":
        from google import genai
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        config = {"response_mime_type": "application/json"}
        if schema is not None:
            config["response_schema"] = schema
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            contents=prompt,
            config=config,
        )
        return json.loads(response.text)
    if LLM_BACKEND == "ollama":
        payload = json.dumps({
            "model": os.getenv("OLLAMA_MODEL", "llama3.1"),
            "prompt": prompt,
            "format": "json",
            "stream": False,
        }).encode()
        request = Request(os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate"),
                          data=payload, headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=180) as response:
            return json.loads(json.load(response)["response"])
    raise RuntimeError("JSON generation requires LLM_BACKEND=gemini or ollama")


def generate_text(prompt: str, offline_text: str) -> str:
    if LLM_BACKEND == "offline":
        return offline_text
    if LLM_BACKEND == "gemini":
        from google import genai
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"), contents=prompt)
        return response.text.strip()
    payload = json.dumps({
        "model": os.getenv("OLLAMA_MODEL", "llama3.1"),
        "prompt": prompt,
        "stream": False,
    }).encode()
    request = Request(os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate"),
                      data=payload, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=180) as response:
        return json.load(response)["response"].strip()

