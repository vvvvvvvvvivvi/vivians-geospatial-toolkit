
import arcpy
import os
import zipfile

# Parameters - USER INPUTS
aprx_link = r"\\location\to.aprx" # Path link to aprx
output_link = r"\\location\to.folder" # Path link to output folder

# Initialising 
aprx = arcpy.mp.ArcGISProject(aprx_link)
print(f"Initiating Map Series export.")

if not os.path.isdir(output_link):
    os.makedirs(output_link, exist_ok=True)
else:
    print("Output path exists, proceeding with export.")
    
# Exporting layouts 
for layout in aprx.listLayouts():
    layout_name = layout.name

    # Output file path (change extension as needed)
    output_file = os.path.join(output_link, f"{layout_name}.pdf")

    # Export layout
    layout.exportToPDF(output_file)

    print(f"Exported: {output_file}")

print("All layouts exported successfully.")
