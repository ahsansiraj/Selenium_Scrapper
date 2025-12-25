import os
import re
import time
import random
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from rapidfuzz import fuzz

from search_engines import search_duckduckgo_and_get_amazon_url
from search_engines import search_google_and_get_amazon_url

# ---------- CONFIG ----------
EXCEL_FILE = "relation_data.xlsx"  # UPDATE THIS PATH
SHEET_NAME = "relation_data"                   # UPDATE THIS SHEET NAME
OUTPUT_CSV = r"E:\R3 Factory\Selenium_Prodcut_Scrapper\Scrapper_Results\Price_Results.csv"
OUTPUT_EXCEL = "Price_Results.xlsx"
START_ROW = 2      # UPDATE THIS
END_ROW = 3000       # UPDATE THIS
            
MATCH_THRESHOLD=80
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
GEO_KEYWORD = "Dubai"

# ---------- MATCHING CONFIGURATION ----------
STOP_WORDS = {'the', 'a', 'an', 'and', 'or', 'in', 'with', 'for', 'of', 'to', 
              'on', 'by', 'as', 'at', 'from', 'version', 'international', 'gb', 
              'single', 'sim', 'unlocked', 'Pre-Owned Phone', 'Pre-Owned Smart Phone' ,
               'Plus', 'renewed', 'refurbished', '+', 'esim', 
              'physical', 'dual'}

PENALTY_WORDS = {'case', 'cover', 'protector', 'accessory', 'skin', 'sticker', 
                 'film', 'adapter', 'charger', 'cable', 'stand', 'holder', 
                 'mount', 'grip', 'ring', 'glass', 'shield', 'sleeve', 'pouch', 
                 'bag', 'box', 'holster', 'battery', 'dock', 'keyboard'}

BRANDS = {'htc', 'xiaomi', 'samsung', 'apple', 'dell', 'hp', 'lenovo', 'lg', 'asus', 
          'acer', 'msi', 'huawei', 'nova', 'oppo', 'vivo', 'realme', 'oneplus',
          'honor', 'redmi', 'poco', 'motorola', 'nokia', 'sony', 'google' , 'Pre-Owned Phone', 'Pre-Owned Smart Phone'}

MODEL_KEYWORDS = {'model', 'item', 'part', 'sku', 'pn', 'id', 'art', 'ref','Pre-Owned Phone', 'Pre-Owned Smart Phone'}

COLOR_DICTIONARY = {
    # Black family
    'black', 'jet black', 'onyx', 'midnight', 'phantom black', 'carbon black', 
    'obsidian', 'space black', 'cosmic black', 'stellar black', 'graphite',
    'charcoal', 'ebony', 'raven', 'brilliant black'
    
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
    'product red', 'coral red', 'fiery red', 'burgundy', '(product)red',
    
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

# Color synonyms for better matching
COLOR_SYNONYMS = {
    'black': {'jet black', 'onyx', 'midnight', 'phantom black', 'carbon black', 'obsidian'},
    'space black': {'space gray', 'cosmic black', 'stellar black'},
    'midnight':  {'night', 'noir', 'phantom black'},
    'white': {'pearl white', 'alpine white', 'glacier white', 'ceramic white', 'ivory'},
    'silver': {'platinum silver', 'metallic silver', 'stainless steel', 'chrome'},
    'blue':  {'sapphire blue', 'ocean blue', 'navy blue', 'cobalt blue', 'arctic blue'},
    'sky blue': {'baby blue', 'azure', 'ice blue'},
    'midnight blue': {'navy', 'deep blue', 'royal blue'},
    'red': {'crimson red', 'ruby red', 'scarlet', 'vermillion', 'rose red', '(product)red', 'product red'},
    'product red':  {'red', '(red)', 'productred'},
    'green': {'forest green', 'emerald green', 'olive green', 'mint green'},
    'alpine green': {'forest green', 'hunter green', 'army green'},
    'gold': {'rose gold', 'champagne gold', 'sunset gold', 'pink gold'},
    'rose gold': {'pink gold', 'blush gold'},
    'purple': {'lavender', 'violet', 'orchid', 'lilac', 'amethyst'},
    'deep purple': {'royal purple', 'eggplant', 'plum'},
    'gray': {'grey', 'graphite', 'charcoal', 'slate', 'steel gray'},
    'space gray': {'space grey', 'metallic gray', 'titanium gray'},
}

# ---------- BROWSER SETUP (VANILLA SELENIUM) ----------
def create_browser_stealth():
    """
    Production-grade browser with MINIMAL anti-detection
    Key insight: Less is more.  Amazon detects "trying too hard"
    """
    options = Options()
    
    # Basic options only
    options.add_argument("--start-maximized")
    options.add_argument(f"user-agent={USER_AGENT}")
    
    # Critical:  Disable automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Basic preferences
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2,
    }
    options.add_experimental_option("prefs", prefs)
    
    # Use webdriver_manager for automatic driver handling
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    
    # ONLY ONE stealth script (critical)
    browser.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get:  () => undefined
        });
    """)
    
    return browser

# ---------- MATCHING LOGIC ----------
def preprocess_text(text):
    """Normalize text for matching"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)      # Normalize spaces
    return ' '.join([word for word in text.split() if word not in STOP_WORDS])

def extract_storage(title):
    """Extract all storage capacities (RAM and ROM)"""
    matches = re.findall(r'(\d+)\s?(gb|tb|mb)', title, re.IGNORECASE)
    if matches:
        # Return as "3gb 32gb"
        return ' '.join([f"{match[0]}{match[1].lower()}" for match in matches])
    return None

def extract_brand_and_model(variant_name):
    """Extract brand and model from variant name"""
    words = variant_name.lower().split()
    brand = None
    model = None
    
    # Find brand in first 5 words
    for word in words[:5]:
        if word in BRANDS:
            brand = word
            break
    
    # Find model number (alphanumeric pattern)
    for i, word in enumerate(words):
        # Model must be at least 4 chars and contain both letters and numbers
        if len(word) >= 4 and any(char.isdigit() for char in word) and any(char.isalpha() for char in word):
            # Check if preceded by model keyword
            if i > 0 and words[i-1] in MODEL_KEYWORDS:
                model = word
                break
            # Or just a valid alphanumeric pattern
            elif not any(char.isspace() for char in word):
                model = word
                break
    
    return brand, model

def extract_colors(text):
    """Extract color names from text"""
    text_lower = text.lower()
    colors_found = set()
    
    # Check for exact color matches
    for color in COLOR_DICTIONARY:
        # Use word boundaries to avoid partial matches
        if re.search(r'\b' + re.escape(color) + r'\b', text_lower):
            colors_found.add(color)
    
    return colors_found

def calculate_color_match_score(variant, product_title):
    """
    Calculate color matching score (0 to 15 points max)
    """
    variant_colors = extract_colors(variant)
    title_colors = extract_colors(product_title)
    
    # No color in variant - neutral (0 points)
    if not variant_colors:
        return 0
    
    # Variant has color but title doesn't - small penalty
    if not title_colors:
        return -5
    
    score = 0
    matched = False
    
    # Check for exact color matches
    for variant_color in variant_colors: 
        if variant_color in title_colors: 
            score += 10  # Exact match bonus
            matched = True
            break
    
    # Check for color synonyms
    if not matched:
        for variant_color in variant_colors: 
            for title_color in title_colors:
                # Check direct synonyms
                if variant_color in COLOR_SYNONYMS: 
                    if title_color in COLOR_SYNONYMS[variant_color]:
                        score += 8  # Synonym match bonus
                        matched = True
                        break
                # Check reverse synonyms
                if title_color in COLOR_SYNONYMS: 
                    if variant_color in COLOR_SYNONYMS[title_color]:
                        score += 8  # Synonym match bonus
                        matched = True
                        break
            if matched:
                break
    
    # Penalty for color mismatch
    if not matched:
        score -= 10
    
    return score

def calculate_match_score(variant, product_title):
    """
    Enhanced matching algorithm - NORMALIZED to 0-100 scale
    
    Breakdown:
    - Base fuzzy score: 0-50 points (50% weight)
    - Storage match: 0-15 points
    - Brand match: 0-15 points  
    - Model match: 0-15 points
    - Color match: -10 to +10 points
    - Keyword overlap: 0-5 points
    - Penalties: -20 points max
    
    Total possible: ~100 points
    """
    
    # Preprocess texts
    variant_proc = preprocess_text(variant)
    title_proc = preprocess_text(product_title)
    title_lower = product_title.lower()
    variant_lower = variant.lower()
    
    # 1. BASE FUZZY SCORE (0-50 points) - 50% of total weight
    base_score = fuzz.token_set_ratio(variant_proc, title_proc) * 1.0
    
    # 2. STORAGE CAPACITY MATCH (0-15 points)
    variant_cap = extract_storage(variant)
    title_cap = extract_storage(product_title)
    
    if variant_cap and title_cap: 
        if variant_cap == title_cap:
            storage_score = 15  # Perfect match
        else: 
            storage_score = -15  # Wrong storage is a big problem
    elif variant_cap and not title_cap:
        storage_score = -5  # Variant specifies storage but title doesn't
    else:
        storage_score = 0  # No storage specified in variant
    
    # 3. BRAND MATCH (0-15 points)
    variant_brand, variant_model = extract_brand_and_model(variant)
    brand_score = 0
    
    if variant_brand:
        if variant_brand in title_lower:
            brand_score = 20  # Correct brand
        else:
            # Check if a competing brand is present
            competing_brands = BRANDS - {variant_brand}
            if any(brand in title_lower for brand in competing_brands):
                brand_score = -20  # Wrong brand - major penalty
            else:
                brand_score = -5  # Brand not found
    
    # 4. MODEL NUMBER MATCH (0-15 points)
    model_score = 0
    if variant_model:
        if variant_model in title_lower: 
            model_score = 15  # Perfect model match
        else:
            # Check for partial model match (e.g., "11" matches "iphone 11")
            if len(variant_model) >= 4: 
                model_score = -10  # Model mismatch
    
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
    # You can add logic here if you want to handle refurbished products differently
    
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
    
    # Clamp score to 0-100 range
    final_score = max(0, min(100, final_score))
    
    return final_score
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
    
    try:
        for condition, keywords in condition_keywords.items():
            for keyword in keywords:
                if keyword in productNameLower:
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

# ---------- SEARCH FUNCTIONS (TAB-BASED) ----------
def search_amazon_ae_direct_tab_based(search_term, browser, match_threshold):
    """
    KEY INSIGHT: Open search in new tab, keep main tab alive
    This mimics human behavior: multiple tabs open
    """
    try:
        print(f"   🔍 Searching Amazon.ae for: {search_term[: 50]}...")
        
        # Open Amazon in NEW TAB (not navigate away)
        browser.execute_script("window.open('https://www.amazon.ae', '_blank');")
        
        # Switch to new tab
        WebDriverWait(browser, 5).until(lambda d:len(d.window_handles) > 1)
        browser.switch_to.window(browser.window_handles[-1])
        
        time.sleep(random.uniform(2, 4))
        handle_amazon_popup(browser)
        # Search
        try:
            search_box = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
            )
        except:
            # If failed, close tab and return
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
            return None
        
        search_box.clear()
        time.sleep(0.5)
        
        # Type slowly
        for char in search_term:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.12))
        
        time.sleep(random.uniform(0.7, 1.5))
        
        # Submit with ENTER key (more human than clicking button)
        search_box.send_keys(Keys.ENTER)
        time.sleep(random.uniform(3, 5))
        
        # Click search button
        # search_button = browser.find_element(By.ID, "nav-search-submit-button")
        # search_button.click()
        

        # Get results
        try:
            search_results = browser.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")
        except:
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
            return None
        
        if not search_results:
            print(f"      ⚠️ No results found")
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
            return None
        
        print(f"   📊 Found {len(search_results)} results")
        
        # Match
        best_score = 0
        best_url = None
        best_title = ""
        
        for result in search_results[:20]: 
            try:
                # Try multiple selectors
                title_elem = None
                for selector in [
                    "div.a-section.a-spacing-none.a-spacing-top-small.s-title-instructions-style",
                    "h2.a-size-base-plus.a-spacing-none.a-color-base.a-text-normal span",
                    "h2.a-size-base-plus span",
                    "h2 span.a-text-normal",
                    "h2 a span",
                ]:
                    try:
                        title_elem = result.find_element(By.CSS_SELECTOR, selector)
                        if title_elem:
                            break
                    except:
                        continue
                
                if not title_elem:
                    continue
                
                title_text = ' '.join(title_elem.text.strip().split())
                
                if not title_text:
                    continue
                
                score = calculate_match_score(search_term, title_text)
                
                print(f"   🎯 Best match score: {best_score} (Threshold: {match_threshold})")
                
                if score > best_score and score >= match_threshold:
                    best_score = score
                    link = result.find_element(By.TAG_NAME, "a")
                    best_url = link.get_attribute("href")
                    best_title = title_text
            except:
                continue
        
        
        if best_url:
            print(f"   ✅ Match:  {best_title[: 60]}...")
        
        # CRITICAL: Close search tab, return to main tab
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
        
        return best_url
        
    except Exception as e:
        print(f"   ❌ Search error: {e}")
        try:
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
        except:
            pass
        return None

def scrape_price_in_new_tab(product_url, browser):
    """
    Open product page in new tab, scrape, close tab
    """
    try: 
        print(f"   📄 Opening product page...")
        
        # Open in new tab
        browser.execute_script(f"window.open('{product_url}', '_blank');")
        WebDriverWait(browser, 5).until(lambda d: len(d.window_handles) > 1)
        browser.switch_to.window(browser.window_handles[-1])
        
        time.sleep(random.uniform(3, 5))
        
        handle_amazon_popup(browser)
        
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "productTitle"))
            )
        except:
            print(f"      ⚠️ Product page failed to load")
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
            return {
                "product_name": "Error",
                "price": "Error",
                "status": "Error"
            }
        
        print(f"   🔍 Extracting price...")
        
        product_name = extract_product_name(browser)
        product_condition = extract_product_condition(product_name, browser)
        price = extract_price(browser)
        
        if price == "Currently Unavailable":
            status = "Currently Unavailable"
        elif price != "Not Found":
            status = "Success"
        else:
            status = "Price Not Found"
        
        # Close product tab
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
        
        return {
            "product_condition": product_condition,
            "product_name": product_name,
            "price": price,
            "status": status
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

# ---------- MAIN LOOP (SINGLE SESSION) ----------
def unified_search_and_scrape():

    total_start_time = time.time()
    
    print(f"\n{'='*80}")
    print(f"🚀 UNIFIED PRICE SCRAPER - Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    # Read Excel
    try:
        full_df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
        full_df = full_df.iloc[START_ROW-2:END_ROW]
        print(f"📊 Loaded {len(full_df)} products from Excel\n")
    except Exception as e:
        print(f"❌ Error reading Excel: {e}")
        return
    
    # Check progress
    if os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0:
        try:
            processed_df = pd.read_csv(OUTPUT_CSV, skipinitialspace=True)
            processed_df.columns = [col.strip() for col in processed_df.columns]
            processed_ids = set(processed_df['variant_id'].astype(str))
            df_to_process = full_df[~full_df['Variant ID'].astype(str).isin(processed_ids)]
            
            print(f"📄 Resuming...  {len(processed_df)+2} products done")
            print(f"📋 Remaining: {len(df_to_process)}\n")
        except Exception as e:
            print(f"⚠️ Could not load progress: {e}")
            df_to_process = full_df.copy()
    else:
        df_to_process = full_df.copy()
        print(f"📄 Starting fresh:  {len(df_to_process)} products\n")
    
    if len(df_to_process) == 0:
        print("✅ All products processed!")
        convert_csv_to_excel(OUTPUT_CSV)
        return
    
    columns = [
        "variant_id",
        "variant_name",
        "super_variant_name",
        "model_name",
        "price",
        "status",
        "product_condition",
        "product_name",
        "product_url"
    ]
    
    file_exists = os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0
    
    # ===== CRITICAL:  Single browser for entire session =====
    browser = create_browser_stealth()
    
    # Open a blank tab (anchor tab that stays open)
    browser.get("about:blank")
    
    search_count = 0
    processed_count = 0
    last_amazon_search = 0
    AMAZON_COOLDOWN = 6  # 6 seconds between Amazon searches
    
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
            
            # ===== GENTLE SESSION REFRESH (every 50, not 15) =====
            if search_count % 50 == 0:
                print(f"\n{'='*80}")
                print(f"🔄 SESSION REFRESH: {search_count} searches")
                print(f"{'='*80}")
                
                # Just clear cookies (don't close browser!)
                try:
                    browser.delete_all_cookies()
                    print("   🍪 Cleared cookies")
                except:
                    pass
                
                # Short break
                wait_time = random.randint(45, 75)
                print(f"   ⏸️ Quick break: {wait_time}s")
                time.sleep(wait_time)
                print(f"{'='*80}\n")
            
            print(f"{'='*80}")
            print(f"🔎 Product {processed_count}/{len(df_to_process)}")
            print(f"🆔 ID: {variant_id}")
            print(f"📝 Variant: {variant_name[: 50]}...")
            print(f"{'='*80}")
            
            product_url = None
            product_name = "Not Found"
            price = "Not Found"
            status = "Not Found"
            
            # ===== STRATEGY 1: Amazon. ae Direct =====
            print(f"\n🎯 STRATEGY 1: Amazon.ae Direct Search")
            
            # Enforce cooldown
            time_since_last = time.time() - last_amazon_search
            if time_since_last < AMAZON_COOLDOWN:
                cooldown_wait = AMAZON_COOLDOWN - time_since_last
                print(f"   ⏳ Cooldown: {cooldown_wait:.1f}s")
                time.sleep(cooldown_wait)
            
            # Try cascade
            for search_name, threshold in [
                (variant_name, 80),
                (super_variant_name, 75) if super_variant_name else (None, 0),
                (model_name, 70) if model_name else (None, 0)
            ]:
                if not search_name:
                    continue
                
                print(f"\n   📍 Trying:  {search_name[:40]}...")
                product_url = search_amazon_ae_direct_tab_based(search_name, browser, threshold)
                last_amazon_search = time.time()
                
                if product_url:
                    break
                
                # Small delay between cascades
                time.sleep(random.uniform(3, 5))
            
            # Scrape if found
            if product_url: 
                print(f"\n   ✅ Found on Amazon.ae!")
                result = scrape_price_in_new_tab(product_url, browser)
                product_name = result["product_name"]
                product_condition = result["product_condition"]
                price = result["price"]
                status = result["status"]
            else:
                # ===== STRATEGY 2: DuckDuckGo Search =====
                print(f"\n   ⚠️ Amazon direct failed - trying DuckDuckGo...")
                print(f"\n🎯 STRATEGY 2: DuckDuckGo Search")
                
                # Try Variant Name
                print(f"\n   📍 Trying:  Variant Name")
                product_url, _ = search_duckduckgo_and_get_amazon_url(variant_name, browser)
                time.sleep(random.uniform(3, 5))
                
                # Try Super Variant Name if failed
                if not product_url and super_variant_name:
                    print(f"\n   📍 Trying: Super Variant Name")
                    product_url, _ = search_duckduckgo_and_get_amazon_url(super_variant_name, browser)
                    time.sleep(random.uniform(3, 5))
                
                # Try Model Name if failed
                if not product_url and model_name: 
                    print(f"\n   📍 Trying: Model Name")
                    product_url, _ = search_duckduckgo_and_get_amazon_url(model_name, browser)
                    time.sleep(random.uniform(3, 5))
                
                # If found on DuckDuckGo, scrape price
                if product_url: 
                    print(f"\n   ✅ Found on DuckDuckGo!")
                    result = scrape_price_in_new_tab(product_url, browser)
                    product_name = result["product_name"]
                    product_condition = result["product_condition"]
                    price = result["price"]
                    status = result["status"]
                else:
                    # ===== STRATEGY 3: Google Search =====
                    print(f"\n   ⚠️ DuckDuckGo failed - trying Google...")
                    print(f"\n🎯 STRATEGY 3: Google Search")
                    
                    # Try Variant Name
                    print(f"\n   📍 Trying: Variant Name")
                    product_url, _ = search_google_and_get_amazon_url(variant_name, browser)
                    time.sleep(random.uniform(3, 5))
                    
                    # Try Super Variant Name if failed
                    if not product_url and super_variant_name:
                        print(f"\n   📍 Trying: Super Variant Name")
                        product_url, _ = search_google_and_get_amazon_url(super_variant_name, browser)
                        time.sleep(random.uniform(3, 5))
                    
                    # Try Model Name if failed
                    if not product_url and model_name: 
                        print(f"\n   📍 Trying: Model Name")
                        product_url, _ = search_google_and_get_amazon_url(model_name, browser)
                        time.sleep(random.uniform(3, 5))
                    
                    # If found on Google, scrape price
                    if product_url:
                        print(f"\n   ✅ Found on Google!")
                        result = scrape_price_in_new_tab(product_url, browser)
                        product_name = result["product_name"]
                        product_condition = result["product_condition"]
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
                "product_condition": product_condition,
                "product_name": product_name,
                "product_url":  product_url if product_url else "Not Found"
            }
            
            result_df = pd.DataFrame([row_data], columns=columns)
            result_df.to_csv(OUTPUT_CSV, mode='a', header=not file_exists, index=False)
            file_exists = True
            
            product_time = time.time() - product_start_time
            print(f"\n   ⏱️ Processed in {product_time:.2f}s")
            print(f"   📊 Status: {status}")
            
            # Natural delay
            wait_time = random.randint(5, 9)
            print(f"   ⏳ Waiting {wait_time}s.. .\n")
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"   ❌ Error:  {str(e)}")
            import traceback
            traceback.print_exc()
            
            try:
                error_row = {
                    "variant_id": variant_id,
                    "variant_name": variant_name,
                    "super_variant_name": super_variant_name if 'super_variant_name' in locals() else "",
                    "model_name": model_name if 'model_name' in locals() else "",
                    "price": "Error",
                    "status":  "Error",
                    "product_condition": "Error",
                    "product_name": "Error",
                    "product_url": "Error"
                }
                result_df = pd.DataFrame([error_row], columns=columns)
                result_df.to_csv(OUTPUT_CSV, mode='a', header=not file_exists, index=False)
                file_exists = True
            except:
                pass
            continue
    
    # Close browser at end
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
    print(f"🏁 Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️ Total time: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
    print(f"📊 Total searches: {search_count}")
    print(f"📊 Total products: {processed_count}")
    print(f"{'='*80}\n")

def convert_csv_to_excel(csv_path):
    """Convert CSV to Excel"""
    print(f"\n{'='*80}")
    print(f"📊 Converting to Excel...")
    
    try:
        csv_df = pd.read_csv(csv_path)
        
        with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
            csv_df.to_excel(writer, sheet_name='Price Results', index=False)
            
            from openpyxl.utils import get_column_letter
            worksheet = writer.sheets['Price Results']
            
            for idx, col in enumerate(csv_df.columns, 1):
                max_length = max(csv_df[col].astype(str).map(len).max(), len(col))
                worksheet.column_dimensions[get_column_letter(idx)].width = min(max_length + 2, 50)
        
        print(f"✅ Excel created:  {OUTPUT_EXCEL}")
        print(f"📊 Total products: {len(csv_df)}")
        
        if 'status' in csv_df.columns:
            print(f"\n📈 Summary:")
            print(csv_df['status'].value_counts())
        
    except Exception as e:
        print(f"⚠️ Excel conversion failed: {e}")
        import traceback
        traceback.print_exc()

# ---------- ENTRY POINT ----------
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🌐 PRODUCTION-GRADE AMAZON. AE PRICE SCRAPER")
    print("="*80)
    print("\n📊 Prices in AED only")
    print("="*80 + "\n")
    
    unified_search_and_scrape()

