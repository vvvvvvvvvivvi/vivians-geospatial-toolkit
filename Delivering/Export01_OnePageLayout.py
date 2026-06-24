""" Part 1/2 of PDF Export
Exporting layout as single page PDF 
"""

import arcpy
import os
import zipfile

# Parameters - USER INPUTS
aprx_path = r"\\location\to.aprx" # Path link to aprx
output_base_folder = r"\\location\to.folder" # Path link to output folder

# Initialising 
aprx = arcpy.mp.ArcGISProject(aprx_path)
print(f"Initiating Map Series export.")

if not os.path.isdir(output_base_folder):
    os.makedirs(output_base_folder, exist_ok=True)
else:
    print("Output path exists, proceeding with export.")
    
# Exporting layouts 
for layout in aprx.listLayouts():
    layout_name = layout.name

    # Output file path (change extension as needed)
    output_file = os.path.join(output_base_folder, f"{layout_name}.pdf")

    # Export layout
    layout.exportToPDF(output_file)

    print(f"Exported: {output_file}")

print("All layouts exported successfully.")
