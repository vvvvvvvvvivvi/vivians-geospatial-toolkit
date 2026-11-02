import arcpy
import os

# Inputs
input_csv_path = r"\path\to.csv"
output_sde_path = r"\path\to.sde"
output_gdb_path = r"\path\to.gdb"
output_name = "just_a_name"

# Coordinate system: British National Grid
spatial_ref = arcpy.SpatialReference(27700)

# Create XY Event Layer
xy_layer = "XY_Layer"

arcpy.management.MakeXYEventLayer(
    table=input_csv_path,
    in_x_field="Easting",
    in_y_field="Northing",
    out_layer=xy_layer,
    spatial_reference=spatial_ref
)

# Export to permanent feature class
output_fc_sde_path = os.path.join(output_sde_path, output_name)

# Export to SDE
arcpy.management.CopyFeatures(
    xy_layer,
    output_fc_sde_path
)

output_gdb_name = output_name + "_01"

# Export to permanent feature class
output_fc_gdb_path = os.path.join(output_gdb_path, output_gdb_name)

# Export to GDB
arcpy.management.CopyFeatures(
    xy_layer,
    output_fc_gdb_path
)

print(f"Feature class created: {output_name} in SDE and {output_gdb_name} in GDB.")