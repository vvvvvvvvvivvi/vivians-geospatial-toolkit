import csv

import arcpy
import os
import string

# =============================================================================
# Settings
# =============================================================================

gdb = r"\\gblon0vs01\GISProj\ReferencedData\BESP0016_KentCC_TransportDashboard\Data\BESP0016_Data.gdb"

datasets = [
    {
        "csv": r"\\gblon0vs01\GISProj\ReferencedData\BESP0016_KentCC_TransportDashboard\Working\VL\20261029\Summary_Sheet.csv",
        "easting": "L",
        "northing": "M",
        "fc": "tr_KentCounts_12"
    },
    # {
    #     "csv": r"\\gblon0vs01\GISProj\B245775P_NW_TeesIndustrialDemand\Working\VL\01_MarineEcologyReceptors\Dependents Mapping\Barriers.csv",
    #     "easting": "B",
    #     "northing": "C",
    #     "fc": "ec_JAC_MarineEcologyReceptors_Barriers"
    # },
    # {
    #     "csv": r"\\gblon0vs01\GISProj\B245775P_NW_TeesIndustrialDemand\Working\VL\01_MarineEcologyReceptors\Dependents Mapping\EA Diatom Sites.csv",
    #     "easting": "E",
    #     "northing": "F",
    #     "fc": "ec_JAC_MarineEcologyReceptors_EADiatomSites"
    # },
    # {
    #     "csv": r"\\gblon0vs01\GISProj\B245775P_NW_TeesIndustrialDemand\Working\VL\01_MarineEcologyReceptors\Dependents Mapping\EA Fish Monitoring Sites.csv",
    #     "easting": "C",
    #     "northing": "D",
    #     "fc": "ec_Jacobs_MarineEcologyReceptors_EAFishMonitoringSites"
    # },
    # {
    #     "csv": r"\\gblon0vs01\GISProj\B245775P_NW_TeesIndustrialDemand\Working\VL\01_MarineEcologyReceptors\Dependents Mapping\EA Invert Monitoring sites.csv",
    #     "easting": "E",
    #     "northing": "F",
    #     "fc": "ec_JAC_MarineEcologyReceptors_EAInvertMonitoringsites"
    # },
    # {
    #     "csv": r"\\gblon0vs01\GISProj\B245775P_NW_TeesIndustrialDemand\Working\VL\01_MarineEcologyReceptors\Dependents Mapping\EA Macrophyte Sites.csv",
    #     "easting": "E",
    #     "northing": "F",
    #     "fc": "ec_JAC_MarineEcologyReceptors_EAMacrophyteSites"
    # },
    # {
    #     "csv": r"\\gblon0vs01\GISProj\B245775P_NW_TeesIndustrialDemand\Working\VL\01_MarineEcologyReceptors\Dependents Mapping\Smelt.csv",
    #     "easting": "B",
    #     "northing": "C",
    #     "fc": "ec_Jacobs_MarineEcologyReceptors_Smelt"
    # },
        # {
        #     "csv": r"\\gblon0vs01\GISProj\BXXXXXXX_AW_PFAS_CRA\IncData\Jacobs\064_WIMSforGIS_20260812\WIMS for GIS.csv",
        #     "easting": "E",
        #     "northing": "F",
        #     "fc": "wa_JAC_WIMS"
        # },
]

spatial_ref = arcpy.SpatialReference(27700)  # British National Grid

arcpy.env.overwriteOutput = True

# =============================================================================
# Helper
# =============================================================================

def excel_col_to_index(col_letter):
    """
    Convert Excel column letter to zero-based index.
    A=0, B=1, C=2 etc.
    """
    return string.ascii_uppercase.index(col_letter.upper())

# =============================================================================
# Processing
# =============================================================================

for ds in datasets:

    csv_path = ds["csv"]
    fc_name = ds["fc"]
    out_fc = os.path.join(gdb, fc_name)

    print(f"\nProcessing {fc_name}")

    # Read header row
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        header_line = f.readline().rstrip("\n")

    headers = [h.strip() for h in header_line.split(",")]

    east_idx = excel_col_to_index(ds["easting"])
    north_idx = excel_col_to_index(ds["northing"])

    east_field = headers[east_idx]
    north_field = headers[north_idx]

    print(f"X Field: {east_field}")
    print(f"Y Field: {north_field}")

    if arcpy.Exists(out_fc):
        arcpy.management.Delete(out_fc)

    # Create point feature class directly from CSV
    arcpy.management.XYTableToPoint(
        in_table=csv_path,
        out_feature_class=out_fc,
        x_field=east_field,
        y_field=north_field,
        coordinate_system=spatial_ref
    )

    print(f"Completed: {fc_name}")

    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        csv_count = sum(1 for row in csv.reader(f)) - 1

    fc_count = int(arcpy.management.GetCount(out_fc)[0])

    print(f"CSV rows: {csv_count}")
    print(f"FC rows : {fc_count}")

print("\nFinished.")
