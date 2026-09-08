from pathlib import Path
import re

root = Path(r"C:\Users\LEEV\OneDrive\toolboxTemplateAPRX\vivians-geospatial-toolkit")
excluded_path_list = [(root / "IncomingData" / "Reiterative").resolve(),]

replacements = {
    "input_fc_path": 'input_fc_path = r"\\path\\to.gdb\featurename"',
    "sde_path": 'sde_path = r"\\path\\to.sde"',
    "output_name": 'output_name = "just_a_name"',
    "layout_name": 'layout_name = "just_a_name"',
    "new_aprx_folder": 'new_aprx_folder = r""',
    "map_name": 'map_name = "just_a_name"',
    "pagx_path": 'pagx_path = r"\\path\\to.pagx"',
    "aprx_path": 'aprx_path = r"\\path\\to.aprx"',
    "new_aprx_name": 'new_aprx_name = "name.aprx"',
    "out_folder_path": 'out_folder_path = r"\\path\\\to\\folder"',
    "input_folder_path": 'input_folder_path = r"\\path\\\to\\folder"',
    "gdb_name": 'gdb_name = r"\\path\\to.gdb"',
    "fc_path": 'fc_path = r"\\path\\to.gdb\featurename"',
    "gdb_path": 'gdb_path = r"\\path\\to.gdb"',
    "input_xlsx_path": 'input_xlsx_path = r"\\path\\to.xlsx"',
    "input_csv_path": 'input_csv_path = r"\\path\\to.csv"',
    "reference_fc": 'reference_fc = r"\\path\\to.gdb\featurename"',
    "working_folder": 'working_folder = r"\\path\\\to\\workingfolder"',
    "layout_keyword": 'layout_keyword = "just_a_name"',
    "suffix": 'suffix = "_name"',
    "output_base_folder": 'output_base_folder = r"\\path\\\to\\outputfolder"',
    "clipped_feature_class": 'clipped_feature_class = "just_a_name"',
    "clipping_feature_class": 'clipping_feature_class = "just_a_name"',
    "input_gdb_path": 'input_gdb_path = r"\\path\\to.gdb"',
    "output_gdb_path": 'output_gdb_path = r"\\path\\to.gdb"',
    "unique_field": 'unique_field = "field_name"',
    "target_feature_class_name": 'target_feature_class_name = "just_a_name"',
    "input_raster_path": 'input_raster_path = r"\\path\\\to\\raster"',
    "output_fc_name": 'output_fc_name = "just_a_name"',
    "sde_user": 'sde_user = "DataOwner."',
    "publishing_aprx_path": 'publishing_aprx_path = r"\\path\\to.aprx"',
    "publishing_map_name": 'publishing_map_name = "just_a_name"',
    "output_sde_path": 'output_sde_path = r"\\path\\to.sde"',
    "input_zip_path": 'input_zip_path = r"\\path\\to.zip"',
    "input_txt_path": 'input_txt_path = r"\\path\\to.txt"',


    "map_list": 'map_list = ["just_a_name"]',
    "feature_classes_to_delete": 'feature_classes_to_delete = []',
    "in_fc_name_list": 'in_fc_name_list = []',
    "in_fc_path_list": 'in_fc_path_list = []'
    
}

for py_file in root.rglob("*.py"):

    resolved_path = py_file.resolve()

    # Skip anything under IncomingData/Reiterative
    if any(excluded in resolved_path.parents for excluded in excluded_path_list):
        continue

    text = py_file.read_text(encoding="utf-8")
    original_text = text

    for var_name, replacement in replacements.items():
        pattern = re.compile(
            rf"^\s*{re.escape(var_name)}\s*=.*$",
            re.MULTILINE
        )
        text = pattern.sub(lambda m: replacement, text)

    if text != original_text:
        py_file.write_text(text, encoding="utf-8")
        print(f"Updated: {py_file}")