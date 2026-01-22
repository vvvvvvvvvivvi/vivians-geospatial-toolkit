# This scripts duplicates features from several .gdbs to one .gdb.

import os
import arcpy

# Define the paths to the geodatabase, and target feature class
gdbPath = r"\\location\to.gdb" # Path link to workspace geodatabase


inputFCs = [
    r"\\full\path\link\to\feature.gdb\one",
    r"\\full\path\link\to\feature.gdb\two"
]

print(f"Set geodatabase to {gdbPath}")
arcpy.env.workspace = gdbPath
arcpy.env.overwriteOutput = True


for fc in inputFCs:
    try:
        arcpy.conversion.FeatureClassToGeodatabase(fc, gdbPath)
        print(f"{fc} duplicated to geodatabase.")
    except Exception as e:
        print(f"Failed to export {fc} to geodatabase. Error: {e}")