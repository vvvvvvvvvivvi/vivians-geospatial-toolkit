# This script creates a .txt file containing the x and y of a point/ top-left corner of a polygon, preparing for georeferencing .pngs in ArcGIS Pro 
""" This is Part 2/2 of the AutoGeoreferencing Toolkit.
Project team also expects you to be able to draw up a Red Line Boundary (RLB) from one blurry .pdf CAD drawing.
And after taking a screenshot of the .pdf and importing into ArcPro, you get brought to the middle of the Pacific Ocean or Africa (often the latter in the UK, used to be the former when I'm in HK)
Well, say bye to dragging the stupid .png half to globe back to Great Britain. 
Initialise your control point table to give yourself a head start <3
You just have to be very good with lines next </3
"""

import arcpy
import os
import csv

# Define the paths to the project, geodatabase, and target feature class
aprx_path = r"\path\to.aprx"
reference_fc = r"\path\to.gdbeaturename"
gdb_path = r"\path\to.gdb"
working_folder_path = r"\\gblon0vs01\GISProj\D3658300_ECRIPP\Working\VL\001_CumulativeAssessment" # Path link to working folder
control_points_txt = os.path.join(working_folder_path, # Path link to working folder
                                  "ControlPoint.txt")

control_points_fc = os.path.join(gdb_path, 
                                  "ControlPoint") # Can leave as it is

# Define WGS 84 spatial reference
wgs84_sr = arcpy.SpatialReference(4326)  # EPSG code for WGS 84

# Create empty Control Point feature class
if not arcpy.Exists(control_points_fc):
    arcpy.CreateFeatureclass_management(
        out_path=os.path.dirname(control_points_fc),
        out_name=os.path.basename(control_points_fc),
        geometry_type="POINT",
        spatial_reference=wgs84_sr  # Use WGS 84 instead of reference_fc's projection
    )
    arcpy.AddField_management(control_points_fc, "X_Coord", "DOUBLE")
    arcpy.AddField_management(control_points_fc, "Y_Coord", "DOUBLE")
    print("Created control points feature class in WGS 84.")

# Extract geometry from reference featureclass to the Control Point
with arcpy.da.SearchCursor(reference_fc, ["SHAPE@XY"]) as cursor:
    for xy in cursor:
        x, y = xy[0]
        with arcpy.da.InsertCursor(control_points_fc, ["SHAPE@XY", "X_Coord", "Y_Coord"]) as insert_cursor:
            insert_cursor.insertRow([(x, y), x, y])
        print(f"Inserted control point at ({x}, {y})")
        break  # Only use the first feature


# Open TXT file for writing
with open(control_points_txt, mode='w') as txtfile:
    # Write header
    txtfile.write("SourceX\tSourceY\tMapX\tMapY\t\n")  # Tab-separated, you can use comma or space if preferred
    # Use a SearchCursor to extract geometry
    with arcpy.da.SearchCursor(control_points_fc, ['SHAPE@XY']) as cursor:
        for row in cursor:
            x, y = row[0]
            txtfile.write(f"{float(0)}\t{float(0)}\t{float(x)}\t{float(y)}\n")  # Write as double precision

    print(f"Exported control point table at {control_points_txt}")

