import pandas as pd
 
# 1. Apni file ka naam yahan likhein
file_path = 'E:\\R3 Factory\\Selenium_Prodcut_Scrapper\\Data Cleaning\\update 1.xlsx'
 
# 2. Data Read karein

df = pd.read_excel(file_path)
 
# --- LOGIC START ---

def clean_data(row):

    name = str(row['Product Name']).lower()

    brand = str(row['Brand'])

    # Logic 1: Repair Parts

    if any(x in name for x in ['lcd', 'display', 'folder', 'battery', 'charging', 'flex']):

        return "Spare Parts", "Mobile Spares", brand

    # Logic 2: Fix iPhones

    if 'iphone' in name:

        return "Mobile", "iPhones", "Apple"

    # Logic 3: Fix Androids & Brands

    if 'samsung' in name: return "Mobile", "Android Phones", "Samsung"

    if 'xiaomi' in name or 'redmi' in name: return "Mobile", "Android Phones", "Xiaomi"

    # Logic 4: Wearables

    if 'watch' in name: return "Wearables", "Smart Watches", brand

    return row['Category'], row['Sub Category'], brand
 
# Logic Apply karein

df[['Category', 'Sub Category', 'Brand']] = df.apply(lambda row: pd.Series(clean_data(row)), axis=1)

# --- LOGIC END ---
 
# 3. Save karein

df.to_csv('Cleaned_Data_Full.csv', index=False)

print("File Saved Successfully!")
 