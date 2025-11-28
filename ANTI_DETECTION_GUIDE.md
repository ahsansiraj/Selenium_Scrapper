# Anti-Bot Detection Integration Guide

## Overview

This guide explains how to integrate the comprehensive anti-detection measures into your `Scrapper.py` file to avoid Google's bot tracking and CAPTCHA challenges.

## What's Included

### 1. **Rotating User Agents** (20+ diverse browsers)

- Chrome, Firefox, Edge, Safari on Windows/Mac/Linux
- Mobile browsers (Chrome on Android, Safari on iOS)
- Different Chrome versions (115-120)
- Prevents bot detection by making each request look different

### 2. **Browser Fingerprint Masking**

- Hides `navigator.webdriver` property
- Spoofs `navigator.plugins` array
- Sets fake `window.chrome` object
- Disables Blink automation features

### 3. **Proxy Rotation Support**

- Free proxy loading (from public sources)
- Paid proxy integration (import your proxy list)
- Automatic proxy rotation per request
- Changes IP address every request

### 4. **Human-like Behavior Simulation**

- Random delays between actions (1-3 seconds)
- Slow character-by-character typing
- Mouse movement simulation
- Realistic page scrolling
- Random pause times

### 5. **Header Rotation**

- Random but realistic HTTP headers
- Multiple language preferences
- Various accept-encoding options
- Proper referer and fetch headers

---

## Integration Steps

### Step 1: Place the anti_detection.py file

The file `anti_detection.py` is already created in your project directory.

### Step 2: Update Imports in Scrapper.py

Add this import at the top of your `Scrapper.py`:

```python
from anti_detection import (
    AntiDetectionConfig,
    AntiDetectionBrowser,
    UserAgentPool,
    HumanBehaviorSimulator
)
```

### Step 3: Replace Browser Initialization

**Old code:**

```python
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument(f"user-agent={USER_AGENT}")

service = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=options)
```

**New code:**

```python
# Initialize anti-detection configuration
config = AntiDetectionConfig()
config.use_user_agent_rotation = True      # Enable user agent rotation
config.use_fingerprint_masking = True      # Hide webdriver detection
config.use_proxy_rotation = False          # Set to True if using proxies
config.simulate_human_behavior = True      # Enable human-like behavior

# Setup anti-detection browser
anti_detection = AntiDetectionBrowser(config)
browser = anti_detection.setup_anti_detection_browser(headless=False)
human_simulator = anti_detection.human_simulator
```

### Step 4: Enable Proxy Support (Optional)

If you want to use proxies to rotate IP addresses:

**Free Proxies:**

```python
config.use_proxy_rotation = True
anti_detection.proxy_rotation.load_free_proxies(limit=50)
```

**Paid Proxies (Recommended):**

```python
config.use_proxy_rotation = True
paid_proxies = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080",
]
anti_detection.proxy_rotation.add_paid_proxies(paid_proxies)
```

### Step 5: Use Human Behavior in Google Search

In your `search_google_and_get_amazon_url()` function, add human behavior:

**Before typing in search box:**

```python
search_box = WebDriverWait(browser, 5).until(
    EC.presence_of_element_located((By.NAME, "q"))
)

# Add human-like behavior before and after typing
if human_simulator:
    human_simulator.type_slowly(search_box, search_query)
else:
    search_box.send_keys(search_query)
```

**After getting search results:**

```python
# Simulate human reading results
if human_simulator:
    human_simulator.human_like_page_interaction()
```

---

## Code Example: Complete Integration

```python
# At the beginning of search_and_scrape() function

print("🚀 Initializing anti-detection measures...")

# Configure anti-detection
config = AntiDetectionConfig()
config.use_user_agent_rotation = True
config.use_fingerprint_masking = True
config.use_proxy_rotation = False  # Set to True if using proxies
config.simulate_human_behavior = True

# Setup browser
anti_detection = AntiDetectionBrowser(config)
browser = anti_detection.setup_anti_detection_browser(headless=False)
human_simulator = anti_detection.human_simulator

# Optional: Load proxies
# anti_detection.proxy_rotation.load_free_proxies(limit=30)

print("✅ Anti-detection browser ready\n")

# Now use browser as normal...
# The anti-detection measures work automatically!
```

---

## How Each Measure Helps

### 1. User Agent Rotation

**Problem:** Google detects the same user agent making repeated requests
**Solution:** Each request uses a different user agent (Chrome, Firefox, Safari, etc.)
**Result:** Requests appear to come from different devices/browsers

### 2. Fingerprint Masking

**Problem:** Google checks for `navigator.webdriver` property to detect automation
**Solution:** Hide or spoof this property using JavaScript
**Result:** Browser appears to be user-controlled, not automated

### 3. Proxy Rotation

**Problem:** Google rate-limits the same IP address
**Solution:** Route requests through different proxy servers
**Result:** Each request appears from a different location/IP
**Cost:** Free proxies (unreliable) or Paid proxies ($10-50/month)

### 4. Human Behavior

**Problem:** Bots make requests at inhuman speeds with perfect consistency
**Solution:** Add random delays, typing delays, mouse movements
**Result:** Behavior matches human browsing patterns

### 5. Header Rotation

**Problem:** Bot detection analyzes HTTP headers for patterns
**Solution:** Randomize headers (Accept-Language, Encoding, etc.)
**Result:** Headers look realistic and vary per request

---

## Recommended Proxy Services (Paid)

For best results, use paid residential proxies:

1. **BrightData** (formerly Luminati)

   - $100-500/month
   - High reliability, residential IPs
   - Website: https://brightdata.com

2. **Oxylabs**

   - $100-500/month
   - Residential and mobile proxies
   - Website: https://oxylabs.io

3. **ScraperAPI**

   - $29-499/month
   - Simple API wrapper around Selenium
   - Website: https://www.scraperapi.com

4. **Smartproxy**
   - $19-99/month
   - Budget-friendly residential proxies
   - Website: https://smartproxy.com

---

## Testing Your Setup

Run this simple test to verify anti-detection is working:

```python
from anti_detection import AntiDetectionBrowser, AntiDetectionConfig

# Test 1: User Agent Rotation
print("Testing user agent rotation...")
for i in range(5):
    config = AntiDetectionConfig()
    from anti_detection import UserAgentPool
    print(f"  {i+1}. {UserAgentPool.get_random_user_agent()[:50]}...")

# Test 2: Browser Setup
print("\nTesting browser setup...")
config = AntiDetectionConfig()
config.simulate_human_behavior = False
anti_bot = AntiDetectionBrowser(config)
driver = anti_bot.setup_anti_detection_browser()

# Test 3: Navigate to test site
print("Testing Google navigation...")
driver.get("https://www.google.com")
time.sleep(2)

print(f"✅ Page title: {driver.title}")
print("✅ Anti-detection working!")

driver.quit()
```

---

## Troubleshooting

### Still Getting CAPTCHA?

1. **Increase delays:**

   ```python
   human_simulator.random_sleep(5, 10)  # Wait 5-10 seconds
   ```

2. **Add proxy:**

   ```python
   config.use_proxy_rotation = True
   anti_detection.proxy_rotation.load_free_proxies()
   ```

3. **Reduce request frequency:**

   ```python
   time.sleep(random.randint(30, 60))  # Wait 30-60 seconds between requests
   ```

4. **Check if Google is blocking:**
   ```python
   if "unusual traffic" in driver.page_source:
       print("Google blocking detected!")
   ```

### Proxies Not Working?

1. Test proxy connectivity first:

   ```python
   import requests
   proxy = {"http": "http://proxy:8080"}
   requests.get("https://ipinfo.io", proxies=proxy)
   ```

2. Try different proxy source:
   ```python
   anti_detection.proxy_rotation.free_proxy_source = "another_url"
   anti_detection.proxy_rotation.load_free_proxies()
   ```

---

## Performance Tips

1. **Reduce delays for testing:**

   ```python
   # During development
   human_simulator.random_sleep(0.1, 0.5)
   ```

2. **Increase delays for production:**

   ```python
   # For real scraping
   human_simulator.random_sleep(2, 5)
   ```

3. **Use headless mode for faster execution:**

   ```python
   browser = anti_detection.setup_anti_detection_browser(headless=True)
   ```

4. **Disable unnecessary features:**
   ```python
   config.simulate_human_behavior = False  # If not needed
   config.use_proxy_rotation = False        # If not needed
   ```

---

## Questions & Support

For issues with:

- **User agents:** Check `UserAgentPool.USER_AGENTS` in anti_detection.py
- **Proxies:** Ensure proxy format is `http://ip:port`
- **Timing:** Adjust delay values in `random_sleep()`
- **Headers:** Modify `HeaderRotation.LANGUAGES` or `ENCODINGS`

---

## Next Steps

1. ✅ Save `anti_detection.py` in your project
2. ✅ Update `Scrapper.py` imports
3. ✅ Replace browser initialization
4. ✅ Test with a single product first
5. ✅ Monitor CAPTCHA challenges
6. ✅ Adjust delays/proxies as needed
7. ✅ Run full scraping

Good luck! 🚀
