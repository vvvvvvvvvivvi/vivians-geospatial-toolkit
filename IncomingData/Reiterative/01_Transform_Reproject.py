import arcpy
import os
import uuid
import sys

working_path = sys.argv[1]
working_map_name = sys.argv[2]
sde_path = sys.argv[3]


BNG_SR = arcpy.SpatialReference(27700)
WGS_BNG = "OSGB_1936_To_WGS_1984_7"

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
            
        # Create temp feature class
        raw_temp_name = f"TMP_BNG_{fc}"
        temp_fc_name = arcpy.ValidateTableName(raw_temp_name, sde_path)
        temp_fc = os.path.join(sde_path, temp_fc_name)

        print(f"Projecting {fc} to BNG...")

        arcpy.management.Project(
            in_dataset=in_path,
            out_dataset=temp_fc,
            out_coor_system=BNG_SR,
            transform_method=WGS_BNG
        )

        print(f"Deleting original feature class: {fc}")

        arcpy.management.Delete(in_path)

        # Rename projected FC back to original name
        original_name = fc.split(".")[-1]

        print(f"Renaming projected feature class to: {original_name}")

        arcpy.management.Rename(
            in_data=temp_fc,
            out_data=original_name,
            data_type="FeatureClass"
        )

        print(f"Superseded in BNG: {fc}")

        # Verification
        final_fc = os.path.join(sde_path, fc)
        final_sr = arcpy.Describe(final_fc).spatialReference

        print(
            f"Final CRS: {final_sr.name} "
            f"(EPSG:{final_sr.factoryCode})"
        )


print("DONE: All data is now in BNG.")