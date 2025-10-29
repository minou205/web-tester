# core/utils.py
# Small utilities: logging, json helpers, directories.

import os
import sys
import json
import datetime
import logging
from contextlib import contextmanager

def ensure_dir(path: str):
    if not path:
        return
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"[WARN] ensure_dir failed for {path}: {e}")

def timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def save_json(data, path):
    try:
        ensure_dir(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[WARN] save_json failed {path}: {e}")

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _rotate_logs(log_dir: str, keep=10):
    try:
        files = sorted([os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.startswith("run_")])
        while len(files) > keep:
            old = files.pop(0)
            try:
                os.remove(old)
            except Exception:
                pass
    except Exception:
        pass

def get_logger(name: str = "AIWebTester"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    log_dir = os.path.join("outputs", "logs")
    ensure_dir(log_dir)
    _rotate_logs(log_dir, keep=10)
    ts = timestamp()
    log_file = os.path.join(log_dir, f"run_{ts}.log")
    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", "%H:%M:%S")
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.info(f"Logging initialized: {log_file}")
    return logger

@contextmanager
def time_track(name: str, logger=None):
    start = datetime.datetime.now()
    try:
        yield
    finally:
        dur = (datetime.datetime.now() - start).total_seconds()
        if logger:
            logger.info(f"{name} took {dur:.2f}s")
        else:
            print(f"{name} took {dur:.2f}s")
