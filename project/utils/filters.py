import pandas as pd
import re

from utils.load_data import (
    COL_BOROUGH,
    COL_YEAR,
    COL_PERSON_INJURY,
    COL_PERSON_TYPE,
    COL_VEHICLE_TYPE,
    COL_FACTOR,
)

# List of borough names for basic matching
KNOWN_BOROUGHS = ["BRONX", "BROOKLYN", "MANHATTAN", "QUEENS", "STATEN ISLAND"]


def parse_search_query(query: str,
                       person_type_options: list,
                       injury_options: list) -> dict:
    """
    Interpret a free-text search query and extract:
      - borough
      - year
      - person_type
      - injury
    Example: 'Brooklyn 2022 pedestrian killed'
    """
    if not query:
        return {}

    text = query.upper()
    result: dict = {}

    # ---- Borough detection ----
    for b in KNOWN_BOROUGHS:
        if b in text:
            result["borough"] = b.title()
            break

    # ---- Year detection (2010–2039) ----
    years = re.findall(r"(20[1-3][0-9])", text)
    if years:
        try:
            result["year"] = int(years[0])
        except ValueError:
            pass

    # ---- Person type detection using the provided options ----
    if "PEDESTRIAN" in text:
        for p in person_type_options:
            if "ped" in p.lower():
                result["person_type"] = p
                break
    elif "CYCLIST" in text or "BICYCLE" in text:
        for p in person_type_options:
            if "cycl" in p.lower() or "bicy" in p.lower():
                result["person_type"] = p
                break
    elif "DRIVER" in text or "MOTORIST" in text:
        for p in person_type_options:
            if "driver" in p.lower() or "motor" in p.lower():
                result["person_type"] = p
                break

    # ---- Injury detection using the provided options ----
    if "KILL" in text or "FATAL" in text:
        for i in injury_options:
            if "kill" in i.lower() or "fatal" in i.lower():
                result["injury"] = i
                break
    elif "INJUR" in text:
        for i in injury_options:
            if "injur" in i.lower():
                result["injury"] = i
                break

    return result


def apply_filters(df: pd.DataFrame,
                  borough=None,
                  year=None,
                  vehicle_type=None,
                  factor=None,
                  injury=None,
                  person_type=None) -> pd.DataFrame:
    """
    Apply all selected filters to the dataframe and return the result.
    """
    filtered = df.copy()

    if borough:
        filtered = filtered[filtered[COL_BOROUGH] == borough]

    if year:
        filtered = filtered[filtered[COL_YEAR] == year]

    if vehicle_type:
        filtered = filtered[filtered[COL_VEHICLE_TYPE] == vehicle_type]

    if factor:
        filtered = filtered[filtered[COL_FACTOR] == factor]

    if injury:
        filtered = filtered[filtered[COL_PERSON_INJURY] == injury]

    if person_type:
        filtered = filtered[filtered[COL_PERSON_TYPE] == person_type]

    return filtered