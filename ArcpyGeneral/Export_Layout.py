import arcpy
import os
from pathlib import PureWindowsPath, Path
from config import load_config

output_folder = (
    r"\\gblon0vs01\GISProj\B245775P_NW_TeesIndustrialDemand\Working\VL"
)
layout_name = "just_a_name"

config = load_config()
template_aprx_path = config["templates"]["template_aprx"]
aprx = arcpy.mp.ArcGISProject(template_aprx_path)

template_layout = next(
    l for l in aprx.listLayouts()
    if l.name == layout_name
)
pagx_project_path = os.path.join(
    output_folder,
    f"{layout_name}.pagx"
)

print(f"Exporting {pagx_project_path}")

template_layout.exportToPAGX(pagx_project_path)

print("Finished")