import arcpy
import os

# Inputs
csv_file = r"C:\Data\Points.csv"
output_sde = r"C:\Data\Output.gdb"
output_gdb = r"C:\Data\Output.gdb"
output_fc = "ec_NEE_ProtectedAndNotableSpecies"

# Coordinate system: British National Grid
spatial_ref = arcpy.SpatialReference(27700)

# Create XY Event Layer
xy_layer = "XY_Layer"

arcpy.management.MakeXYEventLayer(
    table=csv_file,
    in_x_field="Easting",
    in_y_field="Northing",
    out_layer=xy_layer,
    spatial_reference=spatial_ref
)

# Export to permanent feature class
output_sde_path = os.path.join(output_gdb, output_fc)

# Export to SDE
arcpy.management.CopyFeatures(
    xy_layer,
    output_sde_path
)

gdb_name = output_fc + "_01"

# Export to permanent feature class
output_gdb_path = os.path.join(output_gdb, gdb_name)

# Export to GDB
arcpy.management.CopyFeatures(
    xy_layer,
    output_gdb_path
)

print(f"Feature class created: {output_fc} in SDE and {gdb_name} in GDB.")