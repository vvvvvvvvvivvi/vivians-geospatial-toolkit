import arcpy
import os

# Define paths
aprx_path = r"\\location\to.aprx" # Path link to aprx
map_name = "" # Name of the map in the APRX to export layers from
sde_path = r"\\location\to.sde" # Path link to SDE

# Load the project
aprx = arcpy.mp.ArcGISProject(aprx_path)
map_obj = aprx.listMaps(map_name)[0]

# Loop through all maps in the project
for lyr in map_obj.listLayers():
    if lyr.isFeatureLayer:
        # Export each layer to SDE using its name
        output_name = os.path.join(sde_path, lyr.name)
        print(f"Exporting {lyr.name} to {output_name}")
        arcpy.FeatureClassToFeatureClass_conversion(lyr, sde_path, lyr.name)

print("Export complete.")