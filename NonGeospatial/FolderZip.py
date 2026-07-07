import os
import zipfile

# Parameters - USER INPUTS
output_link = r"\\gblon0vs01\GISProj\B245771D_NW_NorthSuffolk\ArcGIS\036_ArchaeologicalDeskBasedAssessment\Outgoing\v5" # Path link to output folder

# Zipping outputs
try:
    base_dir = os.path.split(output_link)[0]
    zip_path = os.path.join(base_dir, f"{os.path.basename(output_link)}.zip")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_cursor:
        for root, dirs, files in os.walk(output_link):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, base_dir)
                zip_cursor.write(abs_path, rel_path)

    print("Output zipped.")
except Exception as e:
    print("Failed to zip outputs:", e)