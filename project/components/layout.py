from dash import html, dcc
import dash_bootstrap_components as dbc

def create_layout(df):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("NYC Collision Explorer"),

                html.Label("Borough"),
                dcc.Dropdown(
                    id="borough-dropdown",
                    placeholder="Select Borough"
                ),

                html.Label("Year"),
                dcc.Dropdown(
                    id="year-dropdown",
                    placeholder="Select Year"
                ),

                html.Label("Vehicle Type"),
                dcc.Dropdown(
                    id="vehicle-dropdown",
                    placeholder="Select Vehicle Type"
                ),

                html.Label("Contributing Factor"),
                dcc.Dropdown(
                    id="factor-dropdown",
                    placeholder="Select Factor"
                ),

                html.Label("Search"),
                dcc.Input(
                    id="search-input",
                    type="text",
                    placeholder='e.g. "Brooklyn 2022 pedestrian crashes"',
                    style={"width": "100%"}
                ),

                html.Br(), html.Br(),
                dbc.Button("Generate Report", id="generate-button", color="primary")
            ], width=3),

            dbc.Col([
                html.Div(id="bar-chart"),
                html.Div(id="line-chart"),
                html.Div(id="map-chart"),
                html.Div(id="heatmap-chart"),
                html.Div(id="pie-chart"),
            ], width=9)
        ])
    ], fluid=True)
