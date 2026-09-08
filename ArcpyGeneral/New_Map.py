import arcpy
aprx_path = r"\path\to.aprx"
map_list = ["just_a_name"]

aprx = arcpy.mp.ArcGISProject(aprx_path)
for m in map_list:
    aprx.createMap(m)

aprx.save()
    
for m in aprx.listMaps():
    print("Map: " + m.name)
    # Map properties 
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

    dt2.forward = True
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

    # Assignment of unique numeric IDs
    print("Set service layer IDs")
    cim.useServiceLayerIDs = True

    print("Set definition")
    m.setDefinition(cim)

aprx.save()

del aprx