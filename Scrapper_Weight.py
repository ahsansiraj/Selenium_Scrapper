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

from Scrapper import search_duckduckgo_and_get_amazon_url

# ---------- CONFIG ----------
EXCEL_FILE = "for Data Scrapping.xlsx"
SHEET_NAME = "Sheet3"
OUTPUT_EXCEL = "Scraped_Product_Weight.xlsx"
MAX_WORD = 10
GEO_KEYWORD = "Dubai"

# Realistic user agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

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
                   "div.a-column.a-span6.block-content.block-type-table.textalign-left.a-span-last div.content-grid-block table tr",
                   "div.content-grid-block table.a-bordered tr",
                   "table.a-bordered tr"]
        
        detail_items = []
        for selector in selectors:
            elements = browser.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                detail_items.extend(elements)
                break
            
        if detail_items:
            print(f"      📊 Found {len(detail_items)} detail items to process")
        else:
            print("      ⚠️ No detail items found")
            return "Not Found"

        for item in detail_items:
            try:
                item_text = item.text.strip()
                
                # Skip empty rows
                if not item_text:
                    continue
                
                print(f"      🔍 Checking row: {item_text[:50]}...")

                # Pattern: "Weight\n6.14 ounces (174 grams)"
                if "Weight" in item_text:
                    # First try: Extract any weight pattern from the text
                    # This handles: "6.14 ounces (174 grams)" or "174 grams (6.14 ounces)"
                    weight_match = re. search(r'([0-9.,]+)\s*(ounces?|grams?|g|kg|lb|oz|kilograms?|pounds?)', item_text, re.IGNORECASE)
                    if weight_match:
                        weight_value = weight_match.group(1).strip()
                        weight_unit = weight_match.group(2).strip().lower()
                        
                        # Normalize units
                        if weight_unit in ['ounce', 'ounces', 'oz']:
                            weight_unit = 'oz'
                        elif weight_unit in ['gram', 'grams']:
                            weight_unit = 'g'
                        elif weight_unit in ['kilogram', 'kilograms']:
                            weight_unit = 'kg'
                        elif weight_unit in ['pound', 'pounds']:
                            weight_unit = 'lb'
                        
                        weight = f"{weight_value} {weight_unit}"
                        weight_in_grams = convert_to_grams(weight_value, weight_unit)
                        if weight_in_grams is not None:
                            weight = f"{weight_in_grams} g"
                        print(f"      ✓ Found weight: {weight}")
                        return weight
                
                # Method 3: Check for "Product Dimensions" or "Package Dimensions"
                # Pattern: "15.24 x 7.62 x 1.27 cm; 174 g"
                elif "Product Dimensions" in item_text or "Package Dimensions" in item_text:
                    print(f"      📦 Checking dimensions for weight...")
                    # Extract weight after semicolon
                    weight_match = re.search(r';\s*([0-9.,]+)\s*(g|kg|lb|oz|ounces|grams|kilograms|pounds)', item_text, re.IGNORECASE)
                    if weight_match:
                        weight_value = weight_match.group(1).strip()
                        weight_unit = weight_match.group(2).strip().lower()
                        
                        # Normalize units
                        if weight_unit in ['ounce', 'ounces', 'oz']:
                            weight_unit = 'oz'
                        elif weight_unit in ['gram', 'grams']:
                            weight_unit = 'g'
                        
                        weight = f"{weight_value} {weight_unit}"
                        weight_in_grams = convert_to_grams(weight_value, weight_unit)
                        if weight_in_grams is not None:
                            weight = f"{weight_in_grams} g"
                        print(f"      ✓ Found weight from dimensions: {weight}")
                        return weight
        
            except Exception as e:
                print(f"      ⚠️ Error processing item: {e}")
                continue

        print("      ❌ Weight not found in product details")
        return "Not Found"

    except Exception as e:
        print(f"      ❌ Error extracting weight: {str(e)}")
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
        return value * 1000
    elif unit in ['oz', 'ounce', 'ounces']:
        return value * 28.3495
    elif unit in ['lb', 'lbs', 'pound', 'pounds']:
        return value * 453.592
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
        
        # Step 5: Wait for search results to load with multiple strategies
        print("   ⏳ Waiting for search results...")
        time.sleep(random.uniform(1,20))  # Give Google time to fully render

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
            Variant_id = str(row['variant_id']).strip()
            full_Variant_name = str(row['variant_name']).strip()
            
            if not Variant_id or not full_Variant_name:
                continue
            
            print(f"{'='*80}")
            print(f"🔎 Product: {full_Variant_name}")
            print(f"🆔 ID: {Variant_id}")
            print(f"{'='*80}")
            
            # Search for product on Google
            product_url, amazon_site = search_google_and_get_amazon_url(full_Variant_name, browser)
            
            # Try Google first, fallback to DuckDuckGo if no results
            if not product_url:
                print("   🔄 Google search failed, trying DuckDuckGo as fallback...")
                product_url, amazon_site = search_duckduckgo_and_get_amazon_url(full_Variant_name, browser)
            
            if product_url:
                print(f"   📦 Found on {amazon_site}")
                
                # Extract data from the product page
                product_data = scrape_product_data(product_url, browser)
                
                # Combine variant info with scraped data
                row_data = {
                    "Variant_id": Variant_id,
                    "Variant_name": full_Variant_name,
                    "product_name": product_data["product_name"],                   
                    "Weight": product_data["product_weight"],
                    "status": product_data["status"],
                    "product_url": product_url,
                }
            else:
                print(f"   ⚠️  Product URL not found on Google")
                
                row_data = {
                    "Variant_id": Variant_id,
                    "Variant_name": full_Variant_name,
                    "product_name": "Not Found",
                    "Weight": "Not Found",
                    "status": "Not Found",
                    "product_url": "URL Not Found",
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
    
    try:
        csv_df = pd.read_csv(output_csv)
        
        # Define column order to match row_data structure
        column_order = [
            "variant_id",
            "variant_name",
            "Weight",
            "status",
            "product_url",
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
    print("  • Product Weight")
    print("  • Product Name")
    print("="*80 + "\n")
    
    site_choice = input("Enter site (amazon.ae / amazon.in / amazon.com): ").strip().lower()
    
    if site_choice in SITE_CONFIG:
        search_and_scrape_data(site_choice)
    else:
        print("❌ Invalid choice. Please choose: amazon.ae, amazon.in, or amazon.com")