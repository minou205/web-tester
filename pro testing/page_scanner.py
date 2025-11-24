"""
Page Scanner Module
Handles scanning pages for elements
"""

from selenium.webdriver.common.by import By
from urllib.parse import urljoin, urlparse, urlunparse
from collections import defaultdict
import re

class PageScanner:
    def __init__(self, domain, base_url):
        self.domain = domain
        self.base = base_url
        self.counter = 1
        self.patterns = defaultdict(int)
    
    def normalize_url(self, url):
        p = urlparse(url)
        return urlunparse((p.scheme, p.netloc, p.path.rstrip('/'), '', '', ''))
    
    def is_valid_url(self, url):
        p = urlparse(url)
        if p.netloc != self.domain:
            return False
        excluded = ['.pdf', '.jpg', '.png', '.gif', '.css', '.js', '.zip', '.mp4']
        return not any(p.path.lower().endswith(ext) for ext in excluded)
    
    def should_avoid_url(self, url):
        path = urlparse(url).path
        pattern = re.sub(r'/\d+|/[a-f0-9]{8,}|/[a-zA-Z0-9_-]{10,}', '/[ID]', path)
        self.patterns[pattern] += 1
        return self.patterns[pattern] > 5
    
    def get_field_id(self):
        fid = f"FIELD_{self.counter:05d}"
        self.counter += 1
        return fid
    
    def extract_element_info(self, elem, ftype, url):
        try:
            info = {
                'field_id': self.get_field_id(),
                'url': url,
                'type': ftype,
                'tag': elem.tag_name,
                'name': elem.get_attribute('name') or '',
                'id': elem.get_attribute('id') or '',
                'class': elem.get_attribute('class') or '',
                'text': elem.text.strip() if elem.text else '',
                'value': elem.get_attribute('value') or '',
                'placeholder': elem.get_attribute('placeholder') or '',
                'role': elem.get_attribute('role') or '',
                'visible': elem.is_displayed(),
                'page_url': url
            }
            
            if info['id']:
                info['selector'] = f"#{info['id']}"
            elif info['name']:
                info['selector'] = f"{elem.tag_name}[name='{info['name']}']"
            else:
                info['selector'] = elem.tag_name
            
            if ftype == 'input':
                info['input_type'] = elem.get_attribute('type') or 'text'
            elif ftype == 'select':
                info['options'] = self._get_options(elem)
            elif ftype == 'link':
                info['href'] = elem.get_attribute('href') or ''
            
            return info
        except:
            return None
    
    def _get_options(self, elem):
        try:
            return [{'value': o.get_attribute('value') or '', 'text': o.text.strip()} 
                   for o in elem.find_elements(By.TAG_NAME, 'option')]
        except:
            return []
    
    def scan_page(self, driver, url):
        fields = []
        configs = [
            ('input', 'input'), ('textarea', 'textarea'), ('select', 'select'),
            ('button', 'button'), ('a[href]', 'link')
        ]
        
        for selector, ftype in configs:
            try:
                for elem in driver.find_elements(By.CSS_SELECTOR, selector):
                    info = self.extract_element_info(elem, ftype, url)
                    if info:
                        fields.append(info)
            except:
                continue
        
        return fields
    
    def get_links(self, driver, visited):
        links = []
        try:
            for anchor in driver.find_elements(By.TAG_NAME, 'a'):
                href = anchor.get_attribute('href')
                if href:
                    full_url = urljoin(driver.current_url, href)
                    normalized = self.normalize_url(full_url)
                    if (self.is_valid_url(normalized) and 
                        normalized not in visited and
                        not self.should_avoid_url(normalized)):
                        links.append(normalized)
        except:
            pass
        return list(set(links))