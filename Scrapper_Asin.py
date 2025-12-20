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
import re

from search_engines import search_duckduckgo_and_get_amazon_url
from search_engines import search_google_and_get_amazon_url

# ---------- CONFIG ----------
EXCEL_FILE = "for Data Scrapping.xlsx"
SHEET_NAME = "Sheet3"
OUTPUT_EXCEL = "Scraped_Product_Data2.xlsx"
MAX_WORD = 11
GEO_KEYWORD = "Dubai"

# Realistic user agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
SITE_CONFIG = {
    "amazon.ae": {
        "CSV": "ASIN_data_Amazon_ae2.csv",
        "START_ROW": 2,
        "END_ROW": 3460,
    },
    "amazon.in": {
        "CSV": "ASIN_data_Amazon_in2.csv",
        "START_ROW": 2,
        "END_ROW": 3460,
    },
    "amazon.com": {
        "CSV": "ASIN_data_Amazon_com2.csv",
        "START_ROW": 2,
        "END_ROW": 3460,
    }
}

def create_browser_with_anti_detection():
    """
    Creates an undetected Chrome browser with anti-detection measures enabled.
    This makes our scraper look like a real human browsing, not a bot. 
    """
    
    # Create options for undetected chrome
    options = uc.ChromeOptions()
    
    # Window settings
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"user-agent={USER_AGENT}")
    # Anti-detection settings (undetected_chromedriver handles most of these automatically)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    
    # Memory limits
    options.add_argument("--max_old_space_size=4096")  # Limit memory to 4GB
    options.add_argument("--js-flags=--max-old-space-size=4096")
    
    # Random user agent
    # user_agent = random.choice(USER_AGENTS)
    # options.add_argument(f"user-agent={user_agent_index}")
    
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
        
        
        # Additional stealth scripts (optional, but helpful)
        browser.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": USER_AGENT
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


def extract_asin_from_url(url):
    """
    Extract ASIN from Amazon URLs using regex patterns.
    
    Examples:
    - https://www.amazon.ae/. ../dp/B09G98MBX1 → B09G98MBX1
    - https://www.amazon.ae/.../dp/B09G98MBX1?th=1 → B09G98MBX1
    - https://www.amazon.ae/.../dp/B09G98MBX1/ref=...  → B09G98MBX1
    """
    try: 
        # Match /dp/ followed by 1-10 alphanumeric characters (uppercase letters and digits)
        # Stop at:  ?, /, #, or end of string
        match = re.search(r'/dp/([A-Z0-9]{1,10})(?:[/?#]|$)', url, re.IGNORECASE)
        if match:
            asin = match.group(1).upper()  # Normalize to uppercase
            print(f"      ✓ Extracted ASIN from URL: {asin}")
            return asin
        
        # Alternative pattern:  sometimes ASIN is in /gp/product/
        match = re.search(r'/gp/product/([A-Z0-9]{1,10})(?:[/?#]|$)', url, re.IGNORECASE)
        if match:
            asin = match.group(1).upper()
            print(f"      ✓ Extracted ASIN from URL (gp/product): {asin}")
            return asin
            
    except Exception as e: 
        print(f"      ⚠️ Error extracting ASIN from URL: {e}")
    
    return None


def extract_asin_from_page(browser):
    """
    Extract ASIN from the detail bullets section on the product page. 
    This is more reliable than URL extraction as it's the official source. 
    
    Looks for: <li>...<span class="a-text-bold">ASIN</span>...<span>B085BF8WSX</span>...</li>
    """
    try:
        # Find all list items in the detail bullets
        selectors = [
            "#detailBullets_feature_div li",
            "#productDetails_techSpec_section_1 tr",
            "#productDetails_detailBullets_sections1 tr",
            "#productDetails_techSpec_section_2 tr",
            "div.a-column.a-span6.block-content.block-type-table.textalign-left.a-span-last div.content-grid-block table tr",
            "div.content-grid-block table.a-bordered tr",
            "table.a-bordered tr"
        ]
        
        # Try each selector until we find ASIN
        for selector_index, selector in enumerate(selectors, 1):
            try:
                elements = browser.find_elements(By.CSS_SELECTOR, selector)
                
                if not elements:
                    continue
                
                # Search through all elements from this selector for ASIN
                for item in elements: 
                    try:
                        item_text = item.text.strip()
                        print(item_text)
                        # Skip empty rows
                        if not item_text:
                            continue

                        if "ASIN" in item_text.upper():
                            # Extract the ASIN value (1-10 character alphanumeric code)
                            match = re.search(r'ASIN\s*(?::\s*)?([A-Z0-9]{,10})', item_text, re.IGNORECASE)
                            if match:
                                asin = match.group(1).upper()
                                print(f"      ✓ Found ASIN from detail bullets: {asin}")
                                return asin
                            
                    except Exception as e:
                        # Error with individual element, continue to next
                        continue
                
            except Exception as e:
                print(f"      ⚠️ Selector {selector_index} error: {e}")
                continue
        
        print("      ⚠️ ASIN not found in page elements")
        return "Not Found"  

    except Exception as e:
        print(f"      ❌ Error extracting ASIN: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Not Found"


def extract_asin(browser, url):
    """
    Extract ASIN using our priority: detail bullets first, then URL fallback.
    
    Returns: 
        str: The ASIN code (e.g., "B09G98MBX1") or "Not Found"
    """
    # Try detail bullets first (more reliable)
    asin = extract_asin_from_page(browser)
    
    # CRITICAL FIX: Check if asin is None or empty, not just truthy
    if asin and asin != "Not Found":
        return asin
    
    # Fallback to URL extraction
    print("      🔄 Falling back to URL extraction...")
    asin = extract_asin_from_url(url)
    if asin:
        return asin
    
    print(f"      ✗ ASIN not found in page or URL")
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
        return "Currently Unavailable" if e else "Not Found"

def extract_launch_date(browser):
    """
    Extract launch date from the detail bullets section.
    Looks for "Date First Available" field.
    
    Example: "Date First Available : 12 December 2023"
    """
    # try:
    #     # Find all list items in the detail bullets
    #     # Try detail bullets first (modern Amazon layout)
    #     detail_items = browser.find_elements(By.CSS_SELECTOR, "#detailBullets_feature_div li")
        
    #     # If not found, try the table layout (older/alternate Amazon layout)
    #     if not detail_items:
    #         detail_items = browser.find_elements(By.CSS_SELECTOR, "#productDetails_detailBullets_sections1 tr")
        
    #     for item in detail_items:
    #         try:
    #             item_text = item.text
    #             # Look for "Date First Available" in the text
    #             if "Product Dimensions" in item_text or "Release Date" in item_text:
    #                 # Extract the date part (everything after the colon)
    #                 match = re.search(r'(?:Date First Available|Release Date)\s*(?::\s*)?(.+?)(?:\n|$)', item_text)
    #                 if match:
    #                     date = match.group(1).strip()
    #                     print(f"      ✓ Found launch date: {date}")
    #                     return date
    #         except:
    #             continue
    # except:
    #     pass
    
    # print(f"      ✗ Launch date not found")
    # return "Not Found"

    try:
        # Find all list items in the detail bullets
        selectors=["#detailBullets_feature_div li",
                   "#productDetails_techSpec_section_1 tr",
                   "#productDetails_detailBullets_sections1 tr",
                   "#productDetails_techSpec_section_2 tr",
                   "div.a-column.a-span6.block-content.block-type-table.textalign-left.a-span-last div.content-grid-block table tr",
                   "div.content-grid-block table.a-bordered tr",
                   "table.a-bordered tr"]
        
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

                        # Check if this item contains "Date First Available" or "Release Date"
                        if "Product Dimensions" in item_text or "Date First Available" in item_text or "Release Date" in item_text:
                            # Extract the date part (everything after the colon)
                            match = re.search(r'(?:Date First Available|Release Date)\s*(?::\s*)?(.+?)(?:\n|$)', item_text)
                            if match:
                                date = match.group(1).strip()
                                print(f"      ✓ Found launch date: {date}")
                                return date

                    except Exception as e:
                        # Error with individual element, continue to next
                        continue
                
                # Finished checking all elements from this selector without finding Release Date
                print(f" ⏭️  Selector {selector_index}: No Release Data found in these elements, trying next selector...")
                
            except Exception as e:
                print(f"      ⚠️  Selector {selector_index} error: {e}")
                continue
        
        # If we've tried all selectors and found nothing
        print(" ❌ Release Data not found in any location")
        return "Not Found"

    except Exception as e:
        print(f" ❌ Error extracting Release Date: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Not Found"

def extract_product_condition(productName, browser):
    """
    Determine product condition based on keywords in the product name.
    First checks if refurbished badge exists on the page, then checks product name keywords.
    """
    condition_keywords = {
        "Used": ["used", "pre-owned", "second hand"],
        "Refurbished": ["refurbished", "renewed", "like new"],
        "New": ["new", "brand new", "sealed"]
    }
    
    productNameLower = productName.lower()
    print(f" Checking product condition for: {productNameLower}")
    
    try:
        for condition, keywords in condition_keywords.items():
            for keyword in keywords:
                if keyword in productNameLower:
                    print(f"Detected product condition: {condition} (keyword: '{keyword}')")
                    return condition
    except Exception as e:
        print(f" Could not check product name keywords: {e}")

    # Check if refurbished badge element exists on the page
    refurbished_elements = browser.find_elements(By.CSS_SELECTOR, ".refurbished-badge-wrapper i.a-icon.a-icon-addon.refurbished-badge")
    if refurbished_elements and len(refurbished_elements) > 0:
        print(f"   Detected product condition: Refurbished (badge found on page)")
        return "Refurbished"
    
    print(f"  Product condition assumed: New (no indicators found)")
    return "New"

def handle_amazon_popup(browser):
    """
    Automatically click the 'Continue Shopping' button on Amazon.ae popup
    Handles both Arabic and English versions
    """
    try: 
        # Wait a bit for popup to appear
        time.sleep(1)
        
        # Multiple selectors for the button (Amazon changes them)
        button_selectors = [
            # Arabic button
            "//button[contains(text(), 'متابعة التسوق')]",
            "//input[@type='submit'][contains(@value, 'متابعة')]",
            "//button[contains(@class, 'a-button-text')][contains(text(), 'متابعة')]",
            
            # English button (fallback)
            "//button[contains(text(), 'Continue shopping')]",
            "//input[@type='submit'][contains(@value, 'Continue')]",
            
            # Generic form submit button
            "form[action*='/errors/validateCaptcha'] button[type='submit']",
            "form[action*='/errors/validateCaptcha'] input[type='submit']",
            
            # By class name
            "button. a-button-text",
        ]
        
        for selector in button_selectors:
            try:
                if selector. startswith("//"):
                    # XPath selector
                    button = browser.find_element(By.XPATH, selector)
                else:
                    # CSS selector
                    button = browser.find_element(By.CSS_SELECTOR, selector)
                
                if button and button.is_displayed():
                    print("      ✓ Found Amazon verification popup - clicking...")
                    button.click()
                    time.sleep(2)  # Wait for page to reload
                    print("      ✅ Popup dismissed")
                    return True
            except: 
                continue
        
        # No popup found (which is fine)
        return False
        
    except Exception as e: 
        # Silently ignore - popup might not exist
        return False
      
def scrape_product_data(product_url, browser):
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
        "product_condition":"Not Found",
        "price": "Not Found",
        "asin": "Not Found",
        "launch_date": "Not Found",
        "status": "Pending"
    }
    
    try:
        print(f"   📄 Opening product page...")
        browser.get(product_url)
        
        # Add human-like delay before scraping
        time.sleep(random.uniform(2, 4))
        
        handle_amazon_popup(browser)

        # Wait for the product title to load (indicates page is ready)
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "productTitle"))
        )
        
        print(f"   🔍 Extracting data...")
        
        # Extract each data point (correct order: product_name, asin, launch_date, price)
        data["product_name"] = extract_product_name(browser)
        data["product_condition"] = extract_product_condition(data["product_name"], browser)
        data["price"] = extract_price(browser)
        data["asin"] = extract_asin(browser, product_url)
        data["launch_date"] = extract_launch_date(browser)
        
        #only mark status success if all data points found
        data["status"] = "Success" if data["asin"] != "Not Found" and data["price"] != "Not Found" and data["price"] != "Currently Unavailable" and data["launch_date"]!="Not Found" and data["product_name"]!="Not Found" and data["product_condition"]!="Not Found" else "Partial Data"


        print(f"   ✅ Data extraction successful")
        return data
        
    except Exception as e:
        print(f"   ❌ Error loading page: {str(e)}")
        
        # Retry strategy: if we haven't exceeded max retries, try again with fresh browser
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
            processed_df = pd.read_csv(output_csv, skipinitialspace=True)
            processed_df.columns = [col.strip() for col in processed_df.columns]  # <-- Add this line
            processed_ids = set(processed_df['variant_id'].astype(str))
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
    browser = create_browser_with_anti_detection()

    # Define the correct column order for output
    columns = [
        "variant_id",
        "variant_name",
        "status",
        "asin",
        "price",
        "launch_date",
        "product_name",
        "product_condition",
        "product_url"
    ]
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
                time.sleep(wait_minutes)
                print(f"   ⏸️ Cooling down for {wait_minutes // 60}m {wait_minutes % 60}s...")
                
                
                # Create new browser with new user agent
                batch_number += 1
                print(f"\n   🆕 Creating new browser instance (Batch #{batch_number})...")
                browser = create_browser_with_anti_detection()
                print(f"{'='*80}\n")
            
            print(f"🔎 Product {processed_count}/{len(df_to_process)}: {full_Variant_name}")
            print(f"📊 Search Count: {search_count}")
            print(f"🆔 ID: {Variant_id}")
            
            # Search for product on DuckDuckGo first
            product_url, amazon_site =  search_duckduckgo_and_get_amazon_url(full_Variant_name, browser)
            
            # Fallback to Google if no results
            if not product_url:
                print("   🔄 DuckDuckGo search failed, trying Google as fallback...")
                product_url, amazon_site = search_google_and_get_amazon_url(full_Variant_name, browser)
            
            if product_url:
                print(f"   📦 Found on {amazon_site}")
                
                # Extract data from the product page
                product_data = scrape_product_data(product_url, browser)
                
                # Write row in correct column order
                row_data = {
                    "variant_id": Variant_id,
                    "variant_name": full_Variant_name,
                    "status": product_data["status"],
                    "asin": product_data["asin"],
                    "price": product_data["price"],
                    "launch_date": product_data["launch_date"],
                    "product_name": product_data["product_name"],
                    "product_condition": product_data["product_condition"],
                    "product_url": product_url
                }
            else:
                print(f"   ⚠️  Product URL not found on Google")
                
                row_data = {
                    "variant_id": Variant_id,
                    "variant_name": full_Variant_name,
                    "status": "URL Not Found",
                    "asin": "Not Found",
                    "price": "Not Found",
                    "launch_date": "Not Found",
                    "product_name": "Not Found",
                    "product_condition": "Not Found",
                    "product_url": "Not Found"
                }
            
            # Save to CSV with correct header and order
            result_df = pd.DataFrame([row_data], columns=columns)
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
                    "status": f"Error: {str(e)[:50]}",
                    "asin": "Error",
                    "price": "Error",
                    "launch_date": "Error",
                    "product_name": "Error",
                    "product_condition": "Error",
                    "product_url": "Error"
                }
                result_df = pd.DataFrame([error_row], columns=columns)
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
    print("  • Product Name")
    print("  • ASIN (Amazon Standard Identification Number)")
    print("  • Price (with currency)")
    print("  • Launch Date")
    print("  • Product URL")
    print("\nOutput: Excel file with all product data")
    print("="*80 + "\n")
    
    site_choice = "amazon.ae"  # Change this to "amazon.in" or "amazon.com" as needed
    
    if site_choice in SITE_CONFIG:
        search_and_scrape_data(site_choice)
    else:
        print("❌ Invalid choice. Please choose: amazon.ae, amazon.in, or amazon.com")