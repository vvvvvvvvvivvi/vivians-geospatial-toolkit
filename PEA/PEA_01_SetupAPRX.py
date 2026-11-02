# This script duplicates a standardised .aprx and .gdb to a new project location and relink features to the new .gdb
""" 
Jacobs has a standardised process for setting up Preliminary Ecological Appraisals (PEA).
And... standardisation is a synonym for automation to me.
"""

import arcpy
import shutil
import os
import re
import sys

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

import config

# Enable overwriting
arcpy.env.overwriteOutput = True

# Inputs
out_folder_path = r"\path\	o\folder"
aprx_name = "NWWARK_EcologySurveys_Otter" # Rename with Project abbreviation/ code ("ProjAbbr_PEAandBNGSurvey")

cfg = config.load_config()
source_aprx = r"\\gblon0vs01\GISProj\_Admin\Geospatial_Templates\Data_Collection_Survey_Templates\Existing_Survey_Templates\Water_vole_otter\WVO template for publishing.aprx" # Path to original ArcGIS Pro project

# Making sure the aprx name is legal as a pathlink
def sanitise_name(name):
    name = os.path.splitext(os.path.basename(name))[0]
    name = name.replace(" ", "_")
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)
    if not name[0].isalpha():
        name = "L_" + name
    return name[:64]

# Making sure all names are unique in case of duplicated layers in original .aprx
def get_unique_name(gdb_path, base_name):
    name = base_name
    i = 1
    while arcpy.Exists(os.path.join(gdb_path, name)):
        name = f"{base_name}_{i:02d}"
        i += 1
    return name


def setupPEAsurvey(source_path, destination_folder, aprx_name):
    if not os.path.isfile(source_path):
        print(f"Source file does not exist: {source_path}")
        sys.exit(1)

    if not os.path.isdir(destination_folder):
        print(f"Destination folder does not exist: {destination_folder}")
        sys.exit(1)

    if not aprx_name.lower().endswith(".aprx"):
        aprx = aprx_name + ".aprx"
    
    destination_aprx_path = os.path.join(destination_folder, aprx)
    shutil.copy2(source_path, destination_aprx_path)

    # Load original and duplicated APRX
    original_aprx = arcpy.mp.ArcGISProject(source_path)
    new_aprx = arcpy.mp.ArcGISProject(destination_aprx_path)

    # Create new GDB
    proj_gdb_name = aprx_name + ".gdb"
    proj_gdb_path = os.path.join(destination_folder, proj_gdb_name)
    arcpy.CreateFileGDB_management(destination_folder, os.path.splitext(aprx_name)[0])

    # Track datasource mappings
    datasource_map = {}

    for map_obj in original_aprx.listMaps():
        for lyr in map_obj.listLayers():
            if lyr.isFeatureLayer and lyr.supports("DATASOURCE"):
                try:
                    source_fc = lyr.dataSource

                    base_name = sanitise_name(lyr.name)
                    proj_output_name = base_name[:64]

                    arcpy.FeatureClassToFeatureClass_conversion(
                        source_fc,
                        proj_gdb_path,
                        proj_output_name
                    )

                    new_fc = os.path.join(proj_gdb_path, proj_output_name)

                    datasource_map[source_fc] = new_fc

                    print(f"Exported {lyr.name} to {new_fc}")

                    layer_map = {}

                    # During export
                    layer_map[lyr.name] = new_fc

                except Exception as e:
                    print(f"Failed to export {lyr.name}: {e}")

    # Update layer connections individually
    # During relink
    for map_obj in new_aprx.listMaps():
        for lyr in map_obj.listLayers():
            if lyr.name in layer_map:
                try:
                    lyr.updateConnectionProperties(
                        lyr.connectionProperties,
                        {
                            **lyr.connectionProperties,
                            "connection_info": {
                                "database": proj_gdb_path
                            },
                            "dataset": os.path.basename(layer_map[lyr.name])
                        }
                    )


                    print(
                        f"Updated {lyr.name}: "
                    )

                except Exception as e:
                    print(f"Failed to update {lyr.name}: {e}")

    new_aprx.save()

    return f"APRX duplicated to {destination_aprx_path} and all layers linked to local GDB: {proj_gdb_path}"

# Run the function
result = setupPEAsurvey(source_aprx, out_folder_path, aprx_name)
print(result)