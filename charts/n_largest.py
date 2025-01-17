import pandas as pd

import plotly.express as px
data = pd.read_csv(r'C:\development\repo\stock_analytics\charts\sp500_sample_data.csv')


top_10 = data.nlargest(10, 'PE_Ratio')
fig = px.bar(top_10, x='Company', y='PE_Ratio', color='Sector',
             title='Top 10 Companies by PE Ratio',
             text='PE_Ratio')
fig.update_layout(xaxis_title="Company", yaxis_title="PE Ratio")
fig.show()
