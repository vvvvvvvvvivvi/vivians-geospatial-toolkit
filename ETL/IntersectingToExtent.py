# This script iterates through all maps in an .aprx to intersect all layers with prefix "Edit_" to clip to the extent of a target feature class

import arcpy
import os

# Set up environment settings
arcpy.env.overwriteOutput = True

# Define the paths to the project, geodatabase, and target feature class
aprx_path = r"\\location\to.aprx" # Path link to workspace ArcGIS Pro project
gdb_path = r"\\location\to.gdb" # Path link to workspace geodatabase
target_feature_class = os.path.join(gdb_path, "Area")

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
                input_fc_path = lyr.dataSource
                output_fc_name = f"{lyr.name}_ProjectScope"
                output_fc_path = os.path.join(gdb_path, output_fc_name)

                print(f"Processing intersection for: {lyr.name}")

                # Perform the Intersect analysis
                arcpy.analysis.Intersect([target_feature_class, input_fc_path], output_fc_path, "ALL", None, "INPUT")

                print(f"Successfully created: {output_fc_name}")

            except arcpy.ExecuteError:
                print(f"ArcPy Error during intersection for {lyr.name}: {arcpy.GetMessages(2)}")
            except Exception as e:
                print(f"General Error processing {lyr.name}: {e}")

print('Done')