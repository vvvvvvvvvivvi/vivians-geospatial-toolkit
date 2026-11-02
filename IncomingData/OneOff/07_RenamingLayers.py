import arcpy
aprx_path = r"\path\to.aprx"

search_text = "Proposed Pipeline 15m Working Area and Site Compound"
replace_text = "Proposed Infrastructure"

aprx = arcpy.mp.ArcGISProject(aprx_path)

for m in aprx.listMaps():

    for lyr in m.listLayers():

        if search_text in lyr.name:

            old_name = lyr.name
            new_name = old_name.replace(search_text, replace_text)

            print(f"Old: {old_name}")
            print(f"New: {new_name}")

            lyr.name = new_name

aprx.save()

print("Done renaming layers. APRX saved.")