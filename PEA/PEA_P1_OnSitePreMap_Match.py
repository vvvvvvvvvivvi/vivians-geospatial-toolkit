import arcpy

# ------------------------------------------------------------------
# INPUTS
# ------------------------------------------------------------------

master_fc = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\ArcGIS\003_PostSurvey\B245776V_CargoFleetLane_PostSurvey.gdb\UK_Habitat__Cleaned__261026"

annotated_fc = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Working\VL\001_DataCollection\CargoFleet_DataCollection.gdb\UK_Habitat___polygon__on_site_mapping__20261026_Extra_HabType"

overlap_threshold = 0.9


"""
PSEUDOCODE

1. Define input feature classes:
      - Master habitat layer
      - Annotated habitat layer
      - Minimum overlap threshold

2. Identify fields to transfer:
      - Read all fields from both datasets
      - Exclude geometry, ObjectID, editor tracking, and system fields
      - Keep only fields that exist in both datasets

3. Determine ObjectID fields:
      - Get OID field name for master layer
      - Get OID field name for annotated layer

4. Create polygon intersections:
      - Delete any existing temporary intersection dataset
      - Run Pairwise Intersect between master and annotated layers

5. Calculate master polygon areas:
      - Store each master polygon's area in a dictionary
      - Key = Master OID
      - Value = Polygon area

6. Find the best annotated polygon for each master polygon:
      - Loop through intersection records
      - Calculate overlap percentage:
            overlap area ÷ master polygon area
      - For each master polygon:
            keep only the annotated polygon with the highest overlap

7. Build an annotation lookup dictionary:
      - Read all annotated features
      - Store FeatureID and transferable attribute values
      - Key = Annotated OID
      - Value = Attribute record

8. Start an edit session on the master dataset

9. Update master polygons:
      - Loop through all master features
      - Skip features where Subtype = 8
      - Skip features with no overlap match
      - Skip matches below the overlap threshold
      - Copy attribute values from the matched annotated feature
      - Update the master record
      - Track which annotated features were used

10. Save edits and end edit session

11. Report skipped master features:
      - List all FeatureIDs with Subtype = 8

12. Report unused annotated features:
      - Identify annotated features that were never matched
      - List their FeatureIDs

13. Print summary statistics:
      - Number of polygons updated
      - Number of Subtype 8 polygons skipped
      - Number of annotated features not used

14. If an error occurs:
      - Roll back all edits
      - Stop editing
      - Raise the error for troubleshooting
"""

# ------------------------------------------------------------------
# BUILD FIELD LIST
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

master_field_names = {
    f.name
    for f in arcpy.ListFields(master_fc)
}

fields_to_transfer = [
    f.name
    for f in arcpy.ListFields(annotated_fc)
    if (
        f.name in master_field_names
        and f.name not in exclude_fields
        and f.type not in ("OID", "Geometry", "Blob", "Raster")
    )
]

print(f"Fields to transfer: {len(fields_to_transfer)}")

for field in fields_to_transfer:
    print(field)

# ------------------------------------------------------------------
# OID FIELDS
# ------------------------------------------------------------------

master_oid_field = arcpy.Describe(master_fc).OIDFieldName
annotated_oid_field = arcpy.Describe(annotated_fc).OIDFieldName

# ------------------------------------------------------------------
# INTERSECT
# ------------------------------------------------------------------

intersect_fc = r"memory\intersections"

if arcpy.Exists(intersect_fc):
    arcpy.management.Delete(intersect_fc)

arcpy.analysis.PairwiseIntersect(
    [master_fc, annotated_fc],
    intersect_fc
)

# ------------------------------------------------------------------
# MASTER AREAS
# ------------------------------------------------------------------

master_area = {}

with arcpy.da.SearchCursor(
    master_fc,
    [master_oid_field, "SHAPE@AREA"]
) as cursor:

    for oid, area in cursor:
        master_area[oid] = area

# ------------------------------------------------------------------
# FIND BEST MATCH
# ------------------------------------------------------------------

master_name = arcpy.Describe(master_fc).baseName
annotated_name = arcpy.Describe(annotated_fc).baseName

fid_master = f"FID_{master_name}"
fid_annotated = f"FID_{annotated_name}"

best_match = {}

with arcpy.da.SearchCursor(
    intersect_fc,
    [fid_master, fid_annotated, "SHAPE@AREA"]
) as cursor:

    for master_oid, anno_oid, overlap_area in cursor:

        if master_oid == -1 or anno_oid == -1:
            continue

        overlap_pct = overlap_area / master_area[master_oid]

        if master_oid not in best_match:
            best_match[master_oid] = (anno_oid, overlap_pct)

        elif overlap_pct > best_match[master_oid][1]:
            best_match[master_oid] = (anno_oid, overlap_pct)

print(f"Matched {len(best_match)} polygons")

# ------------------------------------------------------------------
# BUILD ATTRIBUTE LOOKUP
# ------------------------------------------------------------------

annotation_lookup = {}

with arcpy.da.SearchCursor(
    annotated_fc,
    [annotated_oid_field, "FeatureID"] + fields_to_transfer
) as cursor:

    for row in cursor:

        anno_oid = row[0]
        feature_id = row[1]

        annotation_lookup[anno_oid] = {
            "FeatureID": feature_id,
            "values": row[2:]
        }

print(f"Loaded {len(annotation_lookup)} annotated records")

# ------------------------------------------------------------------
# UPDATE MASTER
# ------------------------------------------------------------------

workspace = arcpy.Describe(master_fc).path

editor = arcpy.da.Editor(workspace)

editor.startEditing(False, True)
editor.startOperation()

try:

    updated_count = 0

    omitted_featureids = []
    used_annotation_oids = set()

    cursor_fields = (
        [master_oid_field, "FeatureID", "Subtype"]
        + fields_to_transfer
    )

    with arcpy.da.UpdateCursor(
        master_fc,
        cursor_fields
    ) as cursor:

        for row in cursor:

            master_oid = row[0]
            master_featureid = row[1]
            subtype = row[2]

            # ------------------------------------------------------
            # OMIT SUBTYPE 8 FEATURES
            # ------------------------------------------------------

            if subtype == 8:
                omitted_featureids.append(master_featureid)
                continue

            if master_oid not in best_match:
                continue

            anno_oid, overlap_pct = best_match[master_oid]

            if overlap_pct < overlap_threshold:
                continue

            if anno_oid not in annotation_lookup:
                continue

            values = annotation_lookup[anno_oid]["values"]

            for i, value in enumerate(values, start=3):
                row[i] = value

            cursor.updateRow(row)

            updated_count += 1
            used_annotation_oids.add(anno_oid)

    editor.stopOperation()
    editor.stopEditing(True)

    print(f"\nUpdated {updated_count} polygons")

    # ------------------------------------------------------------------
    # REPORT OMITTED MASTER FEATURES
    # ------------------------------------------------------------------

    omitted_featureids = sorted(
        [str(fid) for fid in omitted_featureids if fid is not None]
    )

    print("\n==================================================")
    print("MASTER FEATURES SKIPPED (Subtype = 8)")
    print("==================================================")

    if omitted_featureids:
        for fid in omitted_featureids:
            print(fid)
    else:
        print("None")

    # ------------------------------------------------------------------
    # REPORT UNMATCHED ANNOTATED FEATURES
    # ------------------------------------------------------------------

    unused_annotations = []

    for anno_oid, record in annotation_lookup.items():

        if anno_oid not in used_annotation_oids:
            unused_annotations.append(record["FeatureID"])

    unused_annotations = sorted(
        [str(fid) for fid in unused_annotations if fid is not None]
    )

    print("\n==================================================")
    print("ANNOTATED FEATURES NOT APPENDED TO MASTER")
    print("==================================================")

    if unused_annotations:
        for fid in unused_annotations:
            print(fid)
    else:
        print("None")

    print("\nSummary:")
    print(f"  Updated polygons: {updated_count}")
    print(f"  Skipped Subtype=8 polygons: {len(omitted_featureids)}")
    print(f"  Unused annotated features: {len(unused_annotations)}")

except Exception:

    editor.stopOperation()
    editor.stopEditing(False)
    raise