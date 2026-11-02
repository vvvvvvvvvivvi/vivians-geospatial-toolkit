import arcpy
import fnmatch

# =============================================================================
# USER INPUTS
# =============================================================================

# SDE or GDB connection
workspace = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde"

# Wildcard patterns (case-insensitive)
# Examples:
#   *SurveyWIP*
#   *Badger*
#   ec_JAC_*
#   *_FieldSign
patterns = [
    "*SurveyWIP*"
]

# Name of output variable
output_variable_name = "source_fcs"

# =============================================================================
# FIND MATCHING FEATURE CLASSES
# =============================================================================

arcpy.env.workspace = workspace

matching_fcs = []

# Search standalone feature classes and feature datasets
datasets = [''] + (arcpy.ListDatasets(feature_type='feature') or [])

for dataset in datasets:

    feature_classes = arcpy.ListFeatureClasses(feature_dataset=dataset)

    if not feature_classes:
        continue

    for fc in feature_classes:

        fc_lower = fc.lower()

        # Check against all wildcard patterns
        if any(fnmatch.fnmatch(fc_lower, pattern.lower()) for pattern in patterns):

            if dataset:
                full_path = fr"{workspace}\{dataset}\{fc}"
            else:
                full_path = fr"{workspace}\{fc}"

            matching_fcs.append(full_path)

# =============================================================================
# PRINT AS PYTHON LIST
# =============================================================================

print(f"{output_variable_name} = [")

for fc in sorted(matching_fcs):
    print(f'    r"{fc}",')

print("]")

print(f"\nFound {len(matching_fcs)} matching feature class(es).")