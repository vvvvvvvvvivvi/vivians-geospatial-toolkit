import arcpy
import sys
aprx_path = r"\path\to.aprx"
map_name = "just_a_name"
data_list = [
    r"\\gblon0vs01\GISProj\B245775P_NW_TeesIndustrialDemand\IncData\EnvironmentAgency\INC005_WFD Surface Water Operational Catchments Cycle 3_260729.gdb\WFD_Surface_Water_Operational_Catchments_Cycle_3",
    r"\\gblon0vs01\GISProj\B245775P_NW_TeesIndustrialDemand\IncData\EnvironmentAgency\INC006_WFD Lake Water Bodies Cycle 3 Classification 2022_260729\Water_Framework_Directive_WFD_Lake_Water_Bodies_Cycle_3_Classification_2022.gpkg\main.WFD_Lake_Water_Bodies_Cycle_3_Classification_2022",
    r"\\gblon0vs01\GISProj\B245775P_NW_TeesIndustrialDemand\IncData\EnvironmentAgency\INC007_WFD Groundwater Bodies Cycle 3 Classification 2022 (Full Resolution)_260729\WFD_Groundwater_Bodies_Cycle_3_Classification_2022.shp",
    r"\\gblon0vs01\GISProj\B245775P_NW_TeesIndustrialDemand\IncData\EnvironmentAgency\INC008_WFD River Water Body Catchments Cycle 3 Classification 2022 (Full Resolution)_260729.gdb\WFD_River_Water_Body_Catchments_Cycle_3_Classification_2022",
    r"\\gblon0vs01\GISProj\B245775P_NW_TeesIndustrialDemand\IncData\EnvironmentAgency\INC009_Statutory Main River_260729\data.gdb\wa_EAG_StatutoryMainRiverMap"
    # r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\IncData\EnvironmentAgency\INC009_RoFSW_20260708\RoFSW.lyr",
    # "https://services-eu1.arcgis.com/48zF6lPtAjyLTDSU/arcgis/rest/services/ECC_PlanningTransport_GardenCommunities_00/FeatureServer/2",
    # "https://services-eu1.arcgis.com/48zF6lPtAjyLTDSU/arcgis/rest/services/ECC_PlanningTransport_GardenCommunities_00/FeatureServer/8",
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
