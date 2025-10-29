# core/pre_actions.py
# Async pre-actions: cookie acceptance, modal closing, captcha/login detection, manual intervention.

import asyncio
from core.utils import get_logger

log = get_logger()

COOKIE_SELECTORS = [
    "button:has-text('Accept')",
    "button:has-text('I agree')",
    "button:has-text('Agree')",
    "button.cookie-accept",
    "[aria-label*='accept']",
]

POPUP_SELECTORS = [
    "div[role='dialog'] button[aria-label='close']",
    ".modal .close",
    ".popup .close"
]

LOGIN_HINTS = ["login", "sign in", "register", "password", "email"]

async def auto_pre_actions(page, cfg=None):
    """
    Perform small, safe actions to reveal UI: accept cookie banners, close modals.
    """
    try:
        for sel in COOKIE_SELECTORS:
            try:
                btn = await page.query_selector(sel)
                if btn:
                    try:
                        visible = await btn.is_visible()
                    except Exception:
                        visible = True
                    if visible:
                        try:
                            await btn.click(timeout=2000)
                        except Exception:
                            try:
                                await page.evaluate(f"document.querySelector('{sel}') && document.querySelector('{sel}').click()")
                            except Exception:
                                pass
                        await asyncio.sleep(0.4)
            except Exception:
                continue
        # close common modals
        for sel in POPUP_SELECTORS:
            try:
                btn = await page.query_selector(sel)
                if btn:
                    try:
                        await btn.click(timeout=2000)
                        await asyncio.sleep(0.2)
                    except Exception:
                        pass
            except Exception:
                continue
    except Exception as e:
        log.debug(f"auto_pre_actions error: {e}")

async def detect_captcha_or_login(page):
    """
    Detect simple signs of captcha or login forms.
    Returns 'captcha', 'login' or None.
    """
    try:
        html = (await page.content()).lower()
        if any(k in html for k in ["captcha", "recaptcha", "h-captcha"]):
            return "captcha"
        try:
            pw = await page.query_selector("input[type='password']")
            if pw:
                return "login"
        except Exception:
            pass
        for hint in LOGIN_HINTS:
            if hint in html:
                return "login"
        return None
    except Exception:
        return None

async def manual_human_intervention(page, cfg, reason):
    """
    Open a new headed playwright instance for the user to manually solve captcha/login.
    This is blocking until user presses ENTER.
    """
    from playwright.async_api import async_playwright
    log.info(f"Manual intervention required: {reason}")
    print("\nManual step required — a headed browser will open for you now.")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context()
        pg = await ctx.new_page()
        try:
            await pg.goto(page.url, wait_until="domcontentloaded", timeout=cfg.get("nav_timeout_ms", 60000))
        except Exception:
            pass
        input("Please complete the manual step in the opened window, then press ENTER here...")
        try:
            await browser.close()
        except Exception:
            pass
    log.info("Manual intervention finished.")
