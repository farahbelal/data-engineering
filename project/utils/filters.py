def filter_year(df, year):
    if not year or year == "All":
        return df
    return df[df["year"] == int(year)]

def filter_borough(df, borough):
    if not borough or borough == "All":
        return df
    return df[df["BOROUGH"] == borough]

def apply_all_filters(df, year=None, borough=None):
    df = filter_year(df, year)
    df = filter_borough(df, borough)
    return df
