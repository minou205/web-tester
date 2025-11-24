"""
Enhanced Browser Manager Module
Handles browser operations with screenshots, performance tracking, and multi-browser support
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import tkinter as tk
import time
import os
from datetime import datetime

class BrowserManager:
    def __init__(self, browser_type='chrome'):
        self.driver = None
        self.browser_type = browser_type
        self.screenshots_dir = 'screenshots'
        self.performance_data = []
        
        # Create screenshots directory
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
    
    def initialize_browser(self, headless=False, mobile=False):
        """Initialize browser with options"""
        if self.browser_type == 'chrome':
            opts = ChromeOptions()
            opts.add_argument('--no-sandbox')
            opts.add_argument('--disable-dev-shm-usage')
            
            if headless:
                opts.add_argument('--headless')
            
            if mobile:
                # Mobile emulation
                mobile_emulation = {
                    "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
                    "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X) AppleWebKit/605.1.15"
                }
                opts.add_experimental_option("mobileEmulation", mobile_emulation)
            
            self.driver = webdriver.Chrome(options=opts)
        
        elif self.browser_type == 'firefox':
            opts = FirefoxOptions()
            if headless:
                opts.add_argument('--headless')
            
            self.driver = webdriver.Firefox(options=opts)
        
        self.driver.set_page_load_timeout(100)
        if not mobile:
            self.driver.maximize_window()
        
        return self.driver
    
    def measure_page_load_time(self, url):
        """Measure page load performance"""
        start_time = time.time()
        self.driver.get(url)
        load_time = time.time() - start_time
        
        # Get navigation timing metrics
        try:
            navigation_timing = self.driver.execute_script("""
                var performance = window.performance || {};
                var timing = performance.timing || {};
                return {
                    'loadEventEnd': timing.loadEventEnd,
                    'navigationStart': timing.navigationStart,
                    'domContentLoadedEventEnd': timing.domContentLoadedEventEnd
                };
            """)
            
            if navigation_timing['loadEventEnd'] and navigation_timing['navigationStart']:
                page_load = (navigation_timing['loadEventEnd'] - navigation_timing['navigationStart']) / 1000
                dom_ready = (navigation_timing['domContentLoadedEventEnd'] - navigation_timing['navigationStart']) / 1000
            else:
                page_load = load_time
                dom_ready = load_time
        except:
            page_load = load_time
            dom_ready = load_time
        
        perf_data = {
            'url': url,
            'total_load_time': round(load_time, 2),
            'page_load_time': round(page_load, 2),
            'dom_ready_time': round(dom_ready, 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.performance_data.append(perf_data)
        return perf_data
    
    def take_screenshot(self, name, test_id="", failed=False):
        """Take screenshot for documentation or failure"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        status = "FAIL" if failed else "PASS"
        filename = f"{timestamp}_{status}_{test_id}_{name}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        
        try:
            self.driver.save_screenshot(filepath)
            return filepath
        except Exception as e:
            print(f"Failed to take screenshot: {str(e)}")
            return None
    
    def show_manual_check(self, url):
        """Show manual check dialog for cookies/login/captcha"""
        if self.driver:
            self.driver.quit()
        
        self.driver = self.initialize_browser()
        
        try:
            self.driver.get(url)
            time.sleep(2)
            
            root = tk.Tk()
            root.title("Manual Check Required")
            root.geometry("500x250")
            root.attributes('-topmost', True)
            
            msg = "Please handle the following in the browser:\n\n"
            msg += "1. Accept cookies if prompted\n"
            msg += "2. Complete login/sign-up if needed\n"
            msg += "3. Solve CAPTCHA if present\n\n"
            msg += "Click 'Done' when ready to continue"
            
            tk.Label(root, text=msg, font=("Arial", 11), pady=20, justify="left").pack()
            
            def on_done():
                root.destroy()
            
            tk.Button(root, text="✓ Done", command=on_done, font=("Arial", 12), 
                     bg="#4CAF50", fg="white", padx=30, pady=15).pack(pady=10)
            
            root.mainloop()
            
            print("  ✓ Manual checks complete, continuing with visible browser...")
            
        except Exception as e:
            print(f"  ✗ Error during manual check: {str(e)}")
            raise
    
    def execute_action(self, selector, action, data="", timeout=10):
        """Execute an action on an element with performance tracking"""
        start_time = time.time()
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", el)
            time.sleep(0.3)
            
            if action == 'click':
                el = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                el.click()
            elif action == 'fill':
                el.clear()
                el.send_keys(data)
            elif action == 'check':
                if not el.is_selected():
                    el.click()
            elif action == 'select':
                sel_obj = Select(el)
                sel_obj.select_by_value(data)
            
            time.sleep(0.5)
            execution_time = time.time() - start_time
            return True, execution_time
            
        except (TimeoutException, NoSuchElementException) as e:
            execution_time = time.time() - start_time
            raise Exception(f"Element not found or not interactable: {selector}")
        except Exception as e:
            execution_time = time.time() - start_time
            raise Exception(f"Action failed: {str(e)}")
    
    def check_console_errors(self):
        """Check browser console for JavaScript errors"""
        try:
            logs = self.driver.get_log('browser')
            errors = [log for log in logs if log['level'] == 'SEVERE']
            return errors
        except:
            return []
    
    def get_page_metrics(self):
        """Get current page performance metrics"""
        try:
            metrics = self.driver.execute_script("""
                return {
                    'memory': performance.memory ? {
                        'usedJSHeapSize': performance.memory.usedJSHeapSize,
                        'totalJSHeapSize': performance.memory.totalJSHeapSize
                    } : null,
                    'resources': performance.getEntriesByType('resource').length
                };
            """)
            return metrics
        except:
            return {}
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None