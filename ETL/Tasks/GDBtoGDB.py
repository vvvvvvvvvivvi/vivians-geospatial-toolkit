"""This scripts duplicates features from several .gdbs to one .gdb."""

import os
import arcpy

# Define the paths to the geodatabase, and target feature class
gdb_path = r"\path\to.gdb"
in_fc_path_list = []
    r"\\gblon0vs01\GISProj\B3553RG4_SaferSpeeds\IncData\Jacobs\INC004_SpatialSignatures\PlaceAndMovement.gdb\lu_Spatial_Signatures_00",
    # r"\\full\path\link\to\feature.gdb\two"
]

print(f"Set geodatabase to {gdb_path}")
arcpy.env.workspace = gdb_path
arcpy.env.overwriteOutput = True


for fc in in_fc_path_list:
    try:
        arcpy.conversion.FeatureClassToGeodatabase(fc, gdb_path)
        print(f"{fc} duplicated to geodatabase.")
    except Exception as e:
        print(f"Failed to export {fc} to geodatabase. Error: {e}")