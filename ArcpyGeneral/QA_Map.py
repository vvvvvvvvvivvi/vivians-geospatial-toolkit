import arcpy
aprx_path = r"\path\to.aprx"
map_name = "just_a_name"

aprx = arcpy.mp.ArcGISProject(aprx_path)
m = aprx.listMaps(map_name)[0]

for lyr in m.listLayers():
    print("Layer: " + lyr.name)
    print("Data Source: " + lyr.dataSource)
    print("Row Count: " + str(arcpy.GetCount_management(lyr).getOutput(0)))