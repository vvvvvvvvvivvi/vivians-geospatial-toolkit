import arcpy
import pandas as pd
import os

gdb = r"\\gblon0vs01\GISProj\B245774G_NW_Warkworth\ArcGIS\003_PostSurvey\B245774G_Warkworth_PostSurvey.gdb"
output_excel = r"\\gblon0vs01\GISProj\B245774G_NW_Warkworth\ArcGIS\003_PostSurvey\Output\Warkworth_HabitatOutput.xlsx"

arcpy.env.workspace = gdb

feature_classes = arcpy.ListFeatureClasses()

with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:

    for fc in feature_classes:

        fields = [
            f.name
            for f in arcpy.ListFields(fc)
            if f.type not in ("Geometry", "Blob", "Raster")
        ]

        data = [row for row in arcpy.da.SearchCursor(fc, fields)]
        df = pd.DataFrame(data, columns=fields)

        df.to_excel(
            writer,
            sheet_name=fc[:31],
            index=False
        )

        print(f"{fc}: {len(df)} rows exported")

print(f"Finished: {output_excel}")