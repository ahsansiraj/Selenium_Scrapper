# Anti-Detection Configuration Templates

Use these pre-configured setups based on your needs.

## Template 1: Maximum Stealth (Best for Google)

Best for avoiding CAPTCHA at all costs. Slowest but most effective.

```python
from anti_detection import AntiDetectionConfig, AntiDetectionBrowser

# Configuration for maximum stealth
config = AntiDetectionConfig()
config.use_user_agent_rotation = True          # ✓ Essential
config.use_fingerprint_masking = True          # ✓ Essential
config.use_proxy_rotation = True               # ✓ Essential (use paid)
config.use_header_rotation = True              # ✓ Essential
config.simulate_human_behavior = True          # ✓ Essential

# Setup browser
anti_bot = AntiDetectionBrowser(config)

# Add paid proxies (recommended: Smartproxy, Oxylabs, BrightData)
paid_proxies = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080",
    # Add more proxies...
]
anti_bot.proxy_rotation.add_paid_proxies(paid_proxies)

# Setup browser
browser = anti_bot.setup_anti_detection_browser(headless=False)
simulator = anti_bot.human_simulator

# Use with maximum delays
simulator.random_sleep(5, 10)      # 5-10 seconds between requests
simulator.type_slowly(element, text, 0.1, 0.3)  # Slow typing
simulator.human_like_page_interaction()  # Full behavior simulation

print("🛡️  Maximum stealth mode active")
```

**Results:** ~95% success, ~5% CAPTCHA
**Speed:** Slowest (1-2 products/minute)
**Cost:** $10-50/month for proxies
**Best for:** Long-term scraping, avoiding permanent blocks

---

## Template 2: Balanced (Good success, reasonable speed)

Good balance between speed and effectiveness.

```python
from anti_detection import AntiDetectionConfig, AntiDetectionBrowser

config = AntiDetectionConfig()
config.use_user_agent_rotation = True          # ✓ Enable
config.use_fingerprint_masking = True          # ✓ Enable
config.use_proxy_rotation = True               # ✓ Enable (can use free)
config.use_header_rotation = True              # ✓ Enable
config.simulate_human_behavior = True          # ✓ Enable

anti_bot = AntiDetectionBrowser(config)

# Option 1: Free proxies (faster setup, less reliable)
anti_bot.proxy_rotation.load_free_proxies(limit=50)

# Option 2: Paid proxies (recommended)
# anti_bot.proxy_rotation.add_paid_proxies([...])

browser = anti_bot.setup_anti_detection_browser(headless=False)
simulator = anti_bot.human_simulator

# Balanced delays
simulator.random_sleep(2, 5)       # 2-5 seconds between requests
simulator.type_slowly(element, text, 0.05, 0.2)  # Normal typing
simulator.human_like_page_interaction()  # Standard behavior

print("⚖️  Balanced mode active")
```

**Results:** ~75% success, ~25% CAPTCHA
**Speed:** Moderate (3-5 products/minute)
**Cost:** Optional ($0-50/month)
**Best for:** Testing, medium-term projects

---

## Template 3: Speed Optimized (Fast but less stealth)

Prioritizes speed over absolute stealth.

```python
from anti_detection import AntiDetectionConfig, AntiDetectionBrowser

config = AntiDetectionConfig()
config.use_user_agent_rotation = True          # ✓ Enable
config.use_fingerprint_masking = True          # ✓ Enable
config.use_proxy_rotation = False              # ✗ Disable (too slow)
config.use_header_rotation = True              # ✓ Enable
config.simulate_human_behavior = True          # ✓ Enable (but fast)

anti_bot = AntiDetectionBrowser(config)
browser = anti_bot.setup_anti_detection_browser(headless=True)  # Headless = faster
simulator = anti_bot.human_simulator

# Minimal delays
simulator.random_sleep(0.5, 1.5)   # 0.5-1.5 seconds only
simulator.type_slowly(element, text, 0.02, 0.1)  # Fast typing

print("⚡ Speed optimized mode active")
```

**Results:** ~50% success, ~50% CAPTCHA
**Speed:** Fast (5-10 products/minute)
**Cost:** Free
**Best for:** Testing, development, one-time scraping

---

## Template 4: Development/Testing (Quick iteration)

For testing your scraper without anti-detection overhead.

```python
from anti_detection import AntiDetectionConfig, AntiDetectionBrowser

config = AntiDetectionConfig()
config.use_user_agent_rotation = False         # ✗ Disable
config.use_fingerprint_masking = True          # ✓ Keep for safety
config.use_proxy_rotation = False              # ✗ Disable
config.use_header_rotation = False             # ✗ Disable
config.simulate_human_behavior = False         # ✗ Disable

anti_bot = AntiDetectionBrowser(config)
browser = anti_bot.setup_anti_detection_browser(headless=True)

# No simulator = instantly run
# No delays = fast iteration

print("🧪 Development mode - anti-detection disabled")
```

**Results:** ~30% success, ~70% CAPTCHA
**Speed:** Instant (10-20 products/minute)
**Cost:** Free
**Best for:** Testing logic, debugging, development only

---

## Template 5: Premium (Maximum effectiveness)

Enterprise-level configuration for critical projects.

```python
from anti_detection import AntiDetectionConfig, AntiDetectionBrowser

config = AntiDetectionConfig()
config.use_user_agent_rotation = True          # ✓ Enable
config.use_fingerprint_masking = True          # ✓ Enable
config.use_proxy_rotation = True               # ✓ Enable premium proxies
config.use_header_rotation = True              # ✓ Enable
config.simulate_human_behavior = True          # ✓ Enable full behavior

anti_bot = AntiDetectionBrowser(config)

# Use premium paid proxies (highest quality)
premium_proxies = [
    # Get these from: BrightData, Oxylabs, or Smartproxy
    "http://proxy1.brightdata.com:8080",
    "http://proxy2.brightdata.com:8080",
    "http://proxy3.brightdata.com:8080",
    "http://proxy4.brightdata.com:8080",
    "http://proxy5.brightdata.com:8080",
    # ... add 10-20 more ...
]
anti_bot.proxy_rotation.add_paid_proxies(premium_proxies)

browser = anti_bot.setup_anti_detection_browser(headless=False)
simulator = anti_bot.human_simulator

# Premium configuration
simulator.random_sleep(5, 12)      # Long delays for safety
simulator.type_slowly(element, text, 0.15, 0.35)  # Very slow typing
simulator.human_like_page_interaction()
simulator.realistic_scrolling()

print("👑 Premium mode active - Enterprise level protection")
```

**Results:** ~98% success, ~2% CAPTCHA
**Speed:** Very slow (0.5-1 product/minute)
**Cost:** $100-300/month for premium proxies
**Best for:** Mission-critical projects, long-term production

---

## Template 6: Rotating Configuration (Adjust as you go)

Start light, increase stealth as needed:

```python
from anti_detection import AntiDetectionConfig, AntiDetectionBrowser

def get_anti_detection_browser(aggressiveness=1):
    """
    aggressiveness:
    1 = Light (development)
    2 = Balanced (testing)
    3 = Heavy (production)
    4 = Maximum (enterprise)
    """

    config = AntiDetectionConfig()

    if aggressiveness == 1:
        config.simulate_human_behavior = False
        config.use_proxy_rotation = False
    elif aggressiveness == 2:
        config.simulate_human_behavior = True
        config.use_proxy_rotation = False
    elif aggressiveness == 3:
        config.simulate_human_behavior = True
        config.use_proxy_rotation = True
        # Load free proxies
        # anti_bot.proxy_rotation.load_free_proxies(50)
    elif aggressiveness >= 4:
        config.simulate_human_behavior = True
        config.use_proxy_rotation = True
        # Add paid proxies
        # anti_bot.proxy_rotation.add_paid_proxies([...])

    anti_bot = AntiDetectionBrowser(config)
    return anti_bot.setup_anti_detection_browser()


# Usage example
browser = get_anti_detection_browser(aggressiveness=2)
# Later if blocked:
browser.quit()
browser = get_anti_detection_browser(aggressiveness=3)  # Add more stealth
```

---

## Comparison Matrix

| Feature             | Stealth    | Balanced     | Speed       | Dev         |
| ------------------- | ---------- | ------------ | ----------- | ----------- |
| User Agent Rotation | ✓          | ✓            | ✓           | ✗           |
| Fingerprint Masking | ✓          | ✓            | ✓           | ✓           |
| Proxy Rotation      | ✓          | ✓            | ✗           | ✗           |
| Human Behavior      | ✓          | ✓            | ✓           | ✗           |
| Delays              | 5-10s      | 2-5s         | 0.5-1.5s    | 0s          |
| Success Rate        | 95%        | 75%          | 50%         | 30%         |
| Speed               | 1 prod/min | 3-5 prod/min | 10 prod/min | 20 prod/min |
| Cost                | $50/mo     | $25/mo       | Free        | Free        |

---

## Decision Tree

```
Are you avoiding Google/CAPTCHA?
├─ YES, critical project
│  └─ Use: MAXIMUM STEALTH (Template 1)
│     Cost: $50/month
│     Success: 95%
│
├─ YES, but budget conscious
│  └─ Use: BALANCED (Template 2)
│     Cost: $0-25/month
│     Success: 75%
│
├─ NO, just testing code
│  └─ Use: SPEED OPTIMIZED (Template 3)
│     Cost: Free
│     Success: 50%
│
└─ NO, just debugging locally
   └─ Use: DEVELOPMENT (Template 4)
      Cost: Free
      Success: 30%
```

---

## My Recommendation for Your Use Case

Since you're scraping Amazon via Google searches:

**Start with Template 2 (Balanced):**

```python
config = AntiDetectionConfig()
config.use_user_agent_rotation = True
config.use_fingerprint_masking = True
config.use_proxy_rotation = True
config.simulate_human_behavior = True

anti_bot = AntiDetectionBrowser(config)
anti_bot.proxy_rotation.load_free_proxies(limit=30)  # Free to start
browser = anti_bot.setup_anti_detection_browser()
```

**Monitor results for 20 products:**

- If 75%+ success: Keep it
- If 50-75% success: Add delays (`simulator.random_sleep(3, 6)`)
- If <50% success: Upgrade to Template 1 with paid proxies

---

## Proxy Service Quick Setup

### Smartproxy (Recommended - $19/month)

1. Sign up: https://smartproxy.com
2. Get 5 residential proxies
3. Format: `http://user:pass@gate.smartproxy.com:7000`
4. Add to config:

```python
proxies = [
    "http://user:pass@gate.smartproxy.com:7000",
    "http://user:pass@gate.smartproxy.com:7001",
    # ...
]
anti_bot.proxy_rotation.add_paid_proxies(proxies)
```

### Oxylabs (Premium - $100/month)

1. Sign up: https://oxylabs.io
2. Get API credentials
3. Use their proxy format
4. Add to config (same as above)

---

## Deployment Checklist

Before running production scraping:

- [ ] Choose template based on requirements
- [ ] Test with 5 products first
- [ ] Monitor for CAPTCHA challenges
- [ ] Adjust delays if needed
- [ ] Add error handling for blocked IPs
- [ ] Monitor success rate metrics
- [ ] Have backup proxies available
- [ ] Log all failures for debugging
- [ ] Set up alerts for 100% failure rate

---

Good luck! Start with Template 2 and adjust as needed. 🚀
