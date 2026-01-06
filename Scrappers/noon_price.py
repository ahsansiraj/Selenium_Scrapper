import os
import re
import time
import random
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from rapidfuzz import fuzz

from search_engines import search_duckduckgo_and_get_noon_url
from search_engines import search_google_and_get_noon_url

# ---------- MATCHING CONFIGURATION ----------
from config import ( STOP_WORDS,BRANDS, PENALTY_WORDS, OUTPUT_EXCEL , COLOR_DICTIONARY, COLOR_SYNONYMS,MODEL_KEYWORDS)

# ---------- CONFIG ----------
EXCEL_FILE = r"E:\R3 Factory\Selenium_Prodcut_Scrapper\noontest.xlsx"  
SHEET_NAME = "Sheet1"       
OUTPUT_CSV = r"E:\R3 Factory\Selenium_Prodcut_Scrapper\Scrapper_Results\Price_Results_noon_text.csv"
OUTPUT_EXCEL = "Price_Results_noon_text.xlsx"
START_ROW = 2      
END_ROW = 3342                 
MATCH_THRESHOLD=75 
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
GEO_KEYWORD = "Dubai"


# ---------- BROWSER SETUP ----------
def create_browser_with_anti_detection():
    """
    Creates an undetected Chrome browser with anti-detection measures enabled.
    This makes our scraper look like a real human browsing, not a bot. 
    """
    
    # Clean up old chromedriver files to prevent FileExistsError
    try:
        import shutil
        uc_path = os.path.join(os.getenv('APPDATA'), 'undetected_chromedriver')
        if os.path.exists(uc_path):
            print(f"   🧹 Cleaning up old chromedriver files...")
            shutil.rmtree(uc_path, ignore_errors=True)
            time.sleep(1)  # Give OS time to release file handles
    except Exception as e:
        print(f"   ⚠️  Could not clean up old files: {e}")
    
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
        browser = uc.Chrome(
            options=options,
            use_subprocess=True,  # More stable
            version_main=143,  # Uncomment and set your Chrome version if needed
        )
        
        
        # Additional stealth scripts (optional, but helpful)
        browser.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": USER_AGENT
        })
        
        # Set navigator properties to appear more human
        browser.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
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

# ---------- MATCHING LOGIC ----------
def preprocess_text(text):
    """Normalize text for matching"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)      # Normalize spaces
    return ' '.join([word for word in text.split() if word not in STOP_WORDS])

def extract_storage(title):
    """Extract storage capacity"""
    match = re.search(r'(\d+)\s?(gb|tb|mb)', title, re.IGNORECASE)
    return match.group(0).lower().replace(' ', '') if match else None

def extract_brand_and_model(variant_name):
    """Extract brand and model from variant name"""
    words = variant_name.lower().split()
    brand = None
    model = None
    
    # Find brand
    for word in words[:5]:
        if word in BRANDS:
            brand = word
            break
    
    # Find model number
    for i, word in enumerate(words):
        if len(word) >= 4 and any(char.isdigit() for char in word) and any(char.isalpha() for char in word):
            if i > 0 and words[i-1] in MODEL_KEYWORDS:
                model = word
                break
            elif not any(char.isspace() for char in word):
                model = word
                break
    
    return brand, model

def extract_colors(text):
    """Extract color names from text"""
    text_lower = text.lower()
    colors_found = set()
    
    # Check for exact color
    for color in COLOR_DICTIONARY:
        if re.search(r'\b' + re.escape(color) + r'\b', text_lower):
            colors_found.add(color)
    
    return colors_found

def calculate_color_match_score(variant, product_title):
    """ Calculate color matching score (0 to 15 points max) """
    variant_colors = extract_colors(variant)
    title_colors = extract_colors(product_title)
    
    if not variant_colors:
        return 0
    
    if not title_colors:
        return -5
    
    score = 0
    matched = False
    
    for variant_color in variant_colors: 
        if variant_color in title_colors: 
            score += 10  
            matched = True
            break
    
    # Check for color synonyms
    if not matched:
        for variant_color in variant_colors: 
            for title_color in title_colors:
                if variant_color in COLOR_SYNONYMS: 
                    if title_color in COLOR_SYNONYMS[variant_color]:
                        score += 8  
                        matched = True
                        break
                # Check reverse synonyms
                if title_color in COLOR_SYNONYMS: 
                    if variant_color in COLOR_SYNONYMS[title_color]:
                        score += 8  
                        matched = True
                        break
            if matched:
                break
    
    if not matched:
        score -= 10
    
    return score

def calculate_match_score(variant, product_title):
    """
    Enhanced matching algorithm - NORMALIZED to 0-100 scale
    Total possible: ~100 points
    """
    
    variant_proc = preprocess_text(variant)
    title_proc = preprocess_text(product_title)
    title_lower = product_title.lower()
    variant_lower = variant.lower()
    
    base_score = fuzz.token_set_ratio(variant_proc, title_proc) * 0.75
    
    # 2. STORAGE CAPACITY MATCH (0-15 points)
    variant_cap = extract_storage(variant)
    title_cap = extract_storage(product_title)
    
    if variant_cap and title_cap: 
        if variant_cap == title_cap:
            storage_score = 20  
        else: 
            storage_score = -15  
    elif variant_cap and not title_cap:
        storage_score = -5  
    else:
        storage_score = 0  
    
    # 3. BRAND MATCH (0-15 points)
    variant_brand, variant_model = extract_brand_and_model(variant)
    brand_score = 0
    
    if variant_brand:
        if variant_brand in title_lower:
            brand_score = 20  
        else:
            competing_brands = BRANDS - {variant_brand}
            if any(brand in title_lower for brand in competing_brands):
                brand_score = -20  
            else:
                brand_score = -5  
    
    # 4. MODEL NUMBER MATCH (0-15 points)
    model_score = 0
    if variant_model:
        if variant_model in title_lower: 
            model_score = 15  
        else:
            if len(variant_model) >= 4: 
                model_score = -10  
    
    # 5. COLOR MATCH (-10 to +10 points)
    color_score = calculate_color_match_score(variant, product_title)
    
    # 6. KEYWORD OVERLAP BONUS (0-5 points)
    variant_words = set(variant_proc.split())
    title_words = set(title_proc.split())
    common_words = variant_words & title_words
    
    # Only count meaningful words (at least 5 chars)
    meaningful_common = [w for w in common_words if len(w) >= 5]
    keyword_bonus = min(len(meaningful_common), 5)  # Max 5 points 
    
    # 7. ACCESSORY PENALTY (-20 points)
    penalty = 0
    if any(word in title_lower for word in PENALTY_WORDS):
        penalty = -20  # Strong penalty for accessories
    
    # 8. REFURBISHED DETECTION (informational, no penalty for now)
    if any(keyword in title_lower for keyword in ['refurbished', 'renewed', 'pre-owned', 'like new']):
        pass      

    # CALCULATE FINAL SCORE
    final_score = (
        base_score +         # 0-50
        storage_score +      # -15 to +15
        brand_score +        # -20 to +15
        model_score +        # -10 to +15
        color_score +        # -10 to +10
        keyword_bonus +      # 0-5
        penalty              # -20 to 0
    )
    
    final_score = max(0, min(100, final_score))
    
    return final_score
# ---------- PRICE EXTRACTION ----------
def extract_price(browser):
    """ Extract price from the product page. LIKE "AED 2,611.45"  """
    
    for selector in ["div.PriceOfferV2-module-scss-module__dHtRPW__priceNowCtr.PriceOfferV2-module-scss-module__dHtRPW__isCurrencySymbol",
                     "div.PriceOfferV2-module-scss-module__dHtRPW__priceNowCtr"]:
        try:
            price_container = browser.find_element(By.CSS_SELECTOR, selector)
            
            # Try to extract the price text
            try:
                whole = price_container.find_element(By.CSS_SELECTOR, "span.PriceOfferV2-module-scss-module__dHtRPW__priceNowText").text
                whole = whole.replace('\xa0', '').strip()
            except:
                whole = "0"
            
            price = f"AED {whole}"
            print(f"      ✓ Found price: {price}")
            return price
            
        except:
            # This selector didn't work, try the next one
            continue
    
    # If we've tried all selectors and none worked
    print(f"      ✗ Price not found - all selectors failed")
    return "Not Found"
        
def extract_product_name(browser):
    """Extract product name"""
    try:
        product_title = browser.find_element(By.CLASS_NAME, "ProductTitle-module-scss-module__EXiEUa__title")
        name = product_title.text.strip()
        if name:
            print(f"      ✓ Found product name: {name[: 60]}...")
            return name
    except:
        pass
    
    print(f"      ✗ Product name not found")
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

    print(f"  Product condition assumed: New (no indicators found)")
    return "New"

# ---------- SCRAPING FUNCTIONS ----------
def scrape_price_from_url(product_url, browser):
    """
    Open product page and extract price
    """
    try:
        print(f"   📄 Opening product page...")
        
        # Open in new tab
        browser.execute_script(f"window.open('{product_url}', '_blank');")
        WebDriverWait(browser, 5).until(lambda d: len(d.window_handles) > 1)
        browser.switch_to.window(browser.window_handles[-1])
        
        time.sleep(random.uniform(2, 3))
        
        
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ProductTitle-module-scss-module__EXiEUa__title"))
        )
        
        print(f"   🔍 Extracting price...")
        
        product_name = extract_product_name(browser)
        product_condition=extract_product_condition(product_name, browser)
        price = extract_price(browser)
        
        if price == "Currently Unavailable":
            status = "Currently Unavailable"
        elif price == "Not Found":
            status = "Price Not Found"
        else:
            status = "Success"
        
        # Close product tab
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
        
        return {
            "product_name":  product_name,
            "product_condition":product_condition,
            "price": price,
            "status":  status,
            "product_url": product_url
        }
        
    except Exception as e:
        print(f"   ❌ Error scraping price: {str(e)}")
        try:
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
        except:
            pass
        return {
            "product_name": "Error",
            "price": "Error",
            "status": "Error"
        }

def search_noon_ae_direct(search_term, browser, MATCH_THRESHOLD):
    """
    Search directly on Noon.ae using search box
    """
    try: 
        print(f"   🔍 Searching Noon.ae for: {search_term}")
        
        browser.get("https://www.noon.com/uae-en/")
        
        time.sleep(random.uniform(2, 3))
        
        # Find search box
        search_box = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "search-input"))
        )
        search_box.clear()
        
        time.sleep(random.uniform(2, 3))
        
        for char in search_term:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.02, 0.05))  # Random typing speed
        
        # time.sleep(random.uniform(0.5, 1.5))  # Pause before hitting enter
        
        # search_box.send_keys(search_term)
        search_box.send_keys(Keys.ENTER)

        # # Click search button
        # search_button = browser.find_element(By.ID, "nav-search-submit-button")
        # search_button.click()
        
        # time.sleep(random.uniform(2, 3))
        
        # Wait for results
        WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-qa='plp-product-box']"))
        )
        
        search_results = browser.find_elements(By.CSS_SELECTOR, "div[data-qa='plp-product-box']")
        
        print(f"   📊 Found {len(search_results)} results")
        
        # Match products
        best_match_elem = None
        best_score = 0
        best_title = ""
        
        for result in search_results[:20]: 
            try:
                title_elem = result.find_element(By.CSS_SELECTOR, "h2[data-qa='plp-product-box-name']")
                title_text = title_elem.text.strip()
                
                score = calculate_match_score(search_term, title_text)
                
                if score > best_score:
                    best_score = score
                    best_match_elem = result
                    best_title = title_text
                    
            except:
                continue
        
        print(f"   🎯 Best match score: {best_score} (Threshold: {MATCH_THRESHOLD})")
        
        if best_match_elem and best_score >= MATCH_THRESHOLD: 
            try:
                link_elem = best_match_elem.find_element(By.CSS_SELECTOR, "a.PBoxLinkHandler-module-scss-module__WvRpgq__productBoxLink")
                product_url = link_elem.get_attribute("href")
                
                print(f"   ✅ Found matching product: {best_title[: 60]}...")
                return product_url
                
            except Exception as e:
                print(f"   ⚠️ Error extracting URL: {e}")
                return None
        else:
            print(f"   ⚠️ No match found above threshold")
            return None
        
    except Exception as e: 
        print(f"   ❌ Error searching Noon.ae: {str(e)}")
        return None

# ---------- MAIN ORCHESTRATION ----------
def unified_search_and_scrape():
    """ Main function:  3-tier search strategy with cascading variant names """
    total_start_time = time.time()
    
    print(f"\n{'='*80}")
    print(f"🚀 UNIFIED PRICE SCRAPER - Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    # Read Excel
    try:
        full_df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
        full_df = full_df.iloc[START_ROW-2: END_ROW]
        print(f"📊 Loaded {len(full_df)} products from Excel\n")
    except Exception as e:
        print(f"❌ Error reading Excel: {e}")
        return
    
    # Check for existing progress
    if os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0:
        try:
            processed_df = pd.read_csv(OUTPUT_CSV, skipinitialspace=True)
            processed_df.columns = [col.strip() for col in processed_df.columns]  # <-- Add this line
            processed_ids = set(processed_df['variant_id'].astype(str))
            df_to_process = full_df[~full_df['Variant ID'].astype(str).isin(processed_ids)]
            
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
        convert_csv_to_excel(OUTPUT_CSV)
        return
    
    # Column order
    columns = [
        "variant_id",
        "variant_name",
        "super_variant_name",
        "model_name",
        "price",
        "status",
        "product_name",
        "product_condition",
        "product_url"
    ]
    
    file_exists = os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0
    search_count = 0
    batch_number = 0
    browser = create_browser_with_anti_detection()
    
    processed_count = 0
    
    for index , row in df_to_process.iterrows():
        product_start_time = time.time()
        search_count += 1
        
        try:
            variant_id = str(row['Variant ID']).strip()
            variant_name = str(row['Variant Name']).strip()
            super_variant_name = str(row['Super Variant Name']).strip()
            model_name = str(row['Model Name']).strip()
            
            if not variant_id:
                continue
            
            processed_count += 1
            
            # Browser refresh cycle
            if search_count % 15 == 0:
                print(f"\n{'='*80}")
                print(f"🔄 BROWSER REFRESH: Search count reached {search_count}")
                print(f"{'='*80}")
                
                print("   🔒 Closing browser...")
                try:
                    browser.quit()
                except:
                    pass
                
                wait_time = random.randint(120, 180)
                print(f"   ⏸️ Cooling down for {wait_time // 60}m {wait_time % 60}s...")
                time.sleep(wait_time)
                
                batch_number += 1
                print(f"\n   🆕 Creating new browser (Batch #{batch_number})...")
                browser = create_browser_with_anti_detection()
                print(f"{'='*80}\n")
            
            print(f"{'='*80}")
            print(f"🔎 Product {processed_count}/{len(df_to_process)}")
            print(f"🆔 Variant ID: {variant_id}")
            print(f"📝 Variant Name: {variant_name}")
            print(f"📊 Search Count: {search_count}")
            print(f"{'='*80}")
            
            product_url = None
            product_name = "Not Found"
            product_condition="Not Found"
            price = "Not Found"
            status = "Not Found"
            
            # time.sleep(random.uniform(2,3))
            # ===== STRATEGY 1: Noon.ae Direct Search =====
            print(f"\n🎯 STRATEGY 1: Noon.ae Direct Search")
            
            # Try Variant Name
            print(f"\n   📍 Trying: Variant Name")
            
            for search_name, threshold in [
                (variant_name, 70),
                (super_variant_name, 65) ,
                (model_name, 60)
            ]:
                if not search_name:
                    continue
                
                print(f"\n   📍 Trying:  {search_name[:40]}...")
                product_url = search_noon_ae_direct(search_name, browser, threshold)
                
                if product_url:
                    break
                
                # Small delay between cascades
                time.sleep(random.uniform(2, 3))

            # Scrape price if found
            if product_url: 
                print(f"\n   ✅ Found on Noon.ae Direct Search!")
                result = scrape_price_from_url(product_url, browser)
                product_name = result["product_name"]
                product_condition=result["product_condition"]
                price = result["price"]
                status = result["status"]
            else:
                print(f"\n   ⚠️ Strategy 1 failed - trying Strategy 2...")
                
                # ===== STRATEGY 2: DuckDuckGo Search =====
                print(f"\n🎯 STRATEGY 2: DuckDuckGo Search")
                
                # Try Variant Name
                print(f"\n   📍 Trying:  Variant Name")
                product_url, _ = search_duckduckgo_and_get_noon_url(variant_name, browser)
                
                time.sleep(random.uniform(1,2))
            
                # Try Super Variant Name if failed
                if not product_url and super_variant_name: 
                    print(f"\n   📍 Trying: Super Variant Name")
                    product_url, _ = search_duckduckgo_and_get_noon_url(super_variant_name, browser)
                    
                time.sleep(random.uniform(1,2))
                
                # Try Model Name if failed
                if not product_url and model_name:
                    print(f"\n   📍 Trying: Model Name")
                    product_url, _ = search_duckduckgo_and_get_noon_url(model_name, browser)
                
                # Scrape price if found
                if product_url:
                    print(f"\n   ✅ Found on DuckDuckGo!")
                    result = scrape_price_from_url(product_url, browser)
                    product_name = result["product_name"]
                    product_condition=result["product_condition"]
                    price = result["price"]
                    status = result["status"]
                else:
                    print(f"\n   ⚠️ Strategy 2 failed - trying Strategy 3...")
                    
                    # ===== STRATEGY 3: Google Search =====
                    print(f"\n🎯 STRATEGY 3: Google Search")
                    
                    # Try Variant Name
                    print(f"\n   📍 Trying: Variant Name")
                    product_url, _ = search_google_and_get_noon_url(variant_name, browser)

                    time.sleep(random.uniform(1,2))
                    
                    # Try Super Variant Name if failed
                    if not product_url and super_variant_name:
                        print(f"\n   📍 Trying: Super Variant Name")
                        product_url, _ = search_google_and_get_noon_url(super_variant_name, browser)

                    time.sleep(random.uniform(1,2))
                    
                    # Try Model Name if failed
                    if not product_url and model_name:
                        print(f"\n   📍 Trying: Model Name")
                        product_url, _ = search_google_and_get_noon_url(model_name, browser)
                    
                    # Scrape price if found
                    if product_url:
                        print(f"\n   ✅ Found on Google!")
                        result = scrape_price_from_url(product_url, browser)
                        product_name = result["product_name"]
                        product_condition=result["product_condition"]
                        price = result["price"]
                        status = result["status"]
                    else: 
                        print(f"\n   ❌ All strategies failed - product not found")
                        status = "Not Found"
            
            # Save result
            row_data = {
                "variant_id": variant_id,
                "variant_name": variant_name,
                "super_variant_name": super_variant_name,
                "model_name": model_name,
                "price": price,
                "status": status,
                "product_name": product_name,
                "product_condition":product_condition,
                "product_url":  product_url if product_url else "Not Found"
            }

            result_df = pd.DataFrame([row_data], columns=columns)
            result_df.to_csv(OUTPUT_CSV, mode='a', header=not file_exists, index=False)
            file_exists = True
            
            product_time = time.time() - product_start_time
            print(f"\n   ⏱️ Product processed in {product_time:.2f}s")
            print(f"   📊 Status: {status}")
            
            wait_time = random.randint(4, 7)
            print(f"   ⏳ Waiting {wait_time} seconds.. .\n")
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"   ❌ Error processing product: {str(e)}")
            import traceback
            traceback.print_exc()
            
            try:
                error_row = {
                    "variant_id": variant_id,
                    "variant_name": variant_name,
                    "super_variant_name": super_variant_name if 'super_variant_name' in locals() else "",
                    "model_name": model_name if 'model_name' in locals() else "",
                    "price": "Error",
                    "status": "Error",
                    "product_name": "Error",
                    "product_condition": "Error",
                    "product_url": "Error"
                }
                result_df = pd.DataFrame([error_row], columns=columns)
                result_df.to_csv(OUTPUT_CSV, mode='a', header=not file_exists, index=False)
                file_exists = True
            except: 
                pass
            continue
    
    # Close browser
    try:
        browser.quit()
    except:
        pass
    
    # Convert to Excel
    convert_csv_to_excel(OUTPUT_CSV)
    
    elapsed = time.time() - total_start_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    
    print(f"\n{'='*80}")
    print(f"🏁 Scraping completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️ Total time: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
    print(f"📊 Total searches: {search_count}")
    print(f"📊 Total products: {processed_count}")
    print(f"{'='*80}\n")

def convert_csv_to_excel(OUTPUT_CSV):
    """Convert CSV to Excel"""
    print(f"\n{'='*80}")
    print(f"📊 Converting to Excel format...")
    
    try:
        csv_df = pd.read_csv(OUTPUT_CSV)
        
        with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
            csv_df.to_excel(writer, sheet_name='Price Results', index=False)
            
            from openpyxl.utils import get_column_letter
            worksheet = writer.sheets['Price Results']
            
            for idx, col in enumerate(csv_df.columns, 1):
                max_length = max(csv_df[col].astype(str).map(len).max(), len(col))
                worksheet.column_dimensions[get_column_letter(idx)].width = min(max_length + 2, 50)
        
        print(f"✅ Excel file created: {OUTPUT_EXCEL}")
        print(f"📊 Total products: {len(csv_df)}")
        
        # Print summary statistics
        if 'status' in csv_df.columns:
            print(f"\n📈 Summary Statistics:")
            print(csv_df['status'].value_counts())
        
    except Exception as e: 
        print(f"⚠️ Could not create Excel:  {e}")
        import traceback
        traceback.print_exc()

# ---------- MAIN ENTRY POINT ----------
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🌐 UNIFIED NOON.AE PRICE SCRAPER")
    print("="*80)
    print("\n🎯 Search Strategy:")
    print("   1. Noon.ae Direct Search (Variant → Super Variant → Model)")
    print("   2. DuckDuckGo Search (Variant → Super Variant → Model)")
    print("   3. Google Search (Variant → Super Variant → Model)")
    print("\n📊 Output: Price in AED only")
    print("="*80 + "\n")
    
    unified_search_and_scrape()