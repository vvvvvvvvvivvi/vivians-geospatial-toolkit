"""This script iterates through all maps in an .aprx to intersect all layers with prefix "Edit_" to clip to the extent of a target feature class
"""

import arcpy
import os

# Set up environment settings
arcpy.env.overwriteOutput = True

# Define the paths to the project, geodatabase, and target feature class
aprx_path = r"\path\to.aprx"
gdb_path = r"\path\to.gdb"
target_feature_class_name = "just_a_name"

target_feature_class_path = os.path.join(gdb_path, target_feature_class_name)

# Access the ArcGIS Project
try:
    aprx = arcpy.mp.ArcGISProject(aprx_path)
    print(f'Accessed ArcGIS Project: {aprx.filePath}')
except Exception as e:
    print(f"Error accessing project file. Exiting. Error: {e}")
    exit()

# Loop through all maps in the project
for m in aprx.listMaps():
    print(f"Checking map: {m.name}")
    
    # Loop through all layers in the map
    for lyr in m.listLayers():
        if lyr.isFeatureLayer and lyr.name.startswith("Edit_"):
            try:
input_fc_path = r"\path\to.gdbeaturename"
output_fc_name = "just_a_name"
                output_fc_path = os.path.join(gdb_path, output_fc_name)

                print(f"Processing intersection for: {lyr.name}")

                # Perform the Intersect analysis
                arcpy.analysis.Intersect([target_feature_class_path, input_fc_path], output_fc_path, "ALL", None, "INPUT")

                print(f"Successfully created: {output_fc_name}")

            except arcpy.ExecuteError:
                print(f"ArcPy Error during intersection for {lyr.name}: {arcpy.GetMessages(2)}")
            except Exception as e:
                print(f"General Error processing {lyr.name}: {e}")

print('Done')