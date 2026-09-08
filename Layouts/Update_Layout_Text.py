import arcpy
aprx_path = r"\path\to.aprx"

element_name = "ApprovedBy TEXT"
new_text = "JOL"

aprx = arcpy.mp.ArcGISProject(aprx_path)

for layout in aprx.listLayouts():

    text_elements = [
        e for e in layout.listElements("TEXT_ELEMENT")
        if e.name == element_name
    ]

    if text_elements:
        for element in text_elements:
            element.text = new_text
        print(f"✓ {layout.name}")
    else:
        print(f"✗ {layout.name} - 'FigureName TEXT' not found")

aprx.save()
del aprx

print("Completed.")
