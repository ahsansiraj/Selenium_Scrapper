import pandas as pd

def extract_product_condition(productName, browser=None):
    """Extract product condition from product name"""
    condition_keywords = {
        "Used": ["used", "pre-owned", "second hand"],
        "Refurbished": ["refurbished", "reconditioned"],
        "Renewed": ["renewed", "certified pre-owned"],
        "New": ["new", "brand new", "sealed"]
    }
    
    productNameLower = productName.lower()
    
    for condition, keywords in condition_keywords.items():
        for keyword in keywords:
            if keyword in productNameLower:
                return condition

    return "New"


# Read CSV file
csv_path = r"E:\R3 Factory\Selenium_Prodcut_Scrapper\Scrapper_Results\Price_Results_noon_text.xlsx"
print(f"Reading CSV from: {csv_path}\n")

df = pd.read_excel(csv_path)
# Clean column names (remove extra spaces)
df.columns = df.columns.str.strip()
print(f"Loaded {len(df)} products from CSV\n")
print(f"Columns: {list(df.columns)}\n")

# Extract conditions for each product
results = []
count = 0

for idx, row in df.iterrows():
    product_name = str(row["product_name"]).strip()
    condition = extract_product_condition(product_name)
    
    results.append({
        "product_name": product_name,
        "condition": condition
    })
    
    count += 1
    # Print progress
    if count % 20 == 0:
        print(f"Processed {count}/{len(df)} products...")

# Create results dataframe
result_df = pd.DataFrame(results)

# Save to CSV
output_path = r"E:\R3 Factory\Selenium_Prodcut_Scrapper\Scrapper_Results\Price_Results_noon_text.CSV"
result_df.to_csv(output_path, index=False)

print(f"\n{'='*80}")
print(f"✅ Done! Results saved to: {output_path}")
print(f"{'='*80}")
print(f"\nSample Results (first 10):\n")
print(result_df.head(10).to_string(index=False))
print(f"\n📊 Condition Summary:")
print(result_df["condition"].value_counts())
