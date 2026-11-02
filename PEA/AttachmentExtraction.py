# =============================================================================
# Consolidate ArcGIS Attachments into a Single Point Feature Class
#
# PURPOSE
# -------
# Extract all features that have attachments from multiple feature classes
# (point, line, or polygon), convert geometries to points where necessary,
# preserve all attachments, and append them into a single output point
# feature class.
#
# RULES
# -----
# - Empty feature classes are skipped.
# - Features with NO attachments are skipped.
# - Point geometry is retained.
# - Polyline and Polygon geometries use trueCentroid.
# - All attachments are preserved.
# - Feature IDs are generated as:
#       BadgerFieldSign_123
#       BadgerAreasSurveyed_45
#       WatercourseCrossing_8
# - Supports File GDB and Enterprise GDB outputs.
# - Prints a validation summary at the end.
#
# TESTED FOR
# ----------
# ArcGIS Pro 3.5.x
#
# =============================================================================

import arcpy
import os
import re
import shutil
from collections import defaultdict

# =============================================================================
# USER INPUTS
# =============================================================================

source_fcs = [
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_BadgerAreasSurveyed",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_BadgerFieldSign",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_BadgerSettEntrance",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_BatStructureAssessment",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_BatTreeAssessment",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_Ditches",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_GCNDitches",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_GCNPonds",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_Hedgerow",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_IndividualTrees",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_LineOfTrees",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_NotableInvasivesMapping",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_OtterFieldSign",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_TargetNotes",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_UKHabitatsOnSiteMapping",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_UKHabitatsPreMapping",
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde\B245776V_DATAOWNER.ec_JAC_SurveyWIP_WatervoleFieldSign"
]

output_fc = (
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Working\VL\001_DataCollection\CargoFleet_DataCollection.gdb\SurveyPoints_v3"
)

scratch_dir = r"C:\Users\LEEV\AttachmentExport"

print(arcpy.Exists(
    r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Working\VL\003_SurveyPhotos\CFL_SurveyPhotos.gdb"
))

# =============================================================================
# HELPERS
# =============================================================================

def norm_guid(guid):

    if guid is None:
        return None

    guid = str(guid)
    guid = guid.replace("{", "")
    guid = guid.replace("}", "")
    guid = guid.upper()

    return guid


def clean_name(fc):

    name = os.path.basename(fc)

    if "." in name:
        name = name.split(".")[-1]

    prefixes = [
        "ec_JAC_SurveyWIP_",
        "ec_JAC_"
    ]

    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]

    return name


def make_readable_name(fc):

    raw = clean_name(fc)

    tokens = re.findall(
        r"(?:GCN|PEA|UK|[A-Z]+(?=[A-Z][a-z]|$)|[A-Z]?[a-z]+)",
        raw
    )

    return " ".join(tokens)


def create_output_fc():

    workspace, fc_name = os.path.split(output_fc)

    if arcpy.Exists(output_fc):
        arcpy.management.Delete(output_fc)

    sr = arcpy.Describe(source_fcs[0]).spatialReference

    arcpy.management.CreateFeatureclass(
        workspace,
        fc_name,
        "POINT",
        spatial_reference=sr
    )

    arcpy.management.AddField(output_fc, "FeatureID", "TEXT", field_length=255)
    arcpy.management.AddField(output_fc, "SourceType", "TEXT", field_length=255)
    arcpy.management.AddField(output_fc, "SourceFC", "TEXT", field_length=255)
    arcpy.management.AddField(output_fc, "SourceOID", "LONG")
    arcpy.management.AddField(output_fc, "AttachCnt", "LONG")


def load_attachments(fc):

    attach_table = f"{fc}__ATTACH"

    if not arcpy.Exists(attach_table):
        print(f"WARNING: No attachment table: {fc}")
        return {}

    attachment_lookup = defaultdict(list)

    rows = 0
    zero_byte_count = 0

    with arcpy.da.SearchCursor(
        attach_table,
        ["REL_GLOBALID", "ATT_NAME", "DATA"]
    ) as cursor:

        for rel_guid, att_name, blob in cursor:

            rows += 1

            # ---------------------------------------------------------
            # Robust blob conversion
            # ---------------------------------------------------------
            data = None

            try:

                if blob is None:
                    print(f"WARNING: NULL attachment: {att_name}")
                    continue

                elif isinstance(blob, memoryview):
                    data = blob.tobytes()

                elif isinstance(blob, bytes):
                    data = blob

                elif isinstance(blob, bytearray):
                    data = bytes(blob)

                elif hasattr(blob, "tobytes"):
                    data = blob.tobytes()

                elif hasattr(blob, "read"):
                    data = blob.read()

                else:
                    data = bytes(blob)

            except Exception as e:

                print(
                    f"WARNING: Failed to convert attachment "
                    f"'{att_name}' ({type(blob)}): {e}"
                )

                continue

            if not data:

                zero_byte_count += 1

                print(
                    f"WARNING: Zero-byte attachment found: "
                    f"{att_name}"
                )

                continue

            attachment_lookup[
                norm_guid(rel_guid)
            ].append(
                (
                    att_name,
                    data
                )
            )

    print(f"  Attachment records: {rows}")
    print(f"  Features with attachments: {len(attachment_lookup)}")
    print(f"  Zero-byte attachments skipped: {zero_byte_count}")

    return attachment_lookup

# =============================================================================
# MAIN
# =============================================================================

if os.path.exists(scratch_dir):
    shutil.rmtree(scratch_dir)

os.makedirs(scratch_dir)

create_output_fc()

arcpy.ClearWorkspaceCache_management()

csv_path = os.path.join(
    scratch_dir,
    "attachment_match.csv"
)

csv_file = open(
    csv_path,
    "w",
    encoding="utf-8",
    newline=""
)

csv_file.write("FeatureID,PATH\n")

summary = []

total_features_exported = 0
total_attachments_exported = 0

insert_fields = [
    "SHAPE@",
    "FeatureID",
    "SourceType",
    "SourceFC",
    "SourceOID",
    "AttachCnt"
]

desc = arcpy.Describe(output_fc)

print("\nOUTPUT FC INFO")
print(desc.catalogPath)
print(desc.dataType)

try:
    print("isVersioned:", desc.isVersioned)
except:
    pass

with arcpy.da.InsertCursor(
    output_fc,
    insert_fields
) as icur:

    for fc in source_fcs:

        readable = make_readable_name(fc)
        prefix = clean_name(fc)

        print("\n" + "=" * 60)
        print(readable)

        feature_count = int(
            arcpy.management.GetCount(fc)[0]
        )

        if feature_count == 0:

            print("  Empty FC - skipped")

            summary.append(
                (readable, 0, 0, True)
            )

            continue

        attachment_lookup = load_attachments(fc)

        exported_features = 0

        shape_type = arcpy.Describe(fc).shapeType
        oid_field = arcpy.Describe(fc).OIDFieldName

        with arcpy.da.SearchCursor(
            fc,
            [
                oid_field,
                "GLOBALID",
                "SHAPE@"
            ]
        ) as cursor:

            for oid, globalid, geom in cursor:

                guid = norm_guid(globalid)

                attachments = attachment_lookup.get(
                    guid,
                    []
                )

                if not attachments:
                    continue

                if shape_type == "Point":
                    out_geom = geom
                else:
                    out_geom = geom.trueCentroid

                feature_id = f"{prefix}_{oid}"

                icur.insertRow([
                    out_geom,
                    feature_id,
                    readable,
                    os.path.basename(fc),
                    oid,
                    len(attachments)
                ])

                exported_features += 1

                counter = 1

                for att_name, blob in attachments:

                    ext = os.path.splitext(att_name)[1]

                    outfile = os.path.join(
                        scratch_dir,
                        f"{feature_id}_{counter}{ext}"
                    )

                    print("ATT_NAME =", att_name)
                    print("OUTFILE  =", outfile)

                    with open(outfile, "wb") as img:

                        if hasattr(blob, "tobytes"):
                            img.write(blob.tobytes())
                        else:
                            img.write(blob)

                    csv_file.write(
                        f'"{feature_id}","{outfile}"\n'
                    )


                    counter += 1
                    total_attachments_exported += 1
        
        total_features_exported += exported_features

        summary.append(
            (
                readable,
                feature_count,
                exported_features,
                False
            )
        )

# =============================================================================
# ADD ATTACHMENTS
# =============================================================================

arcpy.ClearWorkspaceCache_management()

csv_file.close()

arcpy.management.EnableAttachments(output_fc)

print("\nAdding attachments...")

arcpy.ClearWorkspaceCache_management()

arcpy.management.AddAttachments(
    output_fc,
    "FeatureID",
    csv_path,
    "FeatureID",
    "PATH"
)

# =============================================================================
# SUMMARY
# =============================================================================

print("\n")
print("=" * 70)
print("SUMMARY")
print("=" * 70)

for name, processed, exported, empty in summary:

    if empty:
        print(f"{name}: Empty FC")
    else:
        print(
            f"{name}: "
            f"Processed={processed} "
            f"Exported={exported}"
        )

print("\n")
print(f"Features exported: {total_features_exported}")
print(f"Attachments exported: {total_attachments_exported}")

out_attach_tbl = f"{output_fc}__ATTACH"

if arcpy.Exists(out_attach_tbl):

    output_attach_count = int(
        arcpy.management.GetCount(out_attach_tbl)[0]
    )

    print(
        f"Output attachment count: "
        f"{output_attach_count}"
    )

    if output_attach_count == total_attachments_exported:
        print("VALIDATION PASSED")
    else:
        print("VALIDATION FAILED")

print("\nFinished.")