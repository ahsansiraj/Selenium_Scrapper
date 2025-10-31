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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rapidfuzz import fuzz

# ---------- CONFIG ----------
EXCEL_FILE = "Book1.xlsx"
SHEET_NAME = "Sheet3"
BASE_DIR = r"E:\R3 Factory\Product_images\Mobile"
CHROME_DRIVER_PATH = r"E:\R3 Factory\Selenium_Prodcut_Scrapper\chromedriver.exe"
SEARCH_URL = "https://www.amazon.ae"
WAIT_TIME = 10  # Increased wait time for better reliability
MATCH_THRESHOLD = 90
MAX_PRODUCTS = 5
OUTPUT_CSV = "scrape_results2.csv"
# ----------------------------

def print_time_elapsed(start_time, message=""):
    """Helper function to print elapsed time"""
    elapsed = time.time() - start_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"{message} Time elapsed: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")

def create_variant_folder(variant_id):
    folder_path = os.path.join(BASE_DIR, variant_id)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def download_image(url, save_path):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        img_data = requests.get(url, headers=headers).content
        with open(save_path, "wb") as f:
            f.write(img_data)
        print(f"   ✅ Saved: {save_path}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to download {url} - {e}")
        return False

def shorten_variant_name(name, max_words=12):
    return ' '.join(name.split()[:max_words])

def extract_high_res_url(thumb_url):
    return re.sub(r'\._.*?_\.', '._SL1500_.', thumb_url)

def scrape_product_images(browser, variant_id):
    folder_path = create_variant_folder(variant_id)
    img_count = 0
    seen = set()

    try:
        WebDriverWait(browser, WAIT_TIME).until(
            EC.presence_of_element_located((By.ID, "altImages"))
        )

        thumbnails = browser.find_elements(By.CSS_SELECTOR, "#altImages img")
        print(f"   🔍 Found {len(thumbnails)} thumbnails.")

        for thumb in thumbnails:
            try:
                src = thumb.get_attribute("src")
                if not src or "transparent" in src:
                    continue

                high_res_url = extract_high_res_url(src)

                if high_res_url in seen:
                    continue
                seen.add(high_res_url)

                img_count += 1
                save_path = os.path.join(folder_path, f"image_{img_count}.jpg")
                if not download_image(high_res_url, save_path):
                    continue

            except Exception as e:
                print(f"   ⚠️ Skipping thumbnail due to error: {e}")
                continue

        return img_count > 0

    except Exception as e:
        print(f"   ❌ Error scraping images - {e}")
        return False

def amazon_search_and_scrape():
    total_start_time = time.time()
    print(f"🚀 Starting scraping process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
        df = df.head(MAX_PRODUCTS)
        results = []

        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        service = Service(CHROME_DRIVER_PATH)
        browser = webdriver.Chrome(service=service, options=options)

        for index, row in df.iterrows():
            product_start_time = time.time()
            variant_id = str(row['variant_id']).strip()
            full_variant_name = str(row['variant_name']).strip()
            variant_name = shorten_variant_name(full_variant_name)
            product_url = ""
            status = "Not Done"
            amazon_title = ""

            if not variant_id or not variant_name:
                print(f"   ⚠ Skipping due to missing variant_id or variant_name")
                results.append({
                    "variant_id": variant_id,
                    "variant_name": variant_name,
                    "status": "Skipped - Missing Data",
                    "product_url": "",
                    "amazon_title": ""
                })
                continue

            print(f"\n🔎 Processing product {index+1}/{len(df)}: {variant_name} (ID: {variant_id})")
            
            try:
                # Search phase
                search_start = time.time()
                browser.get(SEARCH_URL)
                WebDriverWait(browser, WAIT_TIME).until(
                    EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
                )
                search_box = browser.find_element(By.ID, "twotabsearchtextbox")
                search_box.clear()
                search_box.send_keys(variant_name)
                browser.find_element(By.ID, "nav-search-submit-button").click()
                print_time_elapsed(search_start, "   Search completed")

                # Matching phase - Improved element location
                match_start = time.time()
                WebDriverWait(browser, WAIT_TIME).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']"))
                )
                search_results = browser.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
                best_match_elem = None
                best_score = 0

                # In your amazon_search_and_scrape function, replace the title extraction part with:

                for result in search_results[:20]:  # Check top 20 results
                    try:
                        title_text = get_amazon_product_title(result)
                        if not title_text or title_text == "Title Not Found":
                            continue
                            
                        score = fuzz.partial_ratio(variant_name.lower(), title_text.lower())
                        if score > best_score:
                            best_score = score
                            best_match_elem = result
                            amazon_title = title_text  # Store the matched title
                    except Exception as e:
                        print(f"   ⚠️ Error processing result: {str(e)[:100]}")
                        continue

                print_time_elapsed(match_start, "   Matching completed")
                print(f"   🔍 Best match score: {best_score}")

                if best_match_elem and best_score >= MATCH_THRESHOLD:
                    print(f"   🎯 Selected product: {amazon_title}")
                    
                    try:
                        link_elem = best_match_elem.find_element(By.CSS_SELECTOR, "h2 a")
                        product_url = link_elem.get_attribute("href")
                        
                        # Scraping phase
                        scrape_start = time.time()
                        browser.execute_script("window.open(arguments[0]);", product_url)
                        WebDriverWait(browser, WAIT_TIME).until(lambda d: len(d.window_handles) > 1)
                        browser.switch_to.window(browser.window_handles[-1])

                        if scrape_product_images(browser, variant_id):
                            status = "Done"
                        else:
                            status = "Partial - Images Failed"

                        browser.close()
                        browser.switch_to.window(browser.window_handles[0])
                        print_time_elapsed(scrape_start, "   Scraping completed")

                    except Exception as e:
                        print(f"   ❌ Error opening product page: {str(e)[:100]}")
                        status = f"Error - Page Navigation Failed"
                else:
                    print(f"   ⚠ No good match found (best score: {best_score})")
                    status = "No Match Found"

                time.sleep(random.uniform(3, 6))  # More natural delay

            except Exception as e:
                print(f"   ❌ Error processing {variant_name} - {str(e)[:100]}")
                status = f"Error - {str(e)[:50]}"

            results.append({
                "variant_id": variant_id,
                "variant_name": variant_name,
                "status": status,
                "product_url": product_url,
                "amazon_title": amazon_title  # Added the matched Amazon title
            })
            
            print_time_elapsed(product_start_time, "   Product processing completed")

        browser.quit()
        
        # Save results with additional column
        pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)
        print(f"\n📄 Results saved to {OUTPUT_CSV}")
        
    except Exception as e:
        print(f"❌ Fatal error in main scraping process: {str(e)}")
    
    print_time_elapsed(total_start_time, "🏁 Total scraping completed")
    print(f"🕒 Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
def get_amazon_product_title(result_element):
    """Robust method to extract product title from Amazon search result"""
    try:
        # Try multiple possible selectors for the title
        selectors = [
            "h2 a span",  # Most common pattern
            "h2 span",    # Alternative pattern
            "h2",         # Fallback to direct h2 text
            "a span.a-text-normal"  # Another common pattern
        ]
        
        for selector in selectors:
            try:
                title_elem = result_element.find_element(By.CSS_SELECTOR, selector)
                title_text = title_elem.get_attribute("textContent").strip()
                if title_text:
                    return title_text
            except:
                continue
        
        # If all selectors fail, try getting text from the h2 directly
        return result_element.find_element(By.TAG_NAME, "h2").text.strip()
    except Exception as e:
        print(f"   ⚠️ Couldn't extract title: {str(e)[:100]}")
        return "Title Not Found"
if __name__ == "__main__":
    amazon_search_and_scrape()