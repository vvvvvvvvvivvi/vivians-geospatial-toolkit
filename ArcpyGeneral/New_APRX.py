import arcpy
import os 
from pathlib import PureWindowsPath, Path
from config import load_config


# Load a blank/template project
new_aprx_folder = r""
new_aprx_name = "name.aprx"

if not os.path.isdir(new_aprx_folder):
    os.makedirs(new_aprx_folder, exist_ok=True)
else:
    print("Output path exists, proceeding.")
    

new_aprx_path = os.path.join(new_aprx_folder, new_aprx_name)

config = load_config()
template_aprx_path = config["templates"]["template_aprx"]
aprx = arcpy.mp.ArcGISProject(template_aprx_path)
aprx.saveACopy(new_aprx_path)

# Clear from memory
del aprx

new_aprx = arcpy.mp.ArcGISProject(new_aprx_path)
new_aprx_folder = r""
project_root = Path(PureWindowsPath(*new_aprx_folder.parts[:4]))

folder_connections = new_aprx.folderConnections

folder_connections.append({
    "alias": "",
    "connectionString": project_root,
    "isHomeFolder": False
})


# Clear from memory
del new_aprx

print("Created:")
print(new_aprx_path)