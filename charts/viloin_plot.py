import pandas as pd

import plotly.express as px
data = pd.read_csv(r'C:\development\repo\stock_analytics\charts\sp500_sample_data.csv')

fig = px.violin(data, x='Sector', y='PE_Ratio', box=True, points='all',
                title='PE Ratios by Sector',
                labels={'PE_Ratio': 'PE Ratio', 'Sector': 'Sector'})
fig.update_layout(xaxis_title="Sector", yaxis_title="PE Ratio")
fig.show()
