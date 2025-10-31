import requests
from bs4 import BeautifulSoup
import os
import re

# Load your Amazon HTML file
html_file = "acer1.html"
with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "html.parser")

# Extract product title from <h2>
title_tag = soup.find("h2", class_="a-size-base-plus a-spacing-none a-color-base a-text-normal")
if title_tag:
    product_title = title_tag.get_text(strip=True)
else:
    product_title = "Amazon_Product"

# Clean product title for folder name
product_title_clean = re.sub(r'[\\/*?:"<>|]', "", product_title).replace(" ", "_")

# Create folder named after the product
output_dir = os.path.join(os.path.dirname(html_file), f"{product_title_clean}_Images")
os.makedirs(output_dir, exist_ok=True)

img_urls = set()

# 1️⃣ Extract images from normal src
for img in soup.find_all("img", src=True):
    if "m.media-amazon.com" in img["src"]:
        img_urls.add(img["src"])

# 2️⃣ Extract high-res images from data-old-hires
for img in soup.find_all("img", attrs={"data-old-hires": True}):
    if img["data-old-hires"].strip():
        img_urls.add(img["data-old-hires"])

# 3️⃣ Extract from srcset (pick highest resolution)
for img in soup.find_all("img", srcset=True):
    if "m.media-amazon.com" in img["srcset"]:
        srcset_parts = img["srcset"].split(",")
        highest_res = srcset_parts[-1].split()[0]  # last one is usually highest res
        img_urls.add(highest_res)

print(f"🔍 Found {len(img_urls)} unique image(s) for: {product_title}")

# Download and save images
for i, url in enumerate(img_urls, 1):
    ext = ".jpg" if ".jpg" in url else ".png"
    img_name = f"image_{i}{ext}"
    img_path = os.path.join(output_dir, img_name)

    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(img_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Saved: {img_name}")
        else:
            print(f"⚠️ Skipped (status {response.status_code}): {url}")
    except Exception as e:
        print(f"❌ Failed: {url} | {e}")

print(f"\n📁 Total images saved: {len(img_urls)}")
print(f"📂 Folder: {output_dir}")
