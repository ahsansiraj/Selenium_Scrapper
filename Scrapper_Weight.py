import math
import os
import re
import time
import random
import pandas as pd
import requests
from datetime import datetime
from selenium. webdriver.common.by import By
from selenium. webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import random

from search_engines import search_duckduckgo_and_get_amazon_url
from search_engines import search_BING_and_get_amazon_url
# ---------- CONFIG ----------
EXCEL_FILE = "for Data Scrapping.xlsx"
SHEET_NAME = "Sheet3"
OUTPUT_EXCEL = "Scraped_Product_Weight.xlsx"
MAX_WORD = 10
GEO_KEYWORD = "Dubai"

# Realistic user agent
# List of user agents to rotate
USER_AGENTS = [
    # Chrome on Windows (Various Versions)
    'Mozilla/5. 0 (Windows NT 10. 0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0. 0.0 Safari/537. 36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537. 36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    
    # Chrome on macOS (Various Versions)
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0. 0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119. 0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0. 0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0. 0.0 Safari/537. 36',
    
    # Chrome on Linux
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120. 0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5. 0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0. 0.0 Safari/537. 36',
    
    # Firefox on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120. 0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    
    # Firefox on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10. 15; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.0; rv:121.0) Gecko/20100101 Firefox/121.0',
    
    # Firefox on Linux
    'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    
    # Safari on macOS
    'Mozilla/5. 0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5. 0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
    'Mozilla/5. 0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605. 1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    
    # Edge on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537. 36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    'Mozilla/5. 0 (Windows NT 10. 0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0. 0.0 Safari/537. 36 Edg/121. 0.0.0',
    
    # Edge on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0. 0.0 Safari/537. 36 Edg/120. 0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0. 0.0 Safari/537. 36 Edg/119. 0.0.0',
    
    # Opera on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0. 0 Safari/537.36 OPR/105.0.0.0',
    
    # Opera on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0. 0.0 Safari/537. 36 OPR/106. 0.0.0',
    
    # Brave on Windows
    'Mozilla/5. 0 (Windows NT 10. 0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0. 0.0 Safari/537. 36 Brave/120.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Brave/119.0.0.0',
    
    # Vivaldi on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0. 0 Safari/537.36 Vivaldi/6.5',
    
    # Chrome on Windows with different Windows versions
    'Mozilla/5. 0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    
    # Mobile User Agents (useful for variety)
    'Mozilla/5. 0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0. 6099.144 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537. 36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537. 36',
]


SITE_CONFIG = {
    "amazon.ae": {
        "CSV": "WEIGHT_data_Amazon_ae2.csv",
        "START_ROW": 2,
        "END_ROW": 3000,
    },
    "amazon.in": {
        "CSV": "WEIGHT_data_Amazon_in2.csv",
        "START_ROW": 2,
        "END_ROW": 3000,
    },
    "amazon.com": {
        "CSV": "WEIGHT_data_Amazon_com2.csv",
        "START_ROW": 2,
        "END_ROW": 3000,
    }
}

def create_browser_with_anti_detection(user_agent_index):
    """
    Creates an undetected Chrome browser with anti-detection measures enabled.
    This makes our scraper look like a real human browsing, not a bot. 
    """
    
    # Create options for undetected chrome
    options = uc.ChromeOptions()
    
    # Window settings
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"user-agent={USER_AGENTS[user_agent_index]}")
    # Anti-detection settings (undetected_chromedriver handles most of these automatically)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    
    # Memory limits
    options.add_argument("--max_old_space_size=4096")  # Limit memory to 4GB
    options.add_argument("--js-flags=--max-old-space-size=4096")
    
    # Random user agent
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"user-agent={user_agent_index}")
    
    # Additional privacy/stealth settings
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    
    
    # Preferences to appear more human-like
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.images": 1,  # Load images
    }
    options.add_experimental_option("prefs", prefs)
    
    try:
        # Create undetected Chrome browser
        # version_main parameter should match your installed Chrome version
        # If not specified, it will try to auto-detect
        browser = uc.Chrome(
            options=options,
            use_subprocess=True,  # More stable
            version_main=142,  # Uncomment and set your Chrome version if needed
        )
        
        print(f"   ✅ Undetected Chrome browser created successfully with user agent {USER_AGENTS[user_agent_index]}")
        
        # Additional stealth scripts (optional, but helpful)
        browser.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": user_agent
        })
        
        # Set navigator properties to appear more human
        browser.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            window.chrome = {
                runtime: {}
            };
            
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: () => Promise.resolve({ state: 'granted' })
                })
            });
        """)
        
        return browser
        
    except Exception as e:
        print(f"   ❌ Error creating undetected browser: {e}")
        print("   💡 Make sure you have installed: pip install undetected-chromedriver")
        raise
    
def extract_product_name(browser):
    """
    Extract the product title from the page.
    Looks for: <span id="productTitle">Apple iPhone 14 Pro...</span>
    """
    try:
        product_title = browser.find_element(By.ID, "productTitle")
        name = product_title.text.strip()
        if name:
            print(f"      ✓ Found product name: {name[:60]}")
            return name
    except:
        pass
    
    print(f"      ✗ Product name not found")
    return "Not Found"

def extract_weight(browser):

    """
    Extract the weight from product details.
    Handles both 'Item Weight' and 'Product Dimensions' formats.
    Returns weight in grams (g) or the original format if not in grams.
    """
    try:

        selectors=["#detailBullets_feature_div li",
                   "#productDetails_techSpec_section_1 tr",
                   "#productDetails_detailBullets_sections1 tr",
                   "#productDetails_techSpec_section_2 tr",
                   "div.a-column.a-span6.block-content.block-type-table.textalign-left.a-span-last div.content-grid-block table tr",
                   "div.content-grid-block table.a-bordered tr",
                   "table.a-bordered tr"]
        
        detail_items = []
        #  Try each selector until we find weight
        for selector_index, selector in enumerate(selectors, 1):
            try:
                elements = browser.find_elements(By.CSS_SELECTOR, selector)
                
                if not elements:
                    print(f"No elements found, trying next...")
                    continue
                
                
                # Search through all elements from this selector for weight
                for item in elements:
                    try:
                        item_text = item.text.strip()
                        
                        # Skip empty rows
                        if not item_text:
                            continue
                        
                        # Check if this row contains weight information
                        if "Weight" in item_text or "Item Weight" in item_text or "weight" in item_text.lower():
                            print(f"      🎯 Found weight row: {item_text[:80]}...")
                            
                            # Extract weight value and unit
                            weight_match = re.search(
                                r'([0-9.,]+)\s*(ounces?|grams?|g|kg|lb|oz|kilograms?|pounds?)',
                                item_text,
                                re.IGNORECASE
                            )
                            
                            if weight_match:
                                weight_value = weight_match.group(1).strip()
                                weight_unit = weight_match.group(2).strip().lower()
                                
                                # Normalize units
                                if weight_unit in ['ounce', 'ounces', 'oz']:
                                    weight_unit = 'oz'
                                elif weight_unit in ['gram', 'grams', 'g']:
                                    weight_unit = 'g'
                                elif weight_unit in ['kilogram', 'kilograms', 'kg']:
                                    weight_unit = 'kg'
                                elif weight_unit in ['pound', 'pounds', 'lb']:
                                    weight_unit = 'lb'
                                
                                # Convert to grams
                                weight_in_grams = convert_to_grams(weight_value, weight_unit)
                                
                                if weight_in_grams is not None:
                                    weight = f"{weight_in_grams} g"
                                else:
                                    weight = f"{weight_value} {weight_unit}"
                                
                                print(f"      ✅ Found weight: {weight}")
                                return weight
                        
                        # Also check for Product Dimensions (weight is often at the end)
                        if "Product Dimensions" in item_text or "Package Dimensions" in item_text:
                            print(f"      📦 Checking dimensions row: {item_text[:80]}...")
                            
                            # Extract weight after semicolon or just search entire text
                            weight_match = re.search(
                                r';\s*([0-9.,]+)\s*(g|kg|lb|oz|ounces|grams|kilograms|pounds)',
                                item_text,
                                re.IGNORECASE
                            )
                            
                            # If semicolon pattern didn't work, try general pattern
                            if not weight_match:
                                weight_match = re.search(
                                    r'([0-9.,]+)\s*(g|kg|lb|oz|ounces|grams|kilograms|pounds)',
                                    item_text,
                                    re.IGNORECASE
                                )
                            
                            if weight_match:
                                weight_value = weight_match.group(1).strip()
                                weight_unit = weight_match.group(2).strip().lower()
                                
                                # Normalize units
                                if weight_unit in ['ounce', 'ounces', 'oz']:
                                    weight_unit = 'oz'
                                elif weight_unit in ['gram', 'grams', 'g']:
                                    weight_unit = 'g'
                                elif weight_unit in ['kilogram', 'kilograms', 'kg']:
                                    weight_unit = 'kg'
                                elif weight_unit in ['pound', 'pounds', 'lb']:
                                    weight_unit = 'lb'
                                
                                weight_in_grams = convert_to_grams(weight_value, weight_unit)
                                
                                if weight_in_grams is not None:
                                    weight = f"{weight_in_grams} g"
                                else:
                                    weight = f"{weight_value} {weight_unit}"
                                
                                print(f"      ✅ Found weight from dimensions: {weight} (from selector {selector_index})")
                                return weight
                    
                    except Exception as e:
                        # Error with individual element, continue to next
                        continue
                
                # Finished checking all elements from this selector without finding weight
                print(f"      ⏭️  Selector {selector_index}: No weight found in these elements, trying next selector...")
                
            except Exception as e:
                print(f"      ⚠️  Selector {selector_index} error: {e}")
                continue
        
        # If we've tried all selectors and found nothing
        print("      ❌ Weight not found in any location")
        return "Not Found"

    except Exception as e:
        print(f"      ❌ Error extracting weight: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Not Found"


def convert_to_grams(value, unit):
    """Convert weight to grams"""
    unit = unit.lower().strip()
    try:
        value = float(value.replace(',', ''))
    except:
        return None
    
    if unit in ['g', 'gram', 'grams']:
        return value
    elif unit in ['kg', 'kilogram', 'kilograms']:
        return math.floor(value * 1000)/100
    elif unit in ['oz', 'ounce', 'ounces']:
        return math.floor(value * 28.3495)/100
    elif unit in ['lb', 'lbs', 'pound', 'pounds']:
        return math.floor(value * 453.592)/100
    return None

def scrape_product_data(product_url, browser, retry_count=0, max_retries=1):
    
    data = {
        "product_name": "Not Found",
        "product_weight": "Not Found",
        "status": "Pending"
    }
    
    try:
        print(f"   📄 Opening product page...")
        browser.get(product_url)
        
        # Add human-like delay before scraping
        time.sleep(random.uniform(2, 4))
        
        # Wait for the product title to load (indicates page is ready)
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "productTitle"))
        )
        
        print(f"   🔍 Extracting data...")
        
        # Extract each data point (correct order: product_name, asin, launch_date, price)
        data["product_name"] = extract_product_name(browser)
        data["product_weight"] = extract_weight(browser)
        data["status"] = "Success" if data["product_weight"] != "Not Found" else "Weight Not Found"
        print(f"   ✅ Data extraction successful")
        return data
        
    except Exception as e:
        print(f"   ❌ Error loading page: {str(e)}")
        
        # # Retry strategy: if we haven't exceeded max retries, try again with fresh browser
        # if retry_count < max_retries:
        #     print(f"   🔄 Retrying with new browser instance ({retry_count + 1}/{max_retries})...")
        #     time.sleep(random.uniform(3, 5))
            
        #     # Close current browser and create a new one
        #     try:
        #         browser.quit()
        #     except:
        #         pass
            
        #     new_browser = create_browser_with_anti_detection()
        #     result = scrape_product_data(product_url, new_browser, retry_count + 1, max_retries)
            
        #     try:
        #         new_browser.quit()
        #     except:
        #         pass
            
        #     return result
        # else:
        #     # Max retries exceeded, mark as failed
        #     data["status"] = "Data Extraction Failed"
        #     print(f"   ⚠️  Max retries exceeded")
    return data

def search_google_and_get_amazon_url(Variant_name, browser, geo_keyword=GEO_KEYWORD):
    """
    Search Google for Amazon product URLs with enhanced anti-detection measures.
    
    This function implements several strategies to avoid Google's bot detection:
    - Realistic typing speed (humans don't type instantly)
    - Random delays between actions
    - Multiple CSS selectors as fallbacks
    - Better error handling and debugging
    
    Args:
        Variant_name: The product name to search for
        browser: Selenium webdriver instance
        geo_keyword: Location keyword to append (default: "Dubai")
    
    Returns:
        tuple: (product_url, site_name) if found, or (None, None) if not found
    """
    try:
        # Step 1: Navigate to Google's homepage first to establish a session
        print("   🔍 Navigating to Google...")
        browser.get("https://www.google.com")
        time.sleep(random.uniform(2, 4))  # Random delay to seem more human
        
        # Check if we got blocked by looking for consent or CAPTCHA pages
        page_source = browser.page_source.lower()
        if "captcha" in page_source or "unusual traffic" in page_source:
            print("   ⚠️  Google detected automation. You might need to:")
            print("      1. Wait a few minutes before trying again")
            print("      2. Use a VPN or change your IP address")
            print("      3. Manually complete CAPTCHA if browser window shows one")
            return None, None
        
        # Step 2: Create the geo-targeted search query
        search_query = f"{Variant_name} {geo_keyword}"
        print(f"   🌍 Search query: '{search_query}'")
        
        # Step 3: Find Google's search box using multiple selectors
        search_box = None
        selectors_to_try = [
            (By.NAME, "q"),
            (By.CSS_SELECTOR, "textarea[name='q']"),
            (By.CSS_SELECTOR, "input[name='q']"),
            (By.XPATH, "//textarea[@name='q']"),
            (By.XPATH, "//input[@name='q']")
        ]
        

        for selector_type, selector_value in selectors_to_try:
            try:
                search_box = WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                if search_box:
                    print(f"   ✓ Found search box using {selector_type}: {selector_value}")
                    break
            except:
                continue
        
        if not search_box:
            print("   ❌ Could not find Google search box. Google might be blocking access.")
            print("   💡 Try opening Google manually in the browser to check for CAPTCHA")
            return None, None
        
        # Step 4: Type the search query character by character (like a human)
        search_box.clear()
        for char in search_query:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Random typing speed
        
        time.sleep(random.uniform(0.5, 1.5))  # Pause before hitting enter
        search_box.send_keys(Keys.ENTER)
        
        time.sleep(random.uniform(10,30))

        # Step 5: Wait for search results to load with multiple strategies
        print("   ⏳ Waiting for search results...")
        time.sleep(random.uniform(1,10))  # Give Google time to fully render

        # NEW: Simple human-like scrolling
        print("   📜 Scanning results...")
        for _ in range(random.randint(2, 4)):  # 2-4 scroll actions
            scroll_distance = random. randint(300, 600)
            browser.execute_script(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
            time.sleep(random.uniform(0.6, 1.2))

        # Scroll back to top
        browser.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
        time.sleep(random.uniform(0.8, 1.5))

        
        # Try multiple selectors for search results
        search_results = []
        result_selectors = [
            "div.g a",
            "div[data-sokoban-container] a",
            "div#search a",
            "div#rso a"
        ]
        
        for selector in result_selectors:
            try:
                search_results = browser.find_elements(By.CSS_SELECTOR, selector)
                if len(search_results) > 5:  # Need reasonable number of results
                    print(f"   ✓ Found results using selector: {selector}")
                    break
            except:
                continue
        
        if not search_results:
            print("   ❌ No search results found. Possible reasons:")
            print("      • Google is showing a CAPTCHA")
            print("      • Google blocked the automated request")
            print("      • Network connectivity issues")
            print("   💡 Current page title:", browser.title)
            
            # Save screenshot for debugging
            try:
                screenshot_path = "google_error_debug.png"
                browser.save_screenshot(screenshot_path)
                print(f"   📸 Saved debug screenshot to: {screenshot_path}")
            except:
                pass
            
            return None, None
        
        # Step 6: Extract all clickable URLs
        all_urls = []
        for result in search_results:
            try:
                url = result.get_attribute("href")
                if url and url.startswith("http") and "google.com" not in url:
                    all_urls.append(url)
            except:
                continue
        
        print(f"   📊 Extracted {len(all_urls)} URLs from search results")
        
        # Debug: Show first few URLs found
        if all_urls:
            print(f"   🔗 Sample URLs found:")
            for url in all_urls[:3]:
                domain = url.split('/')[2] if len(url.split('/')) > 2 else url
                print(f"      • {domain}")
        
        # Step 7: Filter and prioritize Amazon URLs
        # Priority 1: amazon.ae
        for url in all_urls:
            if "amazon.ae" in url and "/dp/" in url:
                print(f"   ✅ Found amazon.ae URL (boosted by '{geo_keyword}')")
                return url, "amazon.ae"
        
        # Priority 2: amazon.in
        for url in all_urls:
            if "amazon.in" in url and "/dp/" in url:
                print(f"   ✅ Found amazon.in URL")
                return url, "amazon.in"
        
        # Priority 3: amazon.com
        for url in all_urls:
            if "amazon.com" in url and "/dp/" in url:
                print(f"   ✅ Found amazon.com URL")
                return url, "amazon.com"
        
        print("   ⚠️  No Amazon product URLs found in results")
        print("   💡 This might mean the product isn't available on Amazon")
        return None, None
        
    except Exception as e:
        print(f"   ❌ Error during Google search: {str(e)}")
        print(f"   📍 Error type: {type(e).__name__}")
        
        # Try to provide helpful context
        try:
            print(f"   🌐 Current URL: {browser.current_url}")
            print(f"   📄 Page title: {browser.title}")
        except:
            pass
        
        return None, None

def search_and_scrape_data(site):
    """
    Main scraping function with batch processing to avoid CAPTCHAs
    """
    cfg = SITE_CONFIG[site]
    total_start_time = time.time()
    
    print(f"\n{'='*80}")
    print(f"🚀 Starting {site} data scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Using geo-keyword: '{GEO_KEYWORD}'")
    print(f"{'='*80}\n")
    
    # Read input Excel
    try:
        full_df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
        full_df = full_df.iloc[cfg["START_ROW"]-2:cfg["END_ROW"]]
        
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return
    
    output_csv = cfg["CSV"]
    
    # Check for existing progress
    if os.path.exists(output_csv) and os.path. getsize(output_csv) > 0:
        try:
            processed_df = pd.read_csv(output_csv)
            
            
            # FIX: Use lowercase 'variant_id' consistently
            processed_ids = set(processed_df['variant_id']. astype(str))
            df_to_process = full_df[~full_df['variant_id'].astype(str).isin(processed_ids)]
            
            print(f"📄 Resuming...  {len(processed_df)} products already processed")
            print(f"📋 Remaining products: {len(df_to_process)}\n")
            
        except Exception as e:
            print(f"⚠️ Could not load progress: {e}")
            import traceback
            traceback.print_exc()
            df_to_process = full_df.copy()
    else:
        df_to_process = full_df.copy()
        print(f"📄 Starting fresh with {len(df_to_process)} products\n")
    
    if len(df_to_process) == 0:
        print("✅ All products already processed!")
        # Still convert to Excel
        convert_csv_to_excel(output_csv)
        return
        
        # Create browser with anti-detection measures
    file_exists = os.path.exists(output_csv) and os.path.getsize(output_csv) > 0
    search_count = 0
    batch_number = 0
    browser = create_browser_with_anti_detection(user_agent_index=batch_number)

    # Process each product
    processed_count = 0
    for index, row in df_to_process.iterrows():
        product_start_time = time.time()
        search_count += 1
        
        try:
            Variant_id = str(row['variant_id']).strip()
            full_Variant_name = str(row['variant_name']).strip()
            
            if not Variant_id or not full_Variant_name:
                continue
            
            processed_count += 1
            
            # Check if search_count is divisible by 15
            if search_count % 15 == 0:
                print(f"\n{'='*80}")
                print(f"🔄 BROWSER REFRESH CYCLE: Search count reached {search_count}")
                print(f"{'='*80}")
                
                # Close current browser
                print("   🔒 Closing current browser...")
                try:
                    browser.quit()
                except:
                    pass
                
                # Wait 2-3 minutes
                wait_minutes = random.randint(120, 180)
                print(f"   ⏸️ Cooling down for {wait_minutes // 60}m {wait_minutes % 60}s...")
                
                
                # Create new browser with new user agent
                batch_number += 1
                print(f"\n   🆕 Creating new browser instance (Batch #{batch_number})...")
                browser = create_browser_with_anti_detection(user_agent_index=batch_number)
                print(f"{'='*80}\n")
            
            print(f"🔎 Product {processed_count}/{len(df_to_process)}: {full_Variant_name}")
            print(f"📊 Search Count: {search_count}")
            print(f"🆔 ID: {Variant_id}")
            
            # Search for product on DuckDuckGo first
            product_url, amazon_site = search_duckduckgo_and_get_amazon_url(full_Variant_name, browser)
            
            # Fallback to Google if no results
            if not product_url:
                print("   🔄 DuckDuckGo search failed, trying Google as fallback...")
                product_url, amazon_site = search_google_and_get_amazon_url(full_Variant_name, browser)
            
            if product_url:
                print(f"   📦 Found on {amazon_site}")
                
                # Extract data from the product page
                product_data = scrape_product_data(product_url, browser)
                
                # Combine variant info with scraped data
                row_data = {
                    "variant_id": Variant_id,
                    "variant_name": full_Variant_name,
                    "product_name": product_data["product_name"],                   
                    "Weight": product_data["product_weight"],
                    "status": product_data["status"],
                    "product_url": product_url,
                }
            else:
                print(f"   ⚠️ Product URL not found")
                
                row_data = {
                    "variant_id": Variant_id,
                    "variant_name": full_Variant_name,
                    "product_name": "Not Found",
                    "Weight": "Not Found",
                    "status": "Not Found",
                    "product_url": "URL Not Found",
                }
            
            # Save to CSV
            result_df = pd.DataFrame([row_data])
            result_df.to_csv(output_csv, mode='a', header=not file_exists, index=False)
            file_exists = True
            
            # ✅ FIXED: Calculate and display progress - removed space before .2f
            product_time = time.time() - product_start_time
            print(f"   ⏱️ Product processed in {product_time:.2f}s")
            
            # Human-like delay before next search
            wait_time = random.randint(4, 7)
            print(f"   ⏳ Waiting {wait_time} seconds.. .\n")
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"   ❌ Error processing product: {str(e)}\n")
            import traceback
            traceback.print_exc()  # This will show the exact line causing the error
            
            # Optionally save error entry
            try:
                error_row = {
                    "variant_id": Variant_id,
                    "variant_name": full_Variant_name,
                    "product_name": "Error",
                    "Weight": "Error",
                    "status": f"Error: {str(e)[:50]}",
                    "product_url": "Error",
                }
                result_df = pd.DataFrame([error_row])
                result_df.to_csv(output_csv, mode='a', header=not file_exists, index=False)
                file_exists = True
            except:
                pass
            continue

    # Close browser if still open
    try:
        browser.quit()
    except:
        pass

    # Convert CSV to Excel
    convert_csv_to_excel(output_csv)

    elapsed = time.time() - total_start_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)

    print(f"{'='*80}")
    print(f"🏁 Scraping completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️ Total time: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
    print(f"📊 Total searches performed: {search_count}")
    print(f"📊 Total products processed: {processed_count}")
    print(f"{'='*80}\n")    

def convert_csv_to_excel(output_csv):
    """Separate function to convert CSV to Excel"""
    print(f"\n{'='*80}")
    print(f"📊 Converting to Excel format...")
    
    try:
        csv_df = pd.read_csv(output_csv)
        excel_path = OUTPUT_EXCEL
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            csv_df.to_excel(writer, sheet_name='Products', index=False)
            
            from openpyxl. utils import get_column_letter
            worksheet = writer.sheets['Products']
            
            for idx, col in enumerate(csv_df. columns, 1):
                max_length = max(csv_df[col].astype(str). map(len).max(), len(col))
                worksheet.column_dimensions[get_column_letter(idx)].width = min(max_length + 2, 50)
        
        print(f"✅ Excel file created: {excel_path}")
        print(f"📊 Total products in Excel: {len(csv_df)}")
        
    except Exception as e:
        print(f"⚠️ Could not create Excel file: {e}")
        import traceback
        traceback. print_exc()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🌐 AMAZON PRODUCT DATA SCRAPER")
    print("="*80)
    print("\nThis scraper extracts:")
    print("  • Product Weight")
    print("  • Product Name")
    print("="*80 + "\n")
    
    # site_choice = input("Enter site (amazon.ae / amazon.in / amazon.com): ").strip().lower()
    site_choice = "amazon.ae"  # Change this value to choose site    
    if site_choice in SITE_CONFIG:
        search_and_scrape_data(site_choice)
    else:
        print("❌ Invalid choice. Please choose: amazon.ae, amazon.in, or amazon.com")