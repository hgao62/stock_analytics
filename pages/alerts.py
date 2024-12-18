import dash
from dash import html

dash.register_page(__name__, name="Alerts", path="/alerts", order=3)

layout = html.Div([
    html.H2("Stock Alerts"),
    html.P("Here are the stocks meeting your alert conditions."),
    html.Div(id='alerts-content', children="No alerts configured yet.")
])
