# This script exports a layout linked to a map series as individual map sheets and a map book and zip the output for delivering.
""" In the process of delivering 33 figures in a map series, 
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
aprx_link = r"\\location\to.aprx" # Path link to aprx
output_link = r"\\location\to.folder" # Path link to output folder

#----------------------------------------------------------------------
# Initialising 
aprx = arcpy.mp.ArcGISProject(aprx_link)
print(f"Initiating Map Series export.")

if not os.path.isdir(output_link):
    os.makedirs(output_link, exist_ok=True)
else:
    print("Output path exists, proceeding with export.")
    
# Exporting map series 
for lyt in aprx.listLayouts():#
    if lyt.name == "NTMNHM": #filter the ss_ layers
        
        ms = lyt.mapSeries
        if ms:
            export_name = arcpy.mp.CreateExportFormat('PDF', os.path.join(output_link, f"{lyt.name}.pdf"))
            export_name.resolution = 500

            ms_ex_opt = arcpy.mp.CreateExportOptions("MAPSERIES")

            # Multiple files
            ms_ex_opt.setExportFileOptions("PDF_MULTIPLE_FILES_PAGE_NAME")
            ms.export(export_name, ms_ex_opt)
            print("Exported as single sheets.")

            # Single map book
            ms_ex_opt.setExportFileOptions("PDF_SINGLE_FILE")
            ms.export(export_name, ms_ex_opt)
            print("Exported as map book.")

        else: #non-map series will not be exported
            print(f"{lyt.name} is not a map series")

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
