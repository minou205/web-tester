# core/scenario_generator.py
# Generate test scenarios for fields using LLM (synchronous) or strong fallback.

import json
from core.llm_handler import OllamaClient
from core.knowledge_manager import find_field_knowledge, save_knowledge
from core.utils import get_logger

log = get_logger()

def build_prompt(fields, context):
    lines = [context.strip(), "\nFIELDS DETECTED:"]
    for f in fields:
        lines.append(f"- selector:{f.get('selector')} tag:{f.get('tag')} name:{f.get('name')} placeholder:{f.get('placeholder')} role:{f.get('role')}")
    lines.append("\nReturn JSON list of: {\"selector\":..., \"cases\":[{\"payload\":...,\"desc\":...,\"type\":\"valid|invalid\"}]}")
    return "\n".join(lines)

def smart_fallback(fields):
    out = []
    for f in fields:
        name = (f.get('name') or f.get('placeholder') or f.get('role') or "").lower()
        sel = f.get('selector')
        cases = []
        def add(p,d,t): cases.append({'payload': p, 'desc': d, 'type': t})
        if 'email' in name:
            add('', 'Empty', 'invalid'); add('user@', 'No domain', 'invalid'); add('user@example.com', 'Valid', 'valid')
            add('a'*300 + '@x.com', 'Very long', 'invalid'); add('user+tag@example.com', 'Plus sign', 'valid')
        elif 'pass' in name:
            add('', 'Empty', 'invalid'); add('123', 'Too short', 'invalid'); add('P@ssw0rd!', 'Strong', 'valid'); add('a'*256, 'Very long', 'invalid')
        elif 'name' in name:
            add('', 'Empty', 'invalid'); add('1234', 'Numeric', 'invalid'); add('John Doe', 'Valid', 'valid')
        elif any(k in name for k in ['age','number','qty','phone']):
            add('', 'Empty', 'invalid'); add('abc', 'Non-numeric', 'invalid'); add('25', 'Valid', 'valid')
        else:
            add('', 'Empty', 'invalid'); add('test', 'Normal text', 'valid'); add("<script>alert(1)</script>", "XSS", "invalid")
        out.append({'selector': sel, 'tag': f.get('tag'), 'cases': cases})
    return out

def generate_scenarios(fields, cfg):
    if not fields:
        return []
    context = cfg.get('context_prompt', "You are a QA engineer. Generate test cases for the fields.")
    combined = []
    for f in fields:
        existing = find_field_knowledge(f)
        if existing and existing.get('cases'):
            combined.append({'selector': f.get('selector'), 'tag': f.get('tag'), 'cases': existing.get('cases')})
        else:
            combined.append(f)
    try:
        llm_cfg = cfg.get('llm', {})
        client = OllamaClient(model=llm_cfg.get('ollama_model'), endpoint=llm_cfg.get('ollama_endpoint'),
                              timeout=llm_cfg.get('timeout', 120), max_retries=llm_cfg.get('max_retries', 2))
        prompt = build_prompt(combined, context)
        raw = client.generate(prompt)
        if raw:
            try:
                data = json.loads(raw)
                if isinstance(data, list):
                    save_knowledge({'last_learned': data})
                    return data
            except Exception:
                log.debug("LLM output not JSON - fallback will be used")
    except Exception as e:
        log.warning(f"LLM generation failed: {e}")
    fallback = smart_fallback(fields)
    save_knowledge({'last_fallback': fallback})
    return fallback
