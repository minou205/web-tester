"""
Professional QA Testing Program - Full Featured Version
Includes: Performance, Accessibility, Workflows, Screenshots, Bug Reports
"""

from urllib.parse import urlparse
import time
from datetime import datetime
import json

from enhanced_browser_manager import BrowserManager
from page_scanner import PageScanner
from llm_manager import LLMManager
from report_generator import ReportGenerator
from accessibility_tester import AccessibilityTester
from workflow_tester import WorkflowTester
from bug_report_generator import BugReportGenerator


class ProfessionalQATester:
    def __init__(self):
        self.visited = set()
        self.all_elements = []
        self.all_scenarios = []
        self.all_results = []
        self.links = set()
        self.queue = []
        self.max_pages = 60
        self.max_depth = 3
        
        # Advanced features
        self.accessibility_results = []
        self.workflow_results = []
        self.performance_data = []
        
        # Modules
        self.browser = BrowserManager()
        self.scanner = None
        self.llm = LLMManager()
        self.reporter = None
        self.accessibility_tester = AccessibilityTester()
        self.workflow_tester = None
        self.bug_reporter = None
        
        self.domain = None
        self.base = None
    
    def print_banner(self):
        print("\n" + "="*80)
        print("    🔍 PROFESSIONAL QA TESTING PROGRAM 🔍")
        print("="*80)
        print("Features: Performance | Accessibility | Workflows | Screenshots | Bug Reports")
        print("="*80 + "\n")
    
    def execute_scenario(self, scenario, url):
        """Execute test scenario with screenshot on failure"""
        res = {
            'scenario_id': scenario.get('scenario_id', ''),
            'title': scenario.get('title', ''),
            'type': scenario.get('type', ''),
            'status': 'passed',
            'error': None,
            'execution_time': 0,
            'page_url': url,
            'screenshot': None,
            'console_errors': []
        }
        
        t1 = time.time()
        
        try:
            targets = scenario.get('target_elements', [])
            for tgt in targets:
                self.browser.execute_action(
                    tgt.get('selector', ''),
                    tgt.get('action', 'click'),
                    tgt.get('test_data', '')
                )
            res['status'] = 'passed'
            
        except Exception as e:
            res['status'] = 'failed'
            res['error'] = str(e)[:200]
            
            # Take screenshot on failure
            screenshot = self.browser.take_screenshot(
                scenario.get('title', 'test')[:30],
                scenario.get('scenario_id', ''),
                failed=True
            )
            res['screenshot'] = screenshot
            
            # Get console errors
            res['console_errors'] = self.browser.check_console_errors()
        
        res['execution_time'] = round(time.time() - t1, 2)
        return res
    
    def process_page_complete(self, url, is_first=False):
        """Complete page processing with ALL advanced features"""
        try:
            print(f"\n{'='*80}")
            print(f"📄 PROCESSING PAGE: {url}")
            print(f"{'='*80}")
            
            if is_first:
                self.browser.show_manual_check(url)
            
            # Measure performance
            print(f"\n  ⚡ Measuring page performance...")
            perf_data = self.browser.measure_page_load_time(url)
            self.performance_data.append(perf_data)
            print(f"  ✓ Page load: {perf_data['page_load_time']}s | DOM ready: {perf_data['dom_ready_time']}s")
            
            self.visited.add(url)
            self.links.add(url)
            
            # STEP 1: Scan page
            print(f"\n  🔍 Step 1: Scanning page for elements...")
            fields = self.scanner.scan_page(self.browser.driver, url)
            
            if not fields:
                print(f"  ⚠️  No testable elements found")
                new_links = []
                if len(self.visited) < self.max_pages:
                    new_links = self.scanner.get_links(self.browser.driver, self.visited)
                    self.links.update(new_links)
                return new_links
            
            print(f"  ✓ Found {len(fields)} elements")
            self.all_elements.extend(fields)
            
            # STEP 2: Accessibility Testing
            print(f"\n  ♿ Step 2: Running accessibility tests...")
            accessibility_result = self.accessibility_tester.test_page_accessibility(
                self.browser.driver, url
            )
            self.accessibility_results.append(accessibility_result)
            print(f"  ✓ Accessibility Score: {accessibility_result['percentage']}% ({accessibility_result['grade']})")
            
            # STEP 3: Detect Workflows
            print(f"\n  🔄 Step 3: Detecting user workflows...")
            workflows = self.workflow_tester.detect_workflows(fields, url)
            if workflows:
                print(f"  ✓ Found {len(workflows)} workflows:")
                for wf in workflows:
                    print(f"     • {wf['name']}")
            else:
                print(f"  ✓ No workflows detected")
            
            # STEP 4: Generate scenarios
            print(f"\n  🧪 Step 4: Generating test scenarios...")
            page_scenarios = []
            
            for idx, elem in enumerate(fields, 1):
                print(f"    Element {idx}/{len(fields)}: {elem['type']} - {elem.get('name', elem.get('id', 'unnamed'))[:30]}")
                scenarios = self.llm.generate_scenarios(elem)
                if scenarios:
                    for scen in scenarios:
                        page_scenarios.append(scen)
                        self.all_scenarios.append(scen)
                        print(f"      → {scen['scenario_id']}: {scen['title'][:70]}")
            
            print(f"\n  ✓ Generated {len(page_scenarios)} total scenarios")
            
            # STEP 5: Execute workflows
            if workflows:
                print(f"\n  🔄 Step 5: Executing workflows...")
                for wf in workflows:
                    print(f"    Executing: {wf['name']}")
                    wf_result = self.workflow_tester.execute_workflow(wf, url)
                    self.workflow_results.append(wf_result)
                    status = "✅" if wf_result['status'] == 'passed' else "❌"
                    print(f"    {status} {wf_result['status'].upper()} - {wf_result['steps_completed']}/{wf_result['total_steps']} steps")
            
            # STEP 6: Execute and analyze scenarios
            print(f"\n  🚀 Step 6: Executing & Analyzing test scenarios...")
            page_results = []
            
            for idx, scenario in enumerate(page_scenarios, 1):
                print(f"\n    [{idx}/{len(page_scenarios)}] {scenario.get('scenario_id')} - {scenario.get('title', '')[:60]}")
                print(f"      Type: {scenario.get('type', 'unknown')}")
                
                self.browser.driver.get(url)
                time.sleep(1.5)
                
                print(f"      ⚙️  Executing test...", end='', flush=True)
                result = self.execute_scenario(scenario, url)
                print(f" Done")
                
                print(f"      🤖 Analyzing result with AI...", end='', flush=True)
                analysis = self.llm.analyze_result(result, scenario)
                print(f" Done")
                
                result['llm_analysis'] = analysis
                result['final_status'] = analysis['final_status']
                
                page_results.append(result)
                self.all_results.append(result)
                
                # Create bug report if failed
                if result['final_status'] == 'failed':
                    self.bug_reporter.create_bug_report(
                        result, scenario,
                        screenshot_path=result.get('screenshot'),
                        console_errors=result.get('console_errors')
                    )
                
                status_icon = "✅" if result['final_status'] == 'passed' else "❌"
                reason = analysis.get('reason', 'No reason provided')
                print(f"      {status_icon} {result['final_status'].upper()}: {reason}")
            
            passed = sum(1 for r in page_results if r['final_status'] == 'passed')
            failed = sum(1 for r in page_results if r['final_status'] == 'failed')
            print(f"\n  📊 Page Summary: {passed} passed, {failed} failed")
            print(f"  ✓ All tests complete for this page")
            
            # Collect links
            new_links = []
            if len(self.visited) < self.max_pages:
                self.browser.driver.get(url)
                time.sleep(1)
                new_links = self.scanner.get_links(self.browser.driver, self.visited)
                self.links.update(new_links)
                if new_links:
                    print(f"  ✓ Found {len(new_links)} new links")
            
            return new_links
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            self.visited.add(url)
            return []
    
    def generate_comprehensive_report(self):
        """Generate comprehensive report with all advanced features"""
        print("\n" + "="*80)
        print("📄 GENERATING COMPREHENSIVE REPORT")
        print("="*80)
        
        # Calculate statistics
        total = len(self.all_results)
        passed = sum(1 for r in self.all_results if r['final_status'] == 'passed')
        failed = sum(1 for r in self.all_results if r['final_status'] == 'failed')
        rate = round((passed / total * 100) if total > 0 else 0, 2)
        
        fails = [r for r in self.all_results if r['final_status'] == 'failed']
        
        # Get LLM analysis
        print("  🤖 Generating overall analysis...", end='', flush=True)
        analysis = self.llm.analyze_overall(
            total, passed, failed, rate,
            len(self.visited), len(self.all_elements), fails
        )
        print(" Done")
        
        # Generate main report
        print("  📝 Writing main report...", end='', flush=True)
        main_report = self.reporter.generate_brief_report(
            self.visited, self.all_elements,
            self.all_scenarios, self.all_results, analysis
        )
        
        # Add performance section
        main_report += "\n\n" + "─" * 90
        main_report += "\n⚡ PERFORMANCE TESTING"
        main_report += "\n" + "─" * 90
        if self.performance_data:
            avg_load = sum(p['page_load_time'] for p in self.performance_data) / len(self.performance_data)
            main_report += f"\nAverage Page Load Time: {avg_load:.2f}s"
            main_report += f"\nFastest Page: {min(self.performance_data, key=lambda x: x['page_load_time'])['url']} ({min(p['page_load_time'] for p in self.performance_data):.2f}s)"
            main_report += f"\nSlowest Page: {max(self.performance_data, key=lambda x: x['page_load_time'])['url']} ({max(p['page_load_time'] for p in self.performance_data):.2f}s)"
        
        # Add accessibility section
        main_report += "\n\n" + "─" * 90
        main_report += "\n♿ ACCESSIBILITY TESTING"
        main_report += "\n" + "─" * 90
        if self.accessibility_results:
            avg_score = sum(a['percentage'] for a in self.accessibility_results) / len(self.accessibility_results)
            main_report += f"\nAverage Accessibility Score: {avg_score:.1f}%"
            for result in self.accessibility_results:
                main_report += f"\n  • {result['url'].replace(self.base, '') or '/'}: {result['percentage']}% ({result['grade']})"
        
        # Add workflow section
        if self.workflow_results:
            main_report += "\n\n" + "─" * 90
            main_report += "\n🔄 WORKFLOW TESTING"
            main_report += "\n" + "─" * 90
            wf_passed = sum(1 for w in self.workflow_results if w['status'] == 'passed')
            wf_failed = sum(1 for w in self.workflow_results if w['status'] == 'failed')
            main_report += f"\nWorkflows Tested: {len(self.workflow_results)}"
            main_report += f"\nPassed: {wf_passed} | Failed: {wf_failed}"
        
        # Save main report
        fname = f"qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(main_report)
        
        print(" Done")
        print(f"  ✅ Main report saved to {fname}")
        
        # Save bug reports
        if self.bug_reporter.bugs:
            bug_file = self.bug_reporter.export_bugs_to_file()
            print(f"  ✅ Bug reports saved to {bug_file}")
        
        # Save JSON data
        self.reporter.save_json_data(self.all_elements, self.all_scenarios, self.all_results)
        
        # Save accessibility report
        if self.accessibility_results:
            acc_file = f"accessibility_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(acc_file, 'w') as f:
                json.dump(self.accessibility_results, f, indent=2)
            print(f"  ✅ Accessibility report saved to {acc_file}")
        
        # Save performance data
        if self.performance_data:
            perf_file = f"performance_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(perf_file, 'w') as f:
                json.dump(self.performance_data, f, indent=2)
            print(f"  ✅ Performance data saved to {perf_file}")
        
        return fname
    
    def run(self):
        try:
            self.print_banner()
            
            url = input("🌐 Enter the website URL to test: ").strip()
            if not url.startswith('http'):
                url = 'https://' + url
            
            self.domain = urlparse(url).netloc
            self.base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            
            print(f"\n✅ Testing URL: {url}")
            print(f"🌐 Base domain: {self.base}")
            
            # Initialize modules
            self.scanner = PageScanner(self.domain, self.base)
            self.reporter = ReportGenerator(self.base)
            self.workflow_tester = WorkflowTester(self.browser, self.llm)
            self.bug_reporter = BugReportGenerator(self.base, 'chrome')
            self.browser.initialize_browser()
            
            # Simple mode: just process one or crawl
            choice = input("\n1. Single page\n2. Crawl\nChoice: ").strip()
            
            if choice == '2':
                print("\n🕷️  Starting crawl mode...")
                self.queue = [(url, 0)]
                is_first = True
                
                while self.queue and len(self.visited) < self.max_pages:
                    curr, depth = self.queue.pop(0)
                    if curr in self.visited or depth > self.max_depth:
                        continue
                    
                    print(f"\n[Page {len(self.visited) + 1}/{self.max_pages}] Depth {depth}")
                    new_links = self.process_page_complete(curr, is_first=is_first)
                    is_first = False
                    
                    for link in new_links:
                        if link not in [u for u, _ in self.queue] and link not in self.visited:
                            self.queue.append((link, depth + 1))
            else:
                print("\n📄 Processing single page...")
                self.process_page_complete(url, is_first=True)
            
            self.browser.close()
            
            # Generate final report
            print("\n" + "="*80)
            print("🎯 TESTING COMPLETE - GENERATING REPORTS")
            print("="*80)
            
            self.generate_comprehensive_report()
            
            # Final summary
            print("\n\n" + "="*80)
            print("✅ ALL TESTING COMPLETE!")
            print("="*80)
            print(f"\n📊 Summary:")
            print(f"  • Pages: {len(self.visited)}")
            print(f"  • Elements: {len(self.all_elements)}")
            print(f"  • Scenarios: {len(self.all_scenarios)}")
            print(f"  • Tests: {len(self.all_results)}")
            print(f"  • Passed: {sum(1 for r in self.all_results if r['final_status'] == 'passed')}")
            print(f"  • Failed: {sum(1 for r in self.all_results if r['final_status'] == 'failed')}")
            print(f"  • Workflows: {len(self.workflow_results)}")
            print(f"  • Bugs Found: {len(self.bug_reporter.bugs)}")
            print(f"  • Screenshots: Check 'screenshots/' folder")
            
            print("\n" + "="*80)
            print("Thank you for using Professional QA Testing Program!")
            print("="*80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            self.browser.close()
        except Exception as e:
            print(f"\n\n❌ Error: {str(e)}")
            self.browser.close()
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    tester = ProfessionalQATester()
    tester.run()