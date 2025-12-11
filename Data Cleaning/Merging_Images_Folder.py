# import os
# import shutil
# import hashlib
# from pathlib import Path


# # # add your actual folder paths here
# # folders = [
# #     r"E:\R3 Factory\Product_images\All category Images\Combined Images",
# #     r"E:\R3 Factory\Product_images\326VariantImages\Images",
# #     r"E:\R3 Factory\Product_images\Mobile\Mobile",
# #     r"E:\R3 Factory\Product_images\Round3\All_Category_Images",
# #     r"E:\R3 Factory\Product_images\Round3\Mobile",
# #     r"E:\R3 Factory\Product_images\Round2\Noon\Mobile",
# #     r"E:\R3 Factory\Product_images\Round2\Amazon.com",
# #     r"E:\R3 Factory\Product_images\Round2\Amazon.ae",
    
# # ]

# # # destination folder
# # output_folder = r"E:\R3 Factory\Product_images\Combined_folder_6_sept_2025"
# # os.makedirs(output_folder, exist_ok=True)

# # def get_file_hash(file_path):
# #     """Generate hash for a file to identify duplicates."""
# #     hash_algo = hashlib.md5()
# #     with open(file_path, "rb") as f:
# #         for chunk in iter(lambda: f.read(4096), b""):
# #             hash_algo.update(chunk)
# #     return hash_algo.hexdigest()

# # def remove_duplicate_images(root_folder):
# #     seen_hashes = {}
# #     removed_files = []

# #     for dirpath, _, filenames in os.walk(root_folder):
# #         for filename in filenames:
# #             file_path = Path(dirpath) / filename

# #             try:
# #                 file_hash = get_file_hash(file_path)

# #                 if file_hash in seen_hashes:
# #                     # Duplicate found → remove it
# #                     os.remove(file_path)
# #                     removed_files.append(str(file_path))
# #                 else:
# #                     seen_hashes[file_hash] = str(file_path)

# #             except Exception as e:
# #                 print(f"Error processing {file_path}: {e}")

# #     print(f"\n✅ Removed {len(removed_files)} duplicate images")
# #     if removed_files:
# #         print("Some removed files:")
# #         for f in removed_files[:10]:  # show only first 10
# #             print(" -", f)


# # for folder in folders:
# #     for variant_id in os.listdir(folder):
# #         source_path = os.path.join(folder, variant_id)
# #         if os.path.isdir(source_path):
# #             dest_path = os.path.join(output_folder, variant_id)
# #             os.makedirs(dest_path, exist_ok=True)

# #             for file in os.listdir(source_path):
# #                 src_file = os.path.join(source_path, file)
# #                 dest_file = os.path.join(dest_path, file)

# #                 if os.path.exists(dest_file):
# #                     base, ext = os.path.splitext(file)
# #                     count = 1
# #                     while os.path.exists(dest_file):
# #                         dest_file = os.path.join(dest_path, f"{base}_{count}{ext}")
# #                         count += 1

# #                 shutil.copy2(src_file, dest_file)

# # print("✅ Merging complete! Check All_Category_Images folder.")

# # if __name__ == "__main__":
# #     root_folder = r"E:\R3 Factory\Product_images\Combined_folder_6_sept_2025"  # <-- change to your folder path
# #     remove_duplicate_images(root_folder)

# # # import os
# # # import hashlib
# # # from pathlib import Path

# # # def get_file_hash(file_path):
# # #     """Generate hash for a file to identify duplicates."""
# # #     hash_algo = hashlib.md5()
# # #     with open(file_path, "rb") as f:
# # #         for chunk in iter(lambda: f.read(4096), b""):
# # #             hash_algo.update(chunk)
# # #     return hash_algo.hexdigest()

# # # def remove_duplicate_images(root_folder):
# # #     seen_hashes = {}
# # #     removed_files = []

# # #     for dirpath, _, filenames in os.walk(root_folder):
# # #         for filename in filenames:
# # #             file_path = Path(dirpath) / filename

# # #             try:
# # #                 file_hash = get_file_hash(file_path)

# # #                 if file_hash in seen_hashes:
# # #                     # Duplicate found → remove it
# # #                     os.remove(file_path)
# # #                     removed_files.append(str(file_path))
# # #                 else:
# # #                     seen_hashes[file_hash] = str(file_path)

# # #             except Exception as e:
# # #                 print(f"Error processing {file_path}: {e}")

# # #     print(f"\n✅ Removed {len(removed_files)} duplicate images")
# # #     if removed_files:
# # #         print("Some removed files:")
# # #         for f in removed_files[:10]:  # show only first 10
# # #             print(" -", f)

# # # # 🔹 Run the function on your folder
# # # if __name__ == "__main__":
# # #     root_folder = r"E:\R3 Factory\Product_images\Combined_folder_6_sept_2025"  # <-- change to your folder path
# # #     remove_duplicate_images(root_folder)



import os
import shutil
import hashlib
from pathlib import Path

# 🔹 Source folders (add your actual folder paths here)
folders = [
    r"E:\R3 Factory\Product_images\tableConvert.com\Round2\Combine_final_11_sept_3100_images",
    r"E:\R3 Factory\Product_images\tableConvert.com\Round1\Combine_final",
    r"E:\R3 Factory\Product_images\326VariantImages\Round2\Images",
    r"E:\R3 Factory\Product_images\326VariantImages\Round2\Images2",
    r"E:\R3 Factory\Product_images\326VariantImages\Images",
    r"E:\R3 Factory\Product_images\326VariantImages\Round1\Amazon.ae"
    r"E:\R3 Factory\Product_images\326VariantImages\Round1\Amazon.com",
    r"E:\R3 Factory\Product_images\326VariantImages\Round1\Amazon.ae",
    r"E:\R3 Factory\Product_images\326VariantImages\Round1\Noon",
    r"E:\R3 Factory\Product_images\57 products\Rounds1\Amazon.ae"
    r"E:\R3 Factory\Product_images\57 products\Rounds2\Images",
    r"E:\R3 Factory\Product_images\Bulk Uploads\Rounds2"
    r"E:\R3 Factory\Product_images\139 products\Rounds1\Amazon.ae"
    r"E:\R3 Factory\Product_images\139 products\Rounds1\Amazon.com"
    r"E:\R3 Factory\Product_images\139 products\Rounds1\Amazon.in"
    r"E:\R3 Factory\Product_images\139 products\Rounds2\Amazon.ae"
    r"E:\R3 Factory\Product_images\Combined_folder_6_sept_2025"
    r"E:\R3 Factory\Product_images\All data for imagr gethering\Combine_final_11_sept_images\Combine_final_11_sept_2887_images"
    r"E:\R3 Factory\Product_images\All data for imagr gethering\Round1\Combine"
    r"E:\R3 Factory\Product_images\All data for imagr gethering\Round1\Combine_Final"
    r"E:\R3 Factory\Product_images\All data for imagr gethering\Round2\Combine_Final_Round_2"
    r"E:\R3 Factory\Product_images\All data for imagr gethering\Round3\Combine_Final"

]
# 🔹 Destination folder
output_folder = r"E:\R3 Factory\Product_images\All category Images\Combine_final_all_old"
os.makedirs(output_folder, exist_ok=True)

def get_file_hash(file_path):
    """Generate hash for a file to identify duplicates."""
    hash_algo = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()

# def remove_duplicate_images(root_folder):
#     """Remove duplicate images by hash inside a folder (including subfolders)."""
#     seen_hashes = {}
#     removed_files = []

#     for dirpath, _, filenames in os.walk(root_folder):
#         for filename in filenames:
#             file_path = Path(dirpath) / filename

#             try:
#                 file_hash = get_file_hash(file_path)

#                 if file_hash in seen_hashes:
#                     # 🔹 Duplicate found → remove it
#                     os.remove(file_path)
#                     removed_files.append(str(file_path))
#                 else:
#                     seen_hashes[file_hash] = str(file_path)

#             except Exception as e:
#                 print(f"⚠️ Error processing {file_path}: {e}")

#     print(f"\n✅ Removed {len(removed_files)} duplicate images")
#     if removed_files:
#         print("Sample removed files:")
#         for f in removed_files[:10]:  # show only first 10
#             print(" -", f)


def merge_folders(source_folders, dest_folder):
    """Merge multiple folders into one while preserving variant_id structure."""
    for folder in source_folders:
        if not os.path.exists(folder):
            print(f"⚠️ Skipping missing folder: {folder}")
            continue

        for variant_id in os.listdir(folder):
            source_path = os.path.join(folder, variant_id)
            if os.path.isdir(source_path):
                dest_path = os.path.join(dest_folder, variant_id)
                os.makedirs(dest_path, exist_ok=True)

                for file in os.listdir(source_path):
                    src_file = os.path.join(source_path, file)
                    dest_file = os.path.join(dest_path, file)

                    # 🔹 Prevent overwriting: add counter if file already exists
                    if os.path.exists(dest_file):
                        base, ext = os.path.splitext(file)
                        count = 1
                        while os.path.exists(dest_file):
                            dest_file = os.path.join(dest_path, f"{base}_{count}{ext}")
                            count += 1

                    shutil.copy2(src_file, dest_file)

    print("✅ Merging complete! All images collected in:", len(dest_folder))


if __name__ == "__main__":
    # Step 1: Merge all folders
    merge_folders(folders, output_folder)

    # Step 2: Remove duplicates in merged folder
    # remove_duplicate_images(output_folder)



