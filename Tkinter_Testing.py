import os
import re
import time
import random
import threading
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
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext

# ---------- CONFIG (defaults; you can change in UI) ----------
BASE_DIR = r"E:\R3 Factory\Product_images\Laptop"
CHROME_DRIVER_PATH = r"E:\R3 Factory\Selenium_Prodcut_Scrapper\chromedriver.exe"
SEARCH_URL = "https://www.amazon.ae"
WAIT_TIME = 15
MATCH_THRESHOLD = 95
OUTPUT_CSV = "scrape_results4.csv"
# -------------------------------------------------------------

def threaded_safe_log(root, text_widget, message):
    """Schedule a log insert on the Tk mainloop (thread-safe)."""
    def inner():
        text_widget.insert(tk.END, message + "\n")
        text_widget.see(tk.END)
    root.after(0, inner)

def print_time_elapsed(start_time):
    elapsed = time.time() - start_time
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"Time elapsed: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def create_variant_folder(base_dir, variant_id):
    folder_path = os.path.join(base_dir, variant_id)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def download_image(url, save_path, log_fn):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(resp.content)
        log_fn(f"   ✅ Saved: {save_path}")
    except Exception as e:
        log_fn(f"   ❌ Failed to download {url} - {e}")

def shorten_variant_name(name, max_words=12):
    return ' '.join(name.split()[:max_words])

def extract_high_res_url(thumb_url):
    # Attempts to convert thumbnail to a high-res variant
    return re.sub(r'\._.*?_\.', '._SL1500_.', thumb_url)

def scrape_product_images(browser, variant_id, base_dir, wait_time, log_fn, stop_event):
    folder_path = create_variant_folder(base_dir, variant_id)
    img_count = 0
    seen = set()
    try:
        WebDriverWait(browser, wait_time).until(
            EC.presence_of_element_located((By.ID, "altImages"))
        )
        thumbnails = browser.find_elements(By.CSS_SELECTOR, "#altImages img")
        log_fn(f"   🔍 Found {len(thumbnails)} thumbnails.")
        for thumb in thumbnails:
            if stop_event.is_set():
                log_fn("   ⚠ Stop requested while scraping images.")
                return img_count > 0
            try:
                src = thumb.get_attribute("src")
                if not src or "transparent" in src:
                    continue
                high_res = extract_high_res_url(src)
                if high_res in seen:
                    continue
                seen.add(high_res)
                img_count += 1
                save_path = os.path.join(folder_path, f"image_{img_count}.jpg")
                download_image(high_res, save_path, log_fn)
                # small delay between downloads
                time.sleep(0.4)
            except Exception as e:
                log_fn(f"   ⚠ Skipping thumbnail due to error: {e}")
                continue
        if img_count == 0:
            log_fn("   ⚠ No images downloaded for this product.")
        return img_count > 0
    except Exception as e:
        log_fn(f"   ❌ Error scraping images - {e}")
        return False

def amazon_search_and_scrape_thread(excel_file, start_row, end_row,
                                    base_dir, chrome_driver_path,
                                    wait_time, match_threshold, output_csv,
                                    log_callback, stop_event):
    total_start = time.time()
    log_callback(f"🚀 Starting scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        log_callback(f"❌ Failed to open Excel file: {e}")
        return

    # slice rows (1-indexed rows from UI)
    df_slice = df.iloc[start_row - 1:end_row]

    # resume: skip already processed variant_ids in CSV
    if os.path.exists(output_csv) and os.path.getsize(output_csv) > 0:
        try:
            processed_df = pd.read_csv(output_csv)
            processed_ids = set(processed_df['variant_id'].astype(str))
            df_slice = df_slice[~df_slice['variant_id'].astype(str).isin(processed_ids)]
            log_callback(f"ℹ️ Resuming: {len(processed_ids)} previously processed - skipping them.")
        except Exception as e:
            log_callback(f"⚠ Could not read existing CSV for resume: {e}")

    options = Options()
    options.add_argument("--start-maximized")
    # optional: run headless? Not by default because you may want to see browser
    service = Service(chrome_driver_path)
    browser = None
    file_exists = os.path.exists(output_csv)

    try:
        browser = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        log_callback(f"❌ Could not start ChromeDriver: {e}")
        return

    try:
        for idx, row in df_slice.iterrows():
            if stop_event.is_set():
                log_callback("⏸️ Stop requested — finishing early.")
                break

            prod_start = time.time()
            variant_id = str(row.get('variant_id', '')).strip()
            full_variant_name = str(row.get('variant_name', '')).strip()
            variant_name = shorten_variant_name(full_variant_name)
            product_url = ""
            status = "Not Done"

            if not variant_id or not variant_name:
                log_callback("⚠ Skipping row with missing variant_id or variant_name.")
                continue

            log_callback(f"\n🔎 Searching for: {variant_name} (Variant ID: {variant_id})\n   📝 Full name: {full_variant_name}")

            try:
                # Search
                s_start = time.time()
                browser.get(SEARCH_URL)
                WebDriverWait(browser, wait_time).until(
                    EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
                )
                search_box = browser.find_element(By.ID, "twotabsearchtextbox")
                search_box.clear()
                search_box.send_keys(variant_name)
                # click search
                # If nav-search-submit-button exists (new layout) use it, else try pressing Enter
                try:
                    browser.find_element(By.ID, "nav-search-submit-button").click()
                except:
                    search_box.send_keys("\n")
                log_callback(f"   Search completed ({print_time_elapsed(s_start)})")

                # Matching
                m_start = time.time()
                WebDriverWait(browser, wait_time).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[@data-component-type='s-search-result']"))
                )
                results = browser.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")
                best_elem = None
                best_score = 0
                best_title = ""
                for result in results[:20]:
                    if stop_event.is_set():
                        break
                    try:
                        title_elem = result.find_element(By.TAG_NAME, "h2")
                        title_text = title_elem.text.strip()
                        score = fuzz.partial_ratio(variant_name.lower(), title_text.lower())
                        if score > best_score:
                            best_score = score
                            best_elem = result
                            best_title = title_text
                        log_callback(f"   🔎 Match Score: {score} — {title_text[:80]}")
                    except Exception:
                        continue
                log_callback(f"   Matching completed ({print_time_elapsed(m_start)})")

                if best_elem and best_score >= match_threshold and not stop_event.is_set():
                    log_callback(f"   🎯 Best match score: {best_score}")
                    try:
                        link = best_elem.find_element(By.TAG_NAME, "a").get_attribute("href")
                        product_url = link
                        log_callback(f"   📦 Picked Amazon product: {best_title}")
                        # open new tab and scrape
                        browser.execute_script("window.open(arguments[0]);", product_url)
                        WebDriverWait(browser, wait_time).until(lambda d: len(d.window_handles) > 1)
                        browser.switch_to.window(browser.window_handles[-1])

                        scraped = scrape_product_images(browser, variant_id, base_dir, wait_time, log_callback, stop_event)
                        if scraped:
                            status = "Done"

                        # close product tab and return
                        browser.close()
                        browser.switch_to.window(browser.window_handles[0])
                        log_callback(f"   Scraping completed ({print_time_elapsed(m_start)})")
                    except Exception as e:
                        log_callback(f"   ❌ Error opening product page: {e}")
                else:
                    log_callback("   ⚠ No good match found.")

                # write immediate row to CSV (append)
                new_row = pd.DataFrame([{
                    "variant_id": variant_id,
                    "variant_name": variant_name,
                    "status": status,
                    "url": product_url
                }])
                new_row.to_csv(output_csv, mode='a', header=not file_exists, index=False)
                file_exists = True

                log_callback(f"   Product processing completed ({print_time_elapsed(prod_start)})")

                # polite random delay and respect stop
                for _ in range(random.randint(5, 8)):
                    if stop_event.is_set():
                        break
                    time.sleep(1)

            except Exception as e:
                log_callback(f"   ❌ Error processing {variant_name} - {e}")
                # still append failed row
                new_row = pd.DataFrame([{
                    "variant_id": variant_id,
                    "variant_name": variant_name,
                    "status": "Error",
                    "url": product_url
                }])
                new_row.to_csv(output_csv, mode='a', header=not file_exists, index=False)
                file_exists = True
                # small sleep
                time.sleep(2)

        log_callback(f"\n📄 Partial results appended to {output_csv}")
    finally:
        try:
            if browser:
                browser.quit()
        except Exception:
            pass
        log_callback(f"🏁 Finished run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (total {print_time_elapsed(total_start)})")

# ----------------- Tkinter GUI -----------------
class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Amazon Image Scraper - Tk")
        self.excel_file = ""
        self.thread = None
        self.stop_event = threading.Event()

        # File selection
        frm_top = tk.Frame(root)
        frm_top.pack(fill="x", padx=8, pady=6)
        tk.Button(frm_top, text="📂 Select Excel", command=self.select_file).pack(side="left")
        self.file_label = tk.Label(frm_top, text="No file selected", anchor="w")
        self.file_label.pack(side="left", padx=6)

        # Options
        frm_opts = tk.Frame(root)
        frm_opts.pack(fill="x", padx=8, pady=6)
        tk.Label(frm_opts, text="Start Row:").pack(side="left")
        self.start_entry = tk.Entry(frm_opts, width=6); self.start_entry.pack(side="left", padx=4)
        tk.Label(frm_opts, text="End Row:").pack(side="left")
        self.end_entry = tk.Entry(frm_opts, width=6); self.end_entry.pack(side="left", padx=4)
        tk.Label(frm_opts, text="MATCH%:").pack(side="left", padx=(10,0))
        self.match_entry = tk.Entry(frm_opts, width=4); self.match_entry.pack(side="left", padx=4)
        self.match_entry.insert(0, str(MATCH_THRESHOLD))

        tk.Label(frm_opts, text="WAIT(s):").pack(side="left", padx=(10,0))
        self.wait_entry = tk.Entry(frm_opts, width=4); self.wait_entry.pack(side="left", padx=4)
        self.wait_entry.insert(0, str(WAIT_TIME))

        tk.Label(frm_opts, text="Rows Max (for quick test):").pack(side="left", padx=(10,0))
        self.max_label = tk.Label(frm_opts, text="use Start/End rows")
        self.max_label.pack(side="left", padx=4)

        # Buttons
        frm_buttons = tk.Frame(root)
        frm_buttons.pack(fill="x", padx=8, pady=6)
        self.start_btn = tk.Button(frm_buttons, text="🚀 Start Scraping", command=self.start_scraping)
        self.start_btn.pack(side="left", padx=4)
        self.stop_btn = tk.Button(frm_buttons, text="⏹ Stop", state="disabled", command=self.stop_scraping)
        self.stop_btn.pack(side="left", padx=4)
        tk.Button(frm_buttons, text="Open CSV", command=self.open_csv).pack(side="left", padx=4)

        # Log area
        self.log = scrolledtext.ScrolledText(root, wrap="word", height=24)
        self.log.pack(fill="both", expand=True, padx=8, pady=6)

    def select_file(self):
        fp = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if fp:
            self.excel_file = fp
            self.file_label.config(text=os.path.basename(fp))
            threaded_safe_log(self.root, self.log, f"📄 Selected: {fp}")

    def log_fn(self, message):
        threaded_safe_log(self.root, self.log, message)

    def start_scraping(self):
        if not self.excel_file:
            messagebox.showerror("Error", "Select an Excel file first.")
            return
        try:
            start_row = int(self.start_entry.get())
            end_row = int(self.end_entry.get())
        except Exception:
            messagebox.showerror("Error", "Enter valid start and end row numbers.")
            return
        try:
            match_threshold = int(self.match_entry.get())
        except:
            match_threshold = MATCH_THRESHOLD
        try:
            wait_time = int(self.wait_entry.get())
        except:
            wait_time = WAIT_TIME

        # disable start button
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.stop_event.clear()

        # launch thread
        args = (self.excel_file, start_row, end_row,
                BASE_DIR, CHROME_DRIVER_PATH,
                wait_time, match_threshold, OUTPUT_CSV,
                self.log_fn, self.stop_event)
        self.thread = threading.Thread(target=amazon_search_and_scrape_thread, args=args, daemon=True)
        self.thread.start()

        # start watcher to re-enable UI when thread ends
        self.root.after(1000, self._watch_thread)

    def _watch_thread(self):
        if self.thread and self.thread.is_alive():
            self.root.after(1000, self._watch_thread)
        else:
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            threaded_safe_log(self.root, self.log, "✅ Background thread finished.")

    def stop_scraping(self):
        if messagebox.askyesno("Stop", "Stop scraping? This will finish the current product and stop."):
            self.stop_event.set()
            self.stop_btn.config(state="disabled")
            threaded_safe_log(self.root, self.log, "⏳ Stop requested...")

    def open_csv(self):
        if os.path.exists(OUTPUT_CSV):
            os.startfile(os.path.abspath(OUTPUT_CSV))
        else:
            messagebox.showinfo("No CSV", "Output CSV not found yet.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperGUI(root)
    root.geometry("900x700")
    root.mainloop()
