import arcpy
import pprint

aprx_path = r"\\gblon0vs01\GISProj\B3553RG4_SaferSpeeds\Working\VL\02_NewData\IncomingData260707.aprx"



print("Open APRX")
aprx = arcpy.mp.ArcGISProject(aprx_path)

print("Get map")
m = aprx.listMaps("TestingMapProperties2")[0]

print("Get CIM")
cim = m.getDefinition("V3")

print("Create dt1")
dt1 = arcpy.cim.CreateCIMObjectFromClassName("CIMDatumTransform", "V3")

print("Create dt2")
dt2 = arcpy.cim.CreateCIMObjectFromClassName("CIMDatumTransform", "V3")

print("Populate")
dt1.forward = True
dt1.geoTransformation = {
    "geoTransforms": [{
        "wkid": 5339,
        "latestWkid": 5339,
        "transformForward": False,
        "name": "OSGB_1936_To_WGS_1984_7"
    }]
}

dt2.forward = False
dt2.geoTransformation = {
    "geoTransforms": [{
        "wkid": 5339,
        "latestWkid": 5339,
        "transformForward": False,
        "name": "OSGB_1936_To_WGS_1984_7"
    }]
}

print("Assign")
cim.datumTransforms = [dt1, dt2]

print("Set definition")
m.setDefinition(cim)

pp = pprint.PrettyPrinter(indent=2)

for dt in cim.datumTransforms:
    for prop in dir(dt):
        if not prop.startswith("_"):
            try:
                print(prop, "=", getattr(dt, prop))
            except:
                pass

print("Save")
aprx.save()