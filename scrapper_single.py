import requests
from bs4 import BeautifulSoup
import os
import re

# Load your Amazon search results HTML
html_file = "acer1.html"
with open(html_file, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Find all product blocks
products = soup.select("div.s-main-slot div.s-result-item")

print(f"🔍 Found {len(products)} products on page.")

for product in products:
    # Extract product title
    title_tag = product.find("h2", class_="a-size-base-plus a-spacing-none a-color-base a-text-normal")
    if not title_tag:
        continue  # skip non-product blocks

    product_title = title_tag.get_text(strip=True)
    product_title_clean = re.sub(r'[\\/*?:"<>|]', "", product_title).replace(" ", "_")

    # Create folder for this product
    output_dir = os.path.join(os.path.dirname(html_file), f"{product_title_clean}_Images")
    os.makedirs(output_dir, exist_ok=True)

    img_urls = set()

    # 1️⃣ From <img src>
    for img in product.find_all("img", src=True):
        if "m.media-amazon.com" in img["src"]:
            img_urls.add(img["src"])

    # 2️⃣ From data-old-hires
    for img in product.find_all("img", attrs={"data-old-hires": True}):
        if img["data-old-hires"].strip():
            img_urls.add(img["data-old-hires"])

    # 3️⃣ From srcset (pick highest res)
    for img in product.find_all("img", srcset=True):
        if "m.media-amazon.com" in img["srcset"]:
            srcset_parts = img["srcset"].split(",")
            highest_res = srcset_parts[-1].split()[0]
            img_urls.add(highest_res)

    print(f"\n📦 Product: {product_title}")
    print(f"   Found {len(img_urls)} images")

    # Download images
    for i, url in enumerate(img_urls, 1):
        ext = ".jpg" if ".jpg" in url else ".png"
        img_name = f"image_{i}{ext}"
        img_path = os.path.join(output_dir, img_name)

        try:
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 200:
                with open(img_path, "wb") as f:
                    f.write(response.content)
                print(f"   ✅ Saved: {img_name}")
            else:
                print(f"   ⚠️ Skipped (status {response.status_code}): {url}")
        except Exception as e:
            print(f"   ❌ Failed: {url} | {e}")

print("\n✅ Scraping complete!")
