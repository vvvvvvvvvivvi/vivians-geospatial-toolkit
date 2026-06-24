import arcpy
import re

aprx_path = r"\\location\to.aprx" # Path link to aprx

map_name = ""


aprx = arcpy.mp.ArcGISProject(aprx_path)

for m in aprx.listMaps(map_name):
    if m.name == map_name:
        for lyr in m.listLayers():
            
            if '_' in lyr.name:
            # if lyr.isFeatureLayer:

                # print(lyr.name)

                print("Old name: " + lyr.name)
                new_name = lyr.name.replace('_', "")
                lyr.name = new_name
                print("New name: " + lyr.name)
aprx.save() 
#new_name = "tr_" + "JAC_" + lyr.name
new_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', lyr.name)
#new_name = lyr.name.replace('2', "")

print("Done renaming layers. APRX saved.")