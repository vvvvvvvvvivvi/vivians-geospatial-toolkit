import arcpy
import sys

aprx_path = r"\\gblon0vs01\GISProj\B3553RG4_SaferSpeeds\Working\VL\02_NewData\IncomingData260707.aprx"
map_name = "IncomingData260707"
data_list = [
    "https://services-eu1.arcgis.com/48zF6lPtAjyLTDSU/arcgis/rest/services/ECC_PlanningTransport_GardenCommunities_00/FeatureServer/0",
    "https://services-eu1.arcgis.com/48zF6lPtAjyLTDSU/arcgis/rest/services/ECC_PlanningTransport_GardenCommunities_00/FeatureServer/4",
    "https://services-eu1.arcgis.com/48zF6lPtAjyLTDSU/arcgis/rest/services/ECC_PlanningTransport_GardenCommunities_00/FeatureServer/2",
    "https://services-eu1.arcgis.com/48zF6lPtAjyLTDSU/arcgis/rest/services/ECC_PlanningTransport_GardenCommunities_00/FeatureServer/8",
]


data_list_txt = r""

def fail(msg):
    print(f"‼️ {msg}")
    sys.exit(1)

def layer_name():
    rest_name = input("\n‼️ Provide name for layer: ")
    if rest_name is None or rest_name.strip() == "":
        fail("No name provided for layer.")
    return rest_name


if len(data_list) == 0 and data_list_txt:
    with open(data_list_txt, "r") as f:
        data_list = [line.strip() for line in f.readlines() if line.strip()]

aprx = arcpy.mp.ArcGISProject(aprx_path)

m = aprx.listMaps(map_name)[0]

for data in data_list:
    layer = m.addDataFromPath(data)
    print(f"✅ Added layer from REST service: {data}")
    new_name = layer_name()
    layer.name  = new_name
    
    
aprx.save()
print(f"✅ Layers added to map '{map_name}' in project '{aprx_path}' and saved successfully.")
