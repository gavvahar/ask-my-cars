from pathlib import Path

import pandas as pd

COLUMN_RENAME_MAP = {
    "Make": "make",
    "Model": "model",
    "Year": "year",
    "Engine Fuel Type": "engine_fuel_type",
    "Engine HP": "engine_hp",
    "Engine Cylinders": "engine_cylinders",
    "Transmission Type": "transmission_type",
    "Driven_Wheels": "driven_wheels",
    "Number of Doors": "number_of_doors",
    "Market Category": "market_category",
    "Vehicle Size": "vehicle_size",
    "Vehicle Style": "vehicle_style",
    "highway MPG": "highway_mpg",
    "city mpg": "city_mpg",
    "Popularity": "popularity",
    "MSRP": "msrp",
}

# Small null counts (69/30/6/3 rows out of 11914) in core spec/filter columns.
# Dropped rather than imputed: fabricating HP/cylinder/door/fuel-type values
# for real car models would misrepresent actual specs in a specs dashboard.
REQUIRED_COLUMNS = ["Engine HP", "Engine Cylinders", "Number of Doors", "Engine Fuel Type"]

# Generous ceiling for data-entry errors, not legitimate outliers — e.g. a
# 2017 Audi A6 row lists 354 highway MPG vs 29-34 for every other row of that
# same model/year. Even the best 1990-2017 hybrids top out around 50 highway
# MPG, so >100 is safely error territory without risking real vehicles.
MPG_UPPER_BOUND = 100

# Anchored to this file's own location, not cwd — the Streamlit app runs from
# repo root, but the FastAPI backend runs via `cd Python && uvicorn ...`, and
# a cwd-relative default silently resolved to the wrong path under that cwd.
DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cars.csv"


def load_data(path=DEFAULT_DATA_PATH):
    df = pd.read_csv(path)
    df = df.dropna(subset=REQUIRED_COLUMNS)
    # Market Category is ~31% null; dropping would lose too much data, so
    # null becomes its own explicit category instead.
    df["Market Category"] = df["Market Category"].fillna("Not Specified")
    df = df[(df["highway MPG"] <= MPG_UPPER_BOUND) & (df["city mpg"] <= MPG_UPPER_BOUND)]
    df = df.rename(columns=COLUMN_RENAME_MAP)
    return df.reset_index(drop=True)
