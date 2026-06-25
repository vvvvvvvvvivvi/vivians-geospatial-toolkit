import os
import subprocess
import sys
from pathlib import Path
import arcpy
import json

SCRIPT_FOLDER = Path(__file__).resolve().parent
CONFIG_PATH = Path(__file__).parent / "publish_defaults.json"

# ==============================
# PARAMETERS
# ==============================
publishing_path = r"\\gblon0vs01\GISProj\B2457705_NW_Lowestoft\ArcGIS\000_ProjectMapper\016_SWRTS_waste_MaterialsWaste.aprx"
working_path = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Working\VL\001_DataCollection\CargoFleet_DataCollection.aprx"
working_map_name = "20260625"

# Optional
sde_path = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data\SDE_Connections\B245776V_DataOwner@B245776V_NWCargoFleetLane.sde"
base_gdb_path = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Data"
sde_user = "B245776V_DATAOWNER."

# ==============================
# HELPER FUNCTIONS
# ==============================
def fail(msg):
    print(f"‼️ {msg}")
    sys.exit(1)

def confirm():
    if input("\n‼️ Proceed? (yes/no): ").lower() != "yes":
        fail("Cancelled.")

def validate_aprx(path):
    p = Path(path)
    if not p.exists():
        fail(f"APRX not found: {p}")
    print(f"✅ APRX exists: {p}")
    return p

def validate_sde(path):
    if not arcpy.Exists(str(path)):
        fail(f"SDE invalid: {path}")

    arcpy.env.workspace = str(path)
    print("✅ SDE validated")

    # Smoke test
    fcs = arcpy.ListFeatureClasses()
    for fc in (fcs or [])[:3]:
        print(arcpy.Describe(fc).catalogPath)


def load_defaults():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_defaults(data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ==============================
# SCRIPT REQUIREMENTS MAP
# ==============================
REQS = {
    "00": ["working_path", "working_map"],
    "01": ["working_path", "working_map"],
    "02": ["working_path", "working_map", "base_gdb"],
    "03": ["working_path", "working_map", "sde"],
    "04": ["working_path", "working_map", "sde"],
    "05": ["working_path", "working_map", "publishing", "publishing_map", "project_code", "project_name", "final_publishing_map_abbrv"],
    "06": ["publishing", "publishing_map"],
    "07": ["publishing", "publishing_map"],
}

# ==============================
# STEP 1: Choose script FIRST
# ==============================
script_code = input("\nEnter script number (e.g. 1 → 01_...): ").zfill(2)

if script_code not in REQS:
    fail("Invalid script code")

requirements = REQS[script_code]

# ==============================
# STEP 2: Conditional validation
# ==============================

# ---- Publishing APRX ----
if "publishing" in requirements:
    publishing_path = validate_aprx(publishing_path)
else:
    publishing_path = Path(publishing_path) if publishing_path else None

# ---- Working APRX ----
if "working_path" in requirements:
    working_path = validate_aprx(working_path)

# ---- Extract project info only if needed ----
project_root = None
if any(x in requirements for x in ["sde", "base_gdb", "publishing"]):
    base_source = publishing_path or Path(working_path)
    project_root = base_source.parents[2]
    project_root_name = project_root.name

    try:
        project_code, project_name = project_root_name.split("_", 1)
    except ValueError:
        fail(f"Invalid project folder name: {project_root_name}")

# ---- Base GDB ----
if "base_gdb" in requirements:
    if not base_gdb_path:
        base_gdb_path = project_root / "Data"
    print(f"✅ Base GDB: {base_gdb_path}")

# ---- SDE ----
sde_name = None

if "sde" in requirements:
    if not sde_path:
        sde_name = f"GBLON0-SQL005_{project_root_name}_DATAOWNER.sde"
        if not sde_user:
            sde_user = f"{project_code}_DATAOWNER"
        sde_path = project_root / "Data" / sde_name
    else:
        sde_path = Path(sde_path)

    validate_sde(sde_path)

# ---- Publishing map logic ----
publishing_map_abbrv = ""
publishing_map_prefix = ""
publishing_map_heading = ""
publishing_map_name = ""
final_abbrv = ""

if "publishing_map" in requirements:
    
    defaults = load_defaults()

    if defaults:
        print("\nPrevious publishing values found:")
        print(f"  Abbreviation : {defaults.get('abbrv')}")
        print(f"  Map prefix   : {defaults.get('prefix')}")
        print(f"  Map heading  : {defaults.get('heading')}")

        use_defaults = input("\nUse these values? (yes/no): ").strip().lower() == "yes"
    else:
        use_defaults = False

    if use_defaults:
        publishing_map_abbrv = defaults.get("abbrv", "")
        publishing_map_prefix = defaults.get("prefix", "")
        publishing_map_heading = defaults.get("heading", "")
    else:
        publishing_map_abbrv = input("Enter project abbreviation (optional): ").strip()
        publishing_map_prefix = input("Enter map prefix: ").strip()
        publishing_map_heading = input("Enter map heading: ").strip()

        save_defaults({
            "abbrv": publishing_map_abbrv,
            "prefix": publishing_map_prefix,
            "heading": publishing_map_heading
        })

    publishing_map_name = publishing_map_abbrv + "_" + publishing_map_prefix + "_" + publishing_map_heading
    print(f"✅ Publishing map name: {publishing_map_name}")

# ==============================
# Confirm
# ==============================
confirm()

# ==============================6
# Find script
# ==============================
selected_script = next(
    (f for f in os.listdir(SCRIPT_FOLDER)
     if f.startswith(script_code) and f.endswith(".py")),
    None
)

if not selected_script:
    fail("Script not found")

script_path = SCRIPT_FOLDER / selected_script
print(f"\n✅ Running {script_path.name}")
confirm()

# ==============================
# Run
# ==============================
args = [
    sys.executable,
    str(script_path),
    str(publishing_path or ""),
    str(working_path or ""),
    working_map_name or "",
    str(base_gdb_path or ""),
    str(sde_path or ""),
    sde_name or "",
    sde_user or "",
    publishing_map_abbrv,
    publishing_map_prefix,
    publishing_map_heading,
    publishing_map_name,
    project_code,
    project_name,
    final_abbrv
]

subprocess.run(args, check=True)

print("\n✅ Script completed.")

# ==============================
# Open APRX
# ==============================
choice = input("\nOpen APRX? (pub / work / no): ").lower()

if choice == "pub" and publishing_path:
    os.startfile(publishing_path)

elif choice == "work" and working_path:
    os.startfile(working_path)

else:
    print("Finished.")
