# This script exports a layout linked to a map series as individual map sheets and a map book and zip the output for delivering.
""" Part 2/2 of PDF Export
In the process of delivering 33 figures in a map series, 
I struggled not with making the maps, but to find the most efficient way to export and send the figures off.
At first I created dedicated Sharepoint folder to share the outputs for draft review, but I slowly realised how inefficient that was.
The manual clicking and long waiting window for all of the 33 pages of the map series to be exported added another level of challenge.
By the third round of review, I wrote this script to create a one-stop solution for the struggle. 
Now, with one button push, I can rest with the ease knowing I can send the figures off in the exact format I wanted and upload everything as a zip.
"""


import arcpy
import os
import zipfile

# Parameters - USER INPUTS
aprx_path = r"\path\to.aprx"
output_link = r"\\gblon0vs01\GISProj\B245775P_NW_TeesIndustrialDemand\ArcGIS\001_Figures\005_GeomorphologyAssessment\Outgoing\v5" # Path link to output folder
layout_keyword = "just_a_name"

#----------------------------------------------------------------------
# Initialising 
aprx = arcpy.mp.ArcGISProject(aprx_path)
print(f"Initiating Map Series export.")

if not os.path.isdir(output_link):
    os.makedirs(output_link, exist_ok=True)
else:
    print("Output path exists, proceeding with export.")
    
# Exporting map series 
for layout in aprx.listLayouts():#
    if layout_keyword not in layout.name:
        print(f"Skipping layout: {layout.name}")
        continue
        
    ms = layout.mapSeries
    if ms:
        export_name = arcpy.mp.CreateExportFormat('PDF', os.path.join(output_link, f"{lyt.name}.pdf"))
        export_name.resolution = 500

        ms_ex_opt = arcpy.mp.CreateExportOptions("MAPSERIES")

        # # Multiple files
        # ms_ex_opt.setExportFileOptions("PDF_MULTIPLE_FILES_PAGE_NAME")
        # ms.export(export_name, ms_ex_opt)
        # print(f"Exported {lyt.name} as single sheets.")

        # Single map book
        ms_ex_opt.setExportFileOptions("PDF_SINGLE_FILE")
        ms.export(export_name, ms_ex_opt)
        print(f"Exported {layout.name} as map book.")

    else: #non-map series will not be exported
        print(f"{layout.name} is not a map series")

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
