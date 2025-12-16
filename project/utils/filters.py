import pandas as pd
from typing import Optional, List, Union, Dict, Any

from project.utils.load_data import (
    COL_BOROUGH,
    COL_YEAR,
    COL_MONTH,
    COL_HOUR,
    COL_PERSON_INJURY,
    COL_PERSON_TYPE,
    COL_VEHICLE_TYPE,
    COL_FACTOR,
)


# ===========================
# Search query parsing
# ===========================
def parse_search_query(
    query: Optional[str],
    person_types: Optional[List[str]] = None,
    injury_types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Parse free-text search into structured filters.

    Returns keys your callbacks expect:
      - borough
      - year
      - person_type
      - injury
      - keywords
    """
    if not query:
        return {}

    person_types = person_types or []
    injury_types = injury_types or []

    parts = query.strip().split()
    result: Dict[str, Any] = {
        "borough": None,
        "year": None,
        "person_type": None,
        "injury": None,
        "keywords": [],
    }

    boroughs = {"MANHATTAN", "BROOKLYN", "QUEENS", "BRONX", "STATEN", "STATEN ISLAND"}

    # Normalize lists for matching
    person_types_up = {str(x).strip().upper(): x for x in person_types}
    injury_types_up = {str(x).strip().upper(): x for x in injury_types}

    i = 0
    while i < len(parts):
        p = parts[i]
        up = p.upper()

        # Handle "STATEN ISLAND" as 2 words
        if up == "STATEN" and i + 1 < len(parts) and parts[i + 1].upper() == "ISLAND":
            result["borough"] = "STATEN ISLAND"
            i += 2
            continue

        # Borough
        if up in boroughs:
            result["borough"] = "STATEN ISLAND" if up == "STATEN" else up
            i += 1
            continue

        # Year (4 digits)
        if p.isdigit() and len(p) == 4:
            try:
                result["year"] = int(p)
            except ValueError:
                pass
            i += 1
            continue

        # Person type (optional matching if lists provided)
        if up in person_types_up and result["person_type"] is None:
            result["person_type"] = person_types_up[up]
            i += 1
            continue

        # Injury (optional matching if lists provided)
        if up in injury_types_up and result["injury"] is None:
            result["injury"] = injury_types_up[up]
            i += 1
            continue

        # Otherwise keyword
        result["keywords"].append(p)
        i += 1

    return result


# ===========================
# Main filtering helper (matches callbacks.py)
# ===========================
def _to_list(x):
    """Convert a single value or list-like to a list, ignoring None/empty."""
    if x is None:
        return []
    if isinstance(x, (list, tuple, set)):
        return [v for v in x if v is not None and str(v).strip() != ""]
    s = str(x).strip()
    return [x] if s != "" else []


def apply_filters(
    df: pd.DataFrame,
    borough=None,
    year=None,
    vehicle_type=None,
    factor=None,
    injury=None,
    person_type=None,
    months=None,
    hours=None,
    search_text: Optional[str] = None,
    **kwargs,
) -> pd.DataFrame:
    """
    Filters dataframe using SINGLE values from Dash dropdowns (your current UI),
    but also tolerates lists if you later switch dropdowns to multi-select.

    Supported filters:
      borough, year, vehicle_type, factor, injury, person_type, months, hours, search_text
    """
    filtered = df.copy()

    # Borough
    b_list = _to_list(borough)
    if b_list and COL_BOROUGH in filtered.columns:
        b_up = [str(b).strip().upper() for b in b_list]
        filtered = filtered[filtered[COL_BOROUGH].astype(str).str.upper().isin(b_up)]

    # Year
    y_list = _to_list(year)
    if y_list and COL_YEAR in filtered.columns:
        y_int = []
        for y in y_list:
            try:
                y_int.append(int(y))
            except Exception:
                pass
        if y_int:
            filtered = filtered[filtered[COL_YEAR].isin(y_int)]

    # Months
    m_list = _to_list(months)
    if m_list and COL_MONTH in filtered.columns:
        m_int = []
        for m in m_list:
            try:
                m_int.append(int(m))
            except Exception:
                pass
        if m_int:
            filtered = filtered[filtered[COL_MONTH].isin(m_int)]

    # Hours
    h_list = _to_list(hours)
    if h_list and COL_HOUR in filtered.columns:
        h_int = []
        for h in h_list:
            try:
                h_int.append(int(h))
            except Exception:
                pass
        if h_int:
            filtered = filtered[filtered[COL_HOUR].isin(h_int)]

    # Injury
    inj_list = _to_list(injury)
    if inj_list and COL_PERSON_INJURY in filtered.columns:
        filtered = filtered[filtered[COL_PERSON_INJURY].isin(inj_list)]

    # Person type
    p_list = _to_list(person_type)
    if p_list and COL_PERSON_TYPE in filtered.columns:
        filtered = filtered[filtered[COL_PERSON_TYPE].isin(p_list)]

    # Vehicle type
    v_list = _to_list(vehicle_type)
    if v_list and COL_VEHICLE_TYPE in filtered.columns:
        filtered = filtered[filtered[COL_VEHICLE_TYPE].isin(v_list)]

    # Contributing factor
    f_list = _to_list(factor)
    if f_list and COL_FACTOR in filtered.columns:
        filtered = filtered[filtered[COL_FACTOR].isin(f_list)]

    # Free-text search (OR across columns, not AND)
    if search_text:
        text = search_text.strip().lower()
        if text:
            masks = []
            for col in [COL_FACTOR, COL_VEHICLE_TYPE, COL_BOROUGH, COL_PERSON_TYPE, COL_PERSON_INJURY]:
                if col in filtered.columns:
                    masks.append(filtered[col].astype(str).str.lower().str.contains(text, na=False))
            if masks:
                mask = masks[0]
                for m in masks[1:]:
                    mask = mask | m
                filtered = filtered[mask]

    return filtered
