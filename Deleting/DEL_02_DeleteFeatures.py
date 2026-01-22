# This script deletes all named features in a .gdb/ .sde
""" Part 1/2 of Deleting toolkit
Sometimes you mess up and need to start with a clean slate (or simply the data got updated).
I use this script to delete feature classes in batch - cus it's like watching paint try if you do it manually on ArcPro.
"""

import arcpy

# Path to the geodatabase
geodatabase_path = r"\\gblon0vs01\GISProj\BESP00A2_PFASAerialEmissions\Data\BESP00A2_PFAS_DataOwner@BESP00A2_PFAS.sde"

# List of feature classes to delete
feature_classes_to_delete = [
    ,
]

# Set workspace
arcpy.env.workspace = geodatabase_path

# Initialise a can't be deleted list
feature_classes_cant_delete = []

# Delete each feature class
for fc in feature_classes_to_delete:
    fc_path = f"{geodatabase_path}\\{fc}"
    if arcpy.Exists(fc_path):
        print(f"Deleting {fc}...")
        try:
            arcpy.Delete_management(fc_path)
            print(f"Deleted: {fc}")
        except Exception as e:
            print(f"Error deleting {fc}: {e}")
            feature_classes_cant_delete.append(fc)
    else:
        print(f"Feature class not found: {fc}")

print("feature_classes_cant_delete = [")
for fc in feature_classes_cant_delete:
    print(f'    "{fc}",')
print("]")

print("Deletion process completed.")