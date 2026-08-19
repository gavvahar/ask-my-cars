def apply_filters(df, makes=None, year_min=None, year_max=None, fuel_types=None):
    if makes is not None:
        df = df[df["make"].isin(makes)]
    if year_min is not None:
        df = df[df["year"] >= year_min]
    if year_max is not None:
        df = df[df["year"] <= year_max]
    if fuel_types is not None:
        df = df[df["engine_fuel_type"].isin(fuel_types)]
    return df


def get_filter_options(df):
    return {
        "makes": sorted(df["make"].unique()),
        "fuel_types": sorted(df["engine_fuel_type"].unique()),
        "year_min": int(df["year"].min()),
        "year_max": int(df["year"].max()),
    }


def parse_list_param(raw):
    if raw is None:
        return None
    if raw == "":
        return []
    return raw.split(",")
