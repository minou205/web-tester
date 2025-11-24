"""
LLM Module
Handles all AI/LLM operations for scenario generation and analysis
"""

import requests
import json
import re
import time

class LLMManager:
    def __init__(self, model="llama3.1:8b", url="http://localhost:11434/api/generate"):
        self.model = model
        self.url = url
        self.scenario_counter = 1
    
    def call_llm(self, prompt, system=""):
        """Call Ollama LLM"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "format": "json"
        }
        
        try:
            r = requests.post(self.url, json=payload, timeout=300)
            r.raise_for_status()
            result = r.json()
            txt = result.get('response', '{}')
            
            try:
                return json.loads(txt)
            except json.JSONDecodeError:
                match = re.search(r'\{.*\}', txt, re.DOTALL)
                if match:
                    return json.loads(match.group())
                else:
                    return None
                    
        except requests.exceptions.ConnectionError:
            print("\n\n❌ ERROR: Cannot connect to Ollama")
            print("Please make sure Ollama is running.")
            print("To start Ollama, run: ollama run llama3.1:8b")
            exit(1)
        except Exception as e:
            print(f"\n\n❌ ERROR: {str(e)}")
            exit(1)
    
    def generate_scenarios(self, elem):
        """Generate multiple test scenarios for an element"""
        sys = """You are an expert QA tester. Generate MULTIPLE comprehensive test scenarios for the given element.

For EACH element, create scenarios covering:
1. Valid Input Test (happy path)
2. Invalid Input Test (negative testing)
3. Boundary Value Test (edge cases)
4. Empty/Null Input Test
5. Special Characters Test (if applicable)

You MUST respond with ONLY a valid JSON object containing an array of scenarios:
{
  "scenarios": [
    {
      "scenario_id": "string",
      "type": "functional/ui_ux/security/boundary/negative",
      "title": "string (max 80 chars)",
      "description": "string (max 150 chars)",
      "steps": ["step1", "step2"],
      "target_elements": [{"selector": "string", "action": "string", "test_data": "string"}],
      "expected_result": "string (max 100 chars)",
      "priority": "high/medium/low"
    }
  ]
}"""
        
        einfo = {
            'type': elem['type'],
            'tag': elem['tag'],
            'selector': elem.get('selector', ''),
            'name': elem.get('name', ''),
            'id': elem.get('id', ''),
            'text': elem.get('text', '')[:50],
            'placeholder': elem.get('placeholder', ''),
            'input_type': elem.get('input_type', ''),
            'page': elem['page_url']
        }
        
        if elem['type'] == 'input':
            num_scenarios = "at least 5"
            focus = "valid data, invalid data, empty input, boundary values, special characters"
        elif elem['type'] == 'button':
            num_scenarios = "at least 3"
            focus = "normal click, double click, disabled state check"
        elif elem['type'] == 'select':
            num_scenarios = "at least 4"
            focus = "select each option, select default, select invalid"
        elif elem['type'] == 'link':
            num_scenarios = "at least 3"
            focus = "click link, verify destination, check if opens in new tab"
        else:
            num_scenarios = "at least 3"
            focus = "basic interaction, UI validation, accessibility"
        
        prompt = f"""Generate {num_scenarios} QA test scenarios for this element:

Element Details:
{json.dumps(einfo, indent=2)}

Create diverse scenarios covering: {focus}

Requirements:
- Each scenario must be unique and test different aspects
- Include positive and negative test cases
- Test boundary conditions where applicable
- Keep titles under 80 characters
- Keep descriptions under 150 characters
- Keep expected_result under 100 characters

Return ONLY a JSON object with an array of scenarios."""

        result = None
        for attempt in range(2):
            result = self.call_llm(prompt, sys)
            if result and 'scenarios' in result and len(result['scenarios']) > 0:
                scenarios = []
                for scen in result['scenarios']:
                    scen['scenario_id'] = f"TEST_{self.scenario_counter:03d}"
                    if 'title' in scen and len(scen['title']) > 80:
                        scen['title'] = scen['title'][:77] + "..."
                    if 'description' in scen and len(scen['description']) > 150:
                        scen['description'] = scen['description'][:147] + "..."
                    if 'expected_result' in scen and len(scen['expected_result']) > 100:
                        scen['expected_result'] = scen['expected_result'][:97] + "..."
                    scenarios.append(scen)
                    self.scenario_counter += 1
                return scenarios
            time.sleep(0.5)
        
        return []
    
    def analyze_result(self, result, scenario):
        """Analyze if a test truly passed or failed"""
        sys = """You are an expert QA analyst. Analyze the test execution result and determine if it truly passed or failed.

IMPORTANT RULES:
- If execution_status is "passed" and there is NO error, the test PASSED
- If execution_status is "failed" or there IS an error, the test FAILED
- Only mark as failed if there's actual evidence of failure
- Successful execution of actions (click, fill, etc.) means the test passed

Respond with ONLY a valid JSON object:
{
  "final_status": "passed" or "failed",
  "reason": "brief explanation (max 80 characters)",
  "severity": "low/medium/high"
}"""
        
        prompt = f"""Analyze this test execution result:

Scenario: {scenario.get('title', '')}
Type: {scenario.get('type', '')}
Expected Result: {scenario.get('expected_result', '')}
Execution Status: {result['status']}
Error: {result.get('error', 'None')}
Execution Time: {result['execution_time']}s

DECISION LOGIC:
- If execution_status = "passed" AND error = "None" → final_status = "passed"
- If execution_status = "failed" OR error exists → final_status = "failed"

Return ONLY a JSON object with a brief reason (max 80 characters)."""

        analysis = None
        for attempt in range(2):
            analysis = self.call_llm(prompt, sys)
            if analysis and 'final_status' in analysis:
                if 'reason' in analysis and len(analysis['reason']) > 80:
                    analysis['reason'] = analysis['reason'][:77] + "..."
                return analysis
            time.sleep(0.5)
        
        return {
            'final_status': result['status'],
            'reason': 'Test execution ' + result['status'],
            'severity': 'low'
        }
    
    def analyze_overall(self, total, passed, failed, rate, pages, elements, failed_tests):
        """Generate overall analysis of all test results"""
        sys = """You are an expert QA analyst. Analyze test results and provide actionable insights.
Respond with ONLY a valid JSON object:
{
  "summary": "brief 2-3 sentence overview",
  "critical_issues": ["issue1", "issue2", "issue3"],
  "recommendations": ["rec1", "rec2", "rec3"],
  "overall_quality": "excellent/good/fair/poor"
}"""
        
        prompt = f"""Analyze these QA test results:

Statistics:
- Total Tests: {total}
- Passed: {passed}
- Failed: {failed}
- Pass Rate: {rate}%
- Pages Tested: {pages}
- Elements Found: {elements}

Failed Tests (showing first 10):
{json.dumps(failed_tests[:10], indent=2)}

Provide comprehensive analysis."""

        analysis = None
        for attempt in range(2):
            analysis = self.call_llm(prompt, sys)
            if analysis:
                return analysis
            time.sleep(2)
        
        return {
            'summary': 'Analysis unavailable',
            'critical_issues': [],
            'recommendations': [],
            'overall_quality': 'unknown'
        }