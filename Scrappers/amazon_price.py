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

from search_engines import search_duckduckgo_and_get_amazon_url
from search_engines import search_google_and_get_amazon_url

from config import ( STOP_WORDS,BRANDS, PENALTY_WORDS, COLOR_DICTIONARY, COLOR_SYNONYMS)


# ---------- CONFIG ----------
EXCEL_FILE = r"E:\R3 Factory\Selenium_Prodcut_Scrapper\relation_data.xlsx"  
SHEET_NAME = "Sheet1"       
OUTPUT_CSV = r"E:\R3 Factory\Selenium_Prodcut_Scrapper\Scrapper_Results\Price_Results_iphones_2.csv"
OUTPUT_EXCEL = "Price_Results_iphones_2.xlsx"
START_ROW = 2      
END_ROW = 305                 
MATCH_THRESHOLD=70  
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
GEO_KEYWORD = "Dubai"


# ---------- BROWSER SETUP ----------
def create_browser_with_anti_detection():
    """
    Creates an undetected Chrome browser with anti-detection measures enabled.
    This makes our scraper look like a real human browsing, not a bot. 
    """
    
    options = uc.ChromeOptions()
    
    # Window settings
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"user-agent={USER_AGENT}")
    # options.add_argument("--headless")  # Use new headless mode
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
    """Extract brand and model from variant name using first few words."""
    words = variant_name.lower().split()
    brand = None
    model = None

    # Find brand in first few words
    for word in words[:8]:
        if word in BRANDS:
            brand = word
            break

    # Remove brand, stopwords, and colors from words
    filtered = [
        w for w in words
        if w not in STOP_WORDS and w not in COLOR_DICTIONARY and (not brand or w != brand)
    ]

    # Model: first word (or two) after brand
    if filtered:
        model = filtered[0]
        # Optionally, use first two words if model names are often two words
        if len(filtered) > 1 and len(filtered[1]) > 1:
            model = f"{filtered[0]} {filtered[1]}"

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
    
    base_score = fuzz.token_set_ratio(variant_proc, title_proc) * 1.0
    
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
    
    # Only count meaningful words (at least 3 chars)
    meaningful_common = [w for w in common_words if len(w) >= 3]
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
    # Try main price selector
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
            whole = whole.replace('\xa0', '').strip()
        except:
            whole = "0"
        # Extract fractional part (the cents)
        try:
            fraction = price_container.find_element(By.CSS_SELECTOR, ".a-price-fraction").text
        except:
            fraction = "00"
        price = f"{currency} {whole}.{fraction}"
        print(f"      ✓ Found price: {price}")
        
        return price
    
    except Exception as e:
        # Fallback: Try twister_swatch_price
        try:
            price_container = browser.find_element(By.CSS_SELECTOR, "span.twister_swatch_price span.olpWrapper")
            price_text = price_container.text.strip()
            match = re.search(r"AED[\s\u00A0]*([\d,]+\.\d{2})", price_text)
            if match:
                price = f"AED {match.group(1)}"
                print(f"      ✓ Found price (fallback): {price}")
                return price
            else:
                print(f"      ✓ Found price (fallback, raw): {price_text}")
                return price_text
        except Exception as e2:
            print(f"      ✗ Price not found: {e2}")
            return "Currently Unavailable" if e2 else "Not Found"

def extract_product_name(browser):
    """Extract product name"""
    try:
        product_title = browser.find_element(By.ID, "productTitle")
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
        "Refurbished": ["refurbished", "reconditioned"],
        "Renewed": ["renewed", "certified pre-owned"],
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
            "button.a-button-text",
        ]
        
        for selector in button_selectors:
            try:
                if selector.startswith("//"):
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

# ---------- SCRAPING FUNCTIONS ----------
def scrape_price_from_url(product_url, browser):
    """
    Open product page and extract price
    """
    # Open in new tab
    browser.execute_script(f"window.open('{product_url}', '_blank');")
    WebDriverWait(browser, 5).until(lambda d: len(d.window_handles) > 1)
    browser.switch_to.window(browser.window_handles[-1])
    
    try:
        print(f"   📄 Opening product page...")
        browser.get(product_url)
        time.sleep(random.uniform(1,2))
        
        handle_amazon_popup(browser)
        
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "productTitle"))
        )
        
        print(f"   🔍 Extracting price...")
        
        product_name = extract_product_name(browser)
        product_condition=extract_product_condition(product_name, browser)
        price = extract_price(browser)
        
        if price == "Currently Unavailable":
            status = "Currently Unavailable"
        elif price != "Not Found":
            status = "Success"
        else:
            status = "Price Not Found"
    
        # Close product tab after scraping all images
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
            "product_condition":"Error",
            "price": "Error",
            "status": "Error",
            "product_url": product_url
        }

def search_amazon_ae_direct(search_term, browser, MATCH_THRESHOLD):
    """
    Search directly on Amazon.ae using search box
    """
    try: 
        print(f"   🔍 Searching Amazon.ae for: {search_term}")
        
        browser.get("https://www.amazon.ae")
        # time.sleep(random.uniform(2, 3))
        
        handle_amazon_popup(browser)
        
        # Find search box
        search_box = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
        )
        search_box.clear()
        
        time.sleep(random.uniform(1, 2))
        
        for char in search_term:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.02, 0.05))  # Random typing speed
        
        # time.sleep(random.uniform(0.5, 1.0))  # Pause before hitting enter
        
        # search_box.send_keys(search_term)

        # Click search button
        search_button = browser.find_element(By.ID, "nav-search-submit-button")
        search_button.click()
        
        # time.sleep(random.uniform(2, 3))
        
        # Wait for results
        WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@data-component-type='s-search-result']"))
        )
        
        search_results = browser.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")
        
        print(f"   📊 Found {len(search_results)} results")
        
        # Match products
        best_match_elem = None
        best_score = 0
        best_title = ""
        
        for result in search_results[:20]: 
            try:
                title_elem = result.find_element(By.CSS_SELECTOR, "div.a-section.a-spacing-none.a-spacing-top-small.s-title-instructions-style")
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
                link_elem = best_match_elem.find_element(By.TAG_NAME, "a")
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
        print(f"   ❌ Error searching Amazon.ae: {str(e)}")
        return None

# ---------- MAIN ORCHESTRATION ----------
def unified_search_and_scrape():
    """
    Main function:  3-tier search strategy with cascading variant names
    """
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
            variant_name = str(row['Variant Name']).strip() if 'Variant Name' in row else ""
            super_variant_name = str(row['Super Variant Name']).strip() if 'Super Variant Name' in row else ""
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
                        
            # Initialize result variables
            product_url = None
            product_name = "Not Found"
            product_condition = "Not Found"
            price = "Not Found"
            status = "Not Found"

            def is_price_valid(price_value):
                """Check if price is valid (not error/unavailable)"""
                invalid_states = ["Not Found", "Currently Unavailable", "Error", ""]
                return price_value not in invalid_states

            def try_search_cascade(search_func, search_terms, browser, **kwargs):
                """
                **kwargs: Additional arguments for search function      
                Returns:
                    product_url or None
                """
                for search_data in search_terms:
                    if len(search_data) == 2:
                        search_term, label = search_data
                        extra_args = {}
                    else:
                        search_term, label, extra_args = search_data
                    
                    # Skip invalid terms
                    if not search_term or search_term == "nan" or pd.isna(search_term):
                        continue
                    
                    print(f"\n   📍 Trying: {label}")
                    
                    try:
                        # Call search function with proper arguments
                        if extra_args:
                            result = search_func(search_term, browser, **extra_args, **kwargs)
                        else:
                            result = search_func(search_term, browser, **kwargs)
                        
                        # Handle different return types
                        if isinstance(result, tuple):
                            product_url, _ = result
                        else:
                            product_url = result
                        
                        if product_url: 
                            print(f"   ✅ Found URL: {product_url[: 60]}...")
                            return product_url
                        
                    except Exception as e:
                        print(f"   ⚠️ Search failed: {e}")
                    
                    time.sleep(random.uniform(1, 2))
                
                return None

            # Prepare search terms for cascade
            search_terms_basic = [
                (variant_name, "Variant Name"),
                (super_variant_name, "Super Variant Name") if super_variant_name != "nan" and not pd.isna(super_variant_name) else None,
                (model_name, "Model Name") if model_name != "nan" and not pd. isna(model_name) else None,
            ]

            search_terms_amazon_direct = [
                (variant_name, "Variant Name", {"match_threshold": 70}),
                (super_variant_name, "Super Variant Name", {"match_threshold": 65}) if super_variant_name != "nan" and not pd.isna(super_variant_name) else None,
                (model_name, "Model Name", {"match_threshold": 60}) if model_name != "nan" and not pd.isna(model_name) else None,
            ]

            # Filter out None values
            search_terms_basic = [t for t in search_terms_basic if t]
            search_terms_amazon_direct = [t for t in search_terms_amazon_direct if t]

            # ========================================
            # STRATEGY 1: DuckDuckGo Search
            # ========================================
            print(f"\n🎯 STRATEGY 1: DuckDuckGo Search")

            product_url = try_search_cascade(
                search_duckduckgo_and_get_amazon_url,
                search_terms_basic,
                browser
            )

            if product_url:
                print(f"\n   ✅ Found on DuckDuckGo!")
                result = scrape_price_from_url(product_url, browser)
                product_name = result["product_name"]
                product_condition = result["product_condition"]
                price = result["price"]
                status = result["status"]
                
                if is_price_valid(price):
                    print(f"   💰 Valid price found: {price}")
                else:
                    print(f"   ⚠️ URL found but price is:  {price}")
                    product_url = None  # Reset to trigger next strategy

            # ========================================
            # STRATEGY 2: Amazon.ae Direct Search
            # (Only if Strategy 1 failed or price invalid)
            # ========================================
            if not product_url or not is_price_valid(price):
                print(f"\n   ⚠️ Strategy 1 didn't find valid price - trying Strategy 2...")
                print(f"\n🎯 STRATEGY 2: Amazon.ae Direct Search")
                
                # Try cascade with different thresholds
                for search_name, label, extra in search_terms_amazon_direct: 
                    if not search_name: 
                        continue
                    
                    print(f"\n   📍 Trying: {label}")
                    
                    try:
                        product_url = search_amazon_ae_direct(
                            search_name,
                            browser,
                            extra["match_threshold"]
                        )
                        
                        if product_url: 
                            print(f"   ✅ Found on Amazon Direct!")
                            result = scrape_price_from_url(product_url, browser)
                            product_name = result["product_name"]
                            product_condition = result["product_condition"]
                            price = result["price"]
                            status = result["status"]
                            
                            if is_price_valid(price):
                                print(f"   💰 Valid price found:  {price}")
                                break  # Exit loop - success!
                            else:
                                print(f"   ⚠️ URL found but price is: {price}")
                                product_url = None  # Reset to try next term
                    
                    except Exception as e: 
                        print(f"   ⚠️ Search failed: {e}")
                    
                    time.sleep(random.uniform(2, 3))

            # ========================================
            # STRATEGY 3: Google Search
            # (Only if Strategy 2 also failed or price invalid)
            # ========================================
            if not product_url or not is_price_valid(price):
                print(f"\n   ⚠️ Strategy 2 didn't find valid price - trying Strategy 3...")
                print(f"\n🎯 STRATEGY 3: Google Search")
                
                product_url = try_search_cascade(
                    search_google_and_get_amazon_url,
                    search_terms_basic,
                    browser
                )
                
                if product_url: 
                    print(f"\n   ✅ Found on Google!")
                    result = scrape_price_from_url(product_url, browser)
                    product_name = result["product_name"]
                    product_condition = result["product_condition"]
                    price = result["price"]
                    status = result["status"]
                    
                    if is_price_valid(price):
                        print(f"   💰 Valid price found: {price}")
                    else:
                        print(f"   ⚠️ URL found but price is:  {price}")

            # ========================================
            # FINAL STATUS DETERMINATION
            # ========================================
            if is_price_valid(price):
                print(f"\n   🎉 SUCCESS - Price: {price}")
                status = "Success"
            else:
                print(f"\n   ❌ All strategies exhausted")
                
                # Set appropriate status based on what we found
                if price == "Currently Unavailable":
                    status = "Currently Unavailable"
                elif product_name != "Not Found":
                    status = "Price Not Found"  # Found product but no price
                else:
                    status = "Not Found"  # Product not found at all

            print(f"\n   📊 Final Status: {status}")
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
    print("🌐 UNIFIED AMAZON.AE PRICE SCRAPER")
    print("="*80)
    print("\n🎯 Search Strategy:")
    print("   1. Amazon.ae Direct Search (Variant → Super Variant → Model)")
    print("   2. DuckDuckGo Search (Variant → Super Variant → Model)")
    print("   3. Google Search (Variant → Super Variant → Model)")
    print("\n📊 Output: Price in AED only")
    print("="*80 + "\n")
    
    unified_search_and_scrape()