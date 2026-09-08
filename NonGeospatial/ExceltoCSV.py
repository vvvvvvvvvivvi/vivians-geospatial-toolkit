import pandas as pd
import os

# Load your Excel workbook
input_xlsx_path = r"\path\to.xlsx"
out_folder_path = r"\path\	o\folder"

if not os.path.isdir(out_folder_path):
    os.makedirs(out_folder_path, exist_ok=True)
else:
    print("Output path exists, proceeding with export.")

# Read all sheets into a dictionary
excel_data = pd.read_excel(input_xlsx_path, sheet_name=None)

# Loop through each sheet and save as a separate CSV
for sheet_name, data in excel_data.items():
    output_file = os.path.join(out_folder_path, # Path link to working folder
                                  f"{sheet_name}.csv")
    data.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Saved: {output_file}")

print("All sheets have been exported successfully!")