import os
import re
import time
import random
import pandas as pd
import requests
from datetime import datetime
from pathvalidate import sanitize_filename
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rapidfuzz import fuzz
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# ---------- CONFIG ----------
EXCEL_FILE = "Remaining_Products.xlsx"
SHEET_NAME = "Sheet1"
CHROME_DRIVER_PATH = r"E:\R3 Factory\Selenium_Prodcut_Scrapper\chromedriver.exe"
# WAIT_TIME = 10
MATCH_THRESHOLD = 80
MAX_WORD=11
# START_ROW = 503
# END_ROW = 1000

STOP_WORDS = {'the', 'a', 'an', 'and', 'or', 'in', 'with', 'for', 'of', 'to', 
              'on', 'by', 'as', 'at', 'from', 'version', 'international', 'gb', 
              'single', 'sim', 'unlocked', 'renewed', 'refurbished' ,'+'}

PENALTY_WORDS = {'case', 'cover', 'protector', 'accessory', 'skin', 'sticker', 
                 'film', 'adapter', 'charger', 'cable', 'stand', 'holder', 
                 'mount', 'grip', 'ring', 'glass', 'shield', 'sleeve', 'pouch', 
                 'bag', 'box', 'holster', 'battery', 'dock', 'keyboard'}

BRANDS = {'xiaomi', 'samsung', 'apple', 'dell', 'hp', 'lenovo', 'lg', 'asus', 'acer', 'msi', 'huawei', 'nova'}
MODEL_KEYWORDS = {'model', 'item', 'part', 'sku', 'pn', 'id', 'art', 'ref'}

# Comprehensive color dictionary with common product colors
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
            
# COLOR_SYNONYMS = {
#     'black': {'jet black', 'onyx', 'midnight', 'phantom black', 'carbon black', 'obsidian'},
#     'space black': {'space gray', 'cosmic black', 'stellar black'},
#     'white': {'pearl white', 'alpine white', 'glacier white', 'ceramic white', 'ivory'},
#     'silver': {'platinum silver', 'metallic silver', 'stainless steel', 'chrome'},
#     'blue': {'sapphire blue', 'ocean blue', 'navy blue', 'cobalt blue', 'arctic blue'},
#     'red': {'crimson red', 'ruby red', 'scarlet', 'vermillion', 'rose red'},
#     'green': {'forest green', 'emerald green', 'olive green', 'mint green'},
#     'gold': {'rose gold', 'champagne gold', 'sunset gold', 'pink gold'},
#     'purple': {'lavender', 'violet', 'orchid', 'lilac', 'amethyst'},
#     'gray': {'grey', 'graphite', 'charcoal', 'slate', 'steel gray'},
# }

# ----------------------------
SITE_CONFIG = {
    "amazon.ae": {
        "SEARCH_URL": "https://www.amazon.ae",
        "SEARCH_BOX": (By.ID, "twotabsearchtextbox"),
        "SEARCH_BUTTON": (By.ID, "nav-search-submit-button"),
        "RESULTS": (By.XPATH, "//div[@data-component-type='s-search-result']"),
        "TITLE": (By.CSS_SELECTOR, "h2.a-size-base-plus.a-spacing-none.a-color-base.a-text-normal span"),
        "IMG_CONTAINER": (By.ID, "altImages"),
        "IMG_SELECTOR": "#altImages img",
        "CSV": "scrape_results_Amazon_ae_R3.csv",
        "OUTPUT_DIR": r"E:\R3 Factory\Product_images\57 products\Rounds2\Amazon.ae",
        "START_ROW" : 2,
        "END_ROW" : 21,
        "IMG_PROCESS": lambda url: re.sub(r'\._.*?_\.', '._AC_.', url) if url else ""
    },
    "amazon.in": {
        "SEARCH_URL": "https://www.amazon.in",
        "SEARCH_BOX": (By.ID, "twotabsearchtextbox"),
        "SEARCH_BUTTON": (By.ID, "nav-search-submit-button"),
        "RESULTS": (By.XPATH, "//div[@data-component-type='s-search-result']"),
        "TITLE": (By.CSS_SELECTOR, "h2.a-size-medium.a-spacing-none.a-color-base.a-text-normal span"),
        "IMG_CONTAINER": (By.ID, "altImages"),
        "IMG_SELECTOR": "#altImages img",
        "CSV": "scrape_results_Amazon_in.csv",
        "OUTPUT_DIR": r"E:\R3 Factory\Product_images\57 products\Rounds2\Amazon.ae",
        "START_ROW" : 7,
        "END_ROW" : 140,
        "IMG_PROCESS": lambda url: re.sub(r'\._.*?_\.', '._AC_.', url) if url else ""
    },
    "amazon.com": {
        "SEARCH_URL": "https://www.amazon.com",
        "SEARCH_BOX": (By.ID, "twotabsearchtextbox"),
        "RESULTS": (By.XPATH, "//div[@data-component-type='s-search-result']"),
        "TITLE": (By.CSS_SELECTOR, "h2.a-size-medium.a-spacing-none.a-color-base.a-text-normal span"),
        "IMG_CONTAINER": (By.ID, "altImages"),
        "IMG_SELECTOR": "#altImages img",
        "CSV": "scrape_results_Amazon_com.csv",
        "OUTPUT_DIR": r"E:\R3 Factory\Product_images\57 products\Rounds2\Amazon.com",
        "START_ROW" : 7,
        "END_ROW" : 140,
        "IMG_PROCESS": lambda url: re.sub(r'\._.*?_\.', '._AC_.', url) if url else ""
    },
    "noon": {
        "SEARCH_URL": "https://www.noon.com/uae-en/",
        "SEARCH_BOX": (By.ID, "search-input"),
        "RESULTS": (By.CSS_SELECTOR, 'div[data-qa="plp-product-box"]'),
        "TITLE": (By.CSS_SELECTOR, 'h2[data-qa="plp-product-box-name"]'),
        "IMG_CONTAINER": (By.CSS_SELECTOR, "div.GalleryV2_thumbnailInnerCtr__i7TLy"),
        "IMG_SELECTOR": "button.GalleryV2_thumbnailElement__3g3ls img",
        "LINK": (By.CSS_SELECTOR, 'a.ProductBoxLinkHandler_productBoxLink__FPhjp'),
        "CSV": "scrape_results_noon.csv",
        "OUTPUT_DIR": r"E:\R3 Factory\Product_images\Bulk Uploads\Rounds2\Noon",
        "START_ROW" :2,
        "END_ROW" : 31,
        "IMG_PROCESS": lambda url: re.sub(r'\._.*_\.', '.', url) if url else ""
    }
}

def preprocess_text(text):
    """Normalize text for matching"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\d+gb', '', text)     # Remove capacity (handled separately)
    return ' '.join([word for word in text.split() if word not in STOP_WORDS])

def extract_storage(title):
    """Extract storage capacity from title"""
    match = re.search(r'(\d+)\s?(gb|mb)', title, re.IGNORECASE)
    return match.group(0).lower() if match else None

def calculate_match_score(variant, product_title):
    """Hybrid matching algorithm with multiple strategies"""
    # Preprocess texts
    variant_proc = preprocess_text(variant)
    title_proc = preprocess_text(product_title)
    title_lower = product_title.lower()

    # Base fuzzy matching score
    base_score = fuzz.token_set_ratio(variant_proc, title_proc)
    
    # Keyword presence bonus
    variant_words = set(variant_proc.split())
    title_words = set(title_proc.split())
    keyword_bonus = len(variant_words & title_words) * 5
    
    # Capacity match bonus
    variant_cap = extract_storage(variant)
    title_cap = extract_storage(product_title)
    capacity_bonus = 20 if variant_cap and title_cap and variant_cap == title_cap else 0

    # Brand scoring
    brand_score = 0
    variant_brand, variant_model = extract_brand_and_model(variant)
    
    if variant_brand:
        if variant_brand in title_lower:
            brand_score += 30
        # Penalty for competing brands
        competing_brands = BRANDS - {variant_brand}
        if any(brand in title_lower for brand in competing_brands):
            brand_score -= 40
    
    # Model number scoring
    model_score = 0
    if variant_model and variant_model in title_lower:
        model_score += 50
    
    # Color matching bonus (NEW)
    color_bonus = calculate_color_match_score(variant, product_title)
    
    # Penalty for accessory keywords
    penalty = -20 if any(word in title_lower for word in PENALTY_WORDS) else 0
    
    return base_score + keyword_bonus + capacity_bonus + brand_score + model_score + penalty + color_bonus

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

def extract_colors(text):
    """Extract color names from text with comprehensive color dictionary"""
    text_lower = text.lower()
    colors_found = set()
    
    # Check for exact color matches
    for color in COLOR_DICTIONARY:
        if color in text_lower:
            colors_found.add(color)
    
    # Also extract color-like words that might be specific to products
    color_patterns = [
        r'\b(\w+)\s*(black|white|blue|red|green|gold|purple|gray|grey|pink|orange|brown|silver)\b',
        r'\b(black|white|blue|red|green|gold|purple|gray|grey|pink|orange|brown|silver)\s*(\w+)\b'
    ]
    
    for pattern in color_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            color_term = ' '.join([word for word in match if word]).strip()
            if len(color_term.split()) <= 2:  # Avoid long phrases
                colors_found.add(color_term)
    
    return colors_found

def print_time_elapsed(start_time, message=""):
    elapsed = time.time() - start_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"{message} Time elapsed: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")

def create_variant_folder(variant_id, site):
    folder_path = os.path.join(SITE_CONFIG[site]["OUTPUT_DIR"], variant_id)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def download_image(url, save_path):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        img_data = requests.get(url, headers=headers).content
        with open(save_path, "wb") as f:
            f.write(img_data)
        print(f"   ✅ Saved: {save_path}")
    except Exception as e:
        print(f"   ❌ Failed to download {url} - {e}")

def shorten_Variant_name(name, MAX_WORD):
    return ' '.join(name.split()[:MAX_WORD])

def scrape_product_images(browser, variant_id, site):
    cfg = SITE_CONFIG[site]
    folder_path = create_variant_folder(variant_id, site)
    img_count = 0
    seen = set()

    try:
        WebDriverWait(browser, 8).until(
            EC.presence_of_element_located(cfg["IMG_CONTAINER"])
        )

        thumbnails = browser.find_elements(By.CSS_SELECTOR, cfg["IMG_SELECTOR"])
        print(f"   🔍 Found {len(thumbnails)} thumbnails.")

        for thumb in thumbnails[1:]: # This skips the first element
            try:
                src = thumb.get_attribute("src")
                if not src or "transparent" in src:
                    continue

                high_res_url = cfg["IMG_PROCESS"](src)

                if high_res_url in seen:
                    continue
                seen.add(high_res_url)

                img_count += 1
                save_path = os.path.join(folder_path, f"image_{img_count}.jpg")
                download_image(high_res_url, save_path)

            except Exception as e:
                print(f"   ⚠️ Skipping thumbnail due to error: {e}")
                continue

        return img_count > 0

    except Exception as e:
        print(f"   ❌ Error scraping images - {e}")
        return False

def search_and_scrape(site):
    cfg = SITE_CONFIG[site]
    total_start_time = time.time()
    print(f"🚀 Starting {site} scraping process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Read the main dataframe
    full_df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    full_df = full_df.loc[SITE_CONFIG[site]["START_ROW"]-2:SITE_CONFIG[site]["END_ROW"]]

    output_csv = cfg["CSV"]
    
    # Filter out already processed items
    if os.path.exists(output_csv) and os.path.getsize(output_csv) > 0:
        try:
            processed_df = pd.read_csv(output_csv)
            processed_ids = set(processed_df['variant_id'].astype(str))
            df_to_process = full_df[~full_df['variant_id'].astype(str).isin(processed_ids)]
            print(f"📄 Resuming scraping... {len(processed_df)} products already processed")
        except Exception as e:
            print(f"⚠️  Error reading processed CSV: {e}")
            df_to_process = full_df.copy()
    else:
        processed_ids = set()
        df_to_process = full_df.copy()
        print("📄 No previous CSV found, starting fresh")

    options = Options()
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)

    file_exists = os.path.exists(output_csv)

    # Use df_to_process instead of df
    for index, row in df_to_process.iterrows():
        product_start_time = time.time()
        variant_id = str(row['variant_id']).strip()
        full_Variant_name = str(row['variant_name']).strip()
        variant_name = shorten_Variant_name(full_Variant_name, MAX_WORD)
        product_url = ""
        matched_product_name = ""  
        status = "Not Done" 


        if not variant_id or not variant_name:
            continue

        print(f"\n🔎 Searching for: {full_Variant_name} (Variant ID: {variant_id})\n 📝 Variant name: {variant_name}")
        status = "Not Done"

        try:
            # Search phase
            browser.get(cfg["SEARCH_URL"])
            if site == "amazon.ae" or site == "amazon.com" or site=="amazon.in":  # Use site parameter, not site_choice
                WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
                )
                search_box = browser.find_element(By.ID, "twotabsearchtextbox")
                search_box.clear()
                search_box.send_keys(variant_name)
                browser.find_element(By.ID, "nav-search-submit-button").click()

            elif site == "noon":
                search_box = WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located(cfg["SEARCH_BOX"])
                )
                search_box.clear()
                search_box.send_keys(variant_name)
                search_box.send_keys(Keys.ENTER)

            # Matching phase
            WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located(cfg["RESULTS"])
            )
            search_results = browser.find_elements(*cfg["RESULTS"])

            best_match_elem = None
            best_score = 0
            best_title = ""
            matched_product_name = ""
            
            for result in search_results[:20]:
                try:
                    title_elem = result.find_element(*cfg["TITLE"]) 
                    title_text = title_elem.text.strip()
                    
                    # Use the enhanced matching function
                    score = calculate_match_score(variant_name, title_text)
                    
                    if score > best_score:
                        best_score = score
                        best_match_elem = result
                        best_title = title_text
                except Exception:
                    continue

            print_time_elapsed(time.time(), "   Matching completed")
            
            # Dynamic threshold
            # MATCH_THRESHOLD = max(30, 90 - len(variant_name.split())/2)

            if best_match_elem and best_score >= MATCH_THRESHOLD:
                print(f"   🎯 Best match score: {best_score} (Threshold: {MATCH_THRESHOLD})")  # Fixed print
                try:
                    link_elem = best_match_elem.find_element(*cfg["LINK"])
                    product_url = link_elem.get_attribute("href")
                except:
                    link_elem = best_match_elem.find_element(By.TAG_NAME, "a")
                    product_url = link_elem.get_attribute("href")
                    
                print(f"   📦 Picked {site} product: {best_title}")
                matched_product_name = best_title

                scrape_start = time.time()
                browser.execute_script("window.open(arguments[0]);", product_url)
                WebDriverWait(browser,5).until(lambda d: len(d.window_handles) > 1)
                browser.switch_to.window(browser.window_handles[-1])

                if scrape_product_images(browser, variant_id, site):
                    status = "Done"

                browser.close()
                browser.switch_to.window(browser.window_handles[0])
                print_time_elapsed(scrape_start, "   Scraping completed")
            else:
                print(f"   ⚠ No good match found. Best match score: {best_score} (Threshold: {MATCH_THRESHOLD})")
                matched_product_name = ""

            time.sleep(random.randint(2, 5))

        except Exception as e:
            print(f"   ❌ Error processing {variant_name} - Product not found on - {SITE_CONFIG[site]}")
            
        new_row = pd.DataFrame([{
            "variant_id": variant_id,
            "variant_name": full_Variant_name,
            "status": status,
            "Matched_Product_Name": matched_product_name,
            "url": product_url
        }])

        new_row.to_csv(output_csv, mode='a', header=not file_exists, index=False)
        file_exists = True

        print_time_elapsed(product_start_time, "   Product processing completed")

    browser.quit()
    print(f"\n📄 Results saved to {output_csv}")
    print_time_elapsed(total_start_time, f"🏁 {site} scraping completed")
    print(f"🕒 Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    site_choice = input("Enter site to scrape amazon.ae  amazon.in  amazon.com  noon : ").strip().lower()
    if site_choice in SITE_CONFIG:
        search_and_scrape(site_choice)
    else:
        print("Invalid choice. Please choose 'amazon' or 'noon'.")