# This script enable Editor Tracking and Attachments for all appropriate features on all maps.
""" 
Jacobs has a standardised process for setting up Preliminary Ecological Appraisals (PEA).
And... standardisation is a synonym for automation to me.
"""

import arcpy

# Define the paths to the project and target geodatabase
aprx_path = r"\\location\to.aprx" # Path link to workspace ArcGIS Pro project
aprx = arcpy.mp.ArcGISProject(aprx_path)

# Loop through all maps and layers
for map_obj in aprx.listMaps():
    for lyr in map_obj.listLayers():
        if lyr.isFeatureLayer and lyr.supports("DATASOURCE"):
            fc_path = lyr.dataSource
            try:
                # Enable editor tracking
                arcpy.EnableEditorTracking_management(
                    in_dataset=fc_path,
                    creator_field="created_user",
                    creation_date_field="created_date",
                    last_editor_field="last_edited_user",
                    last_edit_date_field="last_edited_date"
                )
                print(f"Editor tracking enabled for: {fc_path}")

                # Enable attachments
                arcpy.EnableAttachments_management(fc_path)
                print(f"Attachments enabled for: {fc_path}")

            except Exception as e:
                print(f"Failed to update {fc_path}: {e}")

print("All applicable feature classes updated.")