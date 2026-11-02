""" Part 1/2 of PDF Export
Exporting layout as single page PDF 
"""

import arcpy
import os
import zipfile

# Parameters - USER INPUTS
layout_keyword = "just_a_name"
suffix = "_name"
aprx_path = r"\path\to.aprx"
output_base_folder = r"\path\	o\outputfolder"

# Initialising 
aprx = arcpy.mp.ArcGISProject(aprx_path)
print(f"Initiating Map Series export.")

if not os.path.isdir(output_base_folder):
    os.makedirs(output_base_folder, exist_ok=True)
else:
    print("Output path exists, proceeding with export.")
    
# Exporting layouts 
for layout in aprx.listLayouts():
    if layout_keyword not in layout.name:
        print(f"Skipping layout: {layout.name}")
        continue
    project_layout_name = layout.name

   
    pdf_path = os.path.join(
            output_base_folder,
            f"{project_layout_name}{suffix}.pdf"
        )

    png_path = os.path.join(
                output_base_folder,
                f"{project_layout_name}{suffix}.png"
            )


        # if EXPORT_METHOD == "PDF":
    layout.exportToPDF(
            pdf_path,
            resolution=300
        )
    # elif EXPORT_METHOD == "png":
    layout.exportToPNG(
            png_path,
            resolution=300
        )

print("Done.")