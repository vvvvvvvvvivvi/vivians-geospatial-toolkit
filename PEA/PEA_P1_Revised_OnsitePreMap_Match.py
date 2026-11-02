import arcpy


# ------------------------------------------------------------------
# INPUTS
# ------------------------------------------------------------------

master_fc = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\ArcGIS\003_PostSurvey\B245776V_CargoFleetLane_PostSurvey.gdb\UK_Habitat__Cleaned__261026"

annotated_fc = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Working\VL\001_DataCollection\CargoFleet_DataCollection.gdb\UK_Habitat___polygon__on_site_mapping__20261026_Extra_HabType"

overlap_threshold = 0.9

# Change these settings for each project.
# Width 2 produces CFL_01, CFL_02, ..., CFL_100, etc.
feature_id_prefix = "CFL_"
feature_id_number_width = 2

urban_subtype = 6
water_subtype = 8


# ------------------------------------------------------------------
# CHECK AND ASSIGN FEATURE IDs BEFORE SPATIAL MATCHING
# Uniqueness is checked separately within each layer.
# Existing nonblank, unique IDs are preserved.
# For duplicates, the lowest ObjectID keeps the original ID.
# ------------------------------------------------------------------

def ensure_unique_feature_ids(feature_class):
    oid_field = arcpy.Describe(feature_class).OIDFieldName
    id_fields = [
        field for field in arcpy.ListFields(feature_class)
        if field.name.lower() == "featureid"
    ]

    if not id_fields or id_fields[0].type != "String":
        raise ValueError(
            f"{feature_class}: FeatureID must exist as a text field."
        )

    id_field = id_fields[0]

    with arcpy.da.SearchCursor(
        feature_class, [oid_field, id_field.name]
    ) as cursor:
        records = sorted(list(cursor), key=lambda row: row[0])

    # Compare trimmed IDs case-insensitively without rewriting valid IDs.
    existing_ids = {
        value.strip().casefold()
        for _, value in records
        if value is not None and value.strip()
    }

    highest_number = 0
    for _, value in records:
        if value is None:
            continue
        text = value.strip()
        if text.casefold().startswith(feature_id_prefix.casefold()):
            suffix = "_name"
            if suffix.isascii() and suffix.isdigit():
                highest_number = max(highest_number, int(suffix))

    next_number = highest_number + 1
    seen_ids = set()
    replacements = {}

    for oid, old_id in records:
        key = old_id.strip().casefold() if old_id is not None else ""

        if key and key not in seen_ids:
            seen_ids.add(key)
            continue

        reason = "blank" if not key else "duplicate"

        while True:
            new_id = (
                f"{feature_id_prefix}"
                f"{next_number:0{feature_id_number_width}d}"
            )
            next_number += 1
            if new_id.casefold() not in existing_ids:
                break

        if len(new_id) > id_field.length:
            raise ValueError(
                f"{feature_class}: {new_id!r} exceeds the FeatureID field length."
            )

        existing_ids.add(new_id.casefold())
        seen_ids.add(new_id.casefold())
        replacements[oid] = (old_id, new_id, reason)

    with arcpy.da.UpdateCursor(
        feature_class, [oid_field, id_field.name]
    ) as cursor:
        for row in cursor:
            if row[0] not in replacements:
                continue
            old_id, new_id, reason = replacements[row[0]]
            row[1] = new_id
            cursor.updateRow(row)
            print(
                f"{arcpy.Describe(feature_class).baseName}: "
                f"OID {row[0]} | {old_id!r} -> {new_id!r} ({reason})"
            )

    print(
        f"{arcpy.Describe(feature_class).baseName}: "
        f"{len(replacements)} FeatureIDs assigned/repaired."
    )


ensure_unique_feature_ids(master_fc)
ensure_unique_feature_ids(annotated_fc)


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
    "last_edited_date",
    "FeatureID",  # Preserve each MasterMap feature's own ID.
}

master_field_names = {f.name for f in arcpy.ListFields(master_fc)}

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
# MASTER AREAS AND ORIGINAL SUBTYPES / IDs
# ------------------------------------------------------------------

master_area = {}
master_details = {}

with arcpy.da.SearchCursor(
    master_fc,
    [master_oid_field, "SHAPE@AREA", "FeatureID", "Subtype"]
) as cursor:
    for oid, area, feature_id, subtype in cursor:
        master_area[oid] = area
        master_details[oid] = (feature_id, subtype)


# ------------------------------------------------------------------
# FIND BEST MATCH AND COLLECT ALL URBAN OVERLAP PAIRS
# ------------------------------------------------------------------

master_name = arcpy.Describe(master_fc).baseName
annotated_name = arcpy.Describe(annotated_fc).baseName

fid_master = f"FID_{master_name}"
fid_annotated = f"FID_{annotated_name}"

best_match = {}
urban_overlap_pairs = set()

with arcpy.da.SearchCursor(
    intersect_fc,
    [fid_master, fid_annotated, "SHAPE@AREA"]
) as cursor:
    for master_oid, anno_oid, overlap_area in cursor:
        if master_oid == -1 or anno_oid == -1:
            continue

        # Flag any positive-area urban overlap, regardless of percentage.
        if (
            overlap_area > 0
            and master_details[master_oid][1] == urban_subtype
        ):
            urban_overlap_pairs.add((anno_oid, master_oid))

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
            "values": row[2:],
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

    # Include Subtype only once, while still allowing ordinary matches
    # to receive the survey Subtype as in the original script.
    cursor_fields = [master_oid_field, "FeatureID", "Subtype"] + [
        field for field in fields_to_transfer if field != "Subtype"
    ]
    transfer_indices = [
        cursor_fields.index(field) for field in fields_to_transfer
    ]

    with arcpy.da.UpdateCursor(master_fc, cursor_fields) as cursor:
        for row in cursor:
            master_oid = row[0]
            master_featureid = row[1]
            subtype = row[2]

            # OMIT WATER FEATURES
            if subtype == water_subtype:
                omitted_featureids.append(master_featureid)
                continue

            # HOLD URBAN FEATURES: do not transfer any attributes.
            if subtype == urban_subtype:
                continue

            if master_oid not in best_match:
                continue

            anno_oid, overlap_pct = best_match[master_oid]
            if overlap_pct < overlap_threshold:
                continue
            if anno_oid not in annotation_lookup:
                continue

            values = annotation_lookup[anno_oid]["values"]
            for index, value in zip(transfer_indices, values):
                row[index] = value

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
        str(fid) for fid in omitted_featureids if fid is not None
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
    # REPORT URBAN OVERLAP PAIRS FOR MANUAL QA
    # ------------------------------------------------------------------

    urban_feature_matches = sorted({
        (
            annotation_lookup[anno_oid]["FeatureID"],
            master_details[master_oid][0],
        )
        for anno_oid, master_oid in urban_overlap_pairs
    })

    urban_master_oids = {
        master_oid for _, master_oid in urban_overlap_pairs
    }

    print("\n==================================================")
    print("URBAN OVERLAPS HELD FOR QA (Subtype = 6)")
    print("==================================================")
    print("No survey attributes have been transferred to these urban features.")
    print("Pairs are (Annotated FeatureID, Master FeatureID).")
    print("Includes all positive-area overlaps, including those below 90%.")
    print("Review first; copy ONLY approved pairs into Script 2.")
    print("If a target appears more than once, select at most one source.")
    print("\nfeature_matches = [")
    for source_id, target_id in urban_feature_matches:
        print(f"    ({source_id!r}, {target_id!r}),")
    print("]")

    # ------------------------------------------------------------------
    # REPORT UNMATCHED ANNOTATED FEATURES
    # ------------------------------------------------------------------

    unused_annotations = []
    for anno_oid, record in annotation_lookup.items():
        if anno_oid not in used_annotation_oids:
            unused_annotations.append(record["FeatureID"])

    unused_annotations = sorted(
        str(fid) for fid in unused_annotations if fid is not None
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
    print(f" Updated polygons: {updated_count}")
    print(f" Skipped Subtype=8 polygons: {len(omitted_featureids)}")
    print(f" Urban polygons with overlaps held for QA: {len(urban_master_oids)}")
    print(f" Urban candidate pairs for QA: {len(urban_feature_matches)}")
    print(f" Unused annotated features: {len(unused_annotations)}")

except Exception:
    editor.stopOperation()
    editor.stopEditing(False)
    raise