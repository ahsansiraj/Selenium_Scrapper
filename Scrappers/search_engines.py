import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


# Geographic keyword for prioritizing regional Amazon sites
# "Dubai" will make Google prioritize amazon.ae results
GEO_KEYWORD = "Dubai"

def search_google_and_get_amazon_url(Variant_name, browser, geo_keyword=GEO_KEYWORD):
    """
    Search Google for Amazon product URLs with enhanced anti-detection measures.
    
    This function implements several strategies to avoid Google's bot detection:
    - Realistic typing speed (humans don't type instantly)
    - Random delays between actions
    - Multiple CSS selectors as fallbacks
    - Better error handling and debugging
    
    Args:
        Variant_name: The product name to search for
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
        search_query = f"{Variant_name} amazon {geo_keyword}"
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
        time.sleep(random.uniform(2, 4))
        for char in search_query:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Random typing speed
        
        time.sleep(random.uniform(0.5, 1.5))  # Pause before hitting enter
        search_box.send_keys(Keys.ENTER)
        

        # Step 5: Wait for search results to load with multiple strategies
        print("   ⏳ Waiting for search results...")
        time.sleep(random.uniform(2,6))  # Give Google time to fully render

        # NEW: Simple human-like scrolling
        print("   📜 Scanning results...")
        for _ in range(random.randint(2, 4)):  # 2-4 scroll actions
            scroll_distance = random. randint(300, 600)
            browser.execute_script(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
            time.sleep(random.uniform(0.6, 1.2))

        # Scroll back to top
        browser.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
        time.sleep(random.uniform(0.8, 1.5))

        
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
        
        # # Priority 2: amazon.in
        # for url in all_urls:
        #     if "amazon.in" in url and "/dp/" in url:
        #         print(f"   ✅ Found amazon.in URL")
        #         return url, "amazon.in"
        
        # # Priority 3: amazon.com
        # for url in all_urls:
        #     if "amazon.com" in url and "/dp/" in url:
        #         print(f"   ✅ Found amazon.com URL")
        #         return url, "amazon.com"
        
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

def search_google_and_get_noon_url(Variant_name, browser, geo_keyword=GEO_KEYWORD):
    """
    Search Google for Amazon product URLs with enhanced anti-detection measures.
    
    This function implements several strategies to avoid Google's bot detection:
    - Realistic typing speed (humans don't type instantly)
    - Random delays between actions
    - Multiple CSS selectors as fallbacks
    - Better error handling and debugging
    
    Args:
        Variant_name: The product name to search for
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
        search_query = f"{Variant_name} noon {geo_keyword}"
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
        time.sleep(random.uniform(2, 4))
        for char in search_query:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Random typing speed
        
        time.sleep(random.uniform(0.5, 1.5))  # Pause before hitting enter
        search_box.send_keys(Keys.ENTER)
        

        # Step 5: Wait for search results to load with multiple strategies
        print("   ⏳ Waiting for search results...")
        time.sleep(random.uniform(2,6))  # Give Google time to fully render

        # NEW: Simple human-like scrolling
        print("   📜 Scanning results...")
        for _ in range(random.randint(2, 4)):  # 2-4 scroll actions
            scroll_distance = random.randint(300, 600)
            browser.execute_script(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
            time.sleep(random.uniform(0.6, 1.2))

        # Scroll back to top
        browser.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
        time.sleep(random.uniform(0.8, 1.5))

        
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
            if "noon.com" in url and "/dp/" in url:
                print(f"   ✅ Found noon.com URL (boosted by '{geo_keyword}')")
                return url, "noon.com"
        
        # # Priority 2: amazon.in
        # for url in all_urls:
        #     if "amazon.in" in url and "/dp/" in url:
        #         print(f"   ✅ Found amazon.in URL")
        #         return url, "amazon.in"
        
        # # Priority 3: amazon.com
        # for url in all_urls:
        #     if "amazon.com" in url and "/dp/" in url:
        #         print(f"   ✅ Found amazon.com URL")
        #         return url, "amazon.com"
        
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


def search_duckduckgo_and_get_amazon_url(variant_name, browser, geo_keyword=GEO_KEYWORD):
    """
    Search DuckDuckGo instead of Google - much more bot-friendly!
    DuckDuckGo doesn't have aggressive anti-bot measures like Google does.
    """
    try:
        print("   🔍 Searching on DuckDuckGo...")
        browser.get("https://duckduckgo.com")

        time.sleep(random.uniform(2, 4))
        
        search_query = f"{variant_name} amazon.ae {geo_keyword}"
        print(f"   🌍 Search query: '{search_query}'")
        
        # DuckDuckGo's search box has id="searchbox_input"
        search_box = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "searchbox_input"))
        )
        search_box.clear()
        time.sleep(random.uniform(2, 4))
        for char in search_query:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Random typing speed
        
        time.sleep(random.uniform(0.5, 1.0))
        search_box.send_keys(Keys.ENTER)
        
        # Wait for results
        time.sleep(3)
        WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article"))
        )
        
        # Extract URLs from DuckDuckGo results
        search_results = browser.find_elements(By.CSS_SELECTOR, "article a")
        
        all_urls = []
        for result in search_results:
            try:
                url = result.get_attribute("href")
                if url and "amazon" in url and url.startswith("http"):
                    all_urls.append(url)
            except:
                continue
        
        print(f"   📊 Found {len(all_urls)} Amazon URLs")
        
        # Same priority logic
        for url in all_urls:
            if "amazon.ae" in url and "/dp/" in url:
                print(f"   ✅ Found amazon.ae URL")
                return url, "amazon.ae"
        
        # for url in all_urls:
        #     if "amazon.in" in url and "/dp/" in url:
        #         print(f"   ✅ Found amazon.in URL")
        #         return url, "amazon.in"
        
        # for url in all_urls:
        #     if "amazon.com" in url and "/dp/" in url:
        #         print(f"   ✅ Found amazon.com URL")
        #         return url, "amazon.com"
        
        print("   ⚠️  No Amazon URLs found")
        return None, None
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None, None

def search_BING_and_get_amazon_url(variant_name, browser, geo_keyword=GEO_KEYWORD):
    """
    Search Bing for Amazon product URLs.
    
    Bing is often LESS aggressive than Google with bot detection,
    making it a good middle ground between Google and DuckDuckGo.
    
    Args:
        variant_name: The product name to search for
        browser: Selenium webdriver instance
        geo_keyword: Location keyword to append (default: "Dubai")
    
    Returns:
        tuple: (product_url, site_name) if found, or (None, None) if not found
    """
    try:
        # Step 1: Navigate to Bing
        print("   🔍 Navigating to Bing...")
        browser.get("https://www.bing.com")
        time.sleep(random.uniform(2, 4))
        
        # Check for blocking
        page_source = browser.page_source.lower()
        if "captcha" in page_source or "unusual" in page_source:
            print("   ⚠️  Bing detected automation")
            return None, None
        
        # Step 2: Create search query
        search_query = f"{variant_name} amazon {geo_keyword}"
        print(f"   🌍 Bing search query: '{search_query}'")
        
        # Step 3: Find Bing's search box
        # Bing uses id="sb_form_q" or name="q" for search input
        search_box = None
        selectors_to_try = [
            (By.ID, "sb_form_q"),
            (By.NAME, "q"),
            (By.CSS_SELECTOR, "input[name='q']"),
            (By.CSS_SELECTOR, "#sb_form_q"),
            (By.XPATH, "//input[@id='sb_form_q']"),
            (By.XPATH, "//input[@name='q']")
        ]
        
        for selector_type, selector_value in selectors_to_try:
            try:
                search_box = WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                if search_box:
                    print(f"   ✓ Found Bing search box using {selector_type}")
                    break
            except:
                continue
        
        if not search_box:
            print("   ❌ Could not find Bing search box")
            return None, None
        
        # Step 4: Type search query (human-like)
        search_box.clear()
        for char in search_query:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        time.sleep(random.uniform(0.5, 1.0))
        search_box.send_keys(Keys.ENTER)
        
        # Step 5: Wait for results to load
        print("   ⏳ Waiting for Bing results...")
        time.sleep(random.uniform(3, 5))
        
        # Step 6: Human-like scrolling
        print("   📜 Scanning Bing results...")
        for _ in range(random.randint(2, 3)):
            scroll_distance = random.randint(300, 500)
            browser.execute_script(f"window.scrollBy({{top: {scroll_distance}, behavior: 'smooth'}});")
            time.sleep(random.uniform(0.5, 1.0))
        
        # Scroll back to top
        browser.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
        time.sleep(random.uniform(0.5, 1.0))
        
        # Step 7: Extract URLs from Bing results
        # Bing's HTML structure is different from Google!
        # Bing uses these main selectors for organic results:
        # - li.b_algo (main result container)
        # - h2 a (title links)
        # - cite (URL display)
        
        search_results = []
        result_selectors = [
            "li.b_algo a",           # Main organic results links
            "li.b_algo h2 a",        # Title links in results
            "#b_results a",          # All links in results area
            "ol#b_results li a",     # List items in results
        ]
        
        for selector in result_selectors:
            try:
                elements = browser.find_elements(By.CSS_SELECTOR, selector)
                if len(elements) > 5:
                    search_results = elements
                    print(f"   ✓ Found {len(elements)} Bing results using selector: {selector}")
                    break
            except:
                continue
        
        if not search_results:
            print("   ❌ No Bing search results found")
            print("   💡 Current page title:", browser.title)
            
            # Debug screenshot
            try:
                screenshot_path = "bing_error_debug.png"
                browser.save_screenshot(screenshot_path)
                print(f"   📸 Saved debug screenshot: {screenshot_path}")
            except:
                pass
            
            return None, None
        
        # Step 8: Extract and filter URLs
        all_urls = []
        for result in search_results:
            try:
                url = result.get_attribute("href")
                
                # Filter out Bing's own URLs and invalid links
                if url and url.startswith("http") and "bing.com" not in url:
                    all_urls.append(url)
            except:
                continue
        
        print(f"   📊 Extracted {len(all_urls)} URLs from Bing")
        
        # Debug: Show sample URLs
        if all_urls:
            print(f"   🔗 Sample URLs found:")
            for url in all_urls[:5]:
                try:
                    domain = url.split('/')[2] if len(url.split('/')) > 2 else url[:50]
                    print(f"      • {domain}")
                except:
                    print(f"      • {url[:50]}...")
        
        # Step 9: Filter and prioritize Amazon URLs
        # Priority 1: amazon.ae
        for url in all_urls:
            if "amazon.ae" in url and "/dp/" in url:
                print(f"   ✅ Found amazon.ae URL from Bing")
                return url, "amazon.ae"
        
        # Priority 2: amazon.in
        for url in all_urls:
            if "amazon.in" in url and "/dp/" in url:
                print(f"   ✅ Found amazon.in URL from Bing")
                return url, "amazon.in"
        
        # Priority 3: amazon.com
        for url in all_urls:
            if "amazon.com" in url and "/dp/" in url:
                print(f"   ✅ Found amazon.com URL from Bing")
                return url, "amazon.com"
        
        print("   ⚠️  No Amazon URLs found in Bing results")
        return None, None
        
    except Exception as e:
        print(f"   ❌ Error during Bing search: {str(e)}")
        print(f"   📍 Error type: {type(e).__name__}")
        
        try:
            print(f"   🌐 Current URL: {browser.current_url}")
            print(f"   📄 Page title: {browser.title}")
        except:
            pass
        
        return None, None

def search_duckduckgo_and_get_noon_url(variant_name, browser, geo_keyword=GEO_KEYWORD):
    """
    Search DuckDuckGo instead of Google - much more bot-friendly!
    DuckDuckGo doesn't have aggressive anti-bot measures like Google does.
    """


    try:
        print("   🔍 Searching on DuckDuckGo...")
        browser.get("https://duckduckgo.com")

        time.sleep(random.uniform(2, 4))
        
        search_query = f"{variant_name} noon.com {geo_keyword}"
        print(f"   🌍 Search query: '{search_query}'")
        
        # DuckDuckGo's search box has id="searchbox_input"
        search_box = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "searchbox_input"))
        )
        search_box.clear()
        time.sleep(random.uniform(2, 4))
        for char in search_query:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Random typing speed
        
        time.sleep(random.uniform(0.5, 1.0))
        search_box.send_keys(Keys.ENTER)
        
        # Wait for results
        time.sleep(3)
        WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article"))
        )
        
        # Extract URLs from DuckDuckGo results
        search_results = browser.find_elements(By.CSS_SELECTOR, "article a")
        
        all_urls = []
        for result in search_results:
            try:
                url = result.get_attribute("href")
                if url and "noon.com" in url and url.startswith("http"):
                    all_urls.append(url)
            except:
                continue
        
        print(f"   📊 Found {len(all_urls)} Noon URLs")
        
        # Same priority logic
        for url in all_urls:
            if "noon.com" in url and "/dp/" in url:
                print(f"   ✅ Found noon.com URL")
                return url, "noon.com"
        
        # for url in all_urls:
        #     if "amazon.in" in url and "/dp/" in url:
        #         print(f"   ✅ Found amazon.in URL")
        #         return url, "amazon.in"
        
        # for url in all_urls:
        #     if "amazon.com" in url and "/dp/" in url:
        #         print(f"   ✅ Found amazon.com URL")
        #         return url, "amazon.com"
        
        print("   ⚠️  No Amazon URLs found")
        return None, None
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return None, None
