import arcpy
aprx_path = r"\path\to.aprx"
aprx = arcpy.mp.ArcGISProject(aprx_path)

print("Found maps:")
for m in aprx.listMaps():
    print(m.name)

print("Found layouts:")
for lyt in aprx.listLayouts():
    print(lyt.name)

print("Done.")
