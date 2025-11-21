from dash import Dash
import dash_bootstrap_components as dbc

from utils.load_data import load_data
from components.layout import create_layout
import callbacks


# 1) Load the cleaned integrated dataset
df = load_data()

# 2) Create Dash App
app = Dash(
    _name_,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Needed for deployment platforms like Render
server = app.server

# 3) Set the layout
app.layout = create_layout(df)

# 4) Register all callbacks
callbacks.register_callbacks(app, df)

# 5) Run the server
if _name_ == "_main_":
    app.run_server(debug=True)