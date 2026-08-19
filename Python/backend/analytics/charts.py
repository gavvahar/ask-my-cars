import json, plotly.express as px


def build_hp_mpg_chart(filtered_df):
    fig = px.scatter(
        filtered_df,
        x="engine_hp",
        y="highway_mpg",
        color="engine_fuel_type",
        hover_data=["make", "model", "year"],
        height=600,
        render_mode="svg",
        labels={"engine_hp": "Engine HP", "highway_mpg": "Highway MPG", "engine_fuel_type": "Fuel Type"},
    )
    return json.loads(fig.to_json())


def build_mpg_by_style_chart(filtered_df):
    style_mpg = filtered_df.groupby("vehicle_style")["highway_mpg"].mean().sort_values(ascending=False).reset_index()
    fig = px.bar(
        style_mpg,
        x="vehicle_style",
        y="highway_mpg",
        labels={"vehicle_style": "Vehicle Style", "highway_mpg": "Avg Highway MPG"},
    )
    return json.loads(fig.to_json())


def build_hp_msrp_chart(filtered_df):
    fig = px.scatter(
        filtered_df,
        x="engine_hp",
        y="msrp",
        color="engine_fuel_type",
        log_y=True,
        render_mode="svg",
        labels={"engine_hp": "Engine HP", "msrp": "MSRP", "engine_fuel_type": "Fuel Type"},
    )
    return json.loads(fig.to_json())


def build_year_trend_charts(filtered_df):
    year_trend = filtered_df.groupby("year")[["engine_hp", "highway_mpg"]].mean().reset_index()
    hp_fig = px.line(
        year_trend,
        x="year",
        y="engine_hp",
        markers=True,
        labels={"year": "Year", "engine_hp": "Avg Engine HP"},
    )
    mpg_fig = px.line(
        year_trend,
        x="year",
        y="highway_mpg",
        markers=True,
        labels={"year": "Year", "highway_mpg": "Avg Highway MPG"},
    )
    return {
        "hp_trend": json.loads(hp_fig.to_json()),
        "mpg_trend": json.loads(mpg_fig.to_json()),
    }
