import arcpy
import re

# Configuration

APRX_PATH = r"\\location\to.aprx" # Path link to aprx
MAP_NAME = "EHSaferSpeeds_tr_MapEssex"

MAX_FIELD_LENGTH = 64

# Optional enforced renames (lowercase keys)
COMMON_FIELD_NAMES = {
    # "oldname": "new_name",
}

# Helpers

def sanitise_field_name(field_name):
    """
    Sanitise a field name to comply with FGDB / SDE rules.
    """
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", field_name)
    cleaned = re.sub(r"_+", "_", cleaned)

    if not cleaned[0].isalpha():
        cleaned = f"f_{cleaned}"

    return cleaned[:MAX_FIELD_LENGTH]


def generate_alias(field_name):
    """
    Generate a clean alias:
    - Replace underscores with spaces
    - Title Case
    - Convert standalone 'Id' or 'id' to 'ID'
      (but NOT words like 'collide', 'identifier', etc.)
    """
    alias = field_name.replace("_", " ").title()

    # Replace standalone 'Id' with 'ID'
    alias = re.sub(r"\bId\b", "ID", alias)

    return alias


def rename_and_update_fields(layer):
    """
    Sanitise field names and update aliases for a feature layer.
    """
    print(f"\nProcessing layer: {layer.name}")

    fields = arcpy.ListFields(layer)
    existing_names = {f.name.lower() for f in fields}

    for field in fields:

        # Skip system / non-editable fields
        if (
            field.required
            or field.type in ("OID", "Geometry")
            or field.name.upper() in ("OBJECTID",)
        ):
            continue

        old_name = field.name
        old_name_lc = old_name.lower()

        # Step 1: dictionary override
        if old_name_lc in COMMON_FIELD_NAMES:
            new_name = COMMON_FIELD_NAMES[old_name_lc]
        else:
            new_name = sanitise_field_name(old_name)

        new_alias = generate_alias(new_name)

        # If name is unchanged, only update alias if needed
        if new_name.lower() == old_name_lc:
            if field.aliasName != new_alias:
                print(f"  Updating alias: {old_name} â†’ {new_alias}")
                arcpy.management.AlterField(
                    in_table=layer,
                    field=old_name,
                    new_field_alias=new_alias
                )
            continue

        # Prevent name collision
        if new_name.lower() in existing_names:
            print(f"  âš  Skipping rename: {old_name} â†’ {new_name} (already exists)")
            continue

        print(f"  Renaming: {old_name} â†’ {new_name}")

        arcpy.management.AlterField(
            in_table=layer,
            field=old_name,
            new_field_name=new_name,
            new_field_alias=new_alias
        )

        existing_names.add(new_name.lower())

    arcpy.management.ClearWorkspaceCache()


def list_fields_and_aliases(layer):
    """
    Print all field names and aliases.
    """
    print(f"\nFinal fields for layer: {layer.name}")
    for field in arcpy.ListFields(layer):
        print(f"  {field.name} â†’ {field.aliasName}")


# Execute

aprx = arcpy.mp.ArcGISProject(APRX_PATH)

for m in aprx.listMaps(MAP_NAME):
    for lyr in m.listLayers():
        if lyr.isFeatureLayer and not lyr.isGroupLayer:
            rename_and_update_fields(lyr)
            list_fields_and_aliases(lyr)

print("\nâœ… Field name sanitisation and alias update complete.")