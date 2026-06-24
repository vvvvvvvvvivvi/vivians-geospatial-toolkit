"""
This script breaks the original feature class into multiple FCs (explode) by unique values of the attribute field.
"""

import arcpy
import os
import traceback

# Define the paths to the geodatabase and target feature class
input_gdb = r"\\location\to.gdb" # Path link to geodatabase
input_fc = "fcname"
unique_field = "Name"
output_gdb = r"\\location\to.gdb" # Path link to geodatabase

# Set workspace
arcpy.env.workspace = input_gdb

# Fully qualified path to input FC
in_fc = os.path.join(input_gdb, input_fc)

if arcpy.Exists(in_fc):
    print("Feature class exists, starting to explode feature class by attribute value")
else:
    print(f"ERROR: Input feature class does not exist: {in_fc}")
    raise SystemExit


# STEP 1 â€” GET UNIQUE VALUES
try:
    print("Extracting unique values...")
    unique_vals = sorted({row[0] for row in arcpy.da.SearchCursor(in_fc, [unique_field])})
    print(f"Found {len(unique_vals)} unique values.\n")

except Exception:
    print("ERROR: Failed to read unique values from the feature class.")
    traceback.print_exc()
    raise SystemExit

# Get total row count once
try:
    total_rows = int(arcpy.GetCount_management(in_fc)[0])
except Exception:
    total_rows = -1
    print("WARNING: Could not calculate total row count.\n")

# STEP 2 â€” PROCESS EACH UNIQUE VALUE
for val in unique_vals:
    try:
        print(f"\nProcessing value: {val}")

        # Build SQL query
        where_clause = f"{arcpy.AddFieldDelimiters(in_fc, unique_field)} = '{val}'"

        # Temporary layer
        lyr = "temp_lyr"
        arcpy.MakeFeatureLayer_management(in_fc, lyr, where_clause)

        # Count features with this value
        count = int(arcpy.GetCount_management(lyr)[0])
        print(f"  -> Selected {count} rows out of {total_rows}")

        if count == 0:
            print("  -> Skipped (no matching features).")
            arcpy.Delete_management(lyr)
            continue

        # Generate safe output name
        safe_val = str(val).replace(" ", "_").replace("/", "_")
        out_fc = os.path.join(output_gdb, f"{input_fc}_{safe_val}")

        # Export subset
        arcpy.CopyFeatures_management(lyr, out_fc)
        print(f"  -> Exported subset to: {out_fc}")

        arcpy.Delete_management(lyr)

    except Exception:
        print(f"ERROR: Failed while processing value '{val}'.")
        traceback.print_exc()
        continue


print("All subsets exported successfully.")