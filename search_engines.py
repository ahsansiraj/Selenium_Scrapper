import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


# Geographic keyword for prioritizing regional Amazon sites
# "Dubai" will make Google prioritize amazon.ae results
GEO_KEYWORD = "Dubai"


def search_duckduckgo_and_get_amazon_url(variant_name, browser, geo_keyword=GEO_KEYWORD):
    """
    Search DuckDuckGo instead of Google - much more bot-friendly!
    DuckDuckGo doesn't have aggressive anti-bot measures like Google does.
    """
    try:
        print("   🔍 Searching on DuckDuckGo...")
        browser.get("https://duckduckgo.com")
        time.sleep(2)
        
        search_query = f"{variant_name} amazon {geo_keyword}"
        print(f"   🌍 Search query: '{search_query}'")
        
        # DuckDuckGo's search box has id="searchbox_input"
        search_box = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "searchbox_input"))
        )
        search_box.clear()
        for char in search_query:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Random typing speed
        
        time.sleep(random.uniform(0.5, 1.0))
        search_box.send_keys(Keys.ENTER)
        
        # Wait for results
        time.sleep(3)
        WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article"))
        )
        
        # Extract URLs from DuckDuckGo results
        search_results = browser.find_elements(By.CSS_SELECTOR, "article a")
        
        all_urls = []
        for result in search_results:
            try:
                url = result.get_attribute("href")
                if url and "amazon" in url and url.startswith("http"):
                    all_urls.append(url)
            except:
                continue
        
        print(f"   📊 Found {len(all_urls)} Amazon URLs")
        
        # Same priority logic
        for url in all_urls:
            if "amazon.ae" in url and "/dp/" in url:
                print(f"   ✅ Found amazon.ae URL")
                return url, "amazon.ae"
        
        for url in all_urls:
            if "amazon.in" in url and "/dp/" in url:
                print(f"   ✅ Found amazon.in URL")
                return url, "amazon.in"
        
        for url in all_urls:
            if "amazon.com" in url and "/dp/" in url:
                print(f"   ✅ Found amazon.com URL")
                return url, "amazon.com"
        
        print("   ⚠️  No Amazon URLs found")
        return None, None
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None, None


def search_BING_and_get_amazon_url(variant_name, browser, geo_keyword=GEO_KEYWORD):
    """
    Search Bing for Amazon URLs - good alternative to Google and DuckDuckGo
    Bing has moderate bot-detection, less aggressive than Google
    """
    try:
        print("   🔍 Searching on Bing...")
        browser.get("https://www.bing.com")
        time.sleep(random.uniform(2, 4))
        
        search_query = f"{variant_name} amazon {geo_keyword}"
        print(f"   🌍 Search query: '{search_query}'")
        
        # Bing's search box selectors (multiple fallbacks)
        search_box = None
        selectors_to_try = [
            (By.ID, "sb_form_q"),  # Primary Bing search box ID
            (By.NAME, "q"),         # Generic search box name
            (By.CSS_SELECTOR, "input[aria-label='Enter your search here']"),  # Aria label
            (By.CSS_SELECTOR, "input[placeholder*='Search']"),  # Placeholder text
            (By. XPATH, "//input[@id='sb_form_q']"),  # XPath fallback
        ]
        
        for selector_type, selector_value in selectors_to_try:
            try:
                search_box = WebDriverWait(browser, 5).until(
                    EC. presence_of_element_located((selector_type, selector_value))
                )
                if search_box:
                    print(f"   ✓ Found search box using {selector_type}: {selector_value}")
                    break
            except:
                continue
        
        if not search_box:
            print("   ❌ Could not find Bing search box")
            return None, None
        
        # Type search query character by character (human-like)
        search_box.clear()
        time.sleep(random.uniform(0.3, 0.5))
        
        for char in search_query:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        time.sleep(random.uniform(0.5, 1.0))
        search_box.send_keys(Keys.ENTER)
        
        # Wait for results to load
        print("   ⏳ Waiting for Bing results...")
        time.sleep(random.uniform(3, 5))
        
        # Try multiple result selectors for Bing
        search_results = []
        result_selectors = [
            "li.b_algo a",           # Main result links (Bing uses li.b_algo for results)
            "div.sb_tlst a",         # Alternative Bing result selector
            "#b_results li a",       # Results list container
            "ol#b_results a",        # Ordered list of results
            "a[href*='amazon']",     # Direct Amazon link selector
        ]
        
        for selector in result_selectors:
            try:
                results = browser.find_elements(By.CSS_SELECTOR, selector)
                if len(results) > 3:  # Need reasonable number of results
                    search_results = results
                    print(f"   ✓ Found results using selector: {selector}")
                    break
            except:
                continue
        
        if not search_results:
            print("   ❌ No search results found on Bing")
            return None, None
        
        # Extract all URLs
        all_urls = []
        for result in search_results:
            try:
                url = result.get_attribute("href")
                if url and "amazon" in url. lower() and url.startswith("http"):
                    all_urls.append(url)
            except:
                continue
        
        print(f"   📊 Found {len(all_urls)} Amazon URLs")
        
        if not all_urls:
            print("   ⚠️ No Amazon URLs found in results")
            return None, None
        
        # Show sample URLs found
        print(f"   🔗 Sample URLs found:")
        for url in all_urls[:3]:
            domain = url.split('/')[2] if len(url.split('/')) > 2 else url
            print(f"      • {domain}")
        
        # Priority 1: amazon.ae (best for Dubai)
        for url in all_urls:
            if "amazon.ae" in url. lower():
                if "/dp/" in url or "/gp/product/" in url:
                    print(f"   ✅ Found amazon.ae URL")
                    return url, "amazon.ae"
        
        # Priority 2: amazon.in
        for url in all_urls:
            if "amazon.in" in url.lower():
                if "/dp/" in url or "/gp/product/" in url:
                    print(f"   ✅ Found amazon.in URL")
                    return url, "amazon.in"
        
        # Priority 3: amazon.com
        for url in all_urls:
            if "amazon.com" in url.lower():
                if "/dp/" in url or "/gp/product/" in url:
                    print(f"   ✅ Found amazon.com URL")
                    return url, "amazon.com"
        
        print("   ⚠️ No Amazon product URLs found (no /dp/ paths detected)")
        return None, None
        
    except Exception as e:
        print(f"   ❌ Error during Bing search: {str(e)[:100]}")
        print(f"   📍 Error type: {type(e).__name__}")
        return None, None