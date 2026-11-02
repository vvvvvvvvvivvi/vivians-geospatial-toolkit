"""This script exports attribute table of one or more feature classes into individual Excel Workbooks."""

import arcpy
import os
import pandas as pd

# Define the paths to the geodatabase and target feature class
gdb_path = r"\path\to.gdb"
arcpy.env.workspace = gdb_path
arcpy.env.overwriteOutput = True
in_fc_name_list = []
    # "B245771DWIP_DATAOWNER.ec_ns_jac_WinteringPassageBirdSurveyStudyArea",
    # "B245771DWIP_DATAOWNER.Wilder_Wintering_bird_vantage_points",
    # "B245771DWIP_DATAOWNER.Wilder_Wintering_bird_observations___January",
    # "B245771DWIP_DATAOWNER.Wilder_Wintering_bird_observations___February",
    "SANDYMOUNTCFAS_DATAOWNER.su_DCC_RainGaugeNodes",
    # "B245771DWIP_DATAOWNER.ec_ns_jac_WilderWintBirdObsApril",
    # "B245771DWIP_DATAOWNER.Wilder_Wintering_bird_transects___January",
    # "B245771DWIP_DATAOWNER.Wilder_Wintering_bird_transects___February",
]
output_base_folder = r"\path\	o\outputfolder"

for fc in in_fc_name_list:
    if arcpy.Exists(fc):
        fc_name = fc.replace("B245771DWIP_DATAOWNER.", "")
        print(f"Exporting {fc} as Excel...")
        try:
            output_file = os.path.join(output_base_folder, f"{fc_name}.xlsx")
            fields = [f.name for f in arcpy.ListFields(fc) if f.type not in ('Geometry', 'Date', 'OID')]

            # Use SearchCursor to avoid NumPy type issues
            data = []
            with arcpy.da.SearchCursor(fc, fields) as cursor:
                for row in cursor:
                    data.append(dict(zip(fields, row)))

            df = pd.DataFrame(data)

            if not df.empty:
                with pd.ExcelWriter(output_file) as writer:
                    df.to_excel(writer, sheet_name=fc_name, index=False)
                print(f"Exported {fc} to Excel.")
            else:
                print(f"{fc} is empty. Skipping export.")
        except Exception as e:
            print(f"Failed to export {fc}: {e}")
    else:
        print(f"{fc} does not exist.")

print("All feature classes exported as Excel workbooks.")