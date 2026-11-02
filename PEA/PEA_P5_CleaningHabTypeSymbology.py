import arcpy

# Feature class or table
fc = r"C:\Path\To\Your\FeatureClass"

habitat_field = "HabitatType"
code_field = "essentialcode1"
output_field = "HabitatType_Desc"

# Add output field if it doesn't exist
existing_fields = [f.name for f in arcpy.ListFields(fc)]
if output_field not in existing_fields:
    arcpy.AddField_management(fc, output_field, "TEXT", field_length=255)

# Update values
with arcpy.da.UpdateCursor(
    fc,
    [habitat_field, code_field, output_field]
) as cursor:

    for habitat, code, desc in cursor:

        # Replicate field calculator logic
        habitat_clean = (
            habitat.split(" - ", 1)[0]
            if habitat
            else ""
        )

        if code:
            desc = f"{habitat_clean}, {code}"
        else:
            desc = habitat_clean

        cursor.updateRow((habitat, code, desc))

print("HabitatType_Desc field populated successfully.")