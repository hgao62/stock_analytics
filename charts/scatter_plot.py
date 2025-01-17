
import pandas as pd

import plotly.express as px
data = pd.read_csv(r'C:\development\repo\stock_analytics\charts\sp500_sample_data.csv')

fig = px.scatter(data, x='Sector', y='PE_Ratio', color='Industry',
                 hover_data=['Company', 'PE_Ratio'],
                 title='PE Ratios by Sector and Industry')
fig.update_layout(xaxis_title="Sector", yaxis_title="PE Ratio")
fig.show()
