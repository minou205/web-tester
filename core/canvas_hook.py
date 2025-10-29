# core/canvas_hook.py
# Injects a JS hook to capture canvas drawText/strokeText calls, and exposes them via window.__capturedCanvasTexts

from core.utils import get_logger

log = get_logger()

INJECT_JS = r"""
() => {
  try {
    if (window.__canvasHookInstalled) return;
    window.__canvasHookInstalled = true;
    window.__capturedCanvasTexts = [];
    const proto = CanvasRenderingContext2D.prototype;
    const origFill = proto.fillText;
    const origStroke = proto.strokeText;
    const origDrawImage = proto.drawImage;

    proto.fillText = function(text, x, y, ...rest) {
      try { window.__capturedCanvasTexts.push({type:'fillText', text:String(text), x:x, y:y, time:Date.now()}); } catch(e) {}
      return origFill.apply(this, [text, x, y, ...rest]);
    };
    proto.strokeText = function(text, x, y, ...rest) {
      try { window.__capturedCanvasTexts.push({type:'strokeText', text:String(text), x:x, y:y, time:Date.now()}); } catch(e) {}
      return origStroke.apply(this, [text, x, y, ...rest]);
    };
    proto.drawImage = function(...args) {
      try { window.__capturedCanvasTexts.push({type:'drawImage', args: args.length, time:Date.now()}); } catch(e) {}
      return origDrawImage.apply(this, args);
    };
    console.debug("[CanvasHook] installed");
  } catch(e) { console.warn("[CanvasHook] install failed", e); }
}
"""

async def inject_canvas_hook(page):
    """
    Inject hook via add_init_script when possible, else evaluate after load.
    """
    try:
        await page.add_init_script(INJECT_JS)
        log.debug("Injected canvas hook via add_init_script()")
    except Exception:
        try:
            await page.evaluate(INJECT_JS)
            log.debug("Injected canvas hook via evaluate() fallback")
        except Exception as e:
            log.warning(f"Failed to inject canvas hook: {e}")

async def read_canvas_texts_from_page(page):
    """
    Return list from window.__capturedCanvasTexts (if any).
    """
    try:
        data = await page.evaluate("() => (window.__capturedCanvasTexts || [])")
        if data:
            log.debug(f"CanvasHook: got {len(data)} entries")
        return data or []
    except Exception as e:
        log.debug(f"CanvasHook read failed: {e}")
        return []
