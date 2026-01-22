# This script exports attribute table of one or more feature classes into individual Excel Workbooks.

import arcpy
import os
import pandas as pd

# Define the paths to the geodatabase and target feature class
gdbPath = r"\\location\to.gdb" # Path link to geodatabase
arcpy.env.workspace = gdbPath
arcpy.env.overwriteOutput = True
writingFCs = [
    "Crossings_Tagged",
    "Crossings_Buffered_Tagged"
]

outputPath = r"\\path\to\workingfolder"

for fc in writingFCs:
    if arcpy.Exists(fc):
        print(f"Exporting {fc} as Excel...")
        try:
            output_file = os.path.join(outputPath, f"{fc}.xlsx")
            fields = [f.name for f in arcpy.ListFields(fc) if f.type not in ('Geometry', 'Date', 'OID')]

            # Use SearchCursor to avoid NumPy type issues
            data = []
            with arcpy.da.SearchCursor(fc, fields) as cursor:
                for row in cursor:
                    data.append(dict(zip(fields, row)))

            df = pd.DataFrame(data)

            if not df.empty:
                with pd.ExcelWriter(output_file) as writer:
                    df.to_excel(writer, sheet_name=fc, index=False)
                print(f"Exported {fc} to Excel.")
            else:
                print(f"{fc} is empty. Skipping export.")
        except Exception as e:
            print(f"Failed to export {fc}: {e}")
    else:
        print(f"{fc} does not exist.")

print("All feature classes exported as Excel workbooks.")