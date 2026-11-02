"""
This script adds a new field called "HabitatType_Desc" to the input feature class
And cleans the existing habitat type codes to provide a more descriptive field 
in the attribute table.

"""

import arcpy
input_fc_path = r"\path\to.gdbeaturename"

# Add field if it doesn't exist
field_name = "HabitatType_Desc"

if field_name not in [f.name for f in arcpy.ListFields(input_fc_path)]:
    arcpy.AddField_management(input_fc_path, field_name, "TEXT", field_length=255)

# Habitat lookup
habitat_lookup = {
    "c": "c - cropland",
    "c1": "c1 - arable and horticulture",
    "c1a": "c1a - arable field margins",
    "c1b": "c1b - temporary grass and clover leys",
    "c1c": "c1c - cereal crops",
    "c1d": "c1d - non-cereal crops",
    "c1e": "c1e - intensive orchards",
    "c1f": "c1f - horticulture",

    "f": "f - wetland",
    "f1": "f1 - bog",
    "f1a": "f1a - blanket bog",
    "f1b": "f1b - lowland raised bog",
    "f2": "f2 - fen,marsh and swamp",
    "f2a": "f2a - lowland fens",
    "f2d": "f2d - aquatic marginal vegetation",
    "f2e": "f2e - reedbeds",

    "g": "g - grassland",
    "g1": "g1 - acid grassland",
    "g1a": "g1a - lowland dry acid grassland",
    "g1b": "g1b - upland acid grassland",
    "g1b5": "g1b5 - montane acid grasslands (H6150)",
    "g1b6": "g1b6 - other upland acid grassland",
    "g1c": "g1c - bracken",
    "g2": "g2 - calcareous grassland",
    "g2a": "g2a - lowland calcareous grassland",
    "g2b": "g2b - upland calcareous grassland",
    "g3": "g3 - neutral grassland",
    "g3a": "g3a - lowland meadows",
    "g3b": "g3b - upland hay meadows",
    "g3c": "g3c - other neutral grassland",
    "g3c5": "g3c5 - Arrhenatherum neutral grassland",
    "g3c6": "g3c6 - Lolium-Cynosurus neutral grassland",
    "g3c7": "g3c7 - Deschampsia neutral grassland",
    "g3c8": "g3c8 - Holcus-Juncus neutral grassland",
    "g4": "g4 - modified grassland",

    "h": "h - heathland and shrub",
    "h1": "h1 - dwarf shrub heath",
    "h1a": "h1a - lowland heathland",
    "h1a5": "h1a5 - dry heaths, lowland (H4030)",
    "h1a7": "h1a7 - wet heathland with cross-leaved heath, lowland (H4010)",
    "h1b": "h1b - upland heathland",
    "h1b5": "h1b5 - dry heaths, upland (H4030)",
    "h1b6": "h1b6 - wet heathland with cross-leaved heath, upland (H4010)",
    "h2": "h2 - hedgerow",
    "h2a": "h2a - hedgerow (priority habitat)",
    "h2b": "h2b - other hedgerows",
    "h3": "h3 - dense scrub",

    "r": "r - rivers and lakes",
    "r1": "r1 - standing open water and canals",
    "r1a": "r1a - eutrophic standing water",
    "r1e": "r1e - canals",
    "r2": "r2 - rivers and lakes",

    "s": "s - sparsely vegetated land",
    "s1": "s1 - inland rock",
    "s1a": "s1a - inland rock and scree habitats",
    "s1d": "s1d - other inland rock and scree",
    "s2": "s2 - supralittoral rock",
    "s2a": "s2a - maritime cliff and slopes",
    "s3": "s3 - supralittoral sediment",
    "s3a": "s3a - coastal sand dunes",
    "s3b": "s3b - coastal vegetated shingle",

    "t": "t - marine inlets and transitional waters",
    "t1": "t1 - littoral rock",
    "t2": "t2 - littoral sediment",
    "t2a": "t2a - coastal saltmarsh",
    "t2d": "t2d - intertidal mudflats",

    "u": "u - urban",
    "u1": "u1 - built-up areas and gardens",
    "u1a": "u1a - open mosaic habitats on previously developed land",
    "u1b": "u1b - developed land, sealed surface",
    "u1b5": "u1b5 - buildings",
    "u1b6": "u1b6 - other developed land",
    "u1c": "u1c - artificial unvegetated unsealed surface",
    "u1d": "u1d - suburban mosaic of developed/natural surfaces",
    "u1e": "u1e - built linear features",

    "w": "w - woodland",
    "w1": "w1 - broadleaved, mixed and yew woodland",
    "w1a": "w1a - upland oakwood",
    "w1b": "w1b - upland mixed ashwoods",
    "w1c": "w1c - lowland beech and yew woodland",
    "w1d": "w1d - wet woodland",
    "w1e": "w1e - upland birchwoods",
    "w1f": "w1f - lowland mixed deciduous woodland",
    "w1g": "w1g - other woodland, broadleaved",
    "w1g6": "w1g6 - line of trees",
    "w1h": "w1h - other woodland, mixed",
    "w2": "w2 - coniferous woodland",

    "w2a": "w2a - native pine woodlands",
    "w2b": "w2b - other scots pine woodland",
    "w2c": "w2c - other coniferous woodland",

    "f2e, 10": "f2e, 10 - reedbeds, scattered scrub",
    "g3c, 10": "g3c, 10 - other neutral grassland, scattered scrub",

    "h3c": "h3c - sea buckthorn scrub",
    "h3d": "h3d - bramble scrub",
    "h3h": "h3h - mixed scrub",

    "u1f": "u1f - sparsely vegetated urban land",
    "u1f, 10": "u1f, 10 - sparsely vegetated urban land, scattered scrub",
    "u1f, 16": "u1f, 16 - sparsely vegetated urban land, tall herb",
}

with arcpy.da.UpdateCursor(input_fc_path, ["HabitatType", field_name]) as cursor:
    for row in cursor:
        habitat = row[0]

        if habitat:
            code = habitat.split(" - ")[0].strip().lower()
            row[1] = habitat_lookup.get(code)
        else:
            row[1] = None

        cursor.updateRow(row)

print("HabitatType_Desc populated successfully.")