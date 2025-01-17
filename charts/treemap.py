import pandas as pd

import plotly.express as px
data = pd.read_csv(r'C:\development\repo\stock_analytics\charts\sp500_sample_data.csv')

fig = px.treemap(data, path=['Sector', 'Industry', 'Company'], values='Market_Cap',
                 color='PE_Ratio', color_continuous_scale='RdBu',
                 title='Treemap of PE Ratios and Market Capitalization')
fig.update_layout(coloraxis_colorbar_title="PE Ratio")
fig.show()
