## This script clips specific feature class to the extent of another feature class
""" 
This script was created as I had to clip multiple feature classes to a certain area of interest. 
Due to naming convention, I could conveniently automate the process.
"""

import arcpy
import os

# Define the paths to the geodatabase
arcpy.env.workspace = r"\\location\to.gdb" # Path link to geodatabase
arcpy.env.overwriteOutput = True

# Base name of the input feature classes to be clipped
clipped_feature_class = ""
# Target feature class within the gdb/sde for clipping
clipping_feature_class = "" 

# The script is also set up to iterate through a list of feature classes sharing the same base name
""" # List of input feature class names
clipped_feature_class_names = [
    f"{clipped_feature_class}_2km_Shape",
    f"{clipped_feature_class}_20km_Shape"
] 
"""

# Loop through each input and perform intersection
for input_fc_name in clipped_feature_class:
#for input_fc_name in clipped_feature_class_names:
    output_fc_name = f"{input_fc_name}_clipped" # Or whatever preferred name

    # Clip
    arcpy.Clip_analysis(input_fc_name, clipping_feature_class, output_fc_name)

    print(f"Clipped {input_fc_name} with {clipping_feature_class} to create {output_fc_name}")

print("All clipping completed successfully.")