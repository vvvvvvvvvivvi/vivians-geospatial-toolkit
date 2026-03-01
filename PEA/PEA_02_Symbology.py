# This script apply standardised symbology to UK Habitat polygons.
""" 
Jacobs has a standardised process for setting up Preliminary Ecological Appraisals (PEA).
And... standardisation is a synonym for automation to me.
"""

import arcpy
import os

# Define the paths to the project and target layer file
aprx_path = r"\\location\to.aprx" # Path link to workspace ArcGIS Pro project
symbology_layer_file = r"\\location\to.lyr" # Path link to layer file

# Load the APRX
aprx = arcpy.mp.ArcGISProject(aprx_path)

# Apply symbology to the target layer
for map_obj in aprx.listMaps():
    for lyr in map_obj.listLayers():
        if lyr.name == "UK Habitat - polygon" and lyr.isFeatureLayer:
            try:
                arcpy.management.ApplySymbologyFromLayer(lyr, symbology_layer_file)
                print(f"Symbology applied to '{lyr.name}' using {symbology_layer_file}")
            except Exception as e:
                print(f"Failed to apply symbology to '{lyr.name}': {e}")

# Save the APRX
aprx.save()
print(f"Updated APRX saved.")

