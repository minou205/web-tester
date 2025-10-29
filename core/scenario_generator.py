# core/scenario_generator.py
# Intelligent scenario generator that relies primarily on the LLM (Ollama)
# to produce logical, realistic, and security-aware test cases for form fields.

import json
from core.llm_handler import OllamaClient
from core.knowledge_manager import find_field_knowledge, save_knowledge
from core.utils import get_logger

log = get_logger()


def build_prompt(fields, context):
    """
    Build a detailed and structured prompt for the LLM.
    The model will:
      1. Analyze each detected field and infer its logical type (e.g. email, password, name, etc.).
      2. Generate 3–7 realistic test cases per field, mixing valid, invalid, boundary, and security cases.
      3. Include a short 'brief_justification' (one sentence) to explain why the test case matters.
      4. Return STRICT JSON only — no text, markdown, or commentary outside JSON.
    """
    header = (
        "You are an expert QA engineer specializing in web form testing.\n"
        "Your goal: generate realistic, logical, and diverse test cases for each field below.\n"
        "Follow these steps carefully:\n"
        "1. Identify the logical purpose of each field (email, password, name, phone, search, etc.).\n"
        "2. For each field, propose 3–7 test cases including: normal use, edge cases, invalid data, and security (e.g. XSS).\n"
        "3. Each case should have fields: payload, desc, type (valid|invalid), and brief_justification.\n"
        "4. DO NOT output anything other than a valid JSON array.\n"
        "5. JSON format example:\n"
        '[{\"selector\":\"<css>\",\"cases\":[{\"payload\":\"...\",\"desc\":\"...\",\"type\":\"valid|invalid\",\"brief_justification\":\"one sentence\"}]}]\n\n'
        "Detected fields:"
    )

    lines = [header]
    for f in fields:
        lines.append(
            f"- selector: {f.get('selector')} | tag: {f.get('tag')} | "
            f"name: {f.get('name')} | placeholder: {f.get('placeholder')} | role: {f.get('role')}"
        )
    if context:
        lines.append("\nContext: " + context)
    return "\n".join(lines)


def try_parse_json_from_raw(raw_text):
    """
    Clean and parse model output safely.
    Handles extra text before/after JSON and Markdown wrappers.
    """
    cleaned = raw_text.strip()

    # Remove markdown fences like ```json
    if cleaned.startswith("```"):
        parts = cleaned.split("```")
        for p in parts:
            p = p.strip()
            if p.startswith("[") or p.startswith("{"):
                cleaned = p
                break

    # Cut off anything after the final closing bracket
    end_idx = cleaned.rfind("]")
    if end_idx != -1:
        cleaned = cleaned[:end_idx + 1]

    # Remove anything before the first opening bracket
    start_idx = cleaned.find("[")
    if start_idx != -1:
        cleaned = cleaned[start_idx:]

    return json.loads(cleaned)



def generate_scenarios(fields, cfg):
    """
    Generate intelligent test scenarios for form fields.
    - Prefers LLM-based generation for logical and security-aware cases.
    - Falls back to heuristic patterns if LLM fails or times out.
    """
    if not fields:
        return []

    context = cfg.get("context_prompt", "Generate realistic QA test cases for web form fields.")
    combined = []

    # Load any existing knowledge first
    for f in fields:
        existing = find_field_knowledge(f)
        if existing and existing.get("cases"):
            combined.append({'selector': f.get('selector'), 'tag': f.get('tag'), 'cases': existing.get('cases')})
        else:
            combined.append(f)

    llm_cfg = cfg.get("llm", {})
    try:
        client = OllamaClient(
            model=llm_cfg.get("ollama_model", "llama3.1:8b"),
            endpoint=llm_cfg.get("ollama_endpoint", "http://localhost:11434/api/generate"),
            timeout=llm_cfg.get("timeout", 180),
            max_retries=llm_cfg.get("max_retries", 2)
        )
    except Exception as e:
        log.warning(f"Failed to initialize Ollama client: {e}")
        client = None

    prompt = build_prompt(combined, context)

    # --- Primary: LLM Generation ---
    if client and client.check_available():
        for attempt in range(2):
            try:
                log.info(f"Ollama request attempt {attempt+1}/2")
                raw = client.generate(prompt)
                if not raw:
                    raise ValueError("Empty response from LLM")

                parsed = try_parse_json_from_raw(raw)
                if not isinstance(parsed, list):
                    raise ValueError("Response is not a JSON list")

                # Basic structural validation
                for item in parsed:
                    if "selector" not in item or "cases" not in item:
                        raise ValueError("Missing required fields in LLM response")

                log.info("✅ LLM produced structured logical scenarios.")
                save_knowledge({'last_generated': parsed})
                return parsed

            except Exception as e:
                log.warning(f"LLM output error (attempt {attempt+1}): {e}")
                # Save raw text for debugging
                with open("outputs/llm_raw_output.txt", "w", encoding="utf-8") as f:
                    f.write(raw if 'raw' in locals() else str(e))
                # Slightly reinforce prompt
                prompt += "\nReminder: Return only pure JSON, no markdown or explanations."
                continue

        log.error("❌ LLM failed to produce valid JSON after retries.")
    else:
        log.warning("Ollama not available, skipping LLM generation.")

    # --- Fallback: Heuristic Generator (only if LLM fails) ---
    log.info("🟡 Using safe heuristic fallback scenario generator.")
    fallback = []
    for f in fields:
        name = (f.get("name") or f.get("placeholder") or f.get("role") or "").lower()
        sel = f.get("selector")
        tag = f.get("tag")
        cases = []

        # Logical fallback cases based on field type
        if "email" in name:
            cases = [
                {"payload": "", "desc": "Empty email", "type": "invalid", "brief_justification": "Empty input should not be accepted."},
                {"payload": "user@", "desc": "Incomplete email", "type": "invalid", "brief_justification": "Missing domain part."},
                {"payload": "user@example.com", "desc": "Valid email", "type": "valid", "brief_justification": "Standard valid email format."}
            ]
        elif "pass" in name:
            cases = [
                {"payload": "", "desc": "Empty password", "type": "invalid", "brief_justification": "Cannot be empty."},
                {"payload": "123", "desc": "Too short password", "type": "invalid", "brief_justification": "Too weak or short."},
                {"payload": "P@ssw0rd!", "desc": "Strong password", "type": "valid", "brief_justification": "Contains upper/lowercase, number, and symbol."}
            ]
        elif "name" in name:
            cases = [
                {"payload": "", "desc": "Empty name", "type": "invalid", "brief_justification": "Name is required."},
                {"payload": "1234", "desc": "Numeric name", "type": "invalid", "brief_justification": "Names shouldn't be numbers."},
                {"payload": "John Doe", "desc": "Valid name", "type": "valid", "brief_justification": "Standard name input."}
            ]
        elif any(k in name for k in ["phone", "number", "age", "qty"]):
            cases = [
                {"payload": "", "desc": "Empty input", "type": "invalid", "brief_justification": "Value required."},
                {"payload": "abc", "desc": "Alphabetic in numeric field", "type": "invalid", "brief_justification": "Non-numeric not allowed."},
                {"payload": "25", "desc": "Valid number", "type": "valid", "brief_justification": "Typical valid integer."}
            ]
        else:
            cases = [
                {"payload": "", "desc": "Empty input", "type": "invalid", "brief_justification": "Should not accept empty."},
                {"payload": "test", "desc": "Normal valid input", "type": "valid", "brief_justification": "Common valid case."},
                {"payload": "<script>alert(1)</script>", "desc": "XSS injection", "type": "invalid", "brief_justification": "Test for script injection vulnerability."}
            ]

        fallback.append({"selector": sel, "tag": tag, "cases": cases})

    save_knowledge({'last_fallback': fallback})
    return fallback
