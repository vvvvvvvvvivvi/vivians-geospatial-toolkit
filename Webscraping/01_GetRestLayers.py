import os
import requests

base_url = "https://services-eu1.arcgis.com/48zF6lPtAjyLTDSU/arcgis/rest/services/ECC_PlanningTransport_GardenCommunities_00/FeatureServer"
output_folder = r"\\gblon0vs01\GISProj\B3553RG4_SaferSpeeds\Working\VL\02_NewData"

def get_rest_layers(layer_rest_url):
    url_to_query = layer_rest_url + '?f=json'
    response_json = requests.get(url_to_query).json()

    output_ids = []
    layers_in_service = response_json['layers']
    for layer in layers_in_service:
        output_ids.append(layer['id'])
    return output_ids

output_ids = get_rest_layers(base_url)

print(f"Found {len(output_ids)} REST URLs")

for id in output_ids:
    layer_rest_url = base_url + "/" + str(id)
    print(f"\n{layer_rest_url}")

output_file = os.path.join(output_folder, "rest_layers.txt")

with open(output_file, "w") as f:
    f.write("rest_layers = [\n")
    for id in output_ids:
        layer_rest_url = base_url + "/" + str(id)
        f.write(f'    "{layer_rest_url}",\n')
    f.write("]\n")

print(f"\nREST URLs written to:")
print(f"\n{output_file}")