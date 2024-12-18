import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.navbar import create_navbar

# Initialize Dash app
app = dash.Dash(
    __name__,
    use_pages=True,  # Enable multi-page support
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
server = app.server

# App layout with navigation bar and page content
app.layout = html.Div([
    dcc.Location(id='url'),  # Location component
    create_navbar(),         # Top navbar
    dash.page_container      # Dynamically loads the correct page
])

if __name__ == "__main__":
    app.run_server(debug=True)
