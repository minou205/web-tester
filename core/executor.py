# core/executor.py
# Async executor: apply payloads to page elements, detect validation, take screenshots.

import os
import time
import uuid
import asyncio
from core.utils import get_logger, ensure_dir, timestamp
from core.knowledge_manager import update_field_result

log = get_logger()

async def _save_screenshot(page, output_dir, prefix="screenshot"):
    ensure_dir(output_dir)
    name = f"{prefix}_{timestamp()}_{uuid.uuid4().hex[:6]}.png"
    path = os.path.join(output_dir, name)
    try:
        await page.screenshot(path=path, full_page=False)
        return path
    except Exception as e:
        log.debug(f"screenshot failed: {e}")
        return None

async def _apply_value_to_element(page, el, elem_type, payload):
    """
    Apply a payload to an element handle recognizing types (checkbox, radio, select, input).
    """
    try:
        if elem_type == "checkbox":
            try:
                checked = await el.is_checked()
            except Exception:
                checked = await page.evaluate("(e)=>!!e.checked", el)
            should = str(payload).lower() not in ("false","0","no","", "off", "none")
            if should != checked:
                await el.click()
            return True
        if elem_type == "radio":
            try:
                name = await page.evaluate("(e)=>e.getAttribute('name')", el)
                if name:
                    radios = await page.query_selector_all(f"input[type='radio'][name='{name}']")
                    for r in radios:
                        try:
                            rv = await page.evaluate("(e)=>e.getAttribute('value') || ''", r)
                            if rv == str(payload):
                                await r.click()
                                return True
                        except Exception:
                            continue
            except Exception:
                pass
            try:
                await el.click()
                return True
            except Exception:
                return False
        if elem_type in ("select","select-one","select-multiple"):
            try:
                await el.select_option(value=payload)
                return True
            except Exception:
                try:
                    await page.evaluate("(el,v)=>{el.value=v;el.dispatchEvent(new Event('change'))}", el, payload)
                    return True
                except Exception:
                    return False
        # default text-like
        try:
            await el.fill(payload)
            return True
        except Exception:
            try:
                await page.evaluate("(el,v)=>{el.value=v;el.dispatchEvent(new Event('input'));el.dispatchEvent(new Event('change'))}", el, payload)
                return True
            except Exception:
                return False
    except Exception as e:
        log.debug(f"_apply_value_to_element failed: {e}")
        return False

async def _detect_validation_feedback(page, timeout=1.0):
    msgs = []
    try:
        await asyncio.sleep(timeout)
        candidates = await page.query_selector_all("[role='alert'], .error, .invalid, .field-error, .alert, .validation-message")
        for c in candidates:
            try:
                txt = (await c.inner_text()).strip()
                if txt:
                    msgs.append(txt[:400])
            except Exception:
                continue
        body = (await page.content()).lower()
        for kw in ("invalid","error","required","please enter","must be","invalid email","incorrect"):
            if kw in body:
                msgs.append(f"page_contains_keyword:{kw}")
    except Exception as e:
        log.debug(f"validation detection failed: {e}")
    # deduplicate
    out = []
    seen = set()
    for m in msgs:
        if m not in seen:
            seen.add(m); out.append(m)
    return out

async def _find_submit_in_form(page, el):
    try:
        handle = await page.evaluate_handle("(el)=>{ while(el && el.nodeName.toLowerCase()!=='form') el=el.parentElement; return el; }", el)
        if handle:
            try:
                submits = await handle.query_selector_all("button[type='submit'], input[type='submit']")
                if submits:
                    return submits[0]
            except Exception:
                pass
        btn = await page.query_selector("button[type='submit'], input[type='submit'], button:has-text('Submit'), button:has-text('Send')")
        return btn
    except Exception:
        return None

async def execute_scenarios_on_page(page, scenarios, cfg):
    results = []
    if not scenarios:
        return results
    screenshot_dir = cfg.get("screenshot_dir", "outputs/screenshots")
    ensure_dir(screenshot_dir)
    pause = cfg.get("after_interact_delay", 0.8)
    detect_timeout = cfg.get("validation_detect_seconds", 1.0)

    for sc in scenarios:
        selector = sc.get("selector")
        cases = sc.get("cases") or []
        for case in cases:
            payload = case.get("payload","")
            expected = case.get("type","")
            desc = case.get("desc","")
            res = {"selector": selector, "payload": payload, "desc": desc, "expected": expected, "status":"not_run", "messages": [], "screenshots": {}}
            try:
                el = None
                if selector:
                    try:
                        el = await page.query_selector(selector)
                    except Exception:
                        el = None
                before = await _save_screenshot(page, screenshot_dir, prefix="before")
                if before: res["screenshots"]["before"] = before
                if not el:
                    res["status"] = "element_not_found"
                    results.append(res)
                    try:
                        update_field_result({"selector": selector}, case, res)
                    except Exception:
                        pass
                    continue
                tag = await page.evaluate("(e)=>e.tagName.toLowerCase()", el)
                elem_type = None
                if tag == "input":
                    elem_type = await page.evaluate("(e)=> (e.getAttribute('type')||'text').toLowerCase()", el)
                elif tag == "select":
                    elem_type = "select"
                elif tag == "textarea":
                    elem_type = "textarea"
                else:
                    role = await page.evaluate("(e)=> e.getAttribute('role')||''", el) or ""
                    if "checkbox" in role:
                        elem_type = "checkbox"
                    if "radio" in role:
                        elem_type = "radio"
                applied = await _apply_value_to_element(page, el, elem_type or tag, payload)
                await asyncio.sleep(pause)
                submit = await _find_submit_in_form(page, el)
                if submit:
                    try:
                        await submit.click()
                        await asyncio.sleep(pause)
                    except Exception:
                        try:
                            await page.evaluate("(b)=>b.click()", submit)
                            await asyncio.sleep(pause)
                        except Exception:
                            pass
                observed = None
                try:
                    if elem_type == "checkbox":
                        observed = await el.is_checked()
                    elif elem_type == "radio":
                        observed = await page.evaluate("(e)=> e.checked ? (e.value || true) : false", el)
                    else:
                        observed = await page.evaluate("(e)=>e.value", el)
                except Exception:
                    observed = None
                msgs = await _detect_validation_feedback(page, timeout=detect_timeout)
                if msgs:
                    res["messages"].extend(msgs)
                if not applied:
                    res["status"] = "apply_failed"
                else:
                    if msgs and expected == "valid":
                        res["status"] = "failed_validation"
                    elif not msgs and expected == "invalid":
                        res["status"] = "no_validation_detected"
                    else:
                        res["status"] = "applied"
                after = await _save_screenshot(page, screenshot_dir, prefix="after")
                if after: res["screenshots"]["after"] = after
                res["observed_value"] = str(observed) if observed is not None else None
                results.append(res)
                try:
                    update_field_result({"selector": selector}, case, res)
                except Exception as e:
                    log.debug(f"update_field_result failed: {e}")
            except Exception as e:
                log.exception(f"execute_scenarios_on_page error for {selector}: {e}")
                res["status"] = "error"; res["error"] = str(e)
                results.append(res)
                try:
                    update_field_result({"selector": selector}, case, res)
                except Exception:
                    pass
    return results
