# core/scanner.py
# Async page scanner: extracts interactive elements, shadow DOM, same-origin frames, canvas texts

import time
from urllib.parse import urlparse
from core.utils import get_logger
from core.canvas_hook import inject_canvas_hook, read_canvas_texts_from_page

log = get_logger()

JS_EXTRACTOR = r"""
() => {
  const results = [];
  const visited = new WeakSet();

  function getPath(el){
    if (!el) return null;
    const path = [];
    while (el && el.nodeType === 1){
      let name = el.tagName.toLowerCase();
      if (el.id){ name += "#" + el.id; path.unshift(name); break; }
      let sib = el, idx = 1;
      while ((sib = sib.previousElementSibling)) idx++;
      name += ":nth-child(" + idx + ")";
      path.unshift(name);
      el = el.parentElement;
    }
    return path.join(" > ");
  }

  function isInteractive(node){
    if (!node || node.nodeType !== 1) return false;
    const tag = node.tagName.toLowerCase();
    if (['input','textarea','select','button','a','summary','label'].includes(tag)) return true;
    if (node.hasAttribute && node.hasAttribute('contenteditable')) return true;
    const role = node.getAttribute && node.getAttribute('role');
    if (role && /(button|textbox|slider|menuitem|switch|link|combobox|search|tab|checkbox)/.test(role)) return true;
    try { if (node.tabIndex >= 0) return true; } catch(e) {}
    if (node.onclick || node.oninput || node.onchange) return true;
    return false;
  }

  function walk(node){
    if (!node || visited.has(node)) return;
    visited.add(node);
    try {
      if (isInteractive(node)){
        results.push({
          tag: node.tagName.toLowerCase(),
          name: node.getAttribute ? node.getAttribute('name') : null,
          id: node.id || null,
          type: node.getAttribute ? node.getAttribute('type') : null,
          role: node.getAttribute ? node.getAttribute('role') : null,
          placeholder: node.getAttribute ? node.getAttribute('placeholder') : null,
          text: node.innerText ? node.innerText.trim().slice(0,300) : '',
          visible: !!(node.offsetWidth || node.offsetHeight || node.getClientRects().length),
          selector: getPath(node)
        });
      }
      if (node.shadowRoot) try { walk(node.shadowRoot); } catch(e){}
      for (const c of (node.children || [])) walk(c);
    } catch(e){}
  }

  walk(document);
  return results;
}
"""

async def scan_page_object(page, url, cfg):
    """
    Scan a single page for interactive elements.
    Returns dict: {url, fields, canvas_texts, timestamp}
    """
    log.info(f"[scan_page_object] Scanning {url}")
    all_elements = []
    canvas_texts = []

    # inject canvas hook early (init script)
    try:
        await inject_canvas_hook(page)
    except Exception as e:
        log.debug(f"inject_canvas_hook failed: {e}")

    # evaluate DOM extractor
    try:
        elements = await page.evaluate(JS_EXTRACTOR)
        if elements:
            all_elements.extend(elements)
    except Exception as e:
        log.warning(f"[scan_page_object] JS extraction failed: {e}")

    # same-origin iframes
    try:
        frames = page.frames
        for f in frames:
            try:
                if f.url and urlparse(f.url).netloc == urlparse(url).netloc:
                    sub = await f.evaluate(JS_EXTRACTOR)
                    for el in (sub or []):
                        el["_iframe"] = f.url
                    all_elements.extend(sub or [])
            except Exception:
                continue
    except Exception as e:
        log.debug(f"[scan_page_object] frames iteration failed: {e}")

    # optional canvas screenshots (if OCR enabled)
    try:
        if cfg.get("canvas", {}).get("enable_ocr", False):
            canvases = await page.query_selector_all("canvas")
            for i, c in enumerate(canvases):
                path = f"{cfg.get('output_dir','outputs')}/canvas_{int(time.time())}_{i}.png"
                try:
                    await c.screenshot(path=path)
                    canvas_texts.append({"canvas_image": path})
                except Exception:
                    pass
    except Exception as e:
        log.debug(f"[scan_page_object] canvas screenshot error: {e}")

    # read any texts captured by the injected canvas hook
    try:
        captured = await read_canvas_texts_from_page(page)
        if captured:
            canvas_texts.extend(captured)
    except Exception as e:
        log.debug(f"[scan_page_object] read_canvas_texts failed: {e}")

    # deduplicate and filter invisibles
    seen = set()
    unique = []
    for el in all_elements:
        key = (el.get("selector"), el.get("name"), el.get("id"))
        if key not in seen and el.get("visible", True):
            seen.add(key)
            unique.append(el)

    log.info(f"[scan_page_object] Found {len(unique)} interactive elements on {url}")
    return {
        "url": url,
        "fields": unique,
        "canvas_texts": canvas_texts,
        "timestamp": time.strftime("%Y-%m-%d_%H-%M-%S")
    }
