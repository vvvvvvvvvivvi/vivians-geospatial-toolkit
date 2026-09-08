import arcpy
import sys
aprx_path = r"\path\to.aprx"
map_name = "just_a_name"

def fail(msg):
    print(f"‼️ {msg}")
    sys.exit(1)

def lyrx_file():
    lyrx_file_path = input("\n‼️ Provide path to layer file: ")
    if lyrx_file_path is None or lyrx_file_path.strip() == "":
        fail("No valid link.")
    lyrx_file_path = lyrx_file_path.replace('"','')
    return lyrx_file_path

aprx = arcpy.mp.ArcGISProject(aprx_path)

m = aprx.listMaps(map_name)[0]

for lyr in m.listLayers():

    if not lyr.isFeatureLayer:
        continue

    print(f"Symbolising {lyr.name}...")
    lyrx_file_path = lyrx_file()

    if lyrx_file_path:
        arcpy.management.ApplySymbologyFromLayer(
            lyr,
            lyrx_file_path
        )

print("Done.")