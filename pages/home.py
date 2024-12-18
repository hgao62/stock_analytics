import dash
from dash import html

dash.register_page(__name__, name="Home", path="/", order=1)

layout = html.Div([
    html.H1("Welcome to the Stock Dashboard"),
    html.P("Use the screener to find stocks and set alerts.")
])
