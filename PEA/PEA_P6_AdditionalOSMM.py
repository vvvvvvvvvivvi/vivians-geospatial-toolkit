import arcpy

existing_fc = r"\\gblon0vs01\GISProj\B245774G_NW_Warkworth\ArcGIS\003_PostSurvey\Warkworth_PostSurvey.gdb\UK_Habitat_polygon__Pre_mapped_"
new_fc = r"\\gblon0vs01\GISProj\B245774G_NW_Warkworth\Working\VL\004_HabitatPremapping\Warkworth_Premapping.gdb\bm_OSMM_2026Jan_Warkworth_Merged"

# Create feature layers
arcpy.management.MakeFeatureLayer(existing_fc, "existing_lyr")
arcpy.management.MakeFeatureLayer(new_fc, "new_lyr")

# Copy all new polygons to a temporary fc
new_unique = r"memory\new_unique"
arcpy.management.CopyFeatures(new_fc, new_unique)

# Remove polygons that genuinely overlap existing polygons
with arcpy.da.UpdateCursor(new_unique, ["OID@", "SHAPE@"]) as cursor:
    for oid, shape in cursor:

        overlaps = False

        with arcpy.da.SearchCursor(existing_fc, ["SHAPE@"]) as search_cur:
            for (existing_shape,) in search_cur:

                intersection = shape.intersect(existing_shape, 4)  # polygon

                if intersection.area > 0:
                    overlaps = True
                    break

        if overlaps:
            cursor.deleteRow()

print(f"Remaining new polygons: {arcpy.management.GetCount(new_unique)[0]}")

# Append only genuinely new polygons
arcpy.management.Append(
    new_unique,
    existing_fc,
    "NO_TEST"
)
