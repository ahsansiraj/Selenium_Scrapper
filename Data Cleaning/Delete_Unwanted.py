import os
import shutil
from pathlib import Path
from PIL import Image
import imagehash

# Root folder containing all images
root_folder = r"E:\R3 Factory\Product_images\All category Images\New folder"

# Folder where unwanted images will be moved
deleted_folder = r"E:\R3 Factory\Product_images\All category Images\Deleted_Images"
os.makedirs(deleted_folder, exist_ok=True)

# Reference images (play button overlays)
reference_images = [
    r"E:\R3 Factory\Product_images\All category Images\New folder\image_4_2_11.jpg",
]

# Step 1: Get hashes of reference images
ref_hashes = []
for ref_path in reference_images:
    with Image.open(ref_path) as ref_img:
        ref_img = ref_img.convert("RGB")
        ref_hashes.append({
            "phash": imagehash.phash(ref_img),
            "ahash": imagehash.average_hash(ref_img)
        })

print("🎯 Reference hashes ready.")

# Step 2: Loop through all images
moved_files = []
threshold = 15  # increase for looser match

all_files = [f for f in os.listdir(root_folder) if Path(f).suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]]
total = len(all_files)

for i, filename in enumerate(all_files, 1):
    file_path = Path(root_folder) / filename
    try:
        with Image.open(file_path) as img:
            img = img.convert("RGB")
            img_phash = imagehash.phash(img)
            img_ahash = imagehash.average_hash(img)

        # Compare against reference hashes
        match = False
        for ref in ref_hashes:
            if (abs(img_phash - ref["phash"]) <= threshold) or (abs(img_ahash - ref["ahash"]) <= threshold):
                match = True
                break

        if match:
            # Move file to deleted folder instead of direct delete
            dest_path = Path(deleted_folder) / filename
            # Ensure no overwrite
            if dest_path.exists():
                base, ext = os.path.splitext(filename)
                j = 1
                while dest_path.exists():
                    dest_path = Path(deleted_folder) / f"{base}_{j}{ext}"
                    j += 1
            shutil.move(str(file_path), str(dest_path))
            moved_files.append(str(dest_path))

    except Exception as e:
        print(f"⚠️ Error processing {file_path}: {e}")

    # Progress update
    if i % 100 == 0 or i == total:
        print(f"Processed {i}/{total} images...")

print(f"\n✅ Moved {len(moved_files)} unwanted images to {deleted_folder}")
if moved_files:
    print("Sample moved files:")
    for f in moved_files[:50]:
        print(" -", f)


# import os
# from pathlib import Path
# from PIL import Image
# import imagehash

# # Root folder containing all images
# root_folder = r"E:\R3 Factory\Product_images"

# # Reference image (sample with play button)
# reference_image = r"E:\R3 Factory\Product_images\sample_play_button.jpg"

# # Step 1: Get perceptual hash of reference image
# ref_hash = imagehash.phash(Image.open(reference_image))
# print(f"🎯 Reference image hash: {ref_hash}")

# # Step 2: Loop through all folders and compare
# deleted_files = []
# threshold = 5  # smaller = stricter match, adjust if needed

# for dirpath, _, filenames in os.walk(root_folder):
#     for filename in filenames:
#         file_path = Path(dirpath) / filename

#         if file_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
#             try:
#                 img_hash = imagehash.phash(Image.open(file_path))
#                 diff = abs(ref_hash - img_hash)

#                 if diff <= threshold:  # Similar to reference
#                     os.remove(file_path)
#                     deleted_files.append(str(file_path))

#             except Exception as e:
#                 print(f"⚠️ Error processing {file_path}: {e}")

# print(f"\n✅ Deleted {len(deleted_files)} images with play button overlay")
# if deleted_files:
#     print("Sample deleted files:")
#     for f in deleted_files[:10]:
#         print(" -", f)
