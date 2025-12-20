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

# ---------- CONFIG ----------
EXCEL_FILE = "relation_data.xlsx"  # UPDATE THIS PATH
SHEET_NAME = "relation_data"                   # UPDATE THIS SHEET NAME
OUTPUT_CSV = "Price_Results.csv"
OUTPUT_EXCEL = "Price_Results.xlsx"
START_ROW = 2      # UPDATE THIS
END_ROW = 3000       # UPDATE THIS
FOLDER_PATH = r"E:\R3 Factory\Selenium_Prodcut_Scrapper\Scrapper_Results"
            
MATCH_THRESHOLD=80
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
GEO_KEYWORD = "Dubai"

# Matching configuration
STOP_WORDS = {'the', 'a', 'an', 'and', 'or', 'in', 'with', 'for', 'of', 'to', 
              'on', 'by', 'as', 'at', 'from', 'version', 'international', 'gb', 
              'single', 'sim', 'unlocked', 'renewed', 'refurbished' ,'+'}

PENALTY_WORDS = {'case', 'cover', 'protector', 'accessory', 'skin', 'sticker', 
                 'film', 'adapter', 'charger', 'cable', 'stand', 'holder', 
                 'mount', 'grip', 'ring', 'glass', 'shield', 'sleeve', 'pouch', 
                 'bag', 'box', 'holster', 'battery', 'dock', 'keyboard'}

BRANDS = {'xiaomi', 'samsung', 'apple', 'dell', 'hp', 'lenovo', 'lg', 'asus', 
          'acer', 'msi', 'huawei', 'nova', 'oppo', 'vivo', 'realme', 'oneplus'}

MODEL_KEYWORDS = {'model', 'item', 'part', 'sku', 'pn', 'id', 'art', 'ref'}

COLOR_DICTIONARY = {
    # Black family
    'black', 'jet black', 'onyx', 'midnight', 'phantom black', 'carbon black', 
    'obsidian', 'space black', 'cosmic black', 'stellar black', 'graphite',
    'charcoal', 'ebony', 'raven',
    
    # White family
    'white', 'pearl white', 'alpine white', 'glacier white', 'ceramic white',
    'ivory', 'snow white', 'chalk white', 'silver', 'platinum', 'metallic silver',
    'stainless steel', 'chrome', 'frost white',
    
    # Blue family
    'blue', 'sapphire blue', 'ocean blue', 'navy blue', 'cobalt blue', 
    'arctic blue', 'sky blue', 'baby blue', 'azure', 'ice blue', 'midnight blue',
    'royal blue', 'deep blue', 'pacific blue',
    
    # Red family
    'red', 'crimson red', 'ruby red', 'scarlet', 'vermillion', 'rose red',
    'product red', 'coral red', 'fiery red', 'burgundy',
    
    # Green family
    'green', 'forest green', 'emerald green', 'olive green', 'mint green',
    'alpine green', 'hunter green', 'army green', 'sage green', 'lime green',
    'pine green',
    
    # Gold family
    'gold', 'rose gold', 'champagne gold', 'sunset gold', 'pink gold',
    'blush gold', 'yellow gold', 'starlight gold',
    
    # Purple family
    'purple', 'lavender', 'violet', 'orchid', 'lilac', 'amethyst',
    'deep purple', 'royal purple', 'eggplant', 'plum', 'mauve',
    
    # Gray family
    'gray', 'grey', 'graphite', 'charcoal', 'slate', 'steel gray',
    'space gray', 'space grey', 'metallic gray', 'titanium', 'ash gray',
    
    # Brown family
    'brown', 'espresso brown', 'chocolate brown', 'cognac', 'tan', 'taupe',
    
    # Pink family
    'pink', 'blush pink', 'rose pink', 'coral pink', 'hot pink', 'magenta',
    
    # Orange family
    'orange', 'sunset orange', 'coral orange', 'tangerine', 'amber',
    
    # Yellow family
    'yellow', 'sunflower yellow', 'golden yellow', 'lemon yellow',
    
    # Multi-color
    'rainbow', 'multicolor', 'prism', 'gradient',
    
    # Special editions
    'starlight', 'sunlight', 'moonlight', 'aurora', 'northern lights'
}

# ---------- BROWSER SETUP ----------
def create_browser_with_anti_detection():
    """Create undetected Chrome browser"""
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"user-agent={USER_AGENT}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--max_old_space_size=4096")
    options.add_argument("--js-flags=--max-old-space-size=4096")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.images": 1,
    }
    options.add_experimental_option("prefs", prefs)
    
    try:
        browser = uc.Chrome(options=options, use_subprocess=True, version_main=142)
        
        browser.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": USER_AGENT
        })
        
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
            window.chrome = { runtime: {} };
        """)
        
        return browser
        
    except Exception as e: 
        print(f"   ❌ Error creating browser:  {e}")
        raise

# ---------- MATCHING LOGIC ----------
def preprocess_text(text):
    """Normalize text for matching"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+gb', '', text)
    return ' '.join([word for word in text.split() if word not in STOP_WORDS])

def extract_storage(title):
    """Extract storage capacity"""
    match = re.search(r'(\d+)\s?(gb|tb|mb)', title, re.IGNORECASE)
    return match.group(0).lower() if match else None

def extract_brand_and_model(variant_name):
    """Extract brand and model from variant name"""
    words = variant_name.lower().split()
    brand = None
    model = None
    
    # Find brand in first 3 words
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
    """Extract color names"""
    text_lower = text.lower()
    colors_found = set()
    
    for color in COLOR_DICTIONARY:
        if color in text_lower: 
            colors_found.add(color)
    
    return colors_found

def calculate_color_match_score(variant, product_title):
    """Calculate color matching score with enhanced precision"""
    variant_colors = extract_colors(variant)
    title_colors = extract_colors(product_title)
    
    if not variant_colors:
        return 0
    
    if not title_colors:
        return -15  # Penalty if product title has no color when variant specifies one
    
    score = 0
    
    # Check for exact matches with position bonus
    variant_words = variant.lower().split()
    title_words = product_title.lower().split()
    
    for color in variant_colors:
        # Strong bonus for exact match
        if color in title_colors:
            score += 25
            
            # Additional bonus if color appears in same relative position
            try:
                variant_color_pos = next(i for i, word in enumerate(variant_words) if color in word)
                title_color_pos = next(i for i, word in enumerate(title_words) if color in word)
                
                # More bonus if color position is similar
                position_diff = abs(variant_color_pos/len(variant_words) - title_color_pos/len(title_words))
                if position_diff < 0.3:  # If color appears in similar relative position
                    score += 10
            except:
                pass
                
        # Check for color synonyms with lower score
        else:
            for main_color, variations in COLOR_DICTIONARY.items():
                if color in variations and any(var in title_colors for var in variations):
                    score += 15
                    break
    
    # Penalty for mismatched colors
    title_only_colors = title_colors - variant_colors
    if title_only_colors and not any(c in str(title_only_colors) for c in variant_colors):
        score -= 15
        
    return score
    
    # Check for color synonyms and variations
    color_synonyms = {
        # Black variations
        'black': {'jet black', 'onyx', 'midnight', 'phantom black', 'carbon black', 'obsidian'},
        'space black': {'space gray', 'cosmic black', 'stellar black'},
        'midnight': {'night', 'noir', 'phantom black'},
        
        # White variations  
        'white': {'pearl white', 'alpine white', 'glacier white', 'ceramic white', 'ivory'},
        'silver': {'platinum silver', 'metallic silver', 'stainless steel', 'chrome'},
        
        # Blue variations
        'blue': {'sapphire blue', 'ocean blue', 'navy blue', 'cobalt blue', 'arctic blue'},
        'sky blue': {'baby blue', 'azure', 'ice blue'},
        'midnight blue': {'navy', 'deep blue', 'royal blue'},
        
        # Red variations
        'red': {'crimson red', 'ruby red', 'scarlet', 'vermillion', 'rose red'},
        'product red': {'red', '(red)'},
        
        # Green variations
        'green': {'forest green', 'emerald green', 'olive green', 'mint green'},
        'alpine green': {'forest green', 'hunter green', 'army green'},
        
        # Gold variations
        'gold': {'rose gold', 'champagne gold', 'sunset gold', 'pink gold'},
        'rose gold': {'pink gold', 'blush gold'},
        
        # Purple variations
        'purple': {'lavender', 'violet', 'orchid', 'lilac', 'amethyst'},
        'deep purple': {'royal purple', 'eggplant', 'plum'},
        
        # Gray variations
        'gray': {'grey', 'graphite', 'charcoal', 'slate', 'steel gray'},
        'space gray': {'space grey', 'metallic gray', 'titanium gray'},
    }
    
    # Check for color synonyms
    for variant_color in variant_colors:
        for title_color in title_colors:
            # Check if colors are synonyms
            if (variant_color in color_synonyms and title_color in color_synonyms[variant_color]) or \
               (title_color in color_synonyms and variant_color in color_synonyms[title_color]):
                return 15  # Moderate bonus for synonym match
    
    return -10  # Penalty for color mismatch

def calculate_match_score(variant, product_title):
    
    """Enhanced matching algorithm"""
    variant_proc = preprocess_text(variant)
    title_proc = preprocess_text(product_title)
    title_lower = product_title.lower()
    
    base_score = fuzz.token_set_ratio(variant_proc, title_proc)
    
    variant_words = set(variant_proc.split())
    title_words = set(title_proc.split())
    keyword_bonus = len(variant_words & title_words) * 5
    
    variant_cap = extract_storage(variant)
    title_cap = extract_storage(product_title)
    capacity_bonus = 20 if variant_cap and title_cap and variant_cap == title_cap else 0
    
    brand_score = 0
    variant_brand, variant_model = extract_brand_and_model(variant)
    
    if variant_brand: 
        if variant_brand in title_lower:
            brand_score += 30
        competing_brands = BRANDS - {variant_brand}
        if any(brand in title_lower for brand in competing_brands):
            brand_score -= 40
    
    model_score = 0
    if variant_model and variant_model in title_lower: 
        model_score += 50
    
    color_bonus = calculate_color_match_score(variant, product_title)
    
    penalty = -20 if any(word in title_lower for word in PENALTY_WORDS) else 0
    
    return base_score + keyword_bonus + capacity_bonus + brand_score + model_score + penalty + color_bonus

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

# ---------- PRICE EXTRACTION ----------

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

# ---------- SCRAPING FUNCTIONS ----------
def scrape_price_from_url(product_url, browser):
    """
    Open product page and extract price
    """
    try:
        print(f"   📄 Opening product page...")
        browser.get(product_url)
        time.sleep(random.uniform(2, 4))
        
        handle_amazon_popup(browser)
        
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "productTitle"))
        )
        
        print(f"   🔍 Extracting price...")
        
        product_name = extract_product_name(browser)
        price = extract_price(browser)
        
        if price == "Currently Unavailable":
            status = "Currently Unavailable"
        elif price != "Not Found":
            status = "Success"
        else:
            status = "Price Not Found"
        
        return {
            "product_name":  product_name,
            "price": price,
            "status":  status,
            "product_url": product_url
        }
        
    except Exception as e:
        print(f"   ❌ Error scraping price: {str(e)}")
        return {
            "product_name": "Error",
            "price": "Error",
            "status": "Error",
            "product_url": product_url
        }

def search_amazon_ae_direct(search_term, browser, MATCH_THRESHOLD):
    """
    Search directly on Amazon. ae using search box
    """
    try: 
        print(f"   🔍 Searching Amazon.ae for: {search_term}")
        
        browser.get("https://www.amazon.ae")
        time.sleep(random.uniform(2, 3))
        
        handle_amazon_popup(browser)
        
        # Find search box
        search_box = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
        )
        search_box.clear()
        
        search_box.send_keys(search_term)

        # Click search button
        search_button = browser.find_element(By.ID, "nav-search-submit-button")
        search_button. click()
        
        time.sleep(random.uniform(2, 3))
        
        # Wait for results
        WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By. XPATH, "//div[@data-component-type='s-search-result']"))
        )
        
        search_results = browser.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")
        
        print(f"   📊 Found {len(search_results)} results")
        
        # Match products
        best_match_elem = None
        best_score = 0
        best_title = ""
        
        for result in search_results[:20]: 
            try:
                title_elem = result.find_element(By.CSS_SELECTOR, "h2.a-size-base-plus.a-spacing-none.a-color-base.a-text-normal span")
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
                link_elem = best_match_elem. find_element(By.TAG_NAME, "a")
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
            processed_df = pd.read_csv(OUTPUT_CSV)
            processed_df. columns = [col.strip() for col in processed_df. columns]
            processed_ids = set(processed_df['variant_id']. astype(str))
            df_to_process = full_df[~full_df['variant_id']. astype(str).isin(processed_ids)]
            
            print(f"📄 Resuming...  {len(processed_df)} products already processed")
            print(f"📋 Remaining products: {len(df_to_process)}\n")
        except Exception as e:
            print(f"⚠️ Could not load progress: {e}")
            df_to_process = full_df. copy()
    else:
        df_to_process = full_df.copy()
        print(f"📄 Starting fresh with {len(df_to_process)} products\n")
    
    if len(df_to_process) == 0:
        print("✅ All products already processed!")
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
        "product_url"
    ]
    
    file_exists = os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0
    search_count = 0
    batch_number = 0
    browser = create_browser_with_anti_detection()
    
    processed_count = 0
    
    for index, row in df_to_process.iterrows():
        product_start_time = time.time()
        search_count += 1
        
        try:
            variant_id = str(row['Variant ID']).strip()
            variant_name = str(row['Variant Name']).strip()
            super_variant_name = str(row['Super Variant Name']).strip() if 'Super Variant Name' in row else ""
            model_name = str(row['Model Name']).strip() if 'Model Name' in row else ""
            
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
            price = "Not Found"
            status = "Not Found"
            
            # ===== STRATEGY 1: Amazon.ae Direct Search =====
            print(f"\n🎯 STRATEGY 1: Amazon.ae Direct Search")
            
            # Try Variant Name
            print(f"\n   📍 Trying: Variant Name")
            product_url = search_amazon_ae_direct(variant_name, browser, MATCH_THRESHOLD)
            
            # Try Super Variant Name if failed
            if not product_url and super_variant_name:
                print(f"\n   📍 Trying: Super Variant Name")
                product_url = search_amazon_ae_direct(super_variant_name, browser, MATCH_THRESHOLD)
            
            # Try Model Name if failed
            if not product_url and model_name: 
                print(f"\n   📍 Trying: Model Name")
                product_url = search_amazon_ae_direct(model_name, browser, MATCH_THRESHOLD)
            
            # Scrape price if found
            if product_url: 
                print(f"\n   ✅ Found on Amazon.ae Direct Search!")
                result = scrape_price_from_url(product_url, browser)
                product_name = result["product_name"]
                price = result["price"]
                status = result["status"]
            else:
                print(f"\n   ⚠️ Strategy 1 failed - trying Strategy 2...")
                
                # ===== STRATEGY 2: DuckDuckGo Search =====
                print(f"\n🎯 STRATEGY 2: DuckDuckGo Search")
                
                # Try Variant Name
                print(f"\n   📍 Trying:  Variant Name")
                product_url, _ = search_duckduckgo_and_get_amazon_url(variant_name, browser)
                
                # Try Super Variant Name if failed
                if not product_url and super_variant_name: 
                    print(f"\n   📍 Trying: Super Variant Name")
                    product_url, _ = search_duckduckgo_and_get_amazon_url(super_variant_name, browser)
                
                # Try Model Name if failed
                if not product_url and model_name:
                    print(f"\n   📍 Trying: Model Name")
                    product_url, _ = search_duckduckgo_and_get_amazon_url(model_name, browser)
                
                # Scrape price if found
                if product_url:
                    print(f"\n   ✅ Found on DuckDuckGo!")
                    result = scrape_price_from_url(product_url, browser)
                    product_name = result["product_name"]
                    price = result["price"]
                    status = result["status"]
                else:
                    print(f"\n   ⚠️ Strategy 2 failed - trying Strategy 3...")
                    
                    # ===== STRATEGY 3: Google Search =====
                    print(f"\n🎯 STRATEGY 3: Google Search")
                    
                    # Try Variant Name
                    print(f"\n   📍 Trying: Variant Name")
                    product_url, _ = search_google_and_get_amazon_url(variant_name, browser)
                    
                    # Try Super Variant Name if failed
                    if not product_url and super_variant_name:
                        print(f"\n   📍 Trying: Super Variant Name")
                        product_url, _ = search_google_and_get_amazon_url(super_variant_name, browser)
                    
                    # Try Model Name if failed
                    if not product_url and model_name:
                        print(f"\n   📍 Trying: Model Name")
                        product_url, _ = search_google_and_get_amazon_url(model_name, browser)
                    
                    # Scrape price if found
                    if product_url:
                        print(f"\n   ✅ Found on Google!")
                        result = scrape_price_from_url(product_url, browser)
                        product_name = result["product_name"]
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
                "product_url":  product_url if product_url else "Not Found"
            }

            result_df = pd.DataFrame([row_data], columns=columns)
            full_path = os.path.join(FOLDER_PATH, OUTPUT_CSV)
            result_df.to_csv(full_path, mode='a', header=not file_exists, index=False)
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
                    "product_url": "Error"
                }
                result_df = pd.DataFrame([error_row], columns=columns)
                full_path = os.path.join(FOLDER_PATH, OUTPUT_CSV)
                result_df.to_csv(full_path, mode='a', header=not file_exists, index=False)
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

def convert_csv_to_excel(output_csv):
    """Convert CSV to Excel"""
    print(f"\n{'='*80}")
    print(f"📊 Converting to Excel format...")
    
    try:
        csv_df = pd.read_csv(output_csv)
        
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