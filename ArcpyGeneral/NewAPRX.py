import arcpy
import os 

# Load a blank/template project
new_aprx_folder = r"\\gblon0vs01\GISProj\B3553RG4_SaferSpeeds\Working\VL\02_NewData"
new_aprx_name = "IncomingData260707.aprx"

new_aprx_path = os.path.join(new_aprx_folder, new_aprx_name)

template_aprx_path = r"C:\Users\LEEV\OneDrive\ToolboxTemplateAPRX\ToolboxTemplateAPRX.aprx" # Constant
aprx = arcpy.mp.ArcGISProject(template_aprx_path)
aprx.saveACopy(new_aprx_path)

# Clear from memory
del aprx