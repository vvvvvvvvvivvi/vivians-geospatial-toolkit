import arcpy
import re
import sys
from pathlib import Path

publishing_path = Path(sys.argv[1])
publishing_map_name = sys.argv[11]



aprx = arcpy.mp.ArcGISProject(publishing_path)

for m in aprx.listMaps(publishing_map_name):
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
