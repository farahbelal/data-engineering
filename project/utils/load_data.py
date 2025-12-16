from pathlib import Path
import pandas as pd
import requests
from typing import Union

# ===========================
# Column constants used across the project
# ===========================
COL_BOROUGH = "BOROUGH"
COL_YEAR = "CRASH_YEAR"
COL_MONTH = "CRASH_MONTH"
COL_HOUR = "CRASH_HOUR"
COL_LAT = "LATITUDE"
COL_LON = "LONGITUDE"
COL_COLLISION_ID = "COLLISION_ID"
COL_PERSON_INJURY = "PERSON_INJURY"
COL_PERSON_TYPE = "PERSON_TYPE"
COL_VEHICLE_TYPE = "VEHICLE_TYPE_CODE_1"
COL_FACTOR = "CONTRIBUTING_FACTOR_VEHICLE_1"

# ===========================
# Path to your final CSV (inside repo / Render disk)
# ===========================
DEFAULT_DATA_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "integrated_cleaned_final.csv"
)

# ===========================
# Google Drive direct download URL
# ===========================
CSV_URL = "https://drive.google.com/uc?id=1vJ5IJDLgR2x7_TYkeAWb05EW90jknOcl&export=download"

# ===========================
# Optional column renames
# ===========================
RENAMES = {
    "BOROUGH ": COL_BOROUGH,
    "CRASH YEAR": COL_YEAR,
    "CRASH MONTH": COL_MONTH,
    "CRASH HOUR": COL_HOUR,
    "LATITUDE ": COL_LAT,
    "LONGITUDE ": COL_LON,
    "VEHICLE TYPE CODE 1": COL_VEHICLE_TYPE,
    "CONTRIBUTING FACTOR VEHICLE 1": COL_FACTOR,
    "PERSON TYPE": COL_PERSON_TYPE,
    "PERSON INJURY": COL_PERSON_INJURY,
    "COLLISION_ID": COL_COLLISION_ID,
}


def load_data(path: Union[Path, str] = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """
    Load the cleaned CSV dataset for the dashboard.
    If the CSV is missing (e.g. on Render), download it from Google Drive.
    """
    path = Path(path)

    # Download CSV if it doesn't exist (Render case)
    if not path.exists():
        print("CSV not found locally. Downloading from Google Drive...")
        path.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(CSV_URL, timeout=180)
        response.raise_for_status()
        path.write_bytes(response.content)

    # Load CSV
    df = pd.read_csv(path, low_memory=False)

    # Rename any mismatched columns
    rename_map = {old: new for old, new in RENAMES.items() if old in df.columns}
    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    # Ensure numeric columns are numeric
    for col in [COL_YEAR, COL_MONTH, COL_HOUR]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Clean string columns
    for col in [
        COL_BOROUGH,
        COL_PERSON_INJURY,
        COL_PERSON_TYPE,
        COL_VEHICLE_TYPE,
        COL_FACTOR,
    ]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df
