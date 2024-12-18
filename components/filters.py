import dash_core_components as dcc
import dash_html_components as html

def stock_filters():
    return html.Div([
        html.Label("Select Stock Exchange:"),
        dcc.Dropdown(
            id='stock-exchange-dropdown',
            options=[
                {'label': 'NASDAQ', 'value': 'NASDAQ'},
                {'label': 'NYSE', 'value': 'NYSE'}
            ],
            value='NASDAQ'
        ),
        html.Br(),
        html.Label("Percentage Increase (Yearly):"),
        dcc.Input(
            id='percentage-increase',
            type='number',
            placeholder="e.g., 30"
        ),
        html.Br(),
        html.Button("Search", id='filter-button')
    ])
