import arcpy
import re
aprx_path = r"\path\to.aprx"
# map_name = "260729"
old_name = "Redline boundary"
new_name = "Indicative Redline Boundary"


aprx = arcpy.mp.ArcGISProject(aprx_path)

for m in aprx.listMaps():
    # if m.name == map_name:
        for lyr in m.listLayers():
            
            if old_name in lyr.name:
            # if lyr.isFeatureLayer:

                # print(lyr.name)

                print("Old name: " + lyr.name)
                # new_name = lyr.name.replace('Study', "River")
                # new_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', new_name)
                lyr.name = new_name
                print("New name: " + lyr.name)
aprx.save() 
#new_name = "tr_" + "JAC_" + lyr.name
# new_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', lyr.name)
#new_name = lyr.name.replace('2', "")

print("Done renaming layers. APRX saved.")