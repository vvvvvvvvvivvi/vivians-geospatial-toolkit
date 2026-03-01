""" 
This is a bespoke solution developed for a series of figure production tasks, working with Protected Species records from North East ERIC.
This script takes the BNG information of each species record in Excel workbook format, and convert them into points using the top left corner of the BNG.
As BNG information is sometimes not complete (ranges from 2-8 characters), the script is flexible in how granular the spatial inforamtion is.
It then cleans the data to subset to only records within the past 10 years, aligning with project requirement.
 """

import pandas as pd
import re
import os
from datetime import datetime
from dateutil import parser
from calendar import monthrange

# Define path to working folder
output_folder_path = r"\\location\to\workingfolder" # Path link to working folder

# Load target Excel file
input_path = r"\\location\to\excel.xlsx" # Path link to excel sheet
df = pd.read_excel(input_path)

# Define seasonal end dates
season_end_dates = {
    'spring': '20/06',
    'summer': '22/09',
    'autumn': '21/12',
    'fall': '21/12',
    'winter': '20/03'
}

# Function to clean and standardise date
def clean_date(date_str):
    if pd.isnull(date_str):
        return None
    date_str = str(date_str).strip()
    if '-' in date_str and not re.match(r'\d{1,2}-\d{1,2}-\d{2,4}', date_str):
        parts = re.split(r'\s*-\s*', date_str)
        return clean_date(parts[-1])
    for season, end_date in season_end_dates.items():
        if season.lower() in date_str.lower():
            year_match = re.search(r'\d{4}', date_str)
            if year_match:
                return f"{end_date}/{year_match.group()}"
    try:
        parsed_date = parser.parse(date_str, fuzzy=True, dayfirst=True)
        year = parsed_date.year
        month = parsed_date.month
        last_day = monthrange(year, month)[1]
        return f"{last_day:02d}/{month:02d}/{year}"
    except:
        pass
    if re.fullmatch(r'\d{4}', date_str):
        return f"31/12/{date_str}"
    return None

df['CleanedDate'] = df['Date'].apply(clean_date)

# Calculate years since logged
def calculate_years_since(date_str):
    if date_str is None:
        return None
    try:
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        today = datetime.today()
        return round((today - date_obj).days / 365.25, 2)
    except:
        return None

df['YearSinceLogged'] = df['CleanedDate'].apply(calculate_years_since)

# In Review flag
df['InReview'] = df['YearSinceLogged'].apply(lambda y: 'No record' if y is None else ('T' if y < 10 else 'F'))

# OS Grid Reference Conversion 
grid_offsets = {
    'NZ': (400000, 500000),
    'NY': (300000, 500000),
    'SE': (400000, 400000),
    'SD': (300000, 400000),
}

def os_grid_to_easting_northing(grid_ref):
    if pd.isnull(grid_ref):
        return None, None
    grid_ref = str(grid_ref).strip().upper()

    # Remove trailing letter if present
    if grid_ref[-1].isalpha():
        grid_ref = grid_ref[:-1]

    prefix = grid_ref[:2]
    numbers = grid_ref[2:]
    if prefix not in grid_offsets or not numbers.isdigit():
        return None, None

    offset_e, offset_n = grid_offsets[prefix]
    half = len(numbers) // 2
    e_part, n_part = numbers[:half], numbers[half:]
    scale = 10 ** (5 - len(e_part))  # Adjust scale based on precision
    easting = offset_e + int(e_part) * scale
    northing = offset_n + int(n_part) * scale
    return easting, northing


# Apply conversion
df[['Easting', 'Northing']] = df['Grid Reference'].apply(lambda x: pd.Series(os_grid_to_easting_northing(x)))

# Export full cleaned data to Excel
output_excel_path = os.path.join(output_folder_path, 
                                  "NEEric\ProtectedAndNotableSpecies.xlsx")
df.to_excel(output_excel_path, index=False)

print("Full data exported to Excel.")

# Filter rows where InReview == 'T' and export to CSV
df_in_review = df[df['InReview'] == 'T']
output_csv_path = os.path.join(output_folder_path, 
                                  "NEEric\ProtectedAndNotableSpecies.csv")
df_in_review.to_csv(output_csv_path, index=False)

print("'In Review' data exported to CSV.")