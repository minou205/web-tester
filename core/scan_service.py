# core/scan_service.py
# Orchestration service: crawl -> generate scenarios -> execute -> report

import os
import time
import json
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

    # ====================== 🕷️ STEP 1: CRAWL WEBSITE ======================
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=cfg.get("headless", True))
        context = await browser.new_context(user_agent=cfg.get("stealth", {}).get("user_agent"))
        try:
            pg = await context.new_page()
            await pg.goto(url, wait_until="domcontentloaded", timeout=cfg.get("nav_timeout_ms", 60000))
            await auto_pre_actions(pg, cfg)
            await pg.close()
        except Exception as e:
            log.warning(f"Pre-scan load error: {e}")

        pages = await crawl_site(context, url, cfg, max_depth=cfg.get("crawl_max_depth", 2))
        await browser.close()

    # ====================== 🧩 STEP 2: COLLECT FIELDS ======================
    all_fields = []
    for p in pages:
        all_fields.extend(p.get("fields", []))
    log.info(f"Total fields discovered: {len(all_fields)}")

    # ====================== 🤖 STEP 3: GENERATE SCENARIOS (LLM) ======================
    scenarios = []
    try:
        log.info("Generating test scenarios with LLM (Ollama)...")
        raw = generate_scenarios(all_fields, cfg)

        if isinstance(raw, str):
            # Try to parse raw JSON
            try:
                scenarios = json.loads(raw)
                log.info(f"✅ Parsed {len(scenarios)} LLM scenarios successfully.")
            except Exception:
                log.warning("LLM output not valid JSON. Falling back to smart fallback generation.")
                scenarios = generate_scenarios(all_fields, {**cfg, "force_fallback": True})
        elif isinstance(raw, list):
            scenarios = raw
            log.info(f"✅ Received {len(scenarios)} structured scenarios from LLM.")
        else:
            log.warning("Unexpected LLM response type. Using fallback generator.")
            scenarios = generate_scenarios(all_fields, {**cfg, "force_fallback": True})

    except Exception as e:
        log.error(f"LLM generation failed: {e}")
        scenarios = generate_scenarios(all_fields, {**cfg, "force_fallback": True})

    # ====================== ⚙️ STEP 4: EXECUTE SCENARIOS ======================
    results_exec = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=cfg.get("headless", True))
        context = await browser.new_context(user_agent=cfg.get("stealth", {}).get("user_agent"))
        for pg in pages:
            page_url = pg.get("url")
            try:
                page = await context.new_page()
                await page.goto(page_url, wait_until="load", timeout=cfg.get("nav_timeout_ms", 60000))
                await auto_pre_actions(page, cfg)

                # Match scenarios by selector
                page_selectors = [f.get("selector") for f in pg.get("fields", [])]
                page_scenarios = [s for s in scenarios if s.get("selector") in page_selectors]

                exec_res = await execute_scenarios_on_page(page, page_scenarios, cfg)
                results_exec.append({"page": page_url, "results": exec_res})

            except Exception as e:
                log.warning(f"Execution error for {page_url}: {e}")
            finally:
                try:
                    await page.close()
                except:
                    pass
        await browser.close()

    # ====================== 🧾 STEP 5: BUILD REPORTS ======================
    report = {
        "target_url": url,
        "pages": pages,
        "fields_found": len(all_fields),
        "execution_results": results_exec,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "issues": []
    }

    build_reports(report, output_dir=cfg.get("output_dir", "outputs"))
    save_json(report, os.path.join(cfg.get("output_dir", "outputs"), "last_scan_summary.json"))
    log.info("✅ Full scan completed successfully.")
    return report
