"""
\\gblon0vs01\GISProj\_Admin\Geospatial_Templates\Figures_Templates\ArcProTemplates\Jacobs_Pro_Layout_Templates
"""

import arcpy
aprx_path = r"\path\to.aprx"
pagx_path = r"\path\to.pagx"

aprx = arcpy.mp.ArcGISProject(aprx_path)
aprx.importDocument(pagx_path)

aprx.save()

