import arcpy
import os
import uuid

sde_path = r"\\gblon0vs01\GISProj\B3553RG4_SaferSpeeds\Data\B3553RG4_DataOwner@B3553RG4_SaferSpeeds.sde" # Path link to workspace geodatabase
fc_name = "tr_ESH_HighwayNetwork"
sde_name = "B3553RG4_DATAOWNER." + fc_name
in_dataset = os.path.join(sde_path, sde_name)
out_fc = fc_name + "_WGS84"
out_dataset = os.path.join(sde_path, out_fc)

out_sr = arcpy.SpatialReference(4326)  # WGS 1984

arcpy.env.overwriteOutput = True

arcpy.management.Project(
    in_dataset,
    out_dataset,
    out_sr,
    "OSGB_1936_To_WGS_1984_7"
)

print("DONE: All data reprojected.")