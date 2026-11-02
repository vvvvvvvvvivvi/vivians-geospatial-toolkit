import arcpy
import os

# =============================================================================
# INPUT FEATURE CLASS - ONLY EDIT THESE
# =============================================================================
input_fc_path = r"\path\to.gdbeaturename"

"""
=============================================================================
PSEUDO CODE
=============================================================================

1. Create a copy of the input habitat feature class.

2. Ensure all required habitat value fields exist:
     - BNGMetric
     - DistinctivenessScore
     - ConditionScore
     - StratSigScore
     - HabitatValueScore
     - HabitatValueCat

3. For each habitat polygon:

     a. If Subtype = 8:
           Set BNGMetric = "Watercourse footprint"

     b. Otherwise, if BNGMetric is empty:
           Extract habitat description from HabitatType
           Match description to a BNG metric lookup value
           Populate BNGMetric

     c. Lookup DistinctivenessScore from BNGMetric

     d. Lookup ConditionScore from Condition field

     e. Lookup StratSigScore from Strategic Significance field
        (default to Low = 1 where blank)

     f. Calculate HabitatValueScore:

           HabitatValueScore =
               DistinctivenessScore
               × ConditionScore
               × StratSigScore

     g. Classify HabitatValueScore into:
           - Urban hardstanding
           - Very low habitat value
           - Low habitat value
           - Moderate habitat value
           - High habitat value
           - Very high habitat value

     h. Update the feature.

4. Save all edits.

5. Report:
     - Number of features processed
     - Any habitat descriptions that could not be matched
     - Output feature class location

=============================================================================
"""

arcpy.env.overwriteOutput = True

# =============================================================================
# CREATE OUTPUT FEATURE CLASS
# =============================================================================

desc = arcpy.Describe(input_fc_path)
gdb = desc.path
fc_name = desc.name

output_fc = os.path.join(
    gdb,
    f"{fc_name}_HabitatValue"
)

if arcpy.Exists(output_fc):
    arcpy.management.Delete(output_fc)

print("Copying feature class...")
arcpy.management.CopyFeatures(input_fc_path, output_fc)

# =============================================================================
# ADD FIELDS IF MISSING
# =============================================================================

required_fields = [
    ("BNGMetric", "TEXT", "BNG metric", 255),
    ("ConditionScore", "DOUBLE", "Habitat condition score", None),
    ("DistinctivenessScore", "LONG", "Distinctiveness score", None),
    ("StratSigScore", "DOUBLE", "Strategic significance score", None),
    ("HabitatValueScore", "DOUBLE", "Habitat value score", None),
    ("HabitatValueCat", "TEXT", "Habitat value category", 50)
]

existing_fields = [f.name for f in arcpy.ListFields(output_fc)]

for field_name, field_type, alias, length in required_fields:

    if field_name not in existing_fields:

        print(f"Adding field: {field_name}")

        if length:
            arcpy.management.AddField(
                output_fc,
                field_name,
                field_type,
                field_length=length,
                field_alias=alias
            )

        else:
            arcpy.management.AddField(
                output_fc,
                field_name,
                field_type,
                field_alias=alias
            )

# =============================================================================
# LOOKUPS
# =============================================================================

distinctiveness_lookup = {

    # 0
    "Urban - Artificial unvegetated, unsealed surface": 0,
    "Urban - Built linear features": 0,
    "Urban - Developed land; sealed surface": 0,
    "Urban - Un-vegetated garden": 0,
    "Watercourse footprint": 0,

    # 2
    "Cropland - Cereal crops": 2,
    "Cropland - Cereal crops winter stubble": 2,
    "Cropland - Horticulture": 2,
    "Cropland - Intensive orchards": 2,
    "Cropland - Non-cereal crops": 2,
    "Cropland - Temporary grass and clover leys": 2,
    "Grassland - Bracken": 2,
    "Grassland - Modified grassland": 2,
    "Heathland and shrub - Rhododendron scrub": 2,
    "Lakes - Ornamental lake or pond": 2,
    "Sparsely vegetated land - Ruderal/Ephemeral": 2,
    "Sparsely vegetated land - Tall forbs": 2,
    "Urban - Allotments": 2,
    "Urban - Bioswale": 2,
    "Urban - Intensive green roof": 2,
    "Urban - Other green roof": 2,
    "Urban - Façade-bound green wall": 2,
    "Urban - Ground based green wall": 2,
    "Urban - Ground level planters": 2,
    "Urban - Introduced shrub": 2,
    "Urban - Rain garden": 2,
    "Urban - Sand pit quarry or open cast mine": 2,
    "Urban - Sustainable urban drainage feature": 2,
    "Urban - Vacant/derelict land/bareground": 2,
    "Urban - Bare ground": 2,
    "Urban - vegetated garden": 2,
    "Woodland and forest - Other coniferous woodland": 2,
    "Coastal saltmarsh - Artificial saltmarshes and saline reedbeds": 2,
    "Intertidal sediment - Artificial littoral sand": 2,
    "Intertidal sediment - Artificial littoral mud": 2,
    "Intertidal sediment - Artificial littoral muddy sand": 2,
    "Intertidal sediment - Artificial littoral mixed sediments": 2,
    "Intertidal sediment - Artificial littoral seagrass": 2,
    "Intertidal sediment - Artificial littoral biogenic reefs": 2,
    "Intertidal hard structures - Artificial hard structures": 2,
    "Intertidal hard structures - Artificial features of hard structures": 2,

    # 4
    "Cropland - Arable field margins cultivated annually": 4,
    "Cropland - Arable field margins game bird mix": 4,
    "Cropland - Arable field margins pollen and nectar": 4,
    "Cropland - Arable field margins tussocky": 4,
    "Grassland - Other lowland acid grassland": 4,
    "Grassland - Other neutral grassland": 4,
    "Grassland - Upland acid grassland": 4,
    "Heathland and shrub - Blackthorn scrub": 4,
    "Heathland and shrub - Bramble scrub": 4,
    "Heathland and shrub - Gorse scrub": 4,
    "Heathland and shrub - Hawthorn scrub": 4,
    "Heathland and shrub - Hazel scrub": 4,
    "Heathland and shrub - Mixed scrub": 4,
    "Heathland and shrub - Willow scrub": 4,
    "Lakes - Ponds (Non-priority habitat)": 4,
    "Lakes - Reservoirs": 4,
    "Sparsely vegetated land - Other inland rock and scree": 4,
    "Urban - Cemeteries and churchyards": 4,
    "Urban - Biodiverse green roof": 4,
    "Urban - Urban tree": 4,
    "Individual trees - Rural tree": 4,
    "Woodland and forest - Other Scot's pine woodland": 4,
    "Woodland and forest - Other woodland; broadleaved": 4,
    "Woodland and forest - Other woodland; mixed": 4,
    "Intertidal sediment - Littoral coarse sediment": 4,
    "Intertidal sediment - Littoral sand": 4,
    "Intertidal sediment - Artificial hard structures with integrated greening of grey infrastructure": 4,

    # 6
    "Grassland - Traditional orchards": 6,
    "Grassland - Floodplain Wetland Mosaic (CFGM)": 6,
    "Grassland - Lowland calcareous grassland": 6,
    "Grassland - Tall herb communities": 6,
    "Grassland - Upland calcareous grassland": 6,
    "Heathland and shrub - Lowland heathland": 6,
    "Dunes with sea buckthorn (H2160)": 6,
    "Heathland and shrub - Upland heathland": 6,
    "Lakes - High alkalinity lakes": 6,
    "Lakes - Low alkalinity lakes": 6,
    "Lakes - Marl lakes": 6,
    "Lakes - Moderate alkalinity lakes": 6,
    "Lakes - Peat lakes": 6,
    "Lakes - Ponds (Priority habitat)": 6,
    "Lakes - Temporary lakes, ponds and pools": 6,
    "Sparsely vegetated land - Coastal sand dunes": 6,
    "Sparsely vegetated land - Coastal vegetated shingle": 6,
    "Sparsely vegetated land - Inland rock outcrop and scree habitats": 6,
    "Sparsely vegetated land - Maritime cliff and slopes": 6,
    "Urban - Open mosaic habitats on previously developed land": 6,
    "Wetland - Reedbeds": 6,
    "Woodland and forest - Felled": 6,
    "Woodland and forest - Lowland beech and yew woodland": 6,
    "Woodland and forest - Lowland mixed deciduous woodland": 6,
    "Woodland and forest - Native pine woodlands": 6,
    "Woodland and forest - Upland birchwoods": 6,
    "Woodland and forest - Upland mixed ashwoods": 6,
    "Woodland and forest - Upland oakwood": 6,
    "Woodland and forest - Wet woodland": 6,
    "Coastal lagoons": 6,
    "Rocky shore - High energy littoral rock": 6,
    "Rocky shore - Moderate enegery littoral rock": 6,
    "Rocky shore - Low energy littoral rock": 6,
    "Rocky shore - Features of littoral rock": 6,
    "Coastal saltmarsh - Saltmarshes and saline reedbeds": 6,
    "Intertidal sediment - Littoral mud": 6,
    "Intertidal sediment - Littoral mixed sediments": 6,
    "Intertidal sediment - Littoral seagrass": 6,
    "Intertidal sediment - Littoral biogenic reefs - mussels": 6,
    "Intertidal sediment - Littoral biogenic reefs - Sabellaria": 6,
    "Intertidal sediment - Features of littoral sediment": 6,
    "Intertidal sediment - Littoral muddy sand": 6,

    # 8
    "Grassland - Lowland dry acid grassland": 8,
    "Grassland - Lowland meadows": 8,
    "Grassland - Upland hay meadows": 8,
    "Heathland and shrub - Mountain heaths and willow scrub": 8,
    "Lakes - Aquifer fed naturally fluctuating water bodies": 8,
    "Sparsely vegetated land - Calaminarian grasslands": 8,
    "Sparsely vegetated land - Limestone pavement": 8,
    "Wetland - Blanket bog": 8,
    "Wetland - Depressions on Peat substrates (H7150)": 8,
    "Wetland - Fens (upland and lowland)": 8,
    "Wetland - Lowland raised bog": 8,
    "Wetland - Oceanic valley mire[1] (D2.1)": 8,
    "Wetland - Purple moor grass and rush pastures": 8,
    "Wetland - Transition mires and quaking bogs (H7140)": 8,
    "Woodland and forest - Wood-pasture and parkland": 8,
    "Rocky shore - High energy littoral rock - on peat, clay or chalk": 8,
    "Rocky shore - Moderate energy littoral rock - on peat, clay or chalk": 8,
    "Rocky shore - Low energy littoral rock - on peat, clay or chalk": 8,
    "Rocky shore - Features of littoral rock - on peat, clay or chalk": 8,
    "Intertidal sediment - Littoral seagrass on peat, clay or chalk": 8
}

condition_lookup = {
    # "Good": 3,
    # "Fairly good": 2.5,
    # "Moderate": 2,
    # "Fairly poor": 1.5,
    # "Poor": 1,
    # "N/A": 1,
    "2": 3,
    "1": 2,
    "0": 1,
    None: 1,
    "": 1
}

stratsig_lookup = {
    "Low": 1,
    "Medium": 1.1,
    "High": 1.15,
    None: 1,
    "": 1
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_habitat_description(habitat_type):

    if not habitat_type:
        return None

    if " - " in habitat_type:
        return habitat_type.split(" - ", 1)[1].strip()

    return habitat_type.strip()


def find_bng_metric(habitat_desc):

    if not habitat_desc:
        return None

    matches = [
        metric
        for metric in distinctiveness_lookup.keys()
        if habitat_desc.lower() in metric.lower()
    ]

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:

        exact = [
            m
            for m in matches
            if m.lower().endswith(habitat_desc.lower())
        ]

        if len(exact) == 1:
            return exact[0]

    return None


def classify_habitat_value(score):

    if score is None:
        return None

    if score < 0.01:
        return "Urban hardstanding"

    elif score <= 2.49:
        return "Very low habitat value"

    elif score <= 5.00:
        return "Low habitat value"

    elif score <= 10.00:
        return "Moderate habitat value"

    elif score <= 20.00:
        return "High habitat value"

    else:
        return "Very high habitat value"

# =============================================================================
# PROCESS FEATURES
# =============================================================================



unmatched_habitats = set()

fields = [
    "HabitatType",
    "Subtype",
    "BNGMetric",
    "DistinctivenessScore",
    "Condition",
    "ConditionScore",
    "StratSig",
    "StratSigScore",
    "HabitatValueScore",
    "HabitatValueCat"
]

workspace = arcpy.Describe(output_fc).path

print(f"Starting edit session on:\n{workspace}")

editor = arcpy.da.Editor(workspace)

editor.startEditing(False, True)
editor.startOperation()

count = 0

# --------------------------------------------------------------
# Determine BNG Metric
# --------------------------------------------------------------

"""
PSEUDO CODE:
IF feature is a watercourse (Subtype = 8)
    Force BNGMetric = "Watercourse footprint"
ELSE
    If BNGMetric is blank
        Extract habitat description from HabitatType
        Find matching BNG metric from lookup table
        Populate BNGMetric
    End If
END IF
"""

try:

    with arcpy.da.UpdateCursor(output_fc, fields) as cursor:

        for row in cursor:

            count += 1

            habitat_type = row[0]

            subtype = row[1]

            # --------------------------------------------------------------
            # Force watercourse subtype
            # --------------------------------------------------------------

            if subtype == 8:
                row[2] = "Watercourse footprint"

            # --------------------------------------------------------------
            # Populate BNGMetric if blank
            # --------------------------------------------------------------

            if row[2] in (None, "", " "):

                habitat_desc = get_habitat_description(habitat_type)

                bng_metric = find_bng_metric(habitat_desc)

                if bng_metric:
                    row[2] = bng_metric

                elif habitat_desc:
                    unmatched_habitats.add(habitat_desc)

            # --------------------------------------------------------------
            # Distinctiveness
            # --------------------------------------------------------------

            row[3] = distinctiveness_lookup.get(row[2])

            # --------------------------------------------------------------
            # Condition
            # --------------------------------------------------------------

            row[5] = condition_lookup.get(row[4], 1)

            # --------------------------------------------------------------
            # Strategic Significance
            # --------------------------------------------------------------

            row[7] = stratsig_lookup.get(row[6], 1)

            # --------------------------------------------------------------
            # Habitat Value Score
            # --------------------------------------------------------------

            if row[3] is not None:

                score = (
                    float(row[3])
                    * float(row[5])
                    * float(row[7])
                )

            else:

                score = None

            row[8] = score

            # --------------------------------------------------------------
            # Habitat Value Category
            # --------------------------------------------------------------

            row[9] = classify_habitat_value(score)

            cursor.updateRow(row)

            if count % 1000 == 0:
                print(f"Processed {count:,} features")

    editor.stopOperation()
    editor.stopEditing(True)

except Exception:

    editor.stopOperation()
    editor.stopEditing(False)
    raise

# =============================================================================
# REPORT
# =============================================================================

print("\nProcessing complete")
print(f"Features processed: {count}")

if unmatched_habitats:

    print("\nUnmatched habitat descriptions:")

    for habitat in sorted(unmatched_habitats):
        print(f"  {habitat}")

else:

    print("\nAll habitat descriptions matched successfully.")

print(f"\nOutput feature class:\n{output_fc}")