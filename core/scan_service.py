# core/scan_service.py
# Orchestration service: crawl -> generate scenarios -> execute -> report

import os
import time
from playwright.async_api import async_playwright
from core.crawler import crawl_site
from core.scenario_generator import generate_scenarios
from core.executor import execute_scenarios_on_page
from core.report_generator import build_reports
from core.utils import get_logger, ensure_dir, save_json
from core.pre_actions import auto_pre_actions

log = get_logger()

async def run_full_scan(url, cfg):
    """
    Full async scan flow. Returns final report (dict).
    """
    ensure_dir(cfg.get("output_dir", "outputs"))
    pages = []
    # Crawl
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=cfg.get("headless", True))
        context = await browser.new_context(user_agent=cfg.get("stealth", {}).get("user_agent"))
        try:
            pg = await context.new_page()
            await pg.goto(url, wait_until="domcontentloaded", timeout=cfg.get("nav_timeout_ms", 60000))
            await auto_pre_actions(pg, cfg)
            await pg.close()
        except Exception:
            pass
        pages = await crawl_site(context, url, cfg, max_depth=cfg.get("crawl_max_depth", 2))
        await browser.close()

    # collect fields
    all_fields = []
    for p in pages:
        all_fields.extend(p.get("fields", []))
    log.info(f"Total fields discovered: {len(all_fields)}")

    # scenarios: generator is synchronous (LLM client sync), so call it normally
    scenarios = generate_scenarios(all_fields, cfg)

    # execute scenarios (new browser instance)
    results_exec = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=cfg.get("headless", True))
        context = await browser.new_context(user_agent=cfg.get("stealth", {}).get("user_agent"))
        for pg in pages:
            page = await context.new_page()
            try:
                await page.goto(pg.get("url"), wait_until="load", timeout=cfg.get("nav_timeout_ms", 60000))
                await auto_pre_actions(page, cfg)
                page_selectors = [f.get("selector") for f in pg.get("fields", [])]
                page_scs = [s for s in scenarios if s.get("selector") in page_selectors]
                exec_res = await execute_scenarios_on_page(page, page_scs, cfg)
                results_exec.append({"page": pg.get("url"), "results": exec_res})
            except Exception as e:
                log.warning(f"Execution error for {pg.get('url')}: {e}")
            finally:
                try: await page.close()
                except: pass
        await browser.close()

    report = {
        "target_url": url,
        "pages": pages,
        "fields_found": len(all_fields),
        "execution_results": results_exec,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "issues": []
    }
    build_reports(report, output_dir=cfg.get("output_dir", "outputs"))
    save_json(report, os.path.join(cfg.get("output_dir","outputs"), "last_scan_summary.json"))
    return report
