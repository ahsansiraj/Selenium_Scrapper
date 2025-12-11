# Step 1: Delete the first image in each folder

# import os
# import shutil
# import pandas as pd

# base_folder = r"E:\R3 Factory\Product_images\All category Images\Combine_final_13_sept_3000_images"
# output_folder = r"E:\R3 Factory\Product_images\All category Images\New folder"
# os.makedirs(output_folder, exist_ok=True)

# mappings = []
# count = 0

# for folder_name in os.listdir(base_folder):
#     folder_path = os.path.join(base_folder, folder_name)

#     if os.path.isdir(folder_path):
#         for file in os.listdir(folder_path):
#             if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
#                 src_path = os.path.join(folder_path, file)

#                 # Ensure unique filename in output
#                 dest_file = os.path.join(output_folder, file)
#                 if os.path.exists(dest_file):
#                     base, ext = os.path.splitext(file)
#                     i = 1
#                     while os.path.exists(dest_file):
#                         dest_file = os.path.join(output_folder, f"{base}_{i}{ext}")
#                         i += 1

#                 # Copy image (use move if you want to delete originals)
#                 shutil.move(src_path, dest_file)

#                 # Store mapping: where image came from and where it was copied
#                 mappings.append({"original_folder": folder_path, "filename": os.path.basename(dest_file)})

#                 count += 1

# # Save mappings to Excel/CSV
# df = pd.DataFrame(mappings)
# df.to_csv("image_mapping2.csv", index=False)

# print(f"✅ Collected {count} images into {output_folder}")
# print("✅ Mapping saved to image_mapping.csv")


# Step 2: Restore images back to their respective folders

# When you’re done deleting unwanted images from the collected folder, run this script to send them back:

import os
import shutil
import pandas as pd

output_folder = r"E:\R3 Factory\Product_images\All category Images\New folder"
mapping_file = "image_mapping.csv"

df = pd.read_csv(mapping_file)
restored = 0

for _, row in df.iterrows():
    original_folder = row["original_folder"]
    filename = row["filename"]
    src_path = os.path.join(output_folder, filename)
    dest_path = os.path.join(original_folder, filename)

    if os.path.exists(src_path):  # only restore if file still exists
        os.makedirs(original_folder, exist_ok=True)
        shutil.copy(src_path, dest_path)
        restored += 1

print(f"✅ Re stored {restored} images to their original folders")
