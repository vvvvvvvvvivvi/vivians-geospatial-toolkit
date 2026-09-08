import arcpy

# Define variables
input_fc_path = r"\path\to.gdbeaturename"
out_folder = r"\\gblon0vs01\GISProj\B245771D_NW_NorthSuffolk\Working\VL\022_HRA_FLL\00_Working"

# Run the Feature Class to Shapefile tool
arcpy.conversion.FeatureClassToShapefile(input_fc_path, out_folder)