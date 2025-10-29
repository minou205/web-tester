# core/llm_handler.py
# Advanced, resilient Ollama client with robust retry & stream handling

import requests
import json
import time
from core.utils import get_logger

log = get_logger()

class OllamaClient:
    def __init__(self, model='llama3.1:8b', endpoint='http://127.0.0.1:11434/api/generate', timeout=120, max_retries=2, retry_delay=5):
        self.model = model
        self.endpoint = endpoint.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._available = None

    # ---------------------------
    # Health check
    # ---------------------------
    def check_available(self):
        """Ping Ollama server to verify availability."""
        if self._available is not None:
            return self._available
        try:
            base = self.endpoint.replace('/api/generate', '')
            res = requests.get(base + '/api/tags', timeout=3)
            self._available = (res.status_code == 200)
            log.info(f"Ollama availability check: {self._available}")
        except Exception as e:
            log.warning(f"Ollama not reachable: {e}")
            self._available = False
        return self._available

    @property
    def available(self):
        """Lazy property to check model readiness."""
        return self.check_available()

    # ---------------------------
    # Main generation with retries
    # ---------------------------
    def generate(self, prompt: str):
        """Send a prompt to Ollama and return the full text output."""
        if not self.available:
            raise ConnectionError("Ollama not available or not running.")

        for attempt in range(1, self.max_retries + 1):
            try:
                log.info(f"Ollama request attempt {attempt}/{self.max_retries}")

                payload = {
                    'model': self.model,
                    'prompt': prompt,
                    'stream': True,
                    'max_tokens': 512
                }

                # Start the request
                with requests.post(self.endpoint, json=payload, timeout=self.timeout, stream=True) as res:
                    res.raise_for_status()
                    full_output = ""
                    last_chunk_time = time.time()

                    # Stream response line by line

                    for raw_line in res.iter_lines():
                        if not raw_line:
                            # prevent infinite hang if no data for long time
                            if time.time() - last_chunk_time > self.timeout:
                                raise TimeoutError("Ollama stream stalled.")
                            continue

                        last_chunk_time = time.time()

                        # --- fix: ensure string decoding ---
                        try:
                            line = raw_line.decode('utf-8')
                        except Exception:
                            # fallback to latin or ignore errors
                            line = str(raw_line, errors='ignore')

                        # End signal
                        if '"done":true' in line:
                            break

                        # Each line is partial JSON
                        try:
                            part = json.loads(line)
                            if 'response' in part:
                                text = part['response']
                                full_output += text
                                print(text, end='', flush=True)
                        except json.JSONDecodeError:
                            continue




                    log.info("✅ Ollama streaming completed successfully.")
                    return full_output.strip()

            except Exception as e:
                log.warning(f"Ollama request failed (attempt {attempt}): {e}")
                if attempt < self.max_retries:
                    log.info(f"Retrying in {self.retry_delay}s...")
                    time.sleep(self.retry_delay)
                else:
                    log.error("❌ Ollama request failed after all retries.")
                    raise
