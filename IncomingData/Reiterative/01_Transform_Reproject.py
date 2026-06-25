import arcpy
import os
import uuid
import sys

working_path = sys.argv[2]
working_map_name = sys.argv[3]
sde_path = sys.argv[8]


BNG_SR = arcpy.SpatialReference(27700)

arcpy.env.overwriteOutput = True

for dirpath, dirnames, fc_names in arcpy.da.Walk(
    sde_path,
    datatype="FeatureClass"
):
    for fc in fc_names:
        in_path = os.path.join(dirpath, fc)
        desc = arcpy.Describe(in_path)
        sr = desc.spatialReference

        # Case 1: Spatial reference is UNKNOWN → Define Projection
        if not sr or sr.factoryCode in (None, 0):
            print(f"Unknown CRS → Defining as BNG: {fc}")

            arcpy.management.DefineProjection(
                in_dataset=in_path,
                coor_system=BNG_SR
            )

            print(f"Defined CRS as BNG: {fc}")
            continue

        # Case 2: Already BNG → Skip
        if sr.factoryCode == 27700:
            print(f"Already BNG: {fc}")
            continue

        # Case 3: Known CRS but not BNG → Project to new feature class
        
        # Create temp feature class (same workspace to avoid permissions issues)
        raw_temp_name = f"TMP_BNG_{fc}"
        temp_fc_name = arcpy.ValidateTableName(raw_temp_name, dirpath)
        temp_fc = os.path.join(dirpath, temp_fc_name)

        # Project to temp FC
        arcpy.management.Project(
            in_dataset=in_path,
            out_dataset=temp_fc,
            out_coor_system=BNG_SR
        )

        # Truncate original FC
        arcpy.management.TruncateTable(in_path)

        # Append back into original FC
        arcpy.management.Append(
            inputs=temp_fc,
            target=in_path,
            schema_type="NO_TEST"
        )

        # Clean up temp FC
        arcpy.management.Delete(temp_fc)

        print(f"Superseded in BNG: {fc}")


print("DONE: All data is now in BNG.")