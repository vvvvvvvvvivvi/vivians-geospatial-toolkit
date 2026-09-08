import arcpy
import os
input_fc_path = r"\path\to.gdbeaturename"
sde_path = r"\path\to.sde"
output_name = "just_a_name"

output_fc = os.path.join(sde_path, output_name)

if arcpy.Exists(output_fc):
    print(f"Feature class '{output_name}' already exists in the SDE. Deleting the existing data.")
    arcpy.Delete_management(output_fc)

arcpy.FeatureClassToFeatureClass_conversion(input_fc_path, sde_path, output_name)
print(f"Feature class '{output_name}' has been successfully exported to the SDE.")