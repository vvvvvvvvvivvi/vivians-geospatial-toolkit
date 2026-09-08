import arcpy
import os
input_raster_path = r"\path\	o\raster"
aster"
output_fc_name = "just_a_name"
sde_path = r"\path\to.sde"


output_raster = os.path.join(sde_path, output_fc_name)
arcpy.management.CopyRaster(
    in_raster=input_raster_path,
    out_rasterdataset=output_raster
)

print("Done")
