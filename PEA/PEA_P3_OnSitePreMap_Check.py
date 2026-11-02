import arcpy

master_fc = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\ArcGIS\003_PostSurvey\B245776V_CargoFleetLane_PostSurvey.gdb\UK_Habitat__Cleaned"

annotated_fc = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\ArcGIS\003_PostSurvey\B245776V_CargoFleetLane_PostSurvey.gdb\UK_Habitat__On_site_mapping__Cleaned"

# ------------------------------------------------------------------
# GET UNIQUE FEATURE IDS
# ------------------------------------------------------------------

master_ids = set()

with arcpy.da.SearchCursor(master_fc, ["FeatureID"]) as cursor:
    for row in cursor:
        if row:
            master_ids.add(str(row[0]).strip())

annotated_ids = set()

with arcpy.da.SearchCursor(annotated_fc, ["FeatureID"]) as cursor:
    for row in cursor:
        if row[0]:
            annotated_ids.add(str(row[0]).strip())

#--------------------------------------------------
# FIND MISSING IDS
# ------------------------------------------------------------------

missing_ids = sorted(annotated_ids - master_ids)

print(f"Unique FeatureIDs in annotation layer: {len(annotated_ids)}")
print(f"Unique FeatureIDs in master layer: {len(master_ids)}")
print(f"Missing FeatureIDs: {len(missing_ids)}")

if missing_ids:
    print("\nFeatureIDs present in annotation layer but not in master layer:")
    for fid in missing_ids:
        print(f"  {fid}")
else:
    print("\nAll annotation FeatureIDs are represented in the master layer.")