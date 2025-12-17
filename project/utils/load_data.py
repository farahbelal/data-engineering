from pathlib import Path
import pandas as pd
from typing import Union
import gdown
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

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "integrated_cleaned_final.csv"

CSV_URL = "https://drive.google.com/uc?export=download&id=1vJ5IJDLgR2x7_TYkeAWb05EW90jknOcl"

RENAMES = {
    # NYC open data / common names
    "BOROUGH": COL_BOROUGH,
    "COLLISION_ID": COL_COLLISION_ID,
    "LATITUDE": COL_LAT,
    "LONGITUDE": COL_LON,
    "VEHICLE TYPE CODE 1": COL_VEHICLE_TYPE,
    "CONTRIBUTING FACTOR VEHICLE 1": COL_FACTOR,
    "PERSON TYPE": COL_PERSON_TYPE,
    "PERSON INJURY": COL_PERSON_INJURY,

    # if you already have derived columns with spaces
    "CRASH YEAR": COL_YEAR,
    "CRASH MONTH": COL_MONTH,
    "CRASH HOUR": COL_HOUR,

    # sometimes extra spaces
    "BOROUGH ": COL_BOROUGH,
    "LATITUDE ": COL_LAT,
    "LONGITUDE ": COL_LON,
}




GDRIVE_ID = "1vJ5IJDLgR2x7_TYkeAWb05EW90jknOcl"

def _download_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://drive.google.com/uc?id={GDRIVE_ID}"
    gdown.download(url, str(path), quiet=False)

def load_data(path: Union[Path, str] = DEFAULT_DATA_PATH) -> pd.DataFrame:
    path = Path(path)

    if not path.exists():
        print("CSV not found locally. Downloading from Google Drive...")
        _download_csv(path)

 df = pd.read_csv(path, low_memory=False, nrows=300_000)

    # Rename
    rename_map = {old: new for old, new in RENAMES.items() if old in df.columns}
    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    # If dataset has CRASH DATE/TIME, derive YEAR/MONTH/HOUR (needed by your dashboard)
    if "CRASH DATE" in df.columns and COL_YEAR not in df.columns:
        dt = pd.to_datetime(df["CRASH DATE"], errors="coerce")
        df[COL_YEAR] = dt.dt.year
        df[COL_MONTH] = dt.dt.month

    if "CRASH TIME" in df.columns and COL_HOUR not in df.columns:
        t = pd.to_datetime(df["CRASH TIME"], errors="coerce")
        df[COL_HOUR] = t.dt.hour

    # Ensure numeric
    for col in [COL_YEAR, COL_MONTH, COL_HOUR]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Clean strings
    for col in [COL_BOROUGH, COL_PERSON_INJURY, COL_PERSON_TYPE, COL_VEHICLE_TYPE, COL_FACTOR]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    print("DATAFRAME SHAPE:", df.shape)
    print("HAS BOROUGH?", COL_BOROUGH in df.columns, "HAS YEAR?", COL_YEAR in df.columns)

    return df
