# This script calculates the geometry of a fc (area/ length/ perimetre) and export the relevant information as an Excel workbook.

import arcpy
import os
import pandas as pd
gdb_path = r"\path\to.gdb"
in_fc_name_list = []
    # List of fc name in gdb to iterate through
    "",
    "",
    "",
]
output_name = "just_a_name"
output_base_folder = r"\path\	o\outputfolder"

data = []
for fc in in_fc_name_list:
    full_path = os.path.join(gdb_path, fc)
    if arcpy.Exists(full_path):

        # Adding output to the attribute table
        arcpy.AddField_management(full_path, "perimetre_m", "DOUBLE") 

        try:
            # Performing calculations
            # See https://pro.arcgis.com/en/pro-app/3.4/tool-reference/data-management/calculate-geometry-attributes.htm
            arcpy.CalculateGeometryAttributes_management(full_path,
                [["perimetre_m", "PERIMETER_LENGTH_GEODESIC"]], length_unit="METERS")
            
            # Adding output to the attribute table
            with arcpy.da.SearchCursor(full_path, ["perimetre_m"]) as cursor:
                for row in cursor:
                    data.append({"Area": fc, "Perimtre (m)": row[0]})
                    print(f"{fc} perimetre is {row[0]}")

        except Exception as e:
            print("Failed to calculate perimeter: ", e)
    else:
        print(f"{fc} does not exist.")

try:      
    output_file = os.path.join(output_base_folder, f"{output_name}.xlsx")
    fields = ["Area", "Perimtre (m)"] # Change if necessary

    df = pd.DataFrame(data)

    if not df.empty:
        with pd.ExcelWriter(output_file) as writer:
            df.to_excel(writer, sheet_name=fc, index=False)
        print(f"Exported {output_name} to Excel.")
    else:
        print(f"{output_name} is empty. Skipping export.")
except Exception as e:
    print(f"Failed to export {output_name}: {e}")
    
print("Done.")