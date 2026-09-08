import os
import zipfile

# Parameters - USER INPUTS
input_folder_path = r"\path\	o\folder"

# Zipping outputs
try:
    base_dir = os.path.split(input_folder_path)[0]
    zip_path = os.path.join(base_dir, f"{os.path.basename(input_folder_path)}.zip")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_cursor:
        for root, dirs, files in os.walk(input_folder_path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, base_dir)
                zip_cursor.write(abs_path, rel_path)

    print("Output zipped.")
except Exception as e:
    print("Failed to zip outputs:", e)