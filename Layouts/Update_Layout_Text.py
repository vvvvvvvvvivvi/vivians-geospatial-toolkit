import arcpy
aprx_path = r"\path\to.aprx"
element_name = "Jacobs Copywrite"
new_text = (
    '© Copyright <dyn type="date" format="yyyy"/> Jacobs Engineering Ireland Limited. The concepts and information contained in this document are the property of Jacobs. Use or copying of this document in whole or in part without the written permission of Jacobs constitutes an infringement of copyright.  '
    "Limitation: This drawing has been prepared on behalf of, and for the exclusive use of Jacobs' Client, and is subject to, and issued in accordance with, the provisions of the contract between Jacobs and the Client. Jacobs accepts no liability or responsibility whatsoever for, or in respect of, any use of, or reliance upon, this drawing by any third party."
)
#DrawnBy TEXT VL
#CheckedBy TEXT ÓH
#ReviewedBy TEXT MW
#ApprovedBy TEXT SH
#DrawingNo Bottom TEXT

aprx = arcpy.mp.ArcGISProject(aprx_path)

print(f"Updating layout text for element: {element_name}")

for layout in aprx.listLayouts():

    text_elements = [
        e for e in layout.listElements("TEXT_ELEMENT")
        if e.name == element_name
    ]

    # proj_code, sheet_no, title = layout.name.split("_")

    if text_elements:
        for element in text_elements:
            element.text = new_text
            #new_text + sheet_no[-1]
        print(f"✓ {layout.name} = {element.text}")
    else:
        print(f"✗ {layout.name} - '{element_name}' not found")

aprx.save()
del aprx

print("Completed.")
