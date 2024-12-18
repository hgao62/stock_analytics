import dash_table

def stock_table(dataframe):
    return dash_table.DataTable(
        id='stock-table',
        columns=[{"name": i, "id": i} for i in dataframe.columns],
        data=dataframe.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
    )
