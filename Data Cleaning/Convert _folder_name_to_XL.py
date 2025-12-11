import os
import pandas as pd

# 🔹 Config
base_folder = r"E:\R3 Factory\Product_images\Bulk Uploads\Amazon.ae"   # path where your 1440+ folders exist
output_excel = r"E:\R3 Factory\Product_images\Bulk Uploads\Amazon.ae.xlsx"

# Collect folder names
folders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]

# Save to Excel
df = pd.DataFrame(folders, columns=["Folder_Name"])
df.to_excel(output_excel, index=False)

print(f"✅ Saved {len(folders)} folder names to {output_excel}")
