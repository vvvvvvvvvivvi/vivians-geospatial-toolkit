import arcpy
import sys
import tempfile
from pathlib import Path


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

def apply_metadata(map_obj, name, project_code, project_name, prefix, pm_id, abbrv, details):
    cat_name = prefix_lookup.get(prefix, "Unknown")

    map_obj.metadata.title = name
    map_obj.metadata.tags = f"Project Mapper, PM, {cat_name}, {prefix}, {(details).replace(' ', '')}, {project_code}, {abbrv}, {(project_name).replace(' ', '')}, {name}, {pm_id}"
    map_obj.metadata.summary = f"{details} for {re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', cat_name)} web map for Cargo Fleet Lane Project Mapper."
    map_obj.metadata.description = f"Linked to registered Project Mapper: {pm_id}"


    map_obj.metadata.save()

def get_user_inputs(prefix, heading):
    print(f"\n--- Configuring prefix: {prefix} ---")
    
    publishing_path = Path(
        input(f"Publishing APRX path for '{prefix}' (you may include the full path in quotes): ").strip().strip('"')
    )

    abbrv = input("Project abbreviation (optional): ").strip()

    pm_id = input("Project Mapper ID (optional): ").strip()

    details = input("Layer details/ description (optional): ").strip()

    map_name = f"{abbrv}_{prefix}_{heading}"

    print(f"✅ Map name: {map_name}")

    return publishing_path, abbrv, heading, map_name, pm_id, details

def import_map(publishing_aprx, mapx_path):
    result = publishing_aprx.importDocument(str(mapx_path))

    if isinstance(result, list):
        return result[0]

    return result

def get_max_scale(row_count):
    for threshold, scale in SCALE_RULES:
        if row_count < threshold:
            return scale
    return 5000

def get_row_count(layer):
    return int(arcpy.management.GetCount(layer)[0])
