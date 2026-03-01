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

# Enable overwriting
arcpy.env.overwriteOutput = True

# Inputs
source_aprx = r"\\path\to.aprx"  # Path to original ArcGIS Pro project
destination_dir = r"\\base\path\to\allGDBs" # Path link to where the new .aprx sits
aprx_name = "ProjAbbr_PEAandBNGSurvey" # Rename with Project abbreviation/ code ("ProjAbbr_PEAandBNGSurvey")

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
    gdb_name = os.path.splitext(aprx_name)[0] + ".gdb"
    gdb_path = os.path.join(destination_folder, gdb_name)
    arcpy.CreateFileGDB_management(destination_folder, os.path.splitext(aprx_name)[0])

    # Track original workspaces and export features
    original_workspaces = set()

    for map_obj in original_aprx.listMaps():
        for lyr in map_obj.listLayers():
            if lyr.isFeatureLayer and lyr.supports("DATASOURCE"):
                try:
                    source_fc = lyr.dataSource
                    workspace = os.path.dirname(source_fc)
                    original_workspaces.add(workspace)

                    base_name = sanitise_name(lyr.name)
                    output_name = get_unique_name(gdb_path, base_name)

                    arcpy.FeatureClassToFeatureClass_conversion(source_fc, gdb_path, output_name)
                    print(f"Exported {lyr.name} to {output_name}")
                except Exception as e:
                    print(f"Failed to export {lyr.name}: {e}")

    # Update all workspace connections in the new APRX
    for old_ws in original_workspaces:
        try:
            new_aprx.updateConnectionProperties(old_ws, gdb_path)
            print(f"Updated workspace connection from {old_ws} to {gdb_path}")
        except Exception as e:
            print(f"Failed to update connection from {old_ws}: {e}")

    new_aprx.save()

    return f"APRX duplicated to {destination_aprx_path} and all layers linked to local GDB: {gdb_path}"

# Run the function
result = setupPEAsurvey(source_aprx, destination_dir, aprx_name)
print(result)