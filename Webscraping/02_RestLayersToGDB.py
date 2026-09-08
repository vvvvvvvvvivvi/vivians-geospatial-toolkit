import arcpy
import re
import ast
import sys
input_txt_path = r"\path\to.txt"
output_gdb_path = r"\path\to.gdb"


def rest_service_to_gdb(layer_rest_url, layer_name, output_gdb_path):
    import arcpy
    # Create layer
    print(f"Creating Layer")

    result = arcpy.management.MakeFeatureLayer(layer_rest_url, layer_name)
    in_layer = result.getOutput(0)

    out_feature_class = arcpy.conversion.FeatureClassToFeatureClass(
        in_features=in_layer,
        out_path=output_gdb_path,
        out_name=layer_name
    )
    print(f"Imported into: {out_feature_class}")

    return out_feature_class

def read_txt(input_txt_path, keyword):
    with open(input_txt_path, "r", encoding="utf-8") as f:
        raw = f.read()

    # find: feature_classes_to_migrate = [ ... ]
    m = re.search(rf"{keyword}\s*=\s*(\[.*?\])", raw, flags=re.DOTALL)
    if not m:
        print(f"ERROR: Could not extract {keyword} from file.")
        raise SystemExit(1)
    
    try:
        item_list = ast.literal_eval(m.group(1))
    except Exception as e:
        print("ERROR parsing Python list:", e)
        raise

    if not item_list:
        print("ERROR: list is empty.")
        raise SystemExit(1)
    
    return item_list

def fail(msg):
    print(f"‼️ {msg}")
    sys.exit(1)

def layer_name():
    rest_name = input("\n‼️ Provide name for layer: ").lower()
    if rest_name is None or rest_name.strip() == "":
        fail("No name provided for layer.")

    return rest_name

    
rest_layers = read_txt(input_txt_path, "rest_layers")

for rest_link in rest_layers:
    print(f"\nProcessing: {rest_link}")
    rest_name = layer_name()

    try:
        rest_service_to_gdb(rest_link, rest_name, output_gdb_path)
        print(f"✅ Successfully imported {rest_name} into GDB.")
    except Exception as e:
        print(f"❌ Failed to import {rest_name}: {e}")

print("\nAll REST layers processed.")