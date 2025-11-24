"""
Bug Report Generator Module
Creates professional bug reports with all necessary details
"""

from datetime import datetime
import platform

class BugReportGenerator:
    def __init__(self, base_url, browser_type='chrome'):
        self.base_url = base_url
        self.browser_type = browser_type
        self.bugs = []
    
    def create_bug_report(self, test_result, scenario, screenshot_path=None, console_errors=None):
        """Create a detailed bug report from a failed test"""
        if test_result['final_status'] != 'failed':
            return None
        
        bug = {
            'bug_id': f"BUG_{len(self.bugs) + 1:04d}",
            'title': self._generate_bug_title(test_result, scenario),
            'severity': test_result['llm_analysis'].get('severity', 'medium'),
            'priority': scenario.get('priority', 'medium'),
            'status': 'Open',
            'reported_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'test_scenario_id': test_result['scenario_id'],
            'page_url': test_result['page_url'],
            'browser': self.browser_type.capitalize(),
            'os': platform.system(),
            'description': self._generate_description(test_result, scenario),
            'steps_to_reproduce': self._generate_steps(scenario),
            'expected_result': scenario.get('expected_result', 'Test should pass'),
            'actual_result': test_result.get('error', 'Test failed'),
            'screenshot': screenshot_path,
            'console_errors': console_errors or [],
            'additional_info': {
                'test_type': scenario.get('type', 'unknown'),
                'execution_time': test_result.get('execution_time', 0),
                'ai_analysis': test_result['llm_analysis'].get('reason', '')
            }
        }
        
        self.bugs.append(bug)
        return bug
    
    def _generate_bug_title(self, test_result, scenario):
        """Generate concise bug title"""
        page_name = test_result['page_url'].split('/')[-1] or 'Homepage'
        test_name = scenario.get('title', 'Unknown Test')
        return f"{page_name} - {test_name}"
    
    def _generate_description(self, test_result, scenario):
        """Generate detailed bug description"""
        desc = f"The test '{scenario.get('title', 'Unknown')}' failed on the page {test_result['page_url']}.\n\n"
        desc += f"Test Type: {scenario.get('type', 'unknown').replace('_', ' ').title()}\n"
        desc += f"Error: {test_result.get('error', 'No error message')}\n"
        desc += f"AI Analysis: {test_result['llm_analysis'].get('reason', 'No analysis')}\n"
        return desc
    
    def _generate_steps(self, scenario):
        """Generate steps to reproduce"""
        steps = []
        
        # Add navigation step
        steps.append(f"1. Navigate to the test page")
        
        # Add scenario steps
        if 'steps' in scenario and scenario['steps']:
            for idx, step in enumerate(scenario['steps'], 2):
                steps.append(f"{idx}. {step}")
        
        # Add target element actions
        if 'target_elements' in scenario:
            start_idx = len(steps) + 1
            for idx, target in enumerate(scenario['target_elements'], start_idx):
                action = target.get('action', 'interact with')
                selector = target.get('selector', 'element')
                data = target.get('test_data', '')
                
                if action == 'click':
                    steps.append(f"{idx}. Click on {selector}")
                elif action == 'fill':
                    steps.append(f"{idx}. Enter '{data}' in {selector}")
                elif action == 'select':
                    steps.append(f"{idx}. Select '{data}' from {selector}")
                else:
                    steps.append(f"{idx}. {action.title()} on {selector}")
        
        return steps
    
    def format_bug_report(self, bug):
        """Format bug report as text"""
        lines = []
        lines.append("="*80)
        lines.append(f"BUG REPORT - {bug['bug_id']}")
        lines.append("="*80)
        lines.append("")
        lines.append(f"Title: {bug['title']}")
        lines.append(f"Severity: {bug['severity'].upper()}")
        lines.append(f"Priority: {bug['priority'].upper()}")
        lines.append(f"Status: {bug['status']}")
        lines.append(f"Reported: {bug['reported_date']}")
        lines.append("")
        lines.append("─"*80)
        lines.append("ENVIRONMENT")
        lines.append("─"*80)
        lines.append(f"URL: {bug['page_url']}")
        lines.append(f"Browser: {bug['browser']}")
        lines.append(f"OS: {bug['os']}")
        lines.append("")
        lines.append("─"*80)
        lines.append("DESCRIPTION")
        lines.append("─"*80)
        lines.append(bug['description'])
        lines.append("")
        lines.append("─"*80)
        lines.append("STEPS TO REPRODUCE")
        lines.append("─"*80)
        for step in bug['steps_to_reproduce']:
            lines.append(step)
        lines.append("")
        lines.append("─"*80)
        lines.append("EXPECTED RESULT")
        lines.append("─"*80)
        lines.append(bug['expected_result'])
        lines.append("")
        lines.append("─"*80)
        lines.append("ACTUAL RESULT")
        lines.append("─"*80)
        lines.append(bug['actual_result'])
        lines.append("")
        
        if bug['screenshot']:
            lines.append("─"*80)
            lines.append("SCREENSHOT")
            lines.append("─"*80)
            lines.append(f"File: {bug['screenshot']}")
            lines.append("")
        
        if bug['console_errors']:
            lines.append("─"*80)
            lines.append("CONSOLE ERRORS")
            lines.append("─"*80)
            for error in bug['console_errors'][:5]:
                lines.append(f"• {error.get('message', 'No message')}")
            lines.append("")
        
        lines.append("─"*80)
        lines.append("ADDITIONAL INFORMATION")
        lines.append("─"*80)
        lines.append(f"Test Type: {bug['additional_info']['test_type']}")
        lines.append(f"Execution Time: {bug['additional_info']['execution_time']}s")
        lines.append(f"Test Scenario ID: {bug['test_scenario_id']}")
        lines.append("")
        lines.append("="*80)
        
        return "\n".join(lines)
    
    def generate_bugs_summary(self):
        """Generate summary of all bugs"""
        if not self.bugs:
            return "No bugs found! 🎉"
        
        lines = []
        lines.append("\n" + "="*80)
        lines.append(f"BUG SUMMARY - {len(self.bugs)} TOTAL BUGS")
        lines.append("="*80)
        
        # Group by severity
        by_severity = {'high': [], 'medium': [], 'low': []}
        for bug in self.bugs:
            sev = bug['severity']
            if sev in by_severity:
                by_severity[sev].append(bug)
        
        for severity in ['high', 'medium', 'low']:
            bugs = by_severity[severity]
            if bugs:
                icon = "🔴" if severity == 'high' else "🟡" if severity == 'medium' else "🟢"
                lines.append(f"\n{icon} {severity.upper()} SEVERITY ({len(bugs)} bugs)")
                lines.append("─"*80)
                for bug in bugs:
                    lines.append(f"  {bug['bug_id']}: {bug['title']}")
                    lines.append(f"     Page: {bug['page_url']}")
                    lines.append(f"     Error: {bug['actual_result'][:80]}...")
                    lines.append("")
        
        lines.append("="*80)
        return "\n".join(lines)
    
    def export_bugs_to_file(self, filename="bug_reports.txt"):
        """Export all bug reports to a file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.generate_bugs_summary())
            f.write("\n\n")
            
            for bug in self.bugs:
                f.write(self.format_bug_report(bug))
                f.write("\n\n")
        
        return filename