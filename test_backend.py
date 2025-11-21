from project.utils.load_data import load_data
from project.utils.filters import apply_all_filters

df = load_data()
print("Loaded rows:", len(df))

df2 = apply_all_filters(df, year=2022, borough="Brooklyn")
print(df2.head())
print("Filtered rows:", len(df2))
