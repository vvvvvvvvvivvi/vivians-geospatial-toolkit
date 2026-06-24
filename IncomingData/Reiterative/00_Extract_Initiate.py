
import sys

working_path = sys.argv[2]
working_map_name = sys.argv[3]


working_map = None
for m in working_aprx.listMaps():
    if m.name == working_map_name:
        working_map = m
        break

if not working_map:
    raise Exception(f"Working map '{working_map_name}' not found.")