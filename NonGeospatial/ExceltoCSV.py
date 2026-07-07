import pandas as pd
import os

# Load your Excel workbook
excel_file = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\IncData\NEERIC\INC008_LocalEcologicalRecords_20260702\15-32 AllSp Report Clean.xlsx"
output_folder = r"\\gblon0vs01\GISProj\B245776V_NW_CargoFleetLane\Working\VL\002_NEEric\csv"  # Path link to working folder

if not os.path.isdir(output_folder):
    os.makedirs(output_folder, exist_ok=True)
else:
    print("Output path exists, proceeding with export.")

# Read all sheets into a dictionary
excel_data = pd.read_excel(excel_file, sheet_name=None)

# Loop through each sheet and save as a separate CSV
for sheet_name, data in excel_data.items():
    output_file = os.path.join(output_folder, # Path link to working folder
                                  f"{sheet_name}.csv")
    data.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Saved: {output_file}")

print("All sheets have been exported successfully!")