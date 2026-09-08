import arcpy
import os
import string
import openpyxl

# Accept both csv and xlsx files as input
incoming = [
    {"incoming_path": r"\\gblon0vs01\GISProj\ReferencedData\Foundations\VLWorking\incoming\20260821\BARR .csv",
     "fc_name": "ch_HES_BARR2", 
     "x_col": "AL", 
     "y_col": "AM"}

    #  {"incoming_path": r"",
    # "fc_name": "", 
    # "x_col": "", 
    # "y_col": ""},

]
output_gdb_path = r"\path\to.gdb"

# =============================================================================
# Helper
# =============================================================================

def _excel_col_to_index(col_letter):
    """
    Convert Excel column letters to a zero-based index.

    Examples:
    A  -> 0
    B  -> 1
    Z  -> 25
    AA -> 26
    AC -> 28
    CC -> 80
    CD -> 81
    """
    col_letter = col_letter.upper()
    index = 0

    for char in col_letter:
        index = index * 26 + (ord(char) - ord('A') + 1)

    return index - 1  # Convert from 1-based to 0-based indexing

def _excel_to_csv(input_excel):
    """
    Convert an Excel file to CSV format.

    Parameters:
    - input_excel: Path to the input Excel file.
    - output_csv: Path to the output CSV file.
    """
    # Read the Excel file
    wb = openpyxl.load_workbook(input_excel)
    ws = wb.active

    output_csv = os.path.splitext(input_excel)[0] + ".csv"

    # Save as CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        for row in ws.iter_rows():
            data = [cell.value for cell in row]
            f.write(",".join(str(x) if x is not None else "" for x in data) + "\n")

    return output_csv

def _new_gdb(staging_folder):
    """
    Create a new file geodatabase in the staging folder.

    Parameters:
    - staging_folder: Path to the staging folder.

    Returns:
    - Path to the created geodatabase.
    """
gdb_name = r"\path\to.gdb"
gdb_path = r"\path\to.gdb"

    arcpy.management.CreateFileGDB(staging_folder, gdb_name)

    return gdb_path

for item in incoming:
    incoming_path = item["incoming_path"]
    fc_name = item["fc_name"]
    x_col = item["x_col"]
    y_col = item["y_col"]

    csv_paths = []
    if incoming_path.lower().endswith(".xlsx"):
        csv_path = _excel_to_csv(incoming_path)
        csv_paths.append(csv_path)
    else:
        csv_paths.append(incoming_path)

    spatial_ref = arcpy.SpatialReference(27700)  # British National Grid

    arcpy.env.overwriteOutput = True

    for csv in csv_paths:
        csv_path = csv

        if len(csv_paths) > 1:
            print(f"Multiple CSVs found for {fc_name}.")
            fc_suffix = os.path.basename(csv)
            fc_suffix_cleaned = os.path.splitext(fc_suffix)[0].replace(" ", "_").replace("-", "_")
output_fc_name = "just_a_name"
        else:
output_fc_name = "just_a_name"

        out_fc = os.path.join(output_gdb, output_fc_name)

        print(f"\nProcessing {output_fc_name}")

        # Read header row
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            header_line = f.readline().rstrip("\n")

        headers = [h.strip() for h in header_line.split(",")]

        east_idx = _excel_col_to_index(x_col)
        north_idx = _excel_col_to_index(y_col)

        east_field = headers[east_idx]
        north_field = headers[north_idx]

        print(f"X Field: {east_field}")
        print(f"Y Field: {north_field}")

        if arcpy.Exists(out_fc):
            arcpy.management.Delete(out_fc)

        # Create point feature class directly from CSV
        try:
            temp_fc = os.path.join(
                r"\\gblon0vs01\GISProj\ReferencedData\Foundations\VLWorking\NDS_Working.gdb",
                output_fc_name
            )

            arcpy.management.XYTableToPoint(
                in_table=csv_path,
                out_feature_class=temp_fc,
                x_field=east_field,
                y_field=north_field,
                coordinate_system=spatial_ref
            )

            arcpy.management.CopyFeatures(
                temp_fc,
                out_fc
            )

            arcpy.management.Delete(temp_fc)

        except Exception:
            print(arcpy.GetMessages(0))
            print(arcpy.GetMessages(1))
            print(arcpy.GetMessages(2))
            raise

        print(f"Completed: {fc_name}")

print("\nFinished.")