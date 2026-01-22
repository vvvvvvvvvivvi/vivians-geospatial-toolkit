# This script renames all layers in a specific map to remove/ add a suffix.
""" Part 1/3 of SDR toolkit.
To fulfill the standards in the company, we have to log incoming data to the Spatial Data Register (SDR) each time.
It requires you to make a copy of the data to both the project .sde, as well as the discipline .gdb
However, it also requires any data going into the .gdb to have a version number
This script is developed as I was too lazy to edit each layer by layer.
What I do instead is I inspect all processed data on a specific map, then using the script, renaming and pushing to .gdb/ .sde 
"""

import arcpy
import os

# Define paths
aprx_path = r"\\path\to.aprx"  # Path to ArcGIS Pro project

# Load the project
aprx = arcpy.mp.ArcGISProject(aprx_path)
map_obj = aprx.listMaps("Publishing")[0]

# Loop through all maps in the project
for lyr in map_obj.listLayers():
    if lyr.isFeatureLayer:
        # Export each layer to SDE using its name
        # new_name = lyr.name.replace("_01", "")
        # print(f"Renaming: {lyr.name} â†’ {new_name}")

        new_name = f"{lyr.name}_01"
        print(f"Renaming: {lyr.name} â†’ {new_name}")
        lyr.name = new_name
        
        print("Renamed.")

aprx.save()

print("All layers renamed.")
