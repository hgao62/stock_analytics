import pandas as pd

import plotly.express as px
data = pd.read_csv(r'C:\development\repo\stock_analytics\charts\sp500_sample_data.csv')
fig = px.scatter(data, x='Market_Cap', y='PE_Ratio', size='Market_Cap', color='Sector',
                 hover_data=['Company', 'PE_Ratio', 'Market_Cap'],
                 title='PE Ratios vs. Market Cap')
fig.update_layout(xaxis_title="Market Capitalization", yaxis_title="PE Ratio")
fig.show()
