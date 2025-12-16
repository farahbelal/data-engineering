import pandas as pd
from pathlib import Path

from project.utils.load_data import (
    load_data,
    DEFAULT_DATA_PATH,
    COL_YEAR,
    COL_BOROUGH,
    COL_PERSON_TYPE,
    COL_PERSON_INJURY,
)
from project.utils.filters import apply_filters, parse_search_query


# ---------------------------
# TEST 1 — Data loads correctly
# ---------------------------
def test_load_data_exists():
    """CSV file must exist and load without errors."""
    path = Path(DEFAULT_DATA_PATH)
    assert path.exists(), f"Missing CSV file at: {path}"

    df = load_data()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0, "Loaded dataframe is empty!"


# ---------------------------
# TEST 2 — CRASH_YEAR is numeric
# ---------------------------
def test_year_is_numeric():
    df = load_data()
    if COL_YEAR in df.columns:
        assert pd.api.types.is_numeric_dtype(df[COL_YEAR])


# ---------------------------
# TEST 3 — apply_filters should correctly filter borough + year
# ---------------------------
def test_apply_filters_basic():
    df = pd.DataFrame({
        COL_BOROUGH: ["Brooklyn", "Queens", "Brooklyn"],
        COL_YEAR: [2022, 2023, 2022],
        COL_PERSON_TYPE: ["Pedestrian", "Driver", "Pedestrian"],
        COL_PERSON_INJURY: ["Injured", "No injury", "Killed"],
    })

    filtered = apply_filters(
        df=df,
        borough="Brooklyn",
        year=2022,
        vehicle_type=None,
        factor=None,
        injury=None,
        person_type=None,
    )

    assert len(filtered) == 2
    assert all(filtered[COL_BOROUGH] == "Brooklyn")
    assert all(filtered[COL_YEAR] == 2022)


# ---------------------------
# TEST 4 — parse_search_query detects borough + year
# ---------------------------
def test_search_parser():
    df = load_data()
    person_types = df[COL_PERSON_TYPE].dropna().unique().tolist() if COL_PERSON_TYPE in df.columns else []
    injury_types = df[COL_PERSON_INJURY].dropna().unique().tolist() if COL_PERSON_INJURY in df.columns else []

    parsed = parse_search_query(
        "Brooklyn 2022 pedestrian killed",
        person_types,
        injury_types
    )

    # These should be detected
    assert parsed.get("borough") == "Brooklyn"
    assert parsed.get("year") == 2022
