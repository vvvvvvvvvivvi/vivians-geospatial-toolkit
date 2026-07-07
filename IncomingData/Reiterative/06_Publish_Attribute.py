import arcpy
import re
import sys
from pathlib import Path

publishing_path = Path(sys.argv[8])
publishing_map_name = sys.argv[9]

arcpy.env.overwriteOutput = True

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

KEYWORD_MAP = {
    "name": "Name",
    "add": "Address",
    "ref": "Reference",
    "dist": "Distance",
    "appl": "Application",
    "num": "Number",
    "no": "Number",
    "desc": "Description",
    "feat": "Feature",
    "ngr": "NGR",
    "northing": "Northing",
}

PROTECTED_WORDS = ["SHAPELength", "SHAPEArea", "OBJECTID", "Shape", "Shape_Length", "Shape_Area"]

# ---------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------

def has_camel_case(text):
    """
    Detect camelCase / PascalCase (lowercase followed by uppercase).
    """
    return bool(re.search(r"[a-z][A-Z]", text))


def split_camel_case(text):
    """
    Split camelCase / PascalCase safely.
    """
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)


def expand_keywords(words):
    expanded = []

    for word in words:
        word_lc = word.lower()
        if word_lc in PROTECTED_WORDS:
            continue  # Skip protected words

        # Units (exact match only)
        if word_lc == "m":
            expanded.append("(m)")
            continue
        if word_lc == "km":
            expanded.append("(km)")
            continue
        if word_lc == "ha":
            expanded.append("(ha)")
            continue
        if word_lc == "node":
            expanded.append("Node")
            continue


        # Keyword expansion
        replaced = False
        for key, value in KEYWORD_MAP.items():
            if word_lc.startswith('northing') or word_lc.startswith('Node'):
                expanded.append(word.capitalize())
                replaced = True
                break

            if word_lc == key or word_lc.startswith(key):
                expanded.append(value)
                replaced = True
                break

        if not replaced:
            expanded.append(word.capitalize())

    return expanded


def generate_alias_from_name(field_name):
    alias = field_name.replace("_", " ")

    if has_camel_case(alias):
        alias = split_camel_case(alias)

    words = alias.split()
    words = expand_keywords(words)

    alias = " ".join(words)
    alias = re.sub(r"\bId\b", "ID", alias)

    return alias


def update_field_aliases(layer):
    """
    Update field aliases only (no renaming).
    """
    print(f"\nProcessing layer: {layer.name}")

    for field in arcpy.ListFields(layer):

        if (
            field.required
            or field.type in ("OID", "Geometry")
            or field.name.upper() == "OBJECTID"
        ):
            continue

        new_alias = generate_alias_from_name(field.name)

        if field.aliasName != new_alias:
            print(f"  Updating alias: {field.name} → {new_alias}")

            try:
                arcpy.management.AlterField(
                    in_table=layer,
                    field=field.name,
                    new_field_alias=new_alias
                )
            except Exception:
                print(f"  ❌ Failed on {field.name}")
                print(arcpy.GetMessages())

    arcpy.management.ClearWorkspaceCache()


def list_fields_and_aliases(layer):
    """
    Print final field names and aliases.
    """
    print(f"\nFinal fields for layer: {layer.name}")
    for field in arcpy.ListFields(layer):
        print(f"  {field.name} → {field.aliasName}")


# ---------------------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------------------

aprx = arcpy.mp.ArcGISProject(str(publishing_path))
maps = aprx.listMaps(publishing_map_name)

if not maps:
    raise RuntimeError(f"Map not found: {publishing_map_name}")

for m in maps:
    for lyr in m.listLayers():
        if lyr.isFeatureLayer and not lyr.isGroupLayer:
            update_field_aliases(lyr)
            list_fields_and_aliases(lyr)

print("\n✅ Field alias standardisation complete.")