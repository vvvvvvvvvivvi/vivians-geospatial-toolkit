"""
Script revised based on Hugo Hadfield's uklookup Python package.

Reads an Excel file containing postcodes and appends
British National Grid Easting/Northing coordinates
from Code-Point Open lookup tables.
"""

from pathlib import Path
from functools import lru_cache
from typing import Dict, Tuple, Optional

import numpy as np
import pandas as pd
import os


# =============================================================================
# INPUTS
# =============================================================================
input_xlsx_path = r"\path\to.xlsx"
out_folder_path = r"\path\	o\folder"


# CREATE OUTPUT FOLDER IF REQUIRED

os.makedirs(out_folder_path, exist_ok=True)

print("Output path exists, proceeding with export.")


# LOAD EXCEL

df = pd.read_excel(input_xlsx_path)

print(f"Loaded {len(df)} records")


# HELPER FUNCTIONS

def clean_alphanum(string: str) -> str:
    """
    Remove all non-alphanumeric characters.
    """
    if pd.isna(string):
        return ""

    return "".join(c for c in str(string) if c.isalnum())


def clean_alpha(string: str) -> str:
    """
    Remove all non-alphabetic characters.
    """
    if pd.isna(string):
        return ""

    return "".join(c for c in str(string) if c.isalpha())


# CODE-POINT OPEN LOOKUP

@lru_cache(maxsize=20)
def get_prefix_data(prefix: str) -> Dict[str, Tuple[int, int]]:
    """
    Read a Code-Point Open CSV and return a dictionary:

    {
        POSTCODE: (EASTING, NORTHING)
    }
    """

    current_dir = Path(__file__).resolve().parent

    filename = (
        current_dir /
        "codepointopen" /
        "Data" /
        "CSV" /
        f"{prefix.lower().strip()}.csv.gz"
    )

    if not filename.exists():
        raise FileNotFoundError(
            f"No Code-Point Open file found:\n{filename}"
        )

    codes = np.genfromtxt(
        filename,
        delimiter=",",
        usecols=0,
        dtype=str
    )

    east_north = np.genfromtxt(
        filename,
        delimiter=",",
        usecols=(2, 3),
        dtype=int
    )

    data = {
        clean_alphanum(code.upper()): (east, north)
        for code, (east, north) in zip(codes, east_north)
    }


    return data


def lookup_postcode(postcode: str) -> Optional[Tuple[int, int]]:
    """
    Return (Easting, Northing) for postcode.
    """

    if pd.isna(postcode):
        return None

    # Standardise format
    postcode = clean_alphanum(str(postcode).upper())

    print(f"Looking up postcode: {postcode}")

    if len(postcode) < 2:
        return None

    prefix = clean_alpha(postcode)[:2]

    print(f"Using prefix: {prefix}")

    try:
        data = get_prefix_data(prefix)

        if postcode in data:
            return data[postcode]

    except FileNotFoundError as e:
        print(e)

    return None


def postcode_to_bng(postcode: str) -> pd.Series:
    """
    Convert postcode to Easting/Northing.
    """

    result = lookup_postcode(postcode)

    if result is None:
        return pd.Series([np.nan, np.nan])

    easting, northing = result

    return pd.Series([easting, northing])

# PROCESS DATAFRAME

if "POSTAL" not in df.columns:
    raise ValueError(
        "Column 'POSTAL' not found in Excel sheet."
    )

print("Looking up Easting/Northing values...")

df[["Easting", "Northing"]] = df["POSTAL"].apply(postcode_to_bng)

matched = df["Easting"].notna().sum()

print(f"Matched {matched:,} postcodes")
print(f"Unmatched {len(df) - matched:,} postcodes")


# EXPORT

output_csv_path = os.path.join(
    out_folder_path,
    f"{Path(input_xlsx_path).stem}_with_BNG.csv"
)

df.to_csv(output_csv_path, index=False)

print("\nExport complete")
print(f"Output file:\n{output_csv_path}")