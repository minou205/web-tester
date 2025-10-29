import asyncio
import time
from urllib.parse import urljoin, urlparse
from core.scanner import scan_page_object
from core.pre_actions import auto_pre_actions, detect_captcha_or_login, manual_human_intervention
from core.retry_handler import retry_action
from core.utils import get_logger

log = get_logger()

SAFE_BUTTON_HINTS = ['next','more','load','continue','expand','open','details','show','search','submit']

async def is_same_domain(url, base):
    try:
        return urlparse(url).netloc == urlparse(base).netloc
    except:
        return False

async def extract_links(page, base_url):
    try:
        links = await page.eval_on_selector_all('a', 'els => els.map(a => a.href)')
        base_domain = urlparse(base_url).netloc
        out = []
        for l in links:
            if not l: continue
            full = urljoin(base_url, l)
            if urlparse(full).netloc == base_domain and full.startswith('http'):
                out.append(full)
        return list(set(out))
    except Exception as e:
        log.warning(f'Link extraction failed: {e}')
        return []

async def click_safe_elements(page, cfg):
    try:
        els = await page.query_selector_all("button, a, [role='button'], [role='link']")
        for el in els:
            try:
                txt = (await el.inner_text() or '').strip().lower()
                if any(h in txt for h in SAFE_BUTTON_HINTS) and not any(k in txt for k in ('login','sign in','register','password','email')):
                    try:
                        await el.click(timeout=3000)
                        await asyncio.sleep(cfg.get('after_interact_delay', 1.0))
                    except:
                        try:
                            await page.evaluate('(el) => el.click()', el)
                        except:
                            pass
            except:
                continue
    except Exception as e:
        log.warning(f'click_safe_elements error: {e}')

async def crawl_site(context, start_url, cfg, max_depth=2):
    visited = set()
    to_visit = [(start_url, 0)]
    results = []

    try:
        setup = await context.new_page()
        await setup.goto(start_url, wait_until='load', timeout=cfg.get('nav_timeout_ms', 60000))
        await asyncio.sleep(cfg.get('wait_after_load', 1.0))
        await auto_pre_actions(setup, cfg)
        await setup.close()
    except Exception as e:
        log.warning(f'pre-actions setup failed: {e}')

    while to_visit:
        url, depth = to_visit.pop(0)
        if url in visited or depth > max_depth:
            continue
        visited.add(url)
        page = await context.new_page()
        try:
            async def nav(): return await page.goto(url, wait_until='load', timeout=cfg.get('nav_timeout_ms', 60000))
            await retry_action(nav, attempts=cfg.get('retry_attempts', 2), delay=cfg.get('retry_delay_seconds', 5))
            await asyncio.sleep(cfg.get('wait_after_load', 1.0))
        except Exception as e:
            log.warning(f'goto failed for {url}: {e}')
            await page.close()
            continue

        try:
            await auto_pre_actions(page, cfg)
            reason = await detect_captcha_or_login(page)
            if reason and cfg.get('allow_manual_human_check'):
                await manual_human_intervention(page, cfg, reason)
            await click_safe_elements(page, cfg)
            res = await scan_page_object(page, url, cfg)
            results.append(res)
            if depth < max_depth:
                new_links = await extract_links(page, start_url)
                for n in new_links:
                    if n not in visited and (n, depth + 1) not in to_visit:
                        to_visit.append((n, depth + 1))
        except Exception as e:
            log.warning(f'crawl page error {url}: {e}')
        finally:
            try:
                await page.close()
            except:
                pass

    log.info(f'Crawl finished. Scanned {len(results)} pages.')
    return results
