import arcpy
import os
import sys
from pathlib import Path


working_path = sys.argv[1]
working_map_name = sys.argv[2]
sde_path = sys.argv[3]

BNG_SR = arcpy.SpatialReference(27700)

arcpy.env.overwriteOutput = True

# ==============================
# LOAD PROJECT
# ==============================
aprx = arcpy.mp.ArcGISProject(working_path)

maps = aprx.listMaps(working_map_name)
if not maps:
    raise RuntimeError(f"Map not found: {working_map_name}")

map_obj = maps[0]

# ==============================
# MAIN LOOP
# ==============================
for lyr in map_obj.listLayers():

    if not lyr.isFeatureLayer:
        continue

    layer_name = lyr.name

    try:
        desc = arcpy.Describe(lyr)
        sr = desc.spatialReference

        in_dataset = desc.catalogPath  # ✅ Use real source, not layer object
        print(in_dataset)

        # ------------------------------
        # CASE 1: UNKNOWN CRS
        # ------------------------------
        if not sr or sr.factoryCode in (None, 0):
            print(f"⚠️ Unknown CRS → Defining BNG: {layer_name}")

            arcpy.management.DefineProjection(
                in_dataset=Path(in_dataset),
                coor_system=BNG_SR
            )

            out_dataset = Path(in_dataset)  # No copy needed

        # ------------------------------
        # CASE 2: Already BNG
        # ------------------------------
        elif sr.factoryCode == 27700:
            print(f"✅ Already BNG: {layer_name}")
            out_dataset = in_dataset

        # ------------------------------
        # CASE 3: Needs reprojection
        # ------------------------------
        else:
            print(f"🔄 Reprojecting to BNG: {layer_name}")

            workspace = os.path.dirname(in_dataset)

            temp_name = arcpy.ValidateTableName(f"TMP_BNG_{layer_name}", workspace)
            temp_fc = os.path.join(workspace, temp_name)

            arcpy.management.Project(
                in_dataset=Path(in_dataset),
                out_dataset=Path(temp_fc),
                out_coor_system=BNG_SR
            )

            out_dataset = temp_fc

        # ------------------------------
        # EXPORT TO SDE
        # ------------------------------
                
        # Ensure string paths
        out_dataset = str(out_dataset)

        validated_name = arcpy.CreateUniqueName(layer_name, sde_path)
        export_path = os.path.join(sde_path, validated_name)

        # Delete if exists (important for SDE)
        if arcpy.Exists(export_path):
            arcpy.management.Delete(export_path)

        print(f"🚀 Exporting {layer_name} → {validated_name}")

        arcpy.conversion.ExportFeatures(
            out_dataset,
            export_path
        )

        # ------------------------------
        # CLEANUP TEMP DATA
        # ------------------------------
        if "TMP_BNG_" in out_dataset:
            arcpy.management.Delete(out_dataset)

    except Exception:
        print(f"❌ Failed: {layer_name}")
        print(arcpy.GetMessages())

print("\n✅ Export complete (all data in BNG).")