# This script creates a point feature from a set of latitude and longitude or British National Grid (BNG) reference
""" This is Part 1/2 of the AutoGeoreferencing Toolkit.
It has been created because project team often comes in with a Google maps screenshot and expect you to know where the site is.
In reality, I don't but thankfully there are latitudes and longitudes that I can work with.
Sometimes the team also helpfully provides a BNG, and that's all the information I have.
But I can work with that. """


import os
import arcpy

# Define the paths to the project, geodatabase, and target feature class
gdbPath = r"\\location\to.gdb" # Path link to geodatabase
arcpy.env.workspace = gdbPath
arcpy.env.overwriteOutput = True
print(f"Working with {arcpy.env.workspace}")

# Define spatial references
wgs84 = arcpy.SpatialReference(4326)      # WGS 1984 (lat / lon)
bng = arcpy.SpatialReference(27700)       # British National Grid

"""
Point format:
"FeatureName": {
    "coords": [y, x] OR [easting, northing],
    "coord_type": "latlon" OR "bng"
}
"""

pointFeatures = {
    # Example latlon input:
    # "SiteName": {
    #     "coords": [52.396949, -1.9210947],
    #     "coord_type": "latlon"
    # }
    # Example BNG input:
    # "SiteName": {
    #     "coords": [407250, 282950],
    #     "coord_type": "bng"
    # }
}

for featureName, data in pointFeatures.items():
    try:
        coords = data["coords"]
        coord_type = data["coord_type"].lower()

        # Create geometry based on coordinate type
        if coord_type == "latlon":
            # arcpy.Point(x, y) = (lon, lat)
            point = arcpy.Point(coords[1], coords[0])
            pointGeometry = arcpy.PointGeometry(point, wgs84)
            projectedPoint = pointGeometry.projectAs(bng)

        elif coord_type == "bng":
            # arcpy.Point(x, y) = (easting, northing)
            point = arcpy.Point(coords[0], coords[1])
            projectedPoint = arcpy.PointGeometry(point, bng)

        else:
            raise ValueError(f"Unknown coord_type '{coord_type}'. Use 'latlon' or 'bng'.")

        # Output feature class path
        outputPath = os.path.join(gdbPath, featureName)

        # Create feature class
        arcpy.CreateFeatureclass_management(
            gdbPath,
            featureName,
            "POINT",
            spatial_reference=bng
        )

        # Insert point
        with arcpy.da.InsertCursor(outputPath, ["SHAPE@"]) as cursor:
            cursor.insertRow([projectedPoint])

        print(f"{featureName} plotted successfully ({coord_type}).")

    except Exception as e:
        print(f"Failed to plot {featureName}: {e}")

print("Site location initialised as point.")
