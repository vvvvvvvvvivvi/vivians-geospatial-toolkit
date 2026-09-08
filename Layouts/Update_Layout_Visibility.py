import arcpy
aprx_path = r"\path\to.aprx"

element_name = "DrawingNo Bottom TEXT"

aprx = arcpy.mp.ArcGISProject(aprx_path)

for layout in aprx.listLayouts():
    found = False

    for element in layout.listElements("TEXT_ELEMENT"):
        if element.name == element_name:
            element.visible = False
            found = True
            print(f"{layout.name}: hidden")

    if not found:
        print(f"{layout.name}: element not found")

aprx.save()
print("Project saved.")