"""
Workflow Tester Module
Tests multi-step user journeys and workflows
"""

import time

class WorkflowTester:
    def __init__(self, browser_manager, llm_manager):
        self.browser = browser_manager
        self.llm = llm_manager
        self.workflows = []
    
    def detect_workflows(self, elements, page_url):
        """Detect common workflows from elements"""
        workflows = []
        
        # Detect login workflow
        has_email = any(e['type'] == 'input' and 'email' in e.get('name', '').lower() for e in elements)
        has_password = any(e['type'] == 'input' and e.get('input_type') == 'password' for e in elements)
        has_login_button = any(e['type'] == 'button' and 'login' in e.get('text', '').lower() for e in elements)
        
        if has_email and has_password and has_login_button:
            workflows.append({
                'type': 'login',
                'name': 'User Login Workflow',
                'page': page_url,
                'steps': self._build_login_workflow(elements)
            })
        
        # Detect registration workflow
        has_register_button = any(e['type'] == 'button' and any(word in e.get('text', '').lower() for word in ['register', 'sign up', 'signup']) for e in elements)
        if has_email and has_password and has_register_button:
            workflows.append({
                'type': 'registration',
                'name': 'User Registration Workflow',
                'page': page_url,
                'steps': self._build_registration_workflow(elements)
            })
        
        # Detect contact form workflow
        has_name = any(e['type'] == 'input' and 'name' in e.get('name', '').lower() for e in elements)
        has_message = any(e['type'] == 'textarea' for e in elements)
        has_submit = any(e['type'] == 'button' and any(word in e.get('text', '').lower() for word in ['submit', 'send']) for e in elements)
        
        if has_name and (has_email or has_message) and has_submit:
            workflows.append({
                'type': 'contact_form',
                'name': 'Contact Form Submission Workflow',
                'page': page_url,
                'steps': self._build_contact_workflow(elements)
            })
        
        # Detect search workflow
        has_search = any(e['type'] == 'input' and any(word in e.get('placeholder', '').lower() for word in ['search', 'find']) for e in elements)
        if has_search:
            workflows.append({
                'type': 'search',
                'name': 'Search Workflow',
                'page': page_url,
                'steps': self._build_search_workflow(elements)
            })
        
        self.workflows.extend(workflows)
        return workflows
    
    def _build_login_workflow(self, elements):
        """Build login workflow steps"""
        email_field = next((e for e in elements if e['type'] == 'input' and 'email' in e.get('name', '').lower()), None)
        password_field = next((e for e in elements if e['type'] == 'input' and e.get('input_type') == 'password'), None)
        submit_button = next((e for e in elements if e['type'] == 'button' and 'login' in e.get('text', '').lower()), None)
        
        steps = []
        if email_field:
            steps.append({
                'action': 'fill',
                'selector': email_field['selector'],
                'data': 'testuser@example.com',
                'description': 'Enter email address'
            })
        if password_field:
            steps.append({
                'action': 'fill',
                'selector': password_field['selector'],
                'data': 'TestPassword123!',
                'description': 'Enter password'
            })
        if submit_button:
            steps.append({
                'action': 'click',
                'selector': submit_button['selector'],
                'data': '',
                'description': 'Click login button'
            })
        
        return steps
    
    def _build_registration_workflow(self, elements):
        """Build registration workflow steps"""
        steps = []
        
        name_field = next((e for e in elements if e['type'] == 'input' and 'name' in e.get('name', '').lower() and 'email' not in e.get('name', '').lower()), None)
        email_field = next((e for e in elements if e['type'] == 'input' and 'email' in e.get('name', '').lower()), None)
        password_field = next((e for e in elements if e['type'] == 'input' and e.get('input_type') == 'password'), None)
        submit_button = next((e for e in elements if e['type'] == 'button' and any(word in e.get('text', '').lower() for word in ['register', 'sign up', 'signup'])), None)
        
        if name_field:
            steps.append({
                'action': 'fill',
                'selector': name_field['selector'],
                'data': 'John Doe',
                'description': 'Enter full name'
            })
        if email_field:
            steps.append({
                'action': 'fill',
                'selector': email_field['selector'],
                'data': 'newuser@example.com',
                'description': 'Enter email address'
            })
        if password_field:
            steps.append({
                'action': 'fill',
                'selector': password_field['selector'],
                'data': 'SecurePass123!',
                'description': 'Enter password'
            })
        if submit_button:
            steps.append({
                'action': 'click',
                'selector': submit_button['selector'],
                'data': '',
                'description': 'Click registration button'
            })
        
        return steps
    
    def _build_contact_workflow(self, elements):
        """Build contact form workflow steps"""
        steps = []
        
        name_field = next((e for e in elements if e['type'] == 'input' and 'name' in e.get('name', '').lower()), None)
        email_field = next((e for e in elements if e['type'] == 'input' and 'email' in e.get('name', '').lower()), None)
        message_field = next((e for e in elements if e['type'] == 'textarea'), None)
        submit_button = next((e for e in elements if e['type'] == 'button' and any(word in e.get('text', '').lower() for word in ['submit', 'send'])), None)
        
        if name_field:
            steps.append({
                'action': 'fill',
                'selector': name_field['selector'],
                'data': 'Jane Smith',
                'description': 'Enter name'
            })
        if email_field:
            steps.append({
                'action': 'fill',
                'selector': email_field['selector'],
                'data': 'jane@example.com',
                'description': 'Enter email'
            })
        if message_field:
            steps.append({
                'action': 'fill',
                'selector': message_field['selector'],
                'data': 'This is a test message for the contact form.',
                'description': 'Enter message'
            })
        if submit_button:
            steps.append({
                'action': 'click',
                'selector': submit_button['selector'],
                'data': '',
                'description': 'Submit form'
            })
        
        return steps
    
    def _build_search_workflow(self, elements):
        """Build search workflow steps"""
        steps = []
        
        search_field = next((e for e in elements if e['type'] == 'input' and any(word in e.get('placeholder', '').lower() for word in ['search', 'find'])), None)
        search_button = next((e for e in elements if e['type'] == 'button' and 'search' in e.get('text', '').lower()), None)
        
        if search_field:
            steps.append({
                'action': 'fill',
                'selector': search_field['selector'],
                'data': 'test query',
                'description': 'Enter search query'
            })
        if search_button:
            steps.append({
                'action': 'click',
                'selector': search_button['selector'],
                'data': '',
                'description': 'Click search button'
            })
        
        return steps
    
    def execute_workflow(self, workflow, url):
        """Execute a complete workflow"""
        result = {
            'workflow_name': workflow['name'],
            'workflow_type': workflow['type'],
            'page': url,
            'steps_completed': 0,
            'steps_failed': 0,
            'total_steps': len(workflow['steps']),
            'status': 'passed',
            'errors': [],
            'execution_time': 0,
            'step_results': []
        }
        
        start_time = time.time()
        
        # Navigate to page
        self.browser.driver.get(url)
        time.sleep(2)
        
        # Take screenshot before workflow
        screenshot_before = self.browser.take_screenshot(
            f"{workflow['type']}_before",
            workflow['type']
        )
        
        # Execute each step
        for idx, step in enumerate(workflow['steps'], 1):
            step_result = {
                'step_number': idx,
                'description': step['description'],
                'status': 'passed',
                'error': None
            }
            
            try:
                self.browser.execute_action(
                    step['selector'],
                    step['action'],
                    step.get('data', '')
                )
                result['steps_completed'] += 1
                step_result['status'] = 'passed'
                
            except Exception as e:
                result['steps_failed'] += 1
                result['status'] = 'failed'
                step_result['status'] = 'failed'
                step_result['error'] = str(e)
                result['errors'].append(f"Step {idx} ({step['description']}): {str(e)}")
                break  # Stop workflow on first failure
            
            result['step_results'].append(step_result)
            time.sleep(1)
        
        # Take screenshot after workflow
        screenshot_after = self.browser.take_screenshot(
            f"{workflow['type']}_after",
            workflow['type'],
            failed=(result['status'] == 'failed')
        )
        
        result['execution_time'] = round(time.time() - start_time, 2)
        result['screenshot_before'] = screenshot_before
        result['screenshot_after'] = screenshot_after
        
        return result
    
    def generate_workflow_report(self, results):
        """Generate workflow test report"""
        lines = []
        lines.append("\n🔄 WORKFLOW TEST RESULTS")
        lines.append("─" * 60)
        
        for result in results:
            status_icon = "✅" if result['status'] == 'passed' else "❌"
            lines.append(f"\n{status_icon} {result['workflow_name']}")
            lines.append(f"   Type: {result['workflow_type']}")
            lines.append(f"   Page: {result['page']}")
            lines.append(f"   Steps: {result['steps_completed']}/{result['total_steps']} completed")
            lines.append(f"   Status: {result['status'].upper()}")
            lines.append(f"   Execution Time: {result['execution_time']}s")
            
            if result['errors']:
                lines.append(f"   Errors:")
                for error in result['errors']:
                    lines.append(f"      • {error}")
            
            # Show step details
            if result['step_results']:
                lines.append(f"   Step Details:")
                for step_res in result['step_results']:
                    step_icon = "✓" if step_res['status'] == 'passed' else "✗"
                    lines.append(f"      {step_icon} Step {step_res['step_number']}: {step_res['description']}")
        
        return "\n".join(lines)