import arcpy
import os

base_gdb_path = "\\gblon0vs01\GISProj\B2457705_NW_Lowestoft\Data"

test_fc = os.path.join(base_gdb_path, "lr_LandRegistry.gdb", "TEST_WRITE")

print("\n--- WRITE TEST ---")

try:
    arcpy.CreateFeatureclass_management(
        os.path.join(base_gdb_path, "lr_LandRegistry.gdb"),
        "TEST_WRITE",
        "POINT"
    )
    print("✅ GDB is writable")
except Exception:
    print("❌ GDB WRITE FAILED")
    print(arcpy.GetMessages())
