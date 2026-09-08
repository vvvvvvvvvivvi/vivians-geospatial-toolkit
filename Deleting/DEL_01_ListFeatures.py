# This script lists the name of all features in a .gdb/ .sde
""" Part 1/2 of Deleting toolkit
Sometimes you mess up and need to start with a clean slate (or simply the data got updated).
I use this script to delete feature classes in batch - cus it's like watching paint try if you do it manually on ArcPro.
"""

import arcpy

# Define the paths to the sde/geodatabase
sde_path = r"\path\to.sde"

# Initialise the list
feature_classes_to_delete = []

# Set the workspace to the SDE connection
arcpy.env.workspace = sde_path

# List feature classes in the root of the SDE
for fc in arcpy.ListFeatureClasses():
    feature_classes_to_delete.append(fc)

# List feature classes inside feature datasets
for dataset in arcpy.ListDatasets():
    for fc in arcpy.ListFeatureClasses(feature_dataset=dataset):
        feature_classes_to_delete.append(fc)

# Print in a format that you can populate directly to the next script
print("feature_classes_to_delete = [")
for fc in feature_classes_to_delete:
    print(f'    "{fc}",')
print("]")