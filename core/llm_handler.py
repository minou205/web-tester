# core/llm_handler.py
# Synchronous Ollama client with retries. Caller can decide to use async wrapper if needed.

import requests
import json
import time
from core.utils import get_logger

log = get_logger()

class OllamaClient:
    def __init__(self, model='llama3.1:8b', endpoint='http://localhost:11434/api/generate', timeout=300, max_retries=2):
        self.model = model
        self.endpoint = endpoint.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self._available = None

    def check_available(self):
        if self._available is not None:
            return self._available
        try:
            base = self.endpoint.replace('/api/generate', '')
            res = requests.get(base + '/api/tags', timeout=3)
            self._available = (res.status_code == 200)
        except Exception as e:
            log.debug(f"Ollama health check failed: {e}")
            self._available = False
        return self._available

    def generate(self, prompt):
        if not self.check_available():
            raise ConnectionError("Ollama not available")
        payload = {"model": self.model, "prompt": prompt, "max_tokens": 1024, "stream": False}
        for attempt in range(1, self.max_retries+1):
            try:
                log.info(f"Ollama request attempt {attempt}/{self.max_retries}")
                res = requests.post(self.endpoint, json=payload, timeout=self.timeout)
                if res.status_code != 200:
                    log.warning(f"Ollama HTTP {res.status_code} - {res.text[:200]}")
                    time.sleep(1)
                    continue
                try:
                    data = res.json()
                    if isinstance(data, dict):
                        for k in ("response","text","output"):
                            if k in data:
                                return data[k]
                        return json.dumps(data)
                except json.JSONDecodeError:
                    pass
                return res.text.strip()
            except requests.exceptions.Timeout:
                log.warning("Ollama timeout, retrying...")
                time.sleep(1)
            except Exception as e:
                log.warning(f"Ollama request error: {e}")
                time.sleep(1)
        log.error("Ollama generate failed after retries")
        return ""
