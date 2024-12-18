import dash
from dash import html, Output, Input, callback, State
from components.filters import stock_filters

dash.register_page(__name__, name="Stock Screener", path="/screener", order=2)

layout = html.Div([
    html.H2("Stock Screener"),
    stock_filters(),  # Reusable filter component
    html.Div(id='screener-results')  # Results display section
])

# Example callback for filter button
@callback(
    Output('screener-results', 'children'),
    Input('filter-button', 'n_clicks'),
    State('percentage-increase', 'value'),
    prevent_initial_call=True
)
def update_results(n_clicks, threshold):
    if not threshold:
        return "Please enter a valid percentage."
    return f"Showing stocks with yearly increase above {threshold}%."

