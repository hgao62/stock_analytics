
import pandas as pd

import plotly.express as px
data = pd.read_csv(r'C:\development\repo\stock_analytics\charts\sp500_sample_data.csv')

fig = px.sunburst(data, path=['Sector', 'Industry', 'Company'], values='PE_Ratio',
                  color='PE_Ratio', color_continuous_scale='RdBu',
                  title='Sunburst of PE Ratios by Sector and Industry')
fig.update_layout(coloraxis_colorbar_title="PE Ratio")
fig.show()
