import arcpy
import os
from docx import Document
aprx_path = r"\path\to.aprx"
map_name = "just_a_name"
working_folder = r"\path\	o\workingfolder"
output_docx_path = os.path.join(working_folder, "LayerSourceReport.docx")
sde_path = r"\path\to.sde"

# Create document
doc = Document()
doc.add_heading("Layer Report", level=1)

aprx = arcpy.mp.ArcGISProject(aprx_path)
m = aprx.listMaps(map_name)[0]

count = 0

for lyr in m.listLayers():

    if not lyr.isFeatureLayer:
        continue

    count += 1

    doc.add_heading(f"Layer {count}: {lyr.name}", level=2)

    print(f"Processing layer: {lyr.name}")

    try:

        if ".sde" in lyr.connectionProperties.get("dataset"):

            source_path = lyr.connectionProperties.get("dataset")
            source_path = source_path.replace("%", "")
            full_path = os.path.join(sde_path, source_path)

            field_source = full_path

            doc.add_paragraph(f"Source Type: SDE")
            doc.add_paragraph(f"Source: {full_path}")

        else:

            field_source = lyr.dataSource

            doc.add_paragraph("Source Type: File GDB")
            doc.add_paragraph(f"Source: {lyr.dataSource}")

        row_count = arcpy.management.GetCount(lyr).getOutput(0)
        doc.add_paragraph(f"Row Count: {row_count}")

        doc.add_paragraph("Fields:")

        try:
            for field in arcpy.ListFields(field_source):

                if (
                    field.required
                    or field.type in ("OID", "Geometry")
                    or field.name.upper() == "OBJECTID"
                ):
                    continue

                doc.add_paragraph(field.name, style="List Bullet")

        except Exception as e:
            doc.add_paragraph(f"Unable to read fields: {e}")

    except Exception as e:
        doc.add_paragraph(f"Error reading layer properties: {e}")

    doc.add_paragraph("-" * 80)

doc.add_paragraph(f"Total feature layers processed: {count}")
doc.add_paragraph("Done.")

doc.save(output_file)

print(f"Report saved to: {output_file}")
