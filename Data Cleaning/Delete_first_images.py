# script to deleete first image
import os

# 🔹 Path where all your folders exist
base_folder = r"E:\R3 Factory\Product_images\Super Variant\Rounds1\Amazon.ae_laptop"

deleted_files = []

# Loop through all folders
for root, dirs, files in os.walk(base_folder):
    # Only act inside leaf folders that contain images
    if files:
        files = sorted(files)  # sort alphabetically (so image_1.jpg comes first)
        first_file = files[0]  # pick the first image
        first_file_path = os.path.join(root, first_file)

        try:
            os.remove(first_file_path)
            deleted_files.append(first_file_path)
            print(f"🗑️ Deleted: {first_file_path}")
        except Exception as e:
            print(f"❌ Could not delete {first_file_path} → {e}")

print(f"\n✅ Deleted first image from {len(deleted_files)} folders.")



