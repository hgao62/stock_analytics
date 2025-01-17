

import pandas as pd

import plotly.express as px
data = pd.read_csv(r'C:\development\repo\stock_analytics\charts\sp500_sample_data.csv')
avg_pe_heatmap = data.groupby(['Sector', 'Industry'])['PE_Ratio'].mean().reset_index()
fig = px.density_heatmap(avg_pe_heatmap, x='Sector', y='Industry', z='PE_Ratio',
                         color_continuous_scale='Viridis',
                         title='Heatmap of Average PE Ratios by Sector and Industry')
fig.update_layout(xaxis_title="Sector", yaxis_title="Industry", coloraxis_colorbar_title="PE Ratio")
fig.show()
