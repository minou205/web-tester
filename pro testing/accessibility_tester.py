"""
Accessibility Tester Module
Tests WCAG compliance and accessibility features
"""

from selenium.webdriver.common.by import By
import re

class AccessibilityTester:
    def __init__(self):
        self.issues = []
    
    def test_page_accessibility(self, driver, url):
        """Run comprehensive accessibility tests on a page"""
        results = {
            'url': url,
            'images_without_alt': [],
            'links_without_text': [],
            'form_inputs_without_labels': [],
            'low_contrast_elements': [],
            'missing_heading_hierarchy': False,
            'missing_lang_attribute': False,
            'missing_page_title': False,
            'keyboard_navigation_issues': [],
            'aria_issues': [],
            'score': 0,
            'total_checks': 0
        }
        
        # Test 1: Images without alt text
        results['total_checks'] += 1
        images = driver.find_elements(By.TAG_NAME, 'img')
        for img in images:
            alt = img.get_attribute('alt')
            if not alt or alt.strip() == '':
                results['images_without_alt'].append({
                    'src': img.get_attribute('src'),
                    'id': img.get_attribute('id') or 'no-id'
                })
        if len(results['images_without_alt']) == 0:
            results['score'] += 1
        
        # Test 2: Links without text
        results['total_checks'] += 1
        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            text = link.text.strip()
            aria_label = link.get_attribute('aria-label')
            if not text and not aria_label:
                results['links_without_text'].append({
                    'href': link.get_attribute('href'),
                    'id': link.get_attribute('id') or 'no-id'
                })
        if len(results['links_without_text']) == 0:
            results['score'] += 1
        
        # Test 3: Form inputs without labels
        results['total_checks'] += 1
        inputs = driver.find_elements(By.TAG_NAME, 'input')
        for inp in inputs:
            input_id = inp.get_attribute('id')
            input_type = inp.get_attribute('type')
            
            # Skip hidden and submit/button types
            if input_type in ['hidden', 'submit', 'button']:
                continue
            
            aria_label = inp.get_attribute('aria-label')
            placeholder = inp.get_attribute('placeholder')
            
            # Check if there's an associated label
            has_label = False
            if input_id:
                try:
                    label = driver.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                    has_label = True
                except:
                    pass
            
            if not has_label and not aria_label:
                results['form_inputs_without_labels'].append({
                    'type': input_type,
                    'id': input_id or 'no-id',
                    'name': inp.get_attribute('name') or 'no-name'
                })
        if len(results['form_inputs_without_labels']) == 0:
            results['score'] += 1
        
        # Test 4: Page title
        results['total_checks'] += 1
        try:
            title = driver.title
            if not title or title.strip() == '':
                results['missing_page_title'] = True
            else:
                results['score'] += 1
        except:
            results['missing_page_title'] = True
        
        # Test 5: HTML lang attribute
        results['total_checks'] += 1
        try:
            html_element = driver.find_element(By.TAG_NAME, 'html')
            lang = html_element.get_attribute('lang')
            if not lang or lang.strip() == '':
                results['missing_lang_attribute'] = True
            else:
                results['score'] += 1
        except:
            results['missing_lang_attribute'] = True
        
        # Test 6: Heading hierarchy
        results['total_checks'] += 1
        headings = []
        for i in range(1, 7):
            h_tags = driver.find_elements(By.TAG_NAME, f'h{i}')
            for h in h_tags:
                headings.append(i)
        
        # Check if heading levels are sequential
        if headings:
            for i in range(len(headings) - 1):
                if headings[i+1] - headings[i] > 1:
                    results['missing_heading_hierarchy'] = True
                    break
            if not results['missing_heading_hierarchy']:
                results['score'] += 1
        else:
            results['score'] += 1  # No headings is okay
        
        # Test 7: Buttons with accessible names
        results['total_checks'] += 1
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        button_issues = []
        for btn in buttons:
            text = btn.text.strip()
            aria_label = btn.get_attribute('aria-label')
            if not text and not aria_label:
                button_issues.append({
                    'id': btn.get_attribute('id') or 'no-id',
                    'class': btn.get_attribute('class') or 'no-class'
                })
        if len(button_issues) == 0:
            results['score'] += 1
        else:
            results['aria_issues'].extend(button_issues)
        
        # Test 8: ARIA roles validity
        results['total_checks'] += 1
        valid_roles = ['alert', 'button', 'checkbox', 'dialog', 'link', 'menu', 'menuitem', 
                      'navigation', 'radio', 'search', 'tab', 'textbox', 'banner', 'main', 
                      'complementary', 'contentinfo', 'form', 'region']
        
        elements_with_role = driver.find_elements(By.CSS_SELECTOR, '[role]')
        invalid_roles = []
        for el in elements_with_role:
            role = el.get_attribute('role')
            if role and role not in valid_roles:
                invalid_roles.append({
                    'role': role,
                    'tag': el.tag_name,
                    'id': el.get_attribute('id') or 'no-id'
                })
        if len(invalid_roles) == 0:
            results['score'] += 1
        else:
            results['aria_issues'].extend(invalid_roles)
        
        # Calculate percentage
        results['percentage'] = round((results['score'] / results['total_checks'] * 100), 1) if results['total_checks'] > 0 else 0
        results['grade'] = self._get_accessibility_grade(results['percentage'])
        
        return results
    
    def _get_accessibility_grade(self, percentage):
        """Convert percentage to letter grade"""
        if percentage >= 90:
            return 'A (Excellent)'
        elif percentage >= 80:
            return 'B (Good)'
        elif percentage >= 70:
            return 'C (Fair)'
        elif percentage >= 60:
            return 'D (Poor)'
        else:
            return 'F (Critical Issues)'
    
    def test_keyboard_navigation(self, driver):
        """Test if page is keyboard navigable"""
        try:
            # Find all focusable elements
            focusable_selectors = 'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
            focusable_elements = driver.find_elements(By.CSS_SELECTOR, focusable_selectors)
            
            issues = []
            for el in focusable_elements:
                # Check if element is visible
                if not el.is_displayed():
                    continue
                
                # Check tabindex
                tabindex = el.get_attribute('tabindex')
                if tabindex and int(tabindex) > 0:
                    issues.append({
                        'element': el.tag_name,
                        'id': el.get_attribute('id') or 'no-id',
                        'issue': f'Positive tabindex ({tabindex}) detected - should use 0 or natural order'
                    })
            
            return {
                'focusable_count': len(focusable_elements),
                'issues': issues
            }
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def generate_accessibility_report(self, results):
        """Generate human-readable accessibility report"""
        lines = []
        lines.append("\n♿ ACCESSIBILITY TEST RESULTS")
        lines.append("─" * 60)
        lines.append(f"URL: {results['url']}")
        lines.append(f"Overall Score: {results['score']}/{results['total_checks']} ({results['percentage']}%)")
        lines.append(f"Grade: {results['grade']}")
        lines.append("")
        
        # Issues
        if results['images_without_alt']:
            lines.append(f"❌ Images Without Alt Text: {len(results['images_without_alt'])}")
            for img in results['images_without_alt'][:3]:
                lines.append(f"   • {img['src'][:60]}...")
        
        if results['links_without_text']:
            lines.append(f"❌ Links Without Text: {len(results['links_without_text'])}")
            for link in results['links_without_text'][:3]:
                lines.append(f"   • {link['href'][:60] if link['href'] else 'no-href'}...")
        
        if results['form_inputs_without_labels']:
            lines.append(f"❌ Form Inputs Without Labels: {len(results['form_inputs_without_labels'])}")
            for inp in results['form_inputs_without_labels'][:3]:
                lines.append(f"   • Type: {inp['type']}, ID: {inp['id']}")
        
        if results['missing_page_title']:
            lines.append("❌ Missing Page Title")
        
        if results['missing_lang_attribute']:
            lines.append("❌ Missing HTML Lang Attribute")
        
        if results['missing_heading_hierarchy']:
            lines.append("❌ Incorrect Heading Hierarchy")
        
        if results['aria_issues']:
            lines.append(f"❌ ARIA Issues: {len(results['aria_issues'])}")
        
        # Passed tests
        passed_tests = []
        if not results['images_without_alt']:
            passed_tests.append("All images have alt text")
        if not results['links_without_text']:
            passed_tests.append("All links have text")
        if not results['form_inputs_without_labels']:
            passed_tests.append("All inputs have labels")
        if not results['missing_page_title']:
            passed_tests.append("Page has title")
        if not results['missing_lang_attribute']:
            passed_tests.append("HTML has lang attribute")
        if not results['missing_heading_hierarchy']:
            passed_tests.append("Heading hierarchy is correct")
        
        if passed_tests:
            lines.append("\n✅ Passed Tests:")
            for test in passed_tests:
                lines.append(f"   • {test}")
        
        return "\n".join(lines)