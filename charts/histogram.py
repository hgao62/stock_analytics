import pandas as pd

import plotly.express as px
data = pd.read_csv(r'C:\development\repo\stock_analytics\charts\sp500_sample_data.csv')

fig = px.histogram(data, x='PE_Ratio', nbins=30,
                   title='Distribution of PE Ratios',
                   labels={'PE_Ratio': 'PE Ratio'})
fig.update_layout(xaxis_title="PE Ratio", yaxis_title="Frequency")
fig.show()
