import arcpy
import os

template_aprx = (
    r"\\gblon0vs01\GISProj\B245771D_NW_NorthSuffolk"
    r"\Working\VL\022_HRA_FLL\B245771D_HRA_Figures.aprx"
)

output_folder = (
    r"\\gblon0vs01\GISProj\B245771D_NW_NorthSuffolk"
    r"\Working\VL\022_HRA_FLL\03_Templates"
)
map_name = "just_a_name"


aprx = arcpy.mp.ArcGISProject(template_aprx)

template_map = next(
    m for m in aprx.listMaps()
    if m.name == map_name
)

mapx_path = os.path.join(
    output_folder,
    f"{map_name}.pagx"
)

print(f"Exporting {mapx_path}")

template_map.exportToMAPX(mapx_path)

print("Finished")