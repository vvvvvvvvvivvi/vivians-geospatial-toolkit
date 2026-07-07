import arcpy
import os 
import sys
from pathlib import Path

working_path = Path(sys.argv[1])
working_map_name = sys.argv[2]
sde_path = Path(sys.argv[3])
sde_user = sys.argv[5]


# Parametres
WORKING_GROUP_NAME = "Working"

    
# Open project
aprx = arcpy.mp.ArcGISProject(working_path)

arcpy.env.workspace = str(sde_path)

print("Starting process...")

for m in aprx.listMaps(working_map_name):

    # Get or create the Working group layer
    working_group = None
    for lyr in m.listLayers():
        if lyr.isGroupLayer and lyr.name == WORKING_GROUP_NAME:
            working_group = lyr
            break

    if not working_group:
        working_group = m.createGroupLayer(WORKING_GROUP_NAME)
        print("Created 'Working' group layer")

    # Process target layer
    for lyr in m.listLayers():

        if not lyr.isFeatureLayer or lyr.isGroupLayer:
            continue

        print(f"Processing layer: {lyr.name}")

        # Store definition query
        def_query = lyr.definitionQuery

        # Build SDE feature class path
        fc_path = os.path.join(sde_path, f"{sde_user}.{lyr.name}")

        if arcpy.Describe(lyr).path == fc_path:
            print(f"❌ Layer already driven by SDE data: {fc_path}")
            continue

        # Add SDE layer
        try:
            new_layer = m.addDataFromPath(fc_path)
        except:
            print(f"❌ Failed to add SDE layer: {fc_path}")
            continue


        # Apply symbology (RECOMMENDED method)
        try:
            arcpy.management.ApplySymbologyFromLayer(
                in_layer=new_layer,
                in_symbology_layer=lyr
            )
            print("✅ Symbology applied")
        except Exception as e:
            print(f"⚠️ Symbology application failed: {e}")

        # Apply definition query
        new_layer.definitionQuery = def_query


        # Rename to match original (clean TOC)
        new_layer.name = lyr.name
        lyr.name = ("Working_" + lyr.name)

        # Move old service layer into Working group
        m.moveLayer(working_group, lyr, "BEFORE")

        print("✅ Old service layer archived in 'Working' group")

        

# Save project
aprx.save()
del aprx

print("Done.")