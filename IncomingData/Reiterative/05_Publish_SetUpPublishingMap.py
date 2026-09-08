import arcpy
import sys
import tempfile
from pathlib import Path
import re

# --------------------------------------------------
# Constants
# --------------------------------------------------

prefix_lookup = {
    "ab": "AdministrativeBoundaries",
    "aq": "AirQualityAndEmissions",
    "bm": "BaseMapping",
    "bu": "BuiltAssets",
    "ca": "CommunityAndAccess",
    "ch": "CulturalHeritage",
    "cl": "ClimateAndAtmosphere",
    "de": "Designations",
    "dg": "Demographics",
    "ds": "Designs",
    "ec": "Ecology",
    "ge": "GeologyAndSoils",
    "hs": "HealthAndSafety",
    "in": "Index",
    "lr": "LandRegistry",
    "ls": "Landscape",
    "lu": "LandUse",
    "no": "Noise",
    "pl": "Planning",
    "te": "Terrain",
    "tr": "Transportation",
    "ut": "Utilities",
    "wa": "Water"
}


SCALE_RULES = [
    (100, 1_000_000),
    (1_000, 500_000),
    (2_000, 100_000),
    (5_000, 50_000),
    (10_000, 24_000),
    (50_000, 10_000),
    (100_000, 5_000),
    (250_000, 2_000)
]

# --------------------------------------------------
# Utility Functions
# --------------------------------------------------

def get_prefixes_from_map(map_obj):
    prefixes = set()

    for lyr in map_obj.listLayers():
        if not lyr.isFeatureLayer:
            continue

        name = lyr.name.lower()

        if "_" in name:
            p = name.split("_")[0]
            if p in prefix_lookup:
                prefixes.add(p)

    return sorted(prefixes)


def get_max_scale(row_count):
    for threshold, scale in SCALE_RULES:
        if row_count < threshold:
            return scale
    return 5000


def get_row_count(layer):
    return int(arcpy.management.GetCount(layer)[0])


def export_map_to_mapx(map_obj):
    temp_dir = Path(tempfile.mkdtemp())
    mapx_path = temp_dir / f"{map_obj.name}.mapx"
    map_obj.exportToMAPX(str(mapx_path))
    return mapx_path


def import_map(publishing_aprx, mapx_path):
    result = publishing_aprx.importDocument(str(mapx_path))

    if isinstance(result, list):
        return result[0]

    return result


def filter_layers_by_prefix(map_obj, prefix):
    for lyr in map_obj.listLayers():
        if lyr.isFeatureLayer:
            if not lyr.name.lower().startswith(f"{prefix}_"):
                map_obj.removeLayer(lyr)

def clean_map_layers(map_obj):
    # Copy list to avoid issues while removing
    for lyr in list(map_obj.listLayers()):
        name = lyr.name.strip()

        # Remove "Working" layers
        if "working" in name.lower():
            map_obj.removeLayer(lyr)
            print(f"Removed working layer {name}")
            continue


        # Remove "Working" group
        if lyr.isGroupLayer and name.lower() == "working":
            map_obj.removeLayer(lyr)
            print("Removed group: Working")
            continue

        # Remove unwanted basemap layers
        if name in ["World Topographic Map", "World Hillshade"]:
            map_obj.removeLayer(lyr)
            print(f"Removed layer: {name}")
            continue

    # Set remaining layers to not visible
    for lyr in map_obj.listLayers():
        try:
            lyr.visible = False
        except Exception:
            pass

def apply_metadata(map_obj, name, project_code, project_name, prefix, abbrv, details, pm_id):
    cat_name = prefix_lookup.get(prefix, "Unknown")

    map_obj.metadata.title = name
    map_obj.metadata.tags = f"Project Mapper, PM, {cat_name}, {prefix}, {(details).replace(' ', '')}, {project_code}, {abbrv}, {(project_name).replace(' ', '')}, {name}, {pm_id}"
    map_obj.metadata.summary = f"{details} for {re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', cat_name)} web map for {(project_name).replace(' ', '')} Project Mapper."
    map_obj.metadata.description = f"Linked to registered Project Mapper: {pm_id}"

    map_obj.metadata.save()

def map_properties(map_obj):

    print("Map: " + map_obj.name)
    # Map properties 
    print("Get CIM")
    cim = map_obj.getDefinition("V3")

    print("Create dt1")
    dt1 = arcpy.cim.CreateCIMObjectFromClassName("CIMDatumTransform", "V3")

    print("Create dt2")
    dt2 = arcpy.cim.CreateCIMObjectFromClassName("CIMDatumTransform", "V3")

    print("Populate")
    dt1.forward = True
    dt1.geoTransformation = {
        "geoTransforms": [{
            "wkid": 5339,
            "latestWkid": 5339,
            "transformForward": False,
            "name": "OSGB_1936_To_WGS_1984_7"
        }]
    }

    dt2.forward = True
    dt2.geoTransformation = {
        "geoTransforms": [{
            "wkid": 5339,
            "latestWkid": 5339,
            "transformForward": False,
            "name": "OSGB_1936_To_WGS_1984_7"
        }]
    }

    print("Assign")
    cim.datumTransforms = [dt1, dt2]

    # Assignment of unique numeric IDs
    print("Set service layer IDs")
    cim.useServiceLayerIDs = True

    print("Set definition")
    map_obj.setDefinition(cim)


def get_user_inputs(prefix, heading):
    print(f"\n--- Configuring prefix: {prefix} ---")
    
    publishing_path = Path(
        input(f"Publishing APRX path for '{prefix}' (you may include the full path in quotes): ").strip().strip('"')
    )

    abbrv = input("Project abbreviation (optional): ").strip()

    map_name = f"{abbrv}_{prefix}_{heading}"

    print(f"✅ Map name: {map_name}")

    details = input("Map details/ description (optional): ").strip()

    pm_id = input("Project Mapper ID (optional): ").strip()


    return publishing_path, abbrv, heading, map_name, details, pm_id


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    working_path = Path(sys.argv[1])
    working_map_name = sys.argv[2]
    project_code = sys.argv[7]
    project_name = sys.argv[8]
    sde_user = sys.argv[6]

    working_aprx = arcpy.mp.ArcGISProject(working_path)

    # Find working map
    working_map = None
    for m in working_aprx.listMaps():
        if m.name == working_map_name:
            working_map = m
            break

    if not working_map:
        raise Exception(f"Map '{working_map_name}' not found.")

    # Detect prefixes
    prefixes = get_prefixes_from_map(working_map)

    print(f"\nDetected prefixes: {prefixes}")

    if not prefixes:
        print("No valid prefixes found.")
        return

    # Export working map once
    mapx_path = export_map_to_mapx(working_map)
    heading = input("Map heading: ").strip()

    for prefix in prefixes:

        publishing_path, abbrv, heading, map_name, details, pm_id = get_user_inputs(prefix, heading)
        publishing_aprx = arcpy.mp.ArcGISProject(publishing_path)

        # Import map
        pub_map = import_map(publishing_aprx, mapx_path)
        pub_map.name = map_name

        # Filter layers
        filter_layers_by_prefix(pub_map, prefix)

        # Clean layers
        clean_map_layers(pub_map)

        # Metadata
        apply_metadata(pub_map, map_name, project_code, project_name, prefix, abbrv, details, pm_id)

        map_properties(pub_map)

        publishing_aprx.save()

        print(f"✅ Finished {map_name}")

    print("\n🎉 Publishing map created, configured, and saved successfully.")


if __name__ == "__main__":
    main()