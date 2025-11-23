from dash import Dash
import dash_bootstrap_components as dbc


from components.layout import create_layout
from utils.load_data import load_data
import callbacks


# 1) Load the cleaned integrated dataset
df = load_data()

# 2) Create Dash App
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Needed for deployment (Render, Heroku, etc.)
server = app.server

# 3) Set the layout
app.layout = create_layout(df)

# 4) Register all callbacks
callbacks.register_callbacks(app, df)

# 5) Run the server locally
if __name__ == "__main__":
    app.run(debug=True)
