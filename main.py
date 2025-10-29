import asyncio
import yaml
import os
import json
import time
from playwright.async_api import async_playwright
from core.crawler import crawl_site
from core.scenario_generator import generate_scenarios
from core.executor import execute_scenarios_on_page
from core.report_generator import build_reports
from core.utils import ensure_dir, get_logger, save_json

log = get_logger()

async def run_scan(url):
    """Main scanning routine (async version)."""
    cfg = yaml.safe_load(open('config.yml', encoding='utf-8'))
    ensure_dir(cfg.get('output_dir', 'outputs'))
    all_pages = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=cfg.get('headless', True))
        context = await browser.new_context()

        all_pages = await crawl_site(context, url, cfg, max_depth=cfg.get('crawl_max_depth', 2))
        await browser.close()

    all_fields = []
    for pg in all_pages:
        all_fields.extend(pg.get('fields', []))

    scenarios = generate_scenarios(all_fields, cfg)

    exec_results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=cfg.get('headless', True))
        context = await browser.new_context()

        for pg in all_pages:
            page = await context.new_page()
            try:
                await page.goto(pg.get('url'), wait_until='load', timeout=cfg.get('nav_timeout_ms', 60000))
            except Exception as e:
                log.warning(f"Navigation failed: {e}")
                continue

            page_scenarios = [s for s in scenarios if s.get('selector') in [f.get('selector') for f in pg.get('fields', [])]]
            result_exec = await execute_scenarios_on_page(page, page_scenarios, cfg)
            exec_results.append({'page': pg.get('url'), 'results': result_exec})
        await browser.close()

    report = {
        'url': url,
        'pages': all_pages,
        'counts': {'found': len(all_fields), 'scanned': len(all_pages)},
        'issues': [],
        'execution': exec_results
    }

    paths = build_reports(report, output_dir=cfg.get('output_dir', 'outputs'))
    save_json(os.path.join(cfg.get('output_dir', 'outputs'), 'last_scan_summary.json'), report)
    log.info(f'Reports generated: {paths}')

async def main():
    """CLI Entry point"""
    url = input("Enter website URL: ").strip()
    if not url.startswith("http"):
        url = "https://" + url
    await run_scan(url)

if __name__ == "__main__":
    asyncio.run(main())
