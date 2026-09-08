import arcpy
import os

# Parameters - USER INPUTS
aprx_path = r"\path\to.aprx"
map_name = "just_a_name"
sde_path = r"\path\to.sde"


# Initialising 
aprx = arcpy.mp.ArcGISProject(aprx_path)
map_obj = aprx.listMaps(map_name)[0]

# Workspace for SDE
arcpy.env.workspace = sde_path


for lyr in map_obj.listLayers():
    # Skip non-feature layers
    if not lyr.isFeatureLayer:
        continue
    
    layer_name = lyr.name
    
    try:
        # Count rows in APRX layer
        aprx_count = int(arcpy.GetCount_management(lyr)[0])
        
        # Build SDE path directly
        sde_fc = os.path.join(sde_path, layer_name)
        
        # Check if it exists
        if arcpy.Exists(sde_fc):
            sde_count = int(arcpy.GetCount_management(sde_fc)[0])
            
            status = "MATCH" if aprx_count == sde_count else "MISMATCH"
            
            print(f"  Layer: {layer_name}")
            print(f"    APRX Count: {aprx_count}")
            print(f"    SDE Count : {sde_count}")
            print(f"    Status    : {status}")
        
        else:
            print(f"  Layer: {layer_name}")
            print(f"    WARNING: {sde_fc} not found in SDE")
    
    except Exception as e:
        print(f"  Layer: {layer_name}")
        print(f"    ERROR: {str(e)}")

print("\n=== Finished ===")
