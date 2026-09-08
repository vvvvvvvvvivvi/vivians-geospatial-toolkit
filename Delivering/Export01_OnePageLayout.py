""" Part 1/2 of PDF Export
Exporting layout as single page PDF 
"""

import arcpy
import os
import zipfile

# Parameters - USER INPUTS
aprx_path = r"\path\to.aprx"
output_base_folder = r"\path\	o\outputfolder"
# layout_keyword = "B2457728_Figure" # Keyword to filter the layouts by defined name, e.g. "Figure 1" or "Map Book"

# Initialising 
aprx = arcpy.mp.ArcGISProject(aprx_path)
print(f"Initiating layout export.")

if not os.path.isdir(output_base_folder):
    os.makedirs(output_base_folder, exist_ok=True)
else:
    print("Output path exists, proceeding with export.")
    
# Exporting layouts 
for layout in aprx.listLayouts():
    # if keyword not in layout.name:
    #     print(f"Skipping layout: {layout.name}")
    #     continue
layout_name = "just_a_name"

    # Output file path (change extension as needed)
    output_file = os.path.join(output_base_folder, f"{layout_name}.pdf")

    # Export layout
    layout.exportToPDF(output_file)

    print(f"Exported: {output_file}")

print("All layouts exported successfully.")
