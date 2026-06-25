import arcpy
import os
from pathlib import Path
import sys
import tempfile

publishing_path = Path(sys.argv[1])
working_path = Path(sys.argv[2])
working_map_name = sys.argv[3]

publishing_map_abbrv = sys.argv[8]
publishing_map_prefix = sys.argv[9]
publishing_map_heading = sys.argv[10]
publishing_map_name = sys.argv[11]
project_code = sys.argv[12]
project_name = sys.argv[13]
final_publishing_map_abbrv = sys.argv[14]



# --------------------------------------------------
# Load projects
# --------------------------------------------------
publishing_aprx = arcpy.mp.ArcGISProject(publishing_path)
working_aprx = arcpy.mp.ArcGISProject(working_path)


# --------------------------------------------------
# Prefix dictionary
# --------------------------------------------------
prefix = {
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

cat_abbrv = publishing_map_prefix
cat_name = prefix.get(cat_abbrv, "Unknown")


# --------------------------------------------------
# Find working map
# --------------------------------------------------
working_map = None
for m in working_aprx.listMaps():
    if m.name == working_map_name:
        working_map = m
        break

if not working_map:
    raise Exception(f"Working map '{working_map_name}' not found.")

# --------------------------------------------------
# Import working map into publishing aprx
# --------------------------------------------------
# Create temp MAPX
temp_dir = Path(tempfile.mkdtemp())
mapx_path = temp_dir / f"{working_map_name}.mapx"

# Export map to MAPX
working_map.exportToMAPX(str(mapx_path))

# Import MAPX into publishing APRX
publishing_map = publishing_aprx.importDocument(str(mapx_path))

# Optional rename
publishing_map.name = publishing_map_name

publishing_aprx.save()



# --------------------------------------------------
# Scale rules (row count → max scale)
# --------------------------------------------------
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

def get_max_scale_from_rowcount(row_count):
    for threshold, scale in SCALE_RULES:
        if row_count < threshold:
            return scale
    return 5_000  # fallback for very large datasets

def get_layer_row_count(lyr):
    if lyr.isFeatureLayer:
        return int(arcpy.management.GetCount(lyr)[0])
    raise Exception(f"Layer '{lyr.name}' not found or not a feature layer.")


# --------------------------------------------------
# Apply per-layer scale logic
# --------------------------------------------------

for lyr in publishing_map.listLayers():
    # Skip non-feature layers and broken layers
    if not lyr.isFeatureLayer or lyr.isBroken:
        continue

    try:
        row_count = get_layer_row_count(lyr)
        max_scale = get_max_scale_from_rowcount(row_count)

        lyr.maxScale = max_scale

        print(
            f"Layer '{lyr.name}': "
            f"{row_count:,} rows → maxScale 1:{max_scale:,}"
        )

    except Exception as e:
        print(f"Skipping layer '{lyr.name}': {e}")


# --------------------------------------------------
# Metadata configuration
# --------------------------------------------------
name = publishing_map_name

publishing_map.metadata.title = name
publishing_map.metadata.tags = (
    f"{project_code}, {project_name}, {final_publishing_map_abbrv}, {cat_abbrv}, {cat_name}, {name}"
)
publishing_map.metadata.summary = (
    f"{name} for {project_code} {project_name}"
)
publishing_map.metadata.description = (
    f"{name} for {project_code} {project_name}"
)

publishing_map.metadata.save()

# --------------------------------------------------
# Save publishing project
# --------------------------------------------------
publishing_aprx.save()

print("Publishing map created, configured, and saved successfully.")