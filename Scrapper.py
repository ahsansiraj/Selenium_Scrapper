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

# ---------- CONFIG ----------
EXCEL_FILE = "for Data Scrapping.xlsx"
SHEET_NAME = "Sheet2"
MATCH_THRESHOLD = 50
MAX_WORD = 9

# Geographic keyword for prioritizing regional Amazon sites
# "Dubai" will make Google prioritize amazon.ae results
GEO_KEYWORD = "Dubai"

STOP_WORDS = {'the', 'a', 'an', 'and', 'or', 'in', 'with', 'for', 'of', 'to', 
              'on', 'by', 'as', 'at', 'from', 'version', 'international', 'gb', 
              'single', 'sim', 'unlocked', 'renewed', 'refurbished', '+'}

PENALTY_WORDS = {'case', 'cover', 'protector', 'accessory', 'skin', 'sticker', 
                 'film', 'adapter', 'charger', 'cable', 'stand', 'holder', 
                 'mount', 'grip', 'ring', 'glass', 'shield', 'sleeve', 'pouch', 
                 'bag', 'box', 'holster', 'battery', 'dock', 'keyboard'}

BRANDS = {'xiaomi', 'samsung', 'apple', 'dell', 'hp', 'lenovo', 'lg', 'asus', 'acer', 'msi', 'huawei', 'nova'}
MODEL_KEYWORDS = {'model', 'item', 'part', 'sku', 'pn', 'id', 'art', 'ref'}

COLOR_DICTIONARY = {
    'black', 'jet black', 'onyx', 'midnight', 'phantom black', 'carbon black', 
    'obsidian', 'space black', 'cosmic black', 'stellar black', 'graphite',
    'charcoal', 'ebony', 'raven', 'white', 'pearl white', 'alpine white', 
    'glacier white', 'ceramic white', 'ivory', 'snow white', 'chalk white', 
    'silver', 'platinum', 'metallic silver', 'stainless steel', 'chrome', 
    'frost white', 'blue', 'sapphire blue', 'ocean blue', 'navy blue', 
    'cobalt blue', 'arctic blue', 'sky blue', 'baby blue', 'azure', 'ice blue', 
    'midnight blue', 'royal blue', 'deep blue', 'pacific blue', 'red', 
    'crimson red', 'ruby red', 'scarlet', 'vermillion', 'rose red',
    'product red', 'coral red', 'fiery red', 'burgundy', 'green', 'forest green', 
    'emerald green', 'olive green', 'mint green', 'alpine green', 'hunter green', 
    'army green', 'sage green', 'lime green', 'pine green', 'gold', 'rose gold', 
    'champagne gold', 'sunset gold', 'pink gold', 'blush gold', 'yellow gold', 
    'starlight gold', 'purple', 'lavender', 'violet', 'orchid', 'lilac', 
    'amethyst', 'deep purple', 'royal purple', 'eggplant', 'plum', 'mauve',
    'gray', 'grey', 'graphite', 'charcoal', 'slate', 'steel gray',
    'space gray', 'space grey', 'metallic gray', 'titanium', 'ash gray',
    'brown', 'espresso brown', 'chocolate brown', 'cognac', 'tan', 'taupe',
    'pink', 'blush pink', 'rose pink', 'coral pink', 'hot pink', 'magenta',
    'orange', 'sunset orange', 'coral orange', 'tangerine', 'amber',
    'yellow', 'sunflower yellow', 'golden yellow', 'lemon yellow',
    'rainbow', 'multicolor', 'prism', 'gradient', 'starlight', 'sunlight', 
    'moonlight', 'aurora', 'northern lights'
}

# Site configuration for Amazon sites
SITE_CONFIG = {
    "amazon.ae": {
        "SEARCH_URL": "https://www.amazon.ae",
        "IMG_CONTAINER": (By.ID, "altImages"),
        "IMG_SELECTOR": "#altImages img",
        "CSV": "scrape_results_Amazon_ae_R1.csv",
        "OUTPUT_DIR": r"E:\R3 Factory\Product_images\57 products\Rounds2\Amazon.ae",
        "START_ROW": 2,
        "END_ROW": 12,
        "IMG_PROCESS": lambda url: re.sub(r'\._.*?_\.', '._AC_.', url) if url else ""
    },
    "amazon.in": {
        "SEARCH_URL": "https://www.amazon.in",
        "IMG_CONTAINER": (By.ID, "altImages"),
        "IMG_SELECTOR": "#altImages img",
        "CSV": "scrape_results_Amazon_in_R1.csv",
        "OUTPUT_DIR": r"E:\R3 Factory\Product_images\57 products\Rounds2\Amazon.in",
        "START_ROW": 2,
        "END_ROW": 12,
        "IMG_PROCESS": lambda url: re.sub(r'\._.*?_\.', '._AC_.', url) if url else ""
    },
    "amazon.com": {
        "SEARCH_URL": "https://www.amazon.com",
        "IMG_CONTAINER": (By.ID, "altImages"),
        "IMG_SELECTOR": "#altImages img",
        "CSV": "scrape_results_Amazon_com_R1.csv",
        "OUTPUT_DIR": r"E:\R3 Factory\Product_images\57 products\Rounds2\Amazon.com",
        "START_ROW": 2,
        "END_ROW": 12,
        "IMG_PROCESS": lambda url: re.sub(r'\._.*?_\.', '._AC_.', url) if url else ""
    },
    # "noon": {
    #     "SEARCH_URL": "https://www.noon.com/uae-en/",
    #     "SEARCH_BOX": (By.ID, "search-input"),
    #     "RESULTS": (By.CSS_SELECTOR, 'div[data-qa="plp-product-box"]'),
    #     "TITLE": (By.CSS_SELECTOR, 'h2[data-qa="plp-product-box-name"]'),
    #     "IMG_CONTAINER": (By.CSS_SELECTOR, "div.GalleryV2_thumbnailInnerCtr__i7TLy"),
    #     "IMG_SELECTOR": "button.GalleryV2_thumbnailElement__3g3ls img",
    #     "LINK": (By.CSS_SELECTOR, 'a.ProductBoxLinkHandler_productBoxLink__FPhjp'),
    #     "CSV": "scrape_results_noon.csv",
    #     "OUTPUT_DIR": r"E:\R3 Factory\Product_images\Bulk Uploads\Rounds2\Noon",
    #     "START_ROW": 2,
    #     "END_ROW": 31,
    #     "IMG_PROCESS": lambda url: re.sub(r'\._.*_\.', '.', url) if url else ""
    # }
}

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

def print_time_elapsed(start_time, message=""):
    """Helper function to display elapsed time in HH:MM:SS format"""
    elapsed = time.time() - start_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"{message} Time elapsed: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")

def create_variant_folder(variant_id, site):
    """Create a folder for storing product images"""
    folder_path = os.path.join(SITE_CONFIG[site]["OUTPUT_DIR"], variant_id)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def download_image(url, save_path):
    """Download an image from URL and save it to disk"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        img_data = requests.get(url, headers=headers).content
        with open(save_path, "wb") as f:
            f.write(img_data)
        print(f"   ✅ Saved: {save_path}")
    except Exception as e:
        print(f"   ❌ Failed to download {url} - {e}")

def shorten_Variant_name(name, MAX_WORD):
    """Shorten product name to first N words for cleaner Google searches"""
    return ' '.join(name.split()[:MAX_WORD])

def scrape_product_images(browser, variant_id, site):
    """
    Scrape all product images from the current Amazon product page.
    This works for all Amazon sites (ae, in, com) since they share the same structure.
    """
    cfg = SITE_CONFIG[site]
    folder_path = create_variant_folder(variant_id, site)
    img_count = 0
    seen = set()

    try:
        # Wait for the image container to load
        WebDriverWait(browser, 8).until(
            EC.presence_of_element_located(cfg["IMG_CONTAINER"])
        )

        # Find all thumbnail images
        thumbnails = browser.find_elements(By.CSS_SELECTOR, cfg["IMG_SELECTOR"])
        print(f"   🔍 Found {len(thumbnails)} thumbnails.")

        # Skip first thumbnail (usually a video or duplicate)
        for thumb in thumbnails[1:]:
            try:
                src = thumb.get_attribute("src")
                if not src or "transparent" in src:
                    continue

                # Convert thumbnail URL to high-resolution version
                high_res_url = cfg["IMG_PROCESS"](src)

                # Skip duplicates
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
    """
    MODIFIED MAIN FUNCTION - Now uses Google search instead of direct Amazon search
    
    The key change: Instead of going to Amazon and searching there, we:
    1. Search on Google for the product + "Dubai"
    2. Extract the Amazon product URL from Google results
    3. Go directly to that exact product page
    4. Scrape the images
    
    This eliminates the need for complex product matching logic because
    Google already finds the exact product page for us!
    """
    cfg = SITE_CONFIG[site]
    total_start_time = time.time()
    print(f"🚀 Starting {site} scraping process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Using geo-keyword: '{GEO_KEYWORD}' to prioritize amazon.ae results\n")

    # Read the Excel file containing product information
    full_df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    full_df = full_df.iloc[SITE_CONFIG[site]["START_ROW"]-2:SITE_CONFIG[site]["END_ROW"]]

    output_csv = cfg["CSV"]
    
    # Check if we've already processed some products (resume functionality)
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

    # Set up Chrome browser with anti-detection measures
    options = Options()
    options.add_argument("--start-maximized")
    
    # Critical anti-detection settings
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Set a realistic user agent (makes browser look like a real Chrome browser)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    
    # Hide webdriver property that Google checks
    browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })

    file_exists = os.path.exists(output_csv)

    # Process each product from the Excel file
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

        print(f"\n{'='*80}")
        print(f"🔎 Product: {full_Variant_name}")
        print(f"🆔 Variant ID: {variant_id}")
        print(f"📝 Search query: {variant_name}")
        print(f"{'='*80}")

        try:
            # ============ NEW APPROACH: Search via Google ============
            # This is the major change! Instead of going to Amazon and searching,
            # we search Google and let Google find the exact Amazon product page
            
            product_url, detected_site = search_google_and_get_amazon_url(variant_name, browser)
            
            if product_url:
                # Success! Google found an Amazon product page for us
                print(f"   📦 Found product on {detected_site}")
                matched_product_name = f"Product from {detected_site} (via Google)"
                
                # Now open this exact product page in a new tab
                # No need for matching logic - Google already found the right product!
                scrape_start = time.time()
                browser.execute_script("window.open(arguments[0]);", product_url)
                WebDriverWait(browser, 5).until(lambda d: len(d.window_handles) > 1)
                browser.switch_to.window(browser.window_handles[-1])

                # Scrape images from this product page
                if scrape_product_images(browser, variant_id, detected_site):
                    status = "Done"
                    print(f"   ✅ Successfully scraped images!")
                else:
                    status = "Images Failed"
                    print(f"   ⚠️  Failed to scrape images")

                # Close the product tab and return to Google search tab
                browser.close()
                browser.switch_to.window(browser.window_handles[0])
                print_time_elapsed(scrape_start, "   Scraping completed")
            else:
                # No Amazon URL found in Google results
                print("   ⚠️  No Amazon product found via Google search")
                matched_product_name = ""
                status = "Not Found"

            # Wait a bit before next search to appear more human-like
            # This also helps avoid Google's rate limiting
            wait_time = random.randint(3, 6)
            print(f"   ⏳ Waiting {wait_time} seconds before next search...")
            time.sleep(wait_time)

        except Exception as e:
            print(f"   ❌ Error processing {variant_name}: {e}")
            status = "Error"
            
        # Save results to CSV after each product
        new_row = pd.DataFrame([{
            "variant_id": variant_id,
            "variant_name": full_Variant_name,
            "status": status,
            "Matched_Product_Name": matched_product_name,
            "url": product_url
        }])

        new_row.to_csv(output_csv, mode='a', header=not file_exists, index=False)
        file_exists = True

        print_time_elapsed(product_start_time, "   ⏱️  Product processing completed")

    browser.quit()
    print(f"\n{'='*80}")
    print(f"📄 Results saved to {output_csv}")
    print_time_elapsed(total_start_time, f"🏁 {site} scraping completed")
    print(f"🕒 Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🌐 AMAZON PRODUCT SCRAPER (Google Search Mode)")
    print("="*80)
    print("\nThis scraper uses Google search to find exact Amazon product pages,")
    print("eliminating the need for complex product matching algorithms.")
    print(f"\nGeo-targeting: Using '{GEO_KEYWORD}' to prioritize amazon.ae results")
    print("="*80 + "\n")
    
    site_choice = input("Enter site config to use (amazon.ae / amazon.in / amazon.com / noon): ").strip().lower()
    
    if site_choice in SITE_CONFIG:
        search_and_scrape(site_choice)
    else:
        print("❌ Invalid choice. Please choose from: amazon.ae, amazon.in, amazon.com, or noon")