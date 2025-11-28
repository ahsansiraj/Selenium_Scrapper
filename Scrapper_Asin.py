import os
import re
import time
import random
import pandas as pd
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# ---------- CONFIG ----------
EXCEL_FILE = "for Data Scrapping.xlsx"
SHEET_NAME = "Variant"
OUTPUT_EXCEL = "Scraped_Product_Data2.xlsx"
MAX_WORD = 10
GEO_KEYWORD = "Dubai"

# Realistic user agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

SITE_CONFIG = {
    "amazon.ae": {
        "CSV": "ASIN_data_Amazon_ae2.csv",
        "START_ROW": 5,
        "END_ROW": 21,
    },
    "amazon.in": {
        "CSV": "ASIN_data_Amazon_in2.csv",
        "START_ROW": 5,
        "END_ROW": 21,
    },
    "amazon.com": {
        "CSV": "ASIN_data_Amazon_com2.csv",
        "START_ROW": 5,
        "END_ROW": 21,
    }
}

def create_browser_with_anti_detection():
    """
    Creates a Chrome browser with anti-detection measures enabled.
    This makes our scraper look like a real human browsing, not a bot.
    """
    options = Options()
    options.add_argument("--start-maximized")
    
    # Critical anti-detection settings
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f"user-agent={USER_AGENT}")
    
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    
    # Hide the webdriver property that websites use to detect automation
    browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    return browser

def extract_asin_from_url(url):
    """
    Extract ASIN from Amazon URL.
    ASIN always appears after /dp/ in the URL.
    
    Example: https://www.amazon.ae/.../dp/B085BF8WSX?... → B085BF8WSX
    """
    try:
        match = re.search(r'/dp/([A-Z0-9]{10})', url)
        if match:
            return match.group(1)
    except:
        pass
    return None

def extract_asin_from_page(browser):
    """
    Extract ASIN from the detail bullets section on the product page.
    This is more reliable than URL extraction as it's the official source.
    
    Looks for: <li>...<span class="a-text-bold">ASIN</span>...<span>B085BF8WSX</span>...</li>
    """
    try:
        # Find all list items in the detail bullets
        detail_items = browser.find_elements(By.CSS_SELECTOR, "#detailBullets_feature_div li")
        
        for item in detail_items:
            try:
                item_text = item.text
                # Check if this item contains "ASIN"
                if "ASIN" in item_text:
                    # Extract the ASIN value (10 character alphanumeric code)
                    match = re.search(r'ASIN\s*(?::\s*)?([A-Z0-9]{10})', item_text)
                    if match:
                        asin = match.group(1)
                        print(f"      ✓ Found ASIN from detail bullets: {asin}")
                        return asin
            except:
                continue
    except:
        pass
    
    return None

def extract_asin(browser, url):
    """
    Extract ASIN using our priority: detail bullets first, then URL fallback.
    """
    # Try detail bullets first (more reliable)
    asin = extract_asin_from_page(browser)
    if asin:
        return asin
    
    # Fallback to URL extraction
    asin = extract_asin_from_url(url)
    if asin:
        print(f"      ✓ Found ASIN from URL: {asin}")
        return asin
    
    print(f"      ✗ ASIN not found")
    return "Not Found"

def extract_product_name(browser):
    """
    Extract the product title from the page.
    Looks for: <span id="productTitle">Apple iPhone 14 Pro...</span>
    """
    try:
        product_title = browser.find_element(By.ID, "productTitle")
        name = product_title.text.strip()
        if name:
            print(f"      ✓ Found product name: {name[:60]}...")
            return name
    except:
        pass
    
    print(f"      ✗ Product name not found")
    return "Not Found"

def extract_price(browser):
    """
    Extract price from the product page.
    Amazon stores price in multiple spans:
    - a-price-symbol: "AED"
    - a-price-whole: "2,611"
    - a-price-fraction: "45"
    
    We combine them to get: "AED 2,611.45"
    """
    try:
        price_container = browser.find_element(By.CSS_SELECTOR, "span.a-price.aok-align-center.reinventPricePriceToPayMargin")
        
        # Extract currency symbol
        try:
            currency = price_container.find_element(By.CSS_SELECTOR, ".a-price-symbol").text
        except:
            currency = "AED"
        
        # Extract whole number part (may contain comma like "2,611")
        try:
            whole = price_container.find_element(By.CSS_SELECTOR, ".a-price-whole").text
            # Remove any whitespace but keep the comma and number
            whole = whole.replace('\xa0', '').strip()
        except:
            whole = "0"
        
        # Extract fractional part (the cents)
        try:
            fraction = price_container.find_element(By.CSS_SELECTOR, ".a-price-fraction").text
        except:
            fraction = "00"
        
        # Combine into final price format: "AED 2,611.45"
        price = f"{currency} {whole}.{fraction}"
        print(f"      ✓ Found price: {price}")
        return price
        
    except Exception as e:
        print(f"      ✗ Price not found: {e}")
        return "Not Found"

def extract_launch_date(browser):
    """
    Extract launch date from the detail bullets section.
    Looks for "Date First Available" field.
    
    Example: "Date First Available : 12 December 2023"
    """
    try:
        # Find all list items in the detail bullets
        # Try detail bullets first (modern Amazon layout)
        detail_items = browser.find_elements(By.CSS_SELECTOR, "#detailBullets_feature_div li")
        
        # If not found, try the table layout (older/alternate Amazon layout)
        if not detail_items:
            detail_items = browser.find_elements(By.CSS_SELECTOR, "#productDetails_detailBullets_sections1 tr")
        
        for item in detail_items:
            try:
                item_text = item.text
                # Look for "Date First Available" in the text
                if "Product Dimensions" in item_text or "Release Date" in item_text:
                    # Extract the date part (everything after the colon)
                    match = re.search(r'(?:Date First Available|Release Date)\s*(?::\s*)?(.+?)(?:\n|$)', item_text)
                    if match:
                        date = match.group(1).strip()
                        print(f"      ✓ Found launch date: {date}")
                        return date
            except:
                continue
    except:
        pass
    
    print(f"      ✗ Launch date not found")
    return "Not Found"

def extract_product_condition(productName):
    """
    Determine product condition based on keywords in the product name.
    """
    condition_keywords = {
        "Used": ["used", "pre-owned", "second hand"],
        "Refurbished": ["refurbished", "renewed", "like new"],
        "New": ["new", "brand new", "sealed"]
    }
    
    productNameLower = productName.lower()

    print(productNameLower)
    
    for condition, keywords in condition_keywords.items():
        for keyword in keywords:
            if keyword in productNameLower:
                print(f"      ✓ Detected product condition: {condition}")
                return condition
    
    print(f"      ✓ Product condition assumed: New")
    return "New"
    
def scrape_product_data(product_url, browser, retry_count=0, max_retries=1):
    """
    Extract all product data from an Amazon product page.
    
    This function:
    1. Opens the product page
    2. Waits for the page to load
    3. Extracts ASIN, price, product name, and launch date
    4. Returns a dictionary with all the data
    5. Handles errors by retrying with a fresh browser if needed
    
    Args:
        product_url: Full URL of the Amazon product page
        browser: Selenium browser instance
        retry_count: How many times we've already tried this URL
        max_retries: Maximum number of retry attempts
    
    Returns:
        dict: Contains product_name, asin, price, launch_date, and status
    """
    data = {
        "product_name": "Not Found",
        "asin": "Not Found",
        "price": "Not Found",
        "launch_date": "Not Found",
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
        data["product_condition"] = extract_product_condition(data["product_name"])
        data["asin"] = extract_asin(browser, product_url)
        data["launch_date"] = extract_launch_date(browser)
        data["price"] = extract_price(browser)
        
        data["status"] = "Success"
        print(f"   ✅ Data extraction successful")
        return data
        
    except Exception as e:
        print(f"   ❌ Error loading page: {str(e)}")
        
        # Retry strategy: if we haven't exceeded max retries, try again with fresh browser
        if retry_count < max_retries:
            print(f"   🔄 Retrying with new browser instance ({retry_count + 1}/{max_retries})...")
            time.sleep(random.uniform(3, 5))
            
            # Close current browser and create a new one
            try:
                browser.quit()
            except:
                pass
            
            new_browser = create_browser_with_anti_detection()
            result = scrape_product_data(product_url, new_browser, retry_count + 1, max_retries)
            
            try:
                new_browser.quit()
            except:
                pass
            
            return result
        else:
            # Max retries exceeded, mark as failed
            data["status"] = "Data Extraction Failed"
            print(f"   ⚠️  Max retries exceeded")
            return data

def search_google_and_get_amazon_url(variant_name, browser, geo_keyword=GEO_KEYWORD):
    """
    Search Google for Amazon product URLs with enhanced anti-detection measures.
    
    This function implements several strategies to avoid Google's bot detection:
    - Realistic typing speed (humans don't type instantly)
    - Random delays between actions
    - Multiple CSS selectors as fallbacks
    - Better error handling and debugging
    
    Args:
        variant_name: The product name to search for
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
        search_query = f"{variant_name} {geo_keyword}"
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
        
        time.sleep(random.uniform(0.5, 1.0))  # Pause before hitting enter
        search_box.send_keys(Keys.ENTER)
        
        # Step 5: Wait for search results to load with multiple strategies
        print("   ⏳ Waiting for search results...")
        time.sleep(random.uniform(3, 5))  # Give Google time to fully render
        
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

def shorten_variant_name(name, max_word):
    """Shorten product name for cleaner searches"""
    return ' '.join(name.split()[:max_word])

def search_and_scrape_data(site):
    """
    Main scraping function that processes all products and saves data to Excel.
    
    Flow:
    1. Read products from input Excel file
    2. For each product:
       a. Search Google for Amazon product URL
       b. Extract product data from the Amazon page
       c. Combine with variant info
       d. Save to temporary CSV
    3. Convert CSV to final Excel file with proper formatting
    """
    cfg = SITE_CONFIG[site]
    total_start_time = time.time()
    
    print(f"\n{'='*80}")
    print(f"🚀 Starting {site} data scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Using geo-keyword: '{GEO_KEYWORD}'")
    print(f"{'='*80}\n")
    
    # Read input Excel file with product variants
    try:
        full_df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
        full_df = full_df.iloc[cfg["START_ROW"]-2:cfg["END_ROW"]]
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return
    
    output_csv = cfg["CSV"]
    
    # Check if we're resuming from a previous run
    if os.path.exists(output_csv) and os.path.getsize(output_csv) > 0:
        try:
            processed_df = pd.read_csv(output_csv)
            processed_ids = set(processed_df['variant_id'].astype(str))
            df_to_process = full_df[~full_df['variant_id'].astype(str).isin(processed_ids)]
            print(f"📄 Resuming... {len(processed_df)} products already processed\n")
        except:
            df_to_process = full_df.copy()
    else:
        df_to_process = full_df.copy()
        print(f"📄 Starting fresh with {len(df_to_process)} products\n")
    
    # Create browser with anti-detection measures
    browser = create_browser_with_anti_detection()
    file_exists = os.path.exists(output_csv)
    
    # Process each product
    for index, row in df_to_process.iterrows():
        product_start_time = time.time()
        
        try:
            variant_id = str(row['variant_id']).strip()
            full_variant_name = str(row['variant_name']).strip()
            variant_name = shorten_variant_name(full_variant_name, MAX_WORD)
            
            if not variant_id or not variant_name:
                continue
            
            print(f"{'='*80}")
            print(f"🔎 Product: {full_variant_name}")
            print(f"🆔 ID: {variant_id}")
            print(f"{'='*80}")
            
            # Search for product on Google
            product_url, amazon_site = search_google_and_get_amazon_url(variant_name, browser)
            
            if product_url:
                print(f"   📦 Found on {amazon_site}")
                
                # Extract data from the product page
                product_data = scrape_product_data(product_url, browser)
                
                # Combine variant info with scraped data
                row_data = {
                    "variant_id": variant_id,
                    "variant_name": full_variant_name,
                    "asin": product_data["asin"],
                    "launch_date": product_data["launch_date"],
                    "price": product_data["price"],
                    "product_name": product_data["product_name"],
                    "product_condition": product_data["product_condition"],
                    "product_url": product_url,
                    "status": product_data["status"]
                }
            else:
                print(f"   ⚠️  Product URL not found on Google")
                
                row_data = {
                    "variant_id": variant_id,
                    "variant_name": full_variant_name,
                    "asin": "Not Found",
                    "price": "Not Found",
                    "launch_date": "Not Found",
                    "product_name": "Not Found",
                    "product_condition": "Not Found",
                    "product_url": "Not Found",
                    "status": "URL Not Found"
                }
            
            # Save to CSV
            result_df = pd.DataFrame([row_data])
            result_df.to_csv(output_csv, mode='a', header=not file_exists, index=False)
            file_exists = True
            
            # Human-like delay before next search
            wait_time = random.randint(4, 7)
            print(f"   ⏳ Waiting {wait_time} seconds...\n")
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"   ❌ Error processing product: {str(e)}\n")
            continue
    
    # Close browser
    try:
        browser.quit()
    except:
        pass
    
    # Convert CSV to Excel with proper formatting
    print(f"\n{'='*80}")
    print(f"📊 Converting to Excel format...")
    
    try:
        csv_df = pd.read_csv(output_csv)
        
        # Define column order to match row_data structure
        column_order = [
            "variant_id",
            "variant_name",
            "asin",
            "price",
            "launch_date",
            "product_name",
            "product_url",
            "status"
        ]
        
        # Reorder columns in dataframe
        csv_df = csv_df[[col for col in column_order if col in csv_df.columns]]
        
        excel_path = OUTPUT_EXCEL
        
        # Create Excel writer with formatting
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            csv_df.to_excel(writer, sheet_name='Products', index=False)
            
            # Auto-adjust column widths
            from openpyxl.utils import get_column_letter
            worksheet = writer.sheets['Products']
            
            for idx, col in enumerate(csv_df.columns, 1):
                max_length = max(csv_df[col].astype(str).map(len).max(), len(col))
                worksheet.column_dimensions[get_column_letter(idx)].width = min(max_length + 2, 50)
        
        print(f"✅ Excel file created: {excel_path}")
    except Exception as e:
        print(f"⚠️  Could not create Excel file: {e}")
        print(f"   CSV file available at: {output_csv}")
    elapsed = time.time() - total_start_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    
    print(f"{'='*80}")
    print(f"🏁 Scraping completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Total time: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🌐 AMAZON PRODUCT DATA SCRAPER")
    print("="*80)
    print("\nThis scraper extracts:")
    print("  • Product Name")
    print("  • ASIN (Amazon Standard Identification Number)")
    print("  • Price (with currency)")
    print("  • Launch Date")
    print("  • Product URL")
    print("\nOutput: Excel file with all product data")
    print("="*80 + "\n")
    
    site_choice = input("Enter site (amazon.ae / amazon.in / amazon.com): ").strip().lower()
    
    if site_choice in SITE_CONFIG:
        search_and_scrape_data(site_choice)
    else:
        print("❌ Invalid choice. Please choose: amazon.ae, amazon.in, or amazon.com")