"""
Report Generator Module
Handles generation of test reports
"""

from datetime import datetime
import json

class ReportGenerator:
    def __init__(self, base_url):
        self.base = base_url
    
    def generate_brief_report(self, visited, all_elements, all_scenarios, all_results, analysis):
        """Generate brief web-friendly report"""
        total = len(all_results)
        passed = sum(1 for r in all_results if r['final_status'] == 'passed')
        failed = sum(1 for r in all_results if r['final_status'] == 'failed')
        rate = round((passed / total * 100) if total > 0 else 0, 2)
        
        lines = []
        
        # Header
        lines.append("=" * 90)
        lines.append("QA TEST REPORT".center(90))
        lines.append("=" * 90)
        lines.append(f"Website: {self.base}")
        lines.append(f"Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        lines.append(f"Quality: {analysis.get('overall_quality', 'unknown').upper()}")
        lines.append("")
        
        # Quick Stats
        lines.append("─" * 90)
        lines.append("QUICK STATS")
        lines.append("─" * 90)
        lines.append(f"Pages Tested: {len(visited)}  |  Elements Found: {len(all_elements)}  |  Tests Run: {total}")
        lines.append(f"✓ Passed: {passed} ({rate}%)  |  ✗ Failed: {failed} ({100-rate:.1f}%)")
        lines.append("")
        
        # Summary
        lines.append("─" * 90)
        lines.append("SUMMARY")
        lines.append("─" * 90)
        lines.append(analysis.get('summary', 'No summary available'))
        lines.append("")
        
        # Test Coverage by Page
        lines.append("─" * 90)
        lines.append("TEST COVERAGE BY PAGE")
        lines.append("─" * 90)
        for idx, page in enumerate(sorted(visited), 1):
            page_results = [r for r in all_results if r.get('page_url') == page]
            if page_results:
                page_passed = sum(1 for r in page_results if r['final_status'] == 'passed')
                page_failed = sum(1 for r in page_results if r['final_status'] == 'failed')
                pass_rate = (page_passed / len(page_results) * 100) if page_results else 0
                
                short_url = page.replace(self.base, '') or '/'
                status = "✓" if page_failed == 0 else "⚠"
                
                lines.append(f"{status} {short_url}")
                lines.append(f"   Tests: {len(page_results)} | Passed: {page_passed} | Failed: {page_failed} | Pass Rate: {pass_rate:.0f}%")
        lines.append("")
        
        # Test Types Distribution
        lines.append("─" * 90)
        lines.append("TEST TYPES")
        lines.append("─" * 90)
        stypes = {}
        for s in all_scenarios:
            t = s.get('type', 'unknown')
            stypes[t] = stypes.get(t, 0) + 1
        
        type_list = []
        for t, c in sorted(stypes.items(), key=lambda x: x[1], reverse=True):
            type_list.append(f"{t.replace('_', ' ').title()}: {c}")
        lines.append(" | ".join(type_list))
        lines.append("")
        
        # Failed Tests
        fails = [r for r in all_results if r['final_status'] == 'failed']
        if fails:
            lines.append("─" * 90)
            lines.append(f"FAILED TESTS ({len(fails)} total)")
            lines.append("─" * 90)
            
            high_severity = [f for f in fails if f['llm_analysis'].get('severity') == 'high']
            medium_severity = [f for f in fails if f['llm_analysis'].get('severity') == 'medium']
            low_severity = [f for f in fails if f['llm_analysis'].get('severity') == 'low']
            
            if high_severity:
                lines.append(f"\n🔴 HIGH SEVERITY ({len(high_severity)})")
                for t in high_severity[:5]:
                    short_url = t.get('page_url', '').replace(self.base, '') or '/'
                    lines.append(f"  • {t['title'][:70]}")
                    lines.append(f"    Page: {short_url} | {t['llm_analysis'].get('reason', 'N/A')[:80]}")
            
            if medium_severity:
                lines.append(f"\n🟡 MEDIUM SEVERITY ({len(medium_severity)})")
                for t in medium_severity[:3]:
                    short_url = t.get('page_url', '').replace(self.base, '') or '/'
                    lines.append(f"  • {t['title'][:70]}")
                    lines.append(f"    Page: {short_url} | {t['llm_analysis'].get('reason', 'N/A')[:80]}")
            
            if low_severity and len(high_severity) + len(medium_severity) < 5:
                lines.append(f"\n🟢 LOW SEVERITY ({len(low_severity)})")
                for t in low_severity[:2]:
                    lines.append(f"  • {t['title'][:70]}")
            
            lines.append("")
        
        # Critical Issues
        issues = analysis.get('critical_issues', [])
        if issues:
            lines.append("─" * 90)
            lines.append("CRITICAL ISSUES")
            lines.append("─" * 90)
            for idx, i in enumerate(issues[:5], 1):
                lines.append(f"{idx}. {i}")
            lines.append("")
        
        # Recommendations
        recs = analysis.get('recommendations', [])
        if recs:
            lines.append("─" * 90)
            lines.append("RECOMMENDATIONS")
            lines.append("─" * 90)
            for idx, r in enumerate(recs[:5], 1):
                lines.append(f"{idx}. {r}")
            lines.append("")
        
        # Test Scenarios Summary
        lines.append("─" * 90)
        lines.append("TEST SCENARIOS EXECUTED")
        lines.append("─" * 90)
        
        passed_scenarios = [s for s in all_scenarios if any(r['scenario_id'] == s['scenario_id'] and r['final_status'] == 'passed' for r in all_results)]
        failed_scenarios = [s for s in all_scenarios if any(r['scenario_id'] == s['scenario_id'] and r['final_status'] == 'failed' for r in all_results)]
        
        lines.append(f"✓ {len(passed_scenarios)} scenarios passed")
        lines.append(f"✗ {len(failed_scenarios)} scenarios failed")
        lines.append("")
        
        lines.append("Sample Scenarios by Type:")
        scenario_samples = {}
        for s in all_scenarios:
            stype = s.get('type', 'unknown')
            if stype not in scenario_samples:
                scenario_samples[stype] = []
            if len(scenario_samples[stype]) < 2:
                result_status = "○"
                for r in all_results:
                    if r['scenario_id'] == s['scenario_id']:
                        result_status = "✓" if r['final_status'] == 'passed' else "✗"
                        break
                scenario_samples[stype].append(f"{result_status} {s['title'][:65]}")
        
        for stype, samples in sorted(scenario_samples.items()):
            lines.append(f"\n  {stype.replace('_', ' ').title()}:")
            for sample in samples:
                lines.append(f"    {sample}")
        lines.append("")
        
        # Footer
        lines.append("=" * 90)
        lines.append(f"Full test data exported to JSON files with timestamp {datetime.now().strftime('%Y%m%d_%H%M%S')}")
        lines.append("=" * 90)
        
        return "\n".join(lines)
    
    def save_json_data(self, elements, scenarios, results):
        """Save all data as JSON files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with open(f'elements_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(elements, f, indent=2, ensure_ascii=False)
        
        with open(f'scenarios_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump({'scenarios': scenarios}, f, indent=2, ensure_ascii=False)
        
        with open(f'results_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ JSON data saved with timestamp {timestamp}")