# # fetch all the imags which have been scraped previously

# import os
# import shutil
# import pandas as pd
# from pathlib import Path

# # ---------- CONFIG ----------
# EXCEL_FILE = r"E:\R3 Factory\Selenium_Prodcut_Scrapper\for Data Scrapping.xlsx"  # Excel file path
# SHEET_NAME = "Sheet2"  # Change if different
# VARIANT_COLUMN = "variant_id"  # Column in Excel with variant IDs
# LOCAL_IMAGE_DIR = r"E:\R3 Factory\Product_images\All category Images\Combine_final_13_sept_3000_images\Combine_final_13_sept_3000_images"  # Folders with variant_id names
# DESTINATION_DIR = r"E:\R3 Factory\Product_images\ALREADY_SCRAPED"  # Where matched folders will be copyd
# # ----------------------------

# # Create destination folder if it doesn't exist
# os.makedirs(DESTINATION_DIR, exist_ok=True)

# # Step 1: Load variant IDs from Excel
# df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
# variant_ids = df[VARIANT_COLUMN].astype(str).str.strip().tolist()

# # Step 2: Loop through local folders
# local_folders = [f for f in Path(LOCAL_IMAGE_DIR).iterdir() if f.is_dir()]

# copyd_folders = []
# not_in_excel = []

# for folder in local_folders:
#     folder_name = folder.name.strip()

#     # Check if folder name matches a variant_id from Excel
#     if folder_name in variant_ids:
#         dest_path = Path(DESTINATION_DIR) / folder_name

#         # Avoid overwriting
#         if dest_path.exists():
#             print(f"⚠️ Already exists: {dest_path}")
#         else:
#             shutil.move(str(folder), str(dest_path))
#             copyd_folders.append(folder_name)
#     else:
#         not_in_excel.append(folder_name)

# # Step 3: Summary
# print(f"\n✅ copyd {len(copyd_folders)} folders to {DESTINATION_DIR}")
# print(f"❌ {len(not_in_excel)} folders did not match any Excel Variant_id")

# if copyd_folders:
#     print("\nSome copyd folders:")
#     for f in copyd_folders[:10]:
#         print(" -", f)

#give the list of products which are yet to be scraped
import os
import pandas as pd
from pathlib import Path

# ---------- CONFIG ----------
EXCEL_FILE = r"E:\R3 Factory\Selenium_Prodcut_Scrapper\for Data Scrapping.xlsx"  # Excel file containing all products
SHEET_NAME = "Sheet5"  # Change if needed
VARIANT_ID_COLUMN = "variant_id"    # Column containing variant IDs
VARIANT_NAME_COLUMN = "variant_name" # Column containing variant names
SCRAPED_DIR = r"E:\R3 Factory\Product_images\27Nov\Rounds3\Images"  # Folder that contains already scraped folders
# ----------------------------

# Step 1: Read all products from Excel
df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
all_variants = df[[VARIANT_ID_COLUMN, VARIANT_NAME_COLUMN]].copy()
all_variants[VARIANT_ID_COLUMN] = all_variants[VARIANT_ID_COLUMN].astype(str).str.strip()
all_variants[VARIANT_NAME_COLUMN] = all_variants[VARIANT_NAME_COLUMN].astype(str).str.strip()

# Step 2: Read all folder names from scraped directory
scraped_folders = [f.name.strip() for f in Path(SCRAPED_DIR).iterdir() if f.is_dir()]
.01
# Step 3: Find products that are not yet scraped
remaining_variants = all_variants[~all_variants[VARIANT_ID_COLUMN].isin(scraped_folders)]

# Step 4: Show result
print(f"✅ Total variants in Excel: {len(all_variants)}")
print(f"✅ Scraped folders found: {len(scraped_folders)}")
print(f"❌ Remaining variants to scrape: {len(remaining_variants)}\n")

print("Remaining variants to scrape:")
for _, row in remaining_variants.iterrows():
    print(f"- ID: {row[VARIANT_ID_COLUMN]}")
    print(f"  Name: {row[VARIANT_NAME_COLUMN]}\n")

# Optionally: save remaining variants to Excel
if not remaining_variants.empty:
    output_file = Path(EXCEL_FILE).parent / "Remaining_Products.xlsx"
    remaining_variants.to_excel(output_file, index=False)
    print(f"\n📄 Remaining variants saved to: {output_file}") 