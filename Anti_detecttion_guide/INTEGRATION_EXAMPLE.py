# Quick Integration Example for Scrapper.py

# ============================================================================
# STEP 1: Add this import at the top of your Scrapper.py file
# ============================================================================

from anti_detection import (
    AntiDetectionConfig, 
    AntiDetectionBrowser,
    UserAgentPool,
    HumanBehaviorSimulator
)


# ============================================================================
# STEP 2: Replace the browser initialization in search_and_scrape() function
# ============================================================================

# FIND THIS CODE IN YOUR FILE (around line 380-400):
"""
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
"""

# REPLACE IT WITH THIS:
"""
    # Initialize anti-detection configuration
    print("🛡️  Initializing anti-detection measures...")
    config = AntiDetectionConfig()
    config.use_user_agent_rotation = True          # ✓ Rotate user agents
    config.use_fingerprint_masking = True          # ✓ Hide webdriver detection
    config.use_proxy_rotation = False              # ✗ Set to True if using proxies
    config.simulate_human_behavior = True          # ✓ Simulate human behavior
    
    # Setup anti-detection browser
    anti_detection = AntiDetectionBrowser(config)
    browser = anti_detection.setup_anti_detection_browser(headless=False)
    human_simulator = anti_detection.human_simulator
    
    print("✅ Anti-detection browser ready\n")
"""


# ============================================================================
# STEP 3: Update search_google_and_get_amazon_url() function
# ============================================================================

# In the search_google_and_get_amazon_url() function, find this code:
"""
        # Step 4: Type the search query character by character (like a human)
        search_box.clear()
        for char in search_query:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.25))  # Random typing speed
"""

# REPLACE WITH (to use human-like typing):
"""
        # Step 4: Type the search query with realistic human-like delays
        search_box.clear()
        
        # Use human simulator if available (better realism)
        if 'human_simulator' in locals() and human_simulator:
            human_simulator.type_slowly(search_box, search_query, min_delay=0.05, max_delay=0.25)
        else:
            for char in search_query:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.25))
"""


# ============================================================================
# STEP 4: Optional - Enable Proxy Support
# ============================================================================

# If you want to use proxies (add this right after browser setup):

"""
    # Optional: Enable proxy rotation if you have proxies available
    
    # Option A: Use free proxies (less reliable but free)
    # Uncomment to enable:
    # anti_detection.proxy_rotation.load_free_proxies(limit=30)
    # print("[+] Free proxies loaded\n")
    
    # Option B: Use your paid proxies (highly recommended)
    # Uncomment and add your proxies:
    # paid_proxies = [
    #     "http://proxy1.example.com:8080",
    #     "http://proxy2.example.com:8080", 
    #     "http://proxy3.example.com:8080",
    # ]
    # anti_detection.proxy_rotation.add_paid_proxies(paid_proxies)
    # config.use_proxy_rotation = True
    # print("[+] Paid proxies configured\n")
"""


# ============================================================================
# STEP 5: Add human behavior simulation in wait loops
# ============================================================================

# In search_google_and_get_amazon_url(), after getting search results:

"""
        if not search_results:
            print("   ❌ No search results found...")
            return None, None
        
        # Add human-like interaction before extracting URLs
        if 'human_simulator' in locals() and human_simulator:
            print("   👤 Simulating human reading behavior...")
            human_simulator.human_like_page_interaction()
"""


# ============================================================================
# STEP 6: Add delays between requests
# ============================================================================

# In the main scraping loop, after each product:

"""
        # Human-like delay before next search
        if 'human_simulator' in locals() and human_simulator:
            print(f"   ⏳ Human-like pause...")
            human_simulator.random_sleep(min_sec=3, max_sec=8)
        else:
            wait_time = random.randint(2, 6)
            time.sleep(wait_time)
"""


# ============================================================================
# COMPLETE EXAMPLE: Updated search_and_scrape() beginning
# ============================================================================

def search_and_scrape_with_anti_detection(site):
    """Updated main function with anti-detection measures"""
    
    cfg = SITE_CONFIG[site]
    total_start_time = time.time()
    print(f"🚀 Starting {site} scraping process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Using geo-keyword: '{GEO_KEYWORD}' to prioritize amazon.ae results\n")

    # Read the Excel file
    full_df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    full_df = full_df.iloc[SITE_CONFIG[site]["START_ROW"]-2:SITE_CONFIG[site]["END_ROW"]]

    output_csv = cfg["CSV"]
    
    # Resume from previous run if exists
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

    # ========== ANTI-DETECTION SETUP ==========
    print("\n🛡️  Initializing anti-detection measures...")
    config = AntiDetectionConfig()
    config.use_user_agent_rotation = True
    config.use_fingerprint_masking = True
    config.use_proxy_rotation = False  # Set to True if using proxies
    config.simulate_human_behavior = True
    
    # Setup anti-detection browser
    anti_detection = AntiDetectionBrowser(config)
    browser = anti_detection.setup_anti_detection_browser(headless=False)
    human_simulator = anti_detection.human_simulator
    
    print("✅ Anti-detection browser ready\n")
    # ========== END ANTI-DETECTION SETUP ==========

    file_exists = os.path.exists(output_csv)

    # Process each product
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
            # Search via Google (anti-detection measures activate automatically!)
            product_url, detected_site = search_google_and_get_amazon_url(variant_name, browser)
            
            if product_url:
                print(f"   📦 Found product on {detected_site}")
                matched_product_name = f"Product from {detected_site}"
                
                # Simulate human reading results
                if human_simulator:
                    human_simulator.human_like_page_interaction()
                
                # Open product page in new tab
                scrape_start = time.time()
                browser.execute_script("window.open(arguments[0]);", product_url)
                WebDriverWait(browser, 5).until(lambda d: len(d.window_handles) > 1)
                browser.switch_to.window(browser.window_handles[-1])

                # Scrape images
                if scrape_product_images(browser, variant_id, detected_site):
                    status = "Done"
                    print(f"   ✅ Successfully scraped images!")
                else:
                    status = "Images Failed"

                browser.close()
                browser.switch_to.window(browser.window_handles[0])
            else:
                print("   ⚠️  No Amazon product found via Google search")
                matched_product_name = ""
                status = "Not Found"

            # Human-like pause before next search
            if human_simulator:
                print(f"   ⏳ Realistic pause before next search...")
                human_simulator.random_sleep(min_sec=3, max_sec=8)

        except Exception as e:
            print(f"   ❌ Error: {e}")
            status = "Error"
            
        # Save results
        new_row = pd.DataFrame([{
            "variant_id": variant_id,
            "variant_name": full_Variant_name,
            "status": status,
            "Matched_Product_Name": matched_product_name,
            "url": product_url
        }])

        new_row.to_csv(output_csv, mode='a', header=not file_exists, index=False)
        file_exists = True

    browser.quit()
    print(f"\n✅ Scraping completed! Results saved to {output_csv}")


# ============================================================================
# Usage
# ============================================================================

if __name__ == "__main__":
    # Just call it as usual:
    site_choice = input("Enter site (amazon.ae / amazon.in / amazon.com): ").strip().lower()
    
    if site_choice in SITE_CONFIG:
        search_and_scrape_with_anti_detection(site_choice)  # Now with anti-detection!
    else:
        print("Invalid choice")
