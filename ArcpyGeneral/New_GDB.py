import arcpy
import os
out_folder_path = r"\path\	o\folder"
gdb_name = r"\path\to.gdb"

arcpy.management.CreateFileGDB(out_folder_path, gdb_name)

gdb_link = os.path.join(out_folder_path, gdb_name)

print(f"\nCreated GDB:")
print(f"\n{gdb_link}")

