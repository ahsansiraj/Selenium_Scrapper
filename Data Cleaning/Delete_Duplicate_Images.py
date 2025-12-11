import os
import hashlib
from pathlib import Path

def get_file_hash(file_path):
    """Generate hash for a file to identify duplicates."""
    hash_algo = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()

def remove_duplicate_images_in_folder(folder_path):
    """Remove duplicate images by hash inside a single folder."""
    seen_hashes = {}
    removed_files = []

    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = Path(dirpath) / filename

            if file_path.suffix.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
                continue  # skip non-image files

            try:
                file_hash = get_file_hash(file_path)

                if file_hash in seen_hashes:
                    # Duplicate found → remove it
                    os.remove(file_path)
                    removed_files.append(str(file_path))
                else:
                    seen_hashes[file_hash] = str(file_path)

            except Exception as e:
                print(f"⚠️ Error processing {file_path}: {e}")

    return removed_files

def process_all_folders(root_folder):
    """Loop through all subfolders and remove duplicate images inside each."""
    total_removed = 0
    all_removed_files = []

    for subfolder in Path(root_folder).iterdir():
        if subfolder.is_dir():
            print(f"\n📂 Checking folder: {subfolder.name}")
            removed_files = remove_duplicate_images_in_folder(subfolder)
            total_removed += len(removed_files)
            all_removed_files.extend(removed_files)

    print(f"\n✅ Total removed duplicates: {total_removed}")
    if all_removed_files:
        print("Sample removed files:")
        for f in all_removed_files[:10]:
            print(" -", f)

# ---------- RUN ----------
if __name__ == "__main__":
    root_folder = r"E:\R3 Factory\Product_images\All category Images\Combine_final_12_sept_images\Combine_final_12_sept_images"  # <-- change to your root path
    process_all_folders(root_folder)
