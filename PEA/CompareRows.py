import arcpy
import csv
import os

# =====================================================================
# USER INPUTS
# =====================================================================

old_fc = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\ArcGIS\003_PostSurvey\CargoFleetLane_SurveyUKHabitatData_20261016.gdb\UK_Habitat___polygon__on_site_mapping_"
new_fc = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\ArcGIS\003_PostSurvey\CargoFleetLane_SurveyUKHabitatData_20261026.gdb\UK_Habitat___polygon__on_site_mapping_"

output_csv = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Working\VL\001_DataCollection\Changed_GlobalIDs.csv"

# =====================================================================
# FIELDS TO IGNORE
# =====================================================================

IGNORE_FIELDS = {
    "Shape",
    "Shape_Length",
    "Shape_Area",
    "GlobalID",
    "CreationDate",
    "Creator",
    "EditDate",
    "Editor",
    "FeatureID",
}

# =====================================================================
# GET COMPARISON FIELDS
# =====================================================================

fields = [
    f.name
    for f in arcpy.ListFields(old_fc)
    if f.name not in IGNORE_FIELDS
    and not f.required
]

globalid_field = "ObjectID"

# =====================================================================
# LOAD OLD DATA
# =====================================================================

old_dict = {}

cursor_fields = [globalid_field] + fields

with arcpy.da.SearchCursor(old_fc, cursor_fields) as cursor:
    for row in cursor:
        gid = str(row[0]).upper()
        old_dict[gid] = row[1:]

# =====================================================================
# COMPARE WITH NEW DATA
# =====================================================================

changes = []

with arcpy.da.SearchCursor(new_fc, cursor_fields) as cursor:
    for row in cursor:

        gid = str(row[0]).upper()

        if gid not in old_dict:
            continue

        old_values = old_dict[gid]
        new_values = row[1:]

        for idx, field_name in enumerate(fields):

            old_val = old_values[idx]
            new_val = new_values[idx]

            # Handle NULLs consistently
            if old_val is None:
                old_val = ""

            if new_val is None:
                new_val = ""

            if str(old_val) != str(new_val):

                changes.append([
                    gid,
                    field_name,
                    old_val,
                    new_val
                ])

# =====================================================================
# EXPORT RESULTS
# =====================================================================

with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "ObjectID",
        "FieldName",
        "OldValue",
        "NewValue"
    ])

    writer.writerows(changes)

# =====================================================================
# SUMMARY
# =====================================================================

changed_globalids = len(set(row[0] for row in changes))

print("=" * 60)
print(f"Changed GlobalIDs: {changed_globalids}")
print(f"Changed Attributes: {len(changes)}")
print(f"Output: {output_csv}")
print("=" * 60)