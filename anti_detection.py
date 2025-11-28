"""
Anti-Bot Detection Module for Selenium Web Scraping
Comprehensive solution for bypassing bot detection measures
"""

import random
import time
from typing import List, Dict, Optional, Tuple
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class AntiDetectionConfig:
    """Configuration class for anti-detection features"""
    
    def __init__(self):
        self.use_user_agent_rotation = True
        self.use_proxy_rotation = True
        self.use_header_rotation = True
        self.use_fingerprint_masking = True
        self.simulate_human_behavior = True
        self.proxy_list: List[str] = []
        self.current_proxy_index = 0
        self.free_proxy_source = "http://proxy-list.download/api/v1/get?type=http&country=US"


class UserAgentPool:
    """Pool of diverse user agents from different browsers and OS"""
    
    USER_AGENTS = [
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        
        # Chrome on Windows (older versions)
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
        
        # Chrome on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        
        # Safari on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        
        # Chrome on Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        
        # Firefox on Linux
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
        
        # Chrome on Android
        "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.89 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.66 Mobile Safari/537.36",
        
        # Safari on iOS
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    ]
    
    @staticmethod
    def get_random_user_agent() -> str:
        """Return a random user agent from the pool"""
        return random.choice(UserAgentPool.USER_AGENTS)


class HeaderRotation:
    """Generate random but realistic HTTP headers"""
    
    LANGUAGES = [
        "en-US,en;q=0.9",
        "en-US,en;q=0.9,es;q=0.8",
        "en-US,en;q=0.9,fr;q=0.8",
        "en-US,en;q=0.9,de;q=0.8",
        "en-GB,en;q=0.9",
    ]
    
    ENCODINGS = [
        "gzip, deflate, br",
        "gzip, deflate",
    ]
    
    @staticmethod
    def get_random_headers() -> Dict[str, str]:
        """Generate a random but realistic header set"""
        return {
            "User-Agent": UserAgentPool.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": random.choice(HeaderRotation.LANGUAGES),
            "Accept-Encoding": random.choice(HeaderRotation.ENCODINGS),
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }


class ProxyRotation:
    """Manage proxy rotation for requests"""
    
    def __init__(self, config: AntiDetectionConfig):
        self.config = config
        self.proxy_list = config.proxy_list
        self.current_index = 0
    
    def load_free_proxies(self, limit: int = 50) -> List[str]:
        """Load free proxies from public sources"""
        try:
            print("[*] Loading free proxies...")
            response = requests.get(
                self.config.free_proxy_source,
                timeout=10,
                headers=HeaderRotation.get_random_headers()
            )
            proxies = response.text.strip().split('\r\n')[:limit]
            self.proxy_list = [f"http://{p}" for p in proxies if p]
            print(f"[+] Loaded {len(self.proxy_list)} free proxies")
            return self.proxy_list
        except Exception as e:
            print(f"[-] Error loading free proxies: {e}")
            return []
    
    def add_paid_proxies(self, proxy_list: List[str]) -> None:
        """Add paid proxies to rotation"""
        self.proxy_list.extend(proxy_list)
        print(f"[+] Added {len(proxy_list)} paid proxies")
    
    def get_next_proxy(self) -> Optional[str]:
        """Get the next proxy from rotation"""
        if not self.proxy_list:
            return None
        
        proxy = self.proxy_list[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxy_list)
        return proxy
    
    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """Get proxy in dict format for requests"""
        proxy = self.get_next_proxy()
        if proxy:
            return {"http": proxy, "https": proxy}
        return None


class HumanBehaviorSimulator:
    """Simulate realistic human behavior in browser"""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.actions = ActionChains(driver)
    
    def random_sleep(self, min_sec: float = 1, max_sec: float = 3) -> None:
        """Sleep for random duration to simulate human thinking"""
        sleep_time = random.uniform(min_sec, max_sec)
        time.sleep(sleep_time)
    
    def type_slowly(self, element, text: str, min_delay: float = 0.05, max_delay: float = 0.25) -> None:
        """Type text character by character with random delays"""
        element.click()
        time.sleep(random.uniform(0.1, 0.3))
        
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_delay, max_delay))
    
    def random_mouse_movement(self, x_range: Tuple[int, int] = (0, 800), 
                             y_range: Tuple[int, int] = (0, 600)) -> None:
        """Simulate random mouse movements"""
        num_movements = random.randint(2, 5)
        
        for _ in range(num_movements):
            x = random.randint(x_range[0], x_range[1])
            y = random.randint(y_range[0], y_range[1])
            self.actions.move_by_offset(x, y).perform()
            time.sleep(random.uniform(0.1, 0.5))
    
    def realistic_scrolling(self, scroll_pause_time: float = 0.5) -> None:
        """Scroll page in realistic manner"""
        scroll_amount = random.randint(3, 8)
        
        for _ in range(scroll_amount):
            self.driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(random.uniform(scroll_pause_time, scroll_pause_time + 0.5))
    
    def human_like_page_interaction(self) -> None:
        """Simulate realistic page interaction"""
        # Random page scroll
        if random.random() > 0.3:
            self.realistic_scrolling()
        
        # Random mouse movement
        if random.random() > 0.4:
            self.random_mouse_movement()
        
        # Random pause
        self.random_sleep(1, 3)


class AntiDetectionBrowser:
    """Main class for creating anti-detection configured Selenium browser"""
    
    def __init__(self, config: Optional[AntiDetectionConfig] = None):
        self.config = config or AntiDetectionConfig()
        self.driver: Optional[webdriver.Chrome] = None
        self.proxy_rotation = ProxyRotation(self.config)
        self.human_simulator: Optional[HumanBehaviorSimulator] = None
    
    def setup_anti_detection_browser(self, headless: bool = False) -> webdriver.Chrome:
        """
        Configure Chrome browser with comprehensive anti-detection measures
        
        Args:
            headless: Run browser in headless mode
            
        Returns:
            Configured Selenium WebDriver instance
        """
        options = Options()
        
        # Display configuration
        if not headless:
            options.add_argument("--start-maximized")
        else:
            options.add_argument("--headless")
        
        # User agent rotation
        if self.config.use_user_agent_rotation:
            user_agent = UserAgentPool.get_random_user_agent()
            options.add_argument(f"user-agent={user_agent}")
            print(f"[+] Set user agent: {user_agent[:50]}...")
        
        # Fingerprint masking - Hide webdriver detection
        if self.config.use_fingerprint_masking:
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            print("[+] Fingerprint masking enabled")
        
        # Proxy configuration
        if self.config.use_proxy_rotation and self.config.proxy_list:
            proxy = self.proxy_rotation.get_next_proxy()
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
                print(f"[+] Proxy set: {proxy}")
        
        # Additional anti-detection arguments
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-extensions-file-access-check")
        options.add_argument("--disable-component-extensions-with-background-pages")
        
        # Create driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Execute JavaScript to hide webdriver property
        if self.config.use_fingerprint_masking:
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    window.chrome = {
                        runtime: {}
                    };
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                '''
            })
            print("[+] JavaScript fingerprint masking injected")
        
        # Initialize human behavior simulator
        if self.config.simulate_human_behavior:
            self.human_simulator = HumanBehaviorSimulator(self.driver)
        
        print("[+] Anti-detection browser configured successfully\n")
        return self.driver
    
    def get_driver(self) -> webdriver.Chrome:
        """Get the configured driver"""
        if not self.driver:
            self.setup_anti_detection_browser()
        return self.driver
    
    def close(self) -> None:
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("[+] Browser closed")


def get_random_user_agent() -> str:
    """Standalone function to get random user agent"""
    return UserAgentPool.get_random_user_agent()


def setup_anti_detection_browser(config: Optional[AntiDetectionConfig] = None) -> webdriver.Chrome:
    """Standalone function to setup anti-detection browser"""
    browser = AntiDetectionBrowser(config)
    return browser.setup_anti_detection_browser()


def simulate_human_behavior(driver: webdriver.Chrome) -> None:
    """Standalone function to simulate human behavior"""
    simulator = HumanBehaviorSimulator(driver)
    simulator.human_like_page_interaction()
