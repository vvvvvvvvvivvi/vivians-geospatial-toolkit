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
from config import config

# Enable overwriting
arcpy.env.overwriteOutput = True

# Inputs
out_folder_path = r"\path\	o\folder"
aprx_name = "NWLART_PEASurvey" # Rename with Project abbreviation/ code ("ProjAbbr_PEAandBNGSurvey")

source_aprx = config["templates"]["pea_survey_aprx_path"]  # Path to original ArcGIS Pro project

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
        aprx_name += ".aprx"
    
    destination_aprx_path = os.path.join(destination_folder, aprx_name)
    shutil.copy2(source_path, destination_aprx_path)

    # Load original and duplicated APRX
    original_aprx = arcpy.mp.ArcGISProject(source_path)
    new_aprx = arcpy.mp.ArcGISProject(destination_aprx_path)

    # Create new GDB
gdb_name = r"\path\to.gdb"
gdb_path = r"\path\to.gdb"
    arcpy.CreateFileGDB_management(destination_folder, os.path.splitext(aprx_name)[0])

    # Track datasource mappings
    datasource_map = {}

    for map_obj in original_aprx.listMaps():
        for lyr in map_obj.listLayers():
            if lyr.isFeatureLayer and lyr.supports("DATASOURCE"):
                try:
                    source_fc = lyr.dataSource

                    base_name = sanitise_name(lyr.name)
output_name = "just_a_name"

                    arcpy.FeatureClassToFeatureClass_conversion(
                        source_fc,
                        gdb_path,
                        output_name
                    )

                    new_fc = os.path.join(gdb_path, output_name)

                    datasource_map[source_fc] = new_fc

                    print(f"Exported {lyr.name} to {new_fc}")

                except Exception as e:
                    print(f"Failed to export {lyr.name}: {e}")

    # Update layer connections individually
    for map_obj in new_aprx.listMaps():
        for lyr in map_obj.listLayers():
            if lyr.isFeatureLayer and lyr.supports("DATASOURCE"):
                try:
                    old_source = lyr.dataSource

                    if old_source in datasource_map:
                        lyr.updateConnectionProperties(
                            old_source,
                            datasource_map[old_source]
                        )

                        print(
                            f"Updated {lyr.name}: "
                            f"{old_source} -> {datasource_map[old_source]}"
                        )

                except Exception as e:
                    print(f"Failed to update {lyr.name}: {e}")

    new_aprx.save()

    return f"APRX duplicated to {destination_aprx_path} and all layers linked to local GDB: {gdb_path}"

# Run the function
result = setupPEAsurvey(source_aprx, out_folder_path, aprx_name)
print(result)