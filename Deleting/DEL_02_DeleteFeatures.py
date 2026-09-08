# This script deletes all named features in a .gdb/ .sde
""" Part 1/2 of Deleting toolkit
Sometimes you mess up and need to start with a clean slate (or simply the data got updated).
I use this script to delete feature classes in batch - cus it's like watching paint try if you do it manually on ArcPro.
"""

import arcpy

# Path to the geodatabase
gdb_path = r"\path\to.gdb"

# List of feature classes to delete
feature_classes_to_delete = []
    ,
]

# Set workspace
arcpy.env.workspace = gdb_path

# Initialise a can't be deleted list
feature_classes_cant_delete = []

# Delete each feature class
for fc in feature_classes_to_delete:
fc_path = r"\path\to.gdbeaturename"
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