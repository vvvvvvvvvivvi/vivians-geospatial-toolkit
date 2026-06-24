import arcpy
import os

# --------------------------------------------------
# Parameters
# --------------------------------------------------
publishing_path = r""        # Path to publishing APRX
working_path = r""           # Path to working APRX

working_map_name = ""        # Name of the map to copy
scale_driver_layer = ""      # Layer used to determine scale

publishing_map_abbrv = ""    # Optional override
publishing_map_prefix = ""
publishing_map_heading = ""

# --------------------------------------------------
# Load projects
# --------------------------------------------------
publishing_aprx = arcpy.mp.ArcGISProject(publishing_path)
working_aprx = arcpy.mp.ArcGISProject(working_path)

# --------------------------------------------------
# Extract project info
# --------------------------------------------------
project_folder = os.path.basename(
    os.path.dirname(os.path.dirname(os.path.dirname(publishing_path)))
)
project_code, project_name = project_folder.split("_")

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
# Resolve publishing map abbreviation
# --------------------------------------------------
existing_maps = publishing_aprx.listMaps()
existing_publishing_map_abbrv = existing_maps[0].name if existing_maps else ""

if not publishing_map_abbrv or publishing_map_abbrv == existing_publishing_map_abbrv:
    final_publishing_map_abbrv = existing_publishing_map_abbrv
else:
    final_publishing_map_abbrv = publishing_map_abbrv

# --------------------------------------------------
# Construct publishing map name
# --------------------------------------------------
publishing_map_name = (
    f"{final_publishing_map_abbrv}_"
    f"{publishing_map_prefix}_"
    f"{publishing_map_heading}"
)

print(f"Publishing map named: {publishing_map_name}")

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
# Import working APRX and extract copied map
# --------------------------------------------------
imported_aprx = publishing_aprx.importDocument(working_path)

publishing_map = None
for m in imported_aprx.listMaps():
    if m.name == working_map_name:
        publishing_map = m
        break

if not publishing_map:
    raise Exception("Failed to import working map.")

publishing_map.name = publishing_map_name

# --------------------------------------------------
# Scale rules (row count â†’ max scale)
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

def get_layer_row_count(map_obj, layer_name):
    for lyr in map_obj.listLayers():
        if lyr.name == layer_name and lyr.isFeatureLayer:
            return int(arcpy.management.GetCount(lyr)[0])
    raise Exception(f"Layer '{layer_name}' not found or not a feature layer.")

# --------------------------------------------------
# Apply scale logic
# --------------------------------------------------
row_count = get_layer_row_count(publishing_map, scale_driver_layer)
max_scale = get_max_scale_from_rowcount(row_count)

publishing_map.maxScale = max_scale

print(f"Row count: {row_count:,}")
print(f"Max scale set to 1:{max_scale:,}")

# --------------------------------------------------
# Metadata configuration
# --------------------------------------------------
name = publishing_map_name

publishing_map.metadata.title = name
publishing_map.metadata.tags = (
    f"{project_code}, {project_name}, {final_publishing_map_abbrv}, "
    f"{cat_abbrv}, {cat_name}, {name}"
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