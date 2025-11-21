# trigger backend commit


import pandas as pd
from functools import lru_cache

@lru_cache(maxsize=1)
def load_data(path="project/data/integrated_cleaned_final.csv"):
    df = pd.read_csv(path, low_memory=False)

    df["CRASH_DATETIME"] = pd.to_datetime(
        df["CRASH_DATE"].astype(str) + " " + df["CRASH_TIME"].astype(str),
        errors="coerce"
    )

    df["year"] = df["CRASH_DATETIME"].dt.year
    df["BOROUGH"] = df["BOROUGH"].fillna("Unknown").str.title()

    return df
