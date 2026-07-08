import arcpy
import os

out_folder_path = r"\\gblon0vs01\GISProj\B3553RG4_SaferSpeeds\Working\VL\02_NewData"
out_name = "IncomingData260707.gdb"

arcpy.management.CreateFileGDB(out_folder_path, out_name)

gdb_link = os.path.join(out_folder_path, out_name)

print(f"\nCreated GDB:")
print(f"\n{gdb_link}")

