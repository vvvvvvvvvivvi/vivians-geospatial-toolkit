import arcpy
import os
gdb_path = r"\path\to.gdb"
print(f"Geodatabase: {gdb_path}")
print("-" * 120)

for dirpath, dirnames, filenames in arcpy.da.Walk(gdb_path, datatype="FeatureClass"):
    for fc in filenames:
fc_path = r"\path\to.gdbeaturename"

        desc = arcpy.Describe(fc_path)
        shape_type = desc.shapeType
        count = int(arcpy.management.GetCount(fc_path)[0])

        print(f"Feature Class : {fc}")
        print(f"Path          : {fc_path}")
        print(f"Geometry Type : {shape_type}")
        print(f"Feature Count : {count}")
        print("-" * 120)