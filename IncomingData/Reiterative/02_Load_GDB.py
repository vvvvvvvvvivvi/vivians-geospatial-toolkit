import arcpy
from pathlib import Path
import os
import sys

working_path = Path(sys.argv[2])
working_map_name = sys.argv[3]
base_gdb_path = Path(sys.argv[4])


# ==============================
# GUARD CLAUSES
# ==============================
if not Path(working_path).exists():
    raise RuntimeError(f"APRX not found: {working_path}")

if not Path(base_gdb_path).exists():
    raise RuntimeError(f"Base GDB path does not exist: {base_gdb_path}")

# ==============================
# PREFIX → GDB MAP
# ==============================
prefix_to_gdb = {
    "ab": "ab_AdministrativeBoundaries.gdb",
    "aq": "aq_AirQualityAndEmissions.gdb",
    "bm": "bm_BaseMapping.gdb",
    "bu": "bu_BuiltAssets.gdb",
    "ca": "ca_CommunityAndAccess.gdb",
    "ch": "ch_CulturalHeritage.gdb",
    "cl": "cl_ClimateAndAtmosphere.gdb",
    "de": "de_Designations.gdb",
    "dg": "dg_Demographics.gdb",
    "ds": "ds_Designs.gdb",
    "ec": "ec_Ecology.gdb",
    "ge": "ge_GeologyAndSoils.gdb",
    "hs": "hs_HealthAndSafety.gdb",
    "in": "in_Index.gdb",
    "lr": "lr_LandRegistry.gdb",
    "ls": "ls_Landscape.gdb",
    "lu": "lu_LandUse.gdb",
    "no": "no_Noise.gdb",
    "pl": "pl_Planning.gdb",
    "te": "te_Terrain.gdb",
    "tr": "tr_Transportation.gdb",
    "ut": "ut_Utilities.gdb",
    "wa": "wa_Water.gdb"
}

# ==============================
# LOAD PROJECT + MAP
# ==============================
aprx = arcpy.mp.ArcGISProject(working_path)
arcpy.env.overwriteOutput = True

maps = aprx.listMaps(working_map_name)
if not maps:
    raise RuntimeError(f"Map not found: {working_map_name}")

map_obj = maps[0]

# ==============================
# HELPER: export function
# ==============================
def export_layers(clean_name_func=None):
    unknown_prefixes = []

    for lyr in map_obj.listLayers():
        if not lyr.isFeatureLayer:
            continue

        layer_name = lyr.name
        raw_name = clean_name_func(layer_name) if clean_name_func else layer_name

        prefix = raw_name[:2].lower()

        if prefix in prefix_to_gdb:
            gdb_name = prefix_to_gdb[prefix]
            gdb_path = os.path.join(base_gdb_path, gdb_name)

            if not Path(gdb_path).exists():
                print(f"⚠️ GDB not found: {gdb_path}")
                continue

            # ✅ Ensure valid FGDB name
            base_name = arcpy.ValidateTableName(raw_name, gdb_path)

            # ==============================
            # VERSIONING LOGIC (_00, _01, etc.)
            # ==============================
            name_00 = f"{base_name}_00"
            fc_00_path = os.path.join(gdb_path, name_00)

            try:
                if not arcpy.Exists(fc_00_path):
                    print(f"✅ Exporting {layer_name} → {name_00}")
                    arcpy.FeatureClassToFeatureClass_conversion(lyr, gdb_path, name_00)
                    continue

                # Otherwise increment suffix
                for i in range(1, 100):
                    name_i = f"{base_name}_{i:02d}"
                    fc_path = os.path.join(gdb_path, name_i)

                    if not arcpy.Exists(fc_path):
                        print(f"✅ Exporting {layer_name} → {name_i}")
                        arcpy.FeatureClassToFeatureClass_conversion(lyr, 
                                                                    Path(gdb_path), 
                                                                    name_i)
                        break
                else:
                    print(f"❌ FAILED: No available suffix for {layer_name}")

            except Exception as e:
                print(f"❌ ArcPy failed for {layer_name}")
                print(arcpy.GetMessages())

        else:
            unknown_prefixes.append(layer_name)

    return unknown_prefixes


# ==============================
# FIRST PASS
# ==============================
print("\n--- First pass ---")
unknown = export_layers()

# ==============================
# HANDLE UNKNOWN PREFIXES
# ==============================
if unknown:
    print("\n⚠️ Unknown prefixes detected:")
    for name in unknown:
        print(f" - {name}")

    remove_from_name = input("\nEnter redundant prefix string to strip (or press Enter to skip): ").strip()

    if remove_from_name:
        print("\n--- Second pass (cleaned names) ---")

        def cleaner(name):
            return name.replace(remove_from_name, "", 1)

        export_layers(cleaner)

# ==============================
# DONE
# ==============================
print("\n✅ Export complete.")
