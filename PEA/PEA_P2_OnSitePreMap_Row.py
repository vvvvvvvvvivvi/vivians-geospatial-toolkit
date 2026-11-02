import arcpy

# ------------------------------------------------------------------
# INPUTS
# ------------------------------------------------------------------

master_fc = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\ArcGIS\003_PostSurvey\B245776V_CargoFleetLane_PostSurvey.gdb\UK_Habitat__Cleaned"

annotated_fc = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\ArcGIS\003_PostSurvey\CargoFleetLane_SurveyUKHabitatData_20261016.gdb\UK_Habitat___polygon__pre_mapping_"

"""
PSEUDOCODE

1. Define input feature classes:
      - Master habitat dataset
      - Annotated habitat dataset

2. Define manual feature matches:
      - Create a list of FeatureID pairs
      - Each pair links:
            Annotated FeatureID → Master FeatureID
      - Allow a single annotated feature to populate
        multiple master features

3. Build a target-to-source lookup dictionary:
      - Convert match list into a lookup table
      - Key = Master FeatureID
      - Value = Annotated FeatureID

4. Identify fields to transfer:
      - Read fields from both datasets
      - Exclude geometry, ObjectID, editor tracking,
        and other system fields
      - Keep only fields that exist in both datasets
      - Ignore unsupported field types
        (OID, Geometry, Blob, Raster)

5. Build an annotated feature lookup:
      - Read all annotated records
      - Store transferable field values
      - Key = Annotated FeatureID
      - Value = Attribute values

6. Start an edit session:
      - Open the workspace containing the master dataset
      - Begin a transaction for editing

7. Update manually matched features:
      - Loop through every feature in the master dataset
      - Read its FeatureID

      - If the FeatureID is not in the manual match list:
            Skip the feature

      - Find the corresponding source FeatureID
        in the annotated dataset

      - If the source FeatureID does not exist:
            Report a warning
            Skip the feature

      - Retrieve the source attribute values

      - Copy all transfer fields from the source
        feature to the master feature

      - Save the updated record

      - Increment update counter

      - Print a message showing:
            Master FeatureID updated
            Source FeatureID used

8. Save edits:
      - Commit all updates
      - End the edit operation
      - End the edit session

9. Handle errors:
      - Cancel all edits
      - Roll back changes
      - Stop editing
      - Raise the error for troubleshooting

10. Print summary:
      - Display total number of master polygons
        successfully updated

PROCESS SUMMARY

This script manually transfers attributes from selected
annotated habitat polygons to specific master habitat polygons
using predefined FeatureID relationships. Unlike the spatial
matching workflow, no geometry comparison or overlap analysis
is performed. Attribute values are copied directly according
to the user-defined FeatureID mapping, allowing one annotated
feature to populate one or many master features.
"""

# ------------------------------------------------------------------
# MANUAL FEATURE MATCHES
# (Annotated FeatureID, Master FeatureID)
# ------------------------------------------------------------------

feature_matches = [
    ("add_1", "cor_1"),
    # ("add_1", "cor_2"),
    # ("add_2", "cor_3"),
    # ("add_4", "CFL_534"),
    # ("ano_01", "cor_5"),
    # ("CFL_332", "CFL_332"),
    # ("CFL_332", "CFL_332"),
    # ("Ano_04", "CFL_264"),
    # ("Ano_04", "CFL_22"),
    # ("Ano_04", "CFL_199"),
    # ("CFL_184", "CFL_184"),
    # ("Ano_04", "CFL_90"),
    # ("Ano_05", "CFL_255"),
    # ("Ano_05", "CFL_211"),
    # ("Ano_06", "CFL_392"),
    # ("Ano_05", "CFL_262"),
    # ("APP_8", "CFL_258"),
    # ("APP_9", "CFL_493"),
    # ("APP_9", "CFL_7"),
    # ("APP_9", "CFL_2"),
    # ("APP_10", "CFL_507"),
    # ("APP_9", "CFL_132"),
    # ("APP_3", "CFL_298"),
    # ("APP_11", "CFL_456"),
    # ("APP_12", "CHG_2"),
    # ("APP_13", "CFL_320"),
    # ("APP_13", "CFL_93"),
    # ("APP_13", "CFL_384"),
    # ("APP_14", "CFL_25"),
    # ("APP_14", "CFL_450"),
    # ("APP_14", "CFL_346"),
    # ("APP_14", "CFL_511"),
    # ("APP_15", "CFL_190"),

   
]

# ------------------------------------------------------------------
# BUILD TARGET -> SOURCE LOOKUP
# ------------------------------------------------------------------

target_to_source = {
    target: source
    for source, target in feature_matches
}

# ------------------------------------------------------------------
# FIELDS TO TRANSFER
# ------------------------------------------------------------------

exclude_fields = {
    "OBJECTID",
    "FID",
    "Shape",
    "Shape_Length",
    "Shape_Area",
    "GlobalID",
    "created_user",
    "created_date",
    "last_edited_user",
    "last_edited_date"
}

master_fields = {
    f.name
    for f in arcpy.ListFields(master_fc)
}

fields_to_transfer = [
    f.name
    for f in arcpy.ListFields(annotated_fc)
    if (
        f.name in master_fields
        and f.name not in exclude_fields
        and f.type not in ("OID", "Geometry", "Blob", "Raster")
    )
]

print(f"Transferring {len(fields_to_transfer)} fields")

# ------------------------------------------------------------------
# BUILD ANNOTATED ATTRIBUTE LOOKUP
# ------------------------------------------------------------------

annotated_lookup = {}

with arcpy.da.SearchCursor(
    annotated_fc,
    ["FeatureID"] + fields_to_transfer
) as cursor:

    for row in cursor:
        annotated_lookup[str(row[0])] = row[1:]

print(f"Loaded {len(annotated_lookup)} annotated records")

# ------------------------------------------------------------------
# START EDIT SESSION
# ------------------------------------------------------------------

workspace = arcpy.Describe(master_fc).path

editor = arcpy.da.Editor(workspace)

editor.startEditing(False, True)
editor.startOperation()

updated = 0

try:

    with arcpy.da.UpdateCursor(
        master_fc,
        ["FeatureID"] + fields_to_transfer
    ) as cursor:

        for row in cursor:

            target_featureid = str(row[0])

            if target_featureid not in target_to_source:
                continue

            source_featureid = target_to_source[target_featureid]

            if source_featureid not in annotated_lookup:
                print(
                    f"Could not find source FeatureID: "
                    f"{source_featureid}"
                )
                continue

            values = annotated_lookup[source_featureid]

            for i, value in enumerate(values, start=1):
                row[i] = value

            cursor.updateRow(row)
            updated += 1

            print(
                f"Updated {target_featureid} "
                f"from {source_featureid}"
            )

    editor.stopOperation()
    editor.stopEditing(True)

except Exception:
    editor.stopOperation()
    editor.stopEditing(False)
    raise

print(f"\nUpdated {updated} manually matched polygons.")