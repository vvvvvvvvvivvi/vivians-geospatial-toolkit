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
working_path = r""
working_map_name = ""

publishing_path = r""
publishing_map_name = ""

# Optional
sde_path = r""
base_gdb_path = r""
sde_user = ""

project_code = ""
project_name = ""
script_code = ""

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

    fcs = arcpy.ListFeatureClasses()
    for fc in (fcs or [])[:3]:
        print(arcpy.Describe(fc).catalogPath)

def verify_map(aprx_path, map_name):
    aprx = arcpy.mp.ArcGISProject(aprx_path)
    maps = aprx.listMaps(map_name)

    if maps:
        print(f"✅ Map exists: {map_name}")
        return maps[0]
    else:
        fail(f"Map not found: {map_name}")

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
    "01": ["working_path", "working_map", "sde"],
    "02": ["working_path", "working_map", "base_gdb"],
    "03": ["working_path", "working_map", "sde"],
    "04": ["working_path", "working_map", "sde", "sde_user"],
    "05": ["working_path", "working_map", "project_code", "project_name"],
    "06": ["publishing", "publishing_map"],
    "07": ["publishing", "publishing_map"],
    "08": ["publishing", "publishing_map"],
}

def script_setup():
    global script_code
    global working_path
    global publishing_path
    global publishing_map_name
    global sde_path
    global base_gdb_path
    global sde_user
    global project_code
    global project_name

    script_code = input(
        "\nEnter script number (e.g. 1 → 01_...): "
    ).zfill(2)

    if script_code not in REQS:
        fail("Invalid script code")

    requirements = REQS[script_code]

    # ---- Publishing APRX ----
    if "publishing" in requirements and script_code != "05":

        if not publishing_path:
            publishing_path = input(
                "Enter publishing aprx path link (you may include the full path in quotes): "
            ).strip().strip('"')

        if not publishing_map_name:
            publishing_map_name = input(
                "Enter publishing map name: "
            ).strip()

        validate_aprx(publishing_path)
        verify_map(publishing_path, publishing_map_name)

    else:
        publishing_path = None
        publishing_map_name = None

    # ---- Working APRX ----
    if "working_path" in requirements:
        working_path = validate_aprx(working_path)
        verify_map(working_path, working_map_name)

    # ---- Extract Project Info ----
    project_root = None

    if any(
        x in requirements
        for x in [
            "sde",
            "base_gdb",
            "project_code",
            "project_name",
            "publishing",
        ]
    ):

        base_source = (
            publishing_path
            if publishing_path
            else Path(working_path)
        )

        project_root = (
            str(base_source).split("\\gblon0vs01\\GISProj\\")[-1]
            if "\\gblon0vs01\\GISProj\\" in str(base_source)
            else None
        )

        project_root_name = (
            project_root.split("\\")[0]
            if "\\" in project_root
            else None
        )

        try:
            project_code, project_name = project_root_name.split("_", 1)

        except ValueError:
            fail(
                f"Invalid project folder name: {project_root_name}"
            )

    # ---- Base GDB ----
    if "base_gdb" in requirements:

        if not base_gdb_path:
            base_gdb_path = project_root / "Data"

        print(f"✅ Base GDB: {base_gdb_path}")

    # ---- SDE ----
    if "sde" in requirements:

        if not sde_path:

            sde_name = (
                f"GBLON0-SQL005_{project_root_name}_DATAOWNER.sde"
            )

            if not sde_user:
                sde_user = f"{project_code}_DATAOWNER"

            sde_path = project_root / "Data" / sde_name

        else:
            sde_path = Path(sde_path)

        validate_sde(sde_path)

def run_script(script_code):
    selected_script = next(
        (
            f
            for f in os.listdir(SCRIPT_FOLDER)
            if f.startswith(script_code)
            and f.endswith(".py")
        ),
        None,
    )

    if not selected_script:
        fail("Script not found")

    script_path = SCRIPT_FOLDER / selected_script

    print(f"\n✅ Running {script_path.name}")
    confirm()

    args = [
        sys.executable,
        str(script_path),
        str(working_path or ""),
        working_map_name or "",
        str(sde_path or ""),
        str(base_gdb_path or ""),
        str(sde_user or ""),
        project_code or "",
        project_name or "",
        str(publishing_path or ""),
        publishing_map_name or "",
    ]

    subprocess.run(args, check=True)

    print("\n✅ Script completed.")

def run():
    script_setup()
    run_script(script_code)

# ==============================
# MAIN LOOP
# ==============================
while True:

    confirm()

    run()

    while True:

        choice = input(
            "\nOpen APRX? (pub / work / rerun / no): "
        ).lower()

        if choice == "pub" and publishing_path:
            os.startfile(str(publishing_path))

        elif choice == "work" and working_path:
            os.startfile(str(working_path))

        elif choice == "rerun":
            break

        elif choice == "no":
            print("Finished.")
            sys.exit(0)

        else:
            print("Finished.")
            sys.exit(0)