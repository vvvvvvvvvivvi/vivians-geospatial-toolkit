# This script pushes all layers in a map to a .sde.
""" Part 3/3 of SDR toolkit.
To fulfill the standards in the company, we have to log incoming data to the Spatial Data Register (SDR) each time.
It requires you to make a copy of the data to both the project .sde, as well as the discipline .gdb
However, it also requires any data going into the .gdb to have a version number
This script is developed as I was too lazy to edit each layer by layer.
What I do instead is I inspect all processed data on a specific map, then using the script, renaming and pushing to .gdb/ .sde 
This script is different from the .sde version, as each discipline has its own gdb location.
This script iterates through the layers name and sort them into their respective .gdb by their prefixes.
"""

import arcpy
import os

# Define paths
aprx_path = r"\\path\to.aprx"  # Path to ArcGIS Pro project
base_gdb_path = r"\\base\path\to\allGDBs" # Path link to where the gdbs sit

# Mapping of prefixes to geodatabase names
prefix_to_gdb = {
    "ab": "ab_AdministrativeBoundaries.gdb",
    "aq": "aq_AirQualityAndEmissions.gdb",
    "bm": "bm_BaseMapping.gdb",
    "bu": "bu_BuiltAssets.gdb",
    "ca": "ca_CommunityAndAccess.gdb",
    "ch": "ch_CulturalHeritage.gdb",
    "cl": "cl_ClimateAndAtmosphere.gdb",
    "de": "de_Designations.gdb",
    "dg": "dg_Demographics.gdb",
    "ds": "ds_Designs.gdb",
    "ec": "ec_Ecology.gdb",
    "ge": "ge_GeologyAndSoils.gdb",
    "hs": "hs_HealthAndSafety.gdb",
    "in": "in_Index.gdb",
    "lr": "lr_LandRegistry.gdb",
    "ls": "ls_Landscape.gdb",
    "lu": "lu_LandUse.gdb",
    "no": "no_Noise.gdb",
    "pl": "pl_Planning.gdb",
    "te": "te_Terrain.gdb",
    "tr": "tr_Transportation.gdb",
    "ut": "ut_Utilities.gdb",
    "wa": "wa_Water.gdb"
}

# Load the project
aprx = arcpy.mp.ArcGISProject(aprx_path)
map_obj = aprx.listMaps("Publishing")[0] 

# Export each layer based on prefix
for lyr in map_obj.listLayers():
    if lyr.isFeatureLayer:
        layer_name = lyr.name
        prefix = layer_name[:2].lower()
        if prefix in prefix_to_gdb:
            gdb_name = prefix_to_gdb[prefix]
            gdb_path = os.path.join(base_gdb_path, gdb_name)
            print(f"Exporting {layer_name} to {gdb_path}")
            arcpy.FeatureClassToFeatureClass_conversion(lyr, gdb_path, layer_name)
        else:
            print(f"Prefix '{prefix}' not found for layer '{layer_name}'")

print("Export complete.")