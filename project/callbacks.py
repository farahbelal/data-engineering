from dash import Input, Output, State
import plotly.express as px
import pandas as pd

from utils.filters import parse_search_query, apply_filters
from utils.load_data import (
    COL_BOROUGH,
    COL_YEAR,
    COL_MONTH,
    COL_HOUR,
    COL_LAT,
    COL_LON,
    COL_COLLISION_ID,
    COL_PERSON_INJURY,
    COL_PERSON_TYPE,
)


def register_callbacks(app, df):

    # Preload possible labels for search parser
    person_types = df[COL_PERSON_TYPE].dropna().unique().tolist() \
        if COL_PERSON_TYPE in df.columns else []

    injury_types = df[COL_PERSON_INJURY].dropna().unique().tolist() \
        if COL_PERSON_INJURY in df.columns else []

    # ----------------------------------------------------------
    # CALLBACK 1 — SEARCH BAR → AUTO-FILL FILTERS
    # ----------------------------------------------------------
    @app.callback(
        [
            Output("borough-dropdown", "value"),
            Output("year-dropdown", "value"),
            Output("person-type-dropdown", "value"),
            Output("injury-dropdown", "value"),
            Output("filter-summary", "children"),
        ],
        Input("generate-button", "n_clicks"),
        [
            State("search-input", "value"),
            State("borough-dropdown", "value"),
            State("year-dropdown", "value"),
            State("person-type-dropdown", "value"),
            State("injury-dropdown", "value"),
        ],
    )
    def update_filters(n_clicks, query, b, y, p, inj):
        # Before clicking — leave everything unchanged
        if n_clicks == 0:
            return b, y, p, inj, "Adjust filters or type a search."

        parsed = parse_search_query(query, person_types, injury_types)

        # Auto-fill only empty filters
        b2 = b or parsed.get("borough")
        y2 = y or parsed.get("year")
        p2 = p or parsed.get("person_type")
        inj2 = inj or parsed.get("injury")

        summary_parts = []
        if b2: summary_parts.append(f"Borough: {b2}")
        if y2: summary_parts.append(f"Year: {y2}")
        if p2: summary_parts.append(f"Person: {p2}")
        if inj2: summary_parts.append(f"Injury: {inj2}")

        summary = " | ".join(summary_parts) if summary_parts else "No filters applied."

        return b2, y2, p2, inj2, summary

    # ----------------------------------------------------------
    # CALLBACK 2 — GENERATE REPORT → UPDATE ALL CHARTS
    # ----------------------------------------------------------
    @app.callback(
        [
            Output("summary-total-crashes", "children"),
            Output("summary-total-persons", "children"),
            Output("summary-total-injuries", "children"),
            Output("summary-total-fatalities", "children"),
            Output("time-series-graph", "figure"),
            Output("borough-bar-graph", "figure"),
            Output("injury-pie-graph", "figure"),
            Output("location-scatter-graph", "figure"),
            Output("heatmap-graph", "figure"),
        ],
        Input("generate-button", "n_clicks"),
        [
            State("borough-dropdown", "value"),
            State("year-dropdown", "value"),
            State("vehicle-dropdown", "value"),
            State("factor-dropdown", "value"),
            State("injury-dropdown", "value"),
            State("person-type-dropdown", "value"),
        ],
    )
    def generate_report(n_clicks, borough, year, vehicle, factor, injury, person_type):

        # Before clicking: show entire data
        if n_clicks == 0:
            data = df.copy()
        else:
            data = apply_filters(
                df=df,
                borough=borough,
                year=year,
                vehicle_type=vehicle,
                factor=factor,
                injury=injury,
                person_type=person_type,
            )

        # =====================
        # KPI CARDS
        # =====================

        # 1) Total crashes
        if COL_COLLISION_ID in data.columns:
            total_crashes = data[COL_COLLISION_ID].nunique()
        else:
            total_crashes = len(data)

        # 2) Total persons
        total_persons = len(data)

        # 3–4) Injuries & fatalities
        injuries = 0
        fatalities = 0
        if COL_PERSON_INJURY in data.columns:
            injury_col = data[COL_PERSON_INJURY].astype(str).str.lower()
            injuries = injury_col.str.contains("injur").sum()
            fatalities = injury_col.str.contains("fatal|kill").sum()

        # =====================
        # TIME SERIES GRAPH
        # =====================
        if COL_MONTH in data.columns:
            group = data.groupby([COL_YEAR, COL_MONTH]).size().reset_index(name="count")
            group["YM"] = group[COL_YEAR].astype(str) + "-" + group[COL_MONTH].astype(str)
            fig_time = px.line(group, x="YM", y="count", markers=True)
        else:
            group = data.groupby([COL_YEAR]).size().reset_index(name="count")
            fig_time = px.line(group, x=COL_YEAR, y="count", markers=True)

        # =====================
        # BOROUGH BAR CHART
        # =====================
        if COL_BOROUGH in data.columns:
            boro_data = data[COL_BOROUGH].value_counts().reset_index()
            boro_data.columns = [COL_BOROUGH, "count"]
            fig_boro = px.bar(boro_data, x=COL_BOROUGH, y="count")
        else:
            fig_boro = px.bar(title="BOROUGH column missing")

        # =====================
        # INJURY PIE CHART
        # =====================
        if COL_PERSON_INJURY in data.columns:
            inj_data = data[COL_PERSON_INJURY].value_counts().reset_index()
            inj_data.columns = [COL_PERSON_INJURY, "count"]
            fig_injury = px.pie(inj_data, names=COL_PERSON_INJURY, values="count")
        else:
            fig_injury = px.pie(title="PERSON_INJURY missing")

        # =====================
        # LOCATION MAP
        # =====================
        if COL_LAT in data.columns and COL_LON in data.columns:
            loc = data.dropna(subset=[COL_LAT, COL_LON])
            if len(loc) > 3000:  # prevent lag
                loc = loc.sample(3000)
            fig_loc = px.scatter_geo(loc, lat=COL_LAT, lon=COL_LON)
        else:
            fig_loc = px.scatter(title="Latitude/Longitude missing")

        # =====================
        # HEATMAP (HOUR × BOROUGH)
        # =====================
        if COL_HOUR in data.columns:
            hm = data.groupby([COL_BOROUGH, COL_HOUR]).size().reset_index(name="count")
            fig_heat = px.density_heatmap(
                hm,
                x=COL_HOUR,
                y=COL_BOROUGH,
                z="count",
                nbinsx=24,
            )
        else:
            fig_heat = px.imshow([[0]], title="Hour data missing")

        # Return KPIs & charts
        return (
            f"{total_crashes:,}",
            f"{total_persons:,}",
            f"{injuries:,}",
            f"{fatalities:,}",
            fig_time,
            fig_boro,
            fig_injury,
            fig_loc,
            fig_heat,
        )