import arcpy
import sys
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

def get_row_count(layer):
    return int(arcpy.management.GetCount(layer)[0])

def get_max_scale(row_count):
    for threshold, scale in SCALE_RULES:
        if row_count < threshold:
            return scale
    return 5000

def apply_scale_rules(map_obj):
    for lyr in map_obj.listLayers():
        if not lyr.isFeatureLayer or lyr.isBroken:
            continue

        try:
            count = get_row_count(lyr)
            scale = get_max_scale(count)
            lyr.maxScale = scale

            print(f"{lyr.name}: {count:,} rows → 1:{scale:,}")

        except Exception as e:
            print(f"Skipped {lyr.name}: {e}")

def main():

    publishing_path = Path(sys.argv[8])
    publishing_map_name = sys.argv[9]

    publishing_aprx = arcpy.mp.ArcGISProject(publishing_path)

    # Find working map
    publishing_map = None
    for m in publishing_aprx.listMaps():
        if m.name == publishing_map_name:
            publishing_map = m
            break

    if not publishing_map:
        raise Exception(f"Map '{publishing_map_name}' not found.")

    # Apply rules
    apply_scale_rules(publishing_map)

    publishing_aprx.save()

    print("\n✅ Scale rules applied successfully.")

if __name__ == "__main__":
    main()