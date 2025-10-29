# core/knowledge_manager.py
# Persistent knowledge store for learned field test cases.

import os
import json
import time
from core.utils import get_logger, ensure_dir

log = get_logger()
KNOW_PATH = os.path.join("outputs", "knowledge.json")

def _load():
    try:
        if not os.path.exists(KNOW_PATH):
            return {"fields": {}}
        with open(KNOW_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as e:
        log.warning(f"knowledge load failed: {e}")
        return {"fields": {}}

def _save(data):
    try:
        ensure_dir(os.path.dirname(KNOW_PATH))
        with open(KNOW_PATH, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
    except Exception as e:
        log.warning(f"knowledge save failed: {e}")

def _make_key(field):
    tag = (field.get("tag") or "").lower().strip()
    name = (field.get("name") or "").lower().strip()
    role = (field.get("role") or "").lower().strip()
    ph = (field.get("placeholder") or "").lower().strip()
    return f"{tag}|{name}|{role}|{ph}"

def load_knowledge():
    return _load()

def save_knowledge(data):
    base = _load()
    base.update(data)
    _save(base)

def find_field_knowledge(field):
    data = _load()
    key = _make_key(field)
    entry = data.get("fields", {}).get(key)
    if entry:
        log.debug(f"knowledge found for {key}")
    return entry

def update_field_result(field, scenario, result):
    data = _load()
    key = _make_key(field)
    fld = data.setdefault("fields", {}).setdefault(key, {
        "meta": {"tag": field.get("tag"), "name": field.get("name"), "placeholder": field.get("placeholder"), "role": field.get("role")},
        "cases": [],
        "stats": {"total":0, "success":0, "fail":0},
        "updated": time.strftime("%Y-%m-%d_%H-%M-%S")
    })
    payload = scenario.get("payload")
    desc = scenario.get("desc")
    typ = scenario.get("type")
    if not any(c.get("payload")==payload for c in fld["cases"]):
        fld["cases"].append({"payload": payload, "desc": desc, "type": typ, "first_seen": time.strftime("%Y-%m-%d_%H-%M-%S")})
    fld["stats"]["total"] += 1
    if result.get("status") in ("applied",):
        fld["stats"]["success"] += 1
    else:
        fld["stats"]["fail"] += 1
    fld["updated"] = time.strftime("%Y-%m-%d_%H-%M-%S")
    _save(data)
    return True

def clear_knowledge():
    try:
        if os.path.exists(KNOW_PATH):
            os.remove(KNOW_PATH)
            log.info("knowledge cleared")
    except Exception as e:
        log.warning(f"clear_knowledge failed: {e}")
