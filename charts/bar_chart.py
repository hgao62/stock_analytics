import pandas as pd

import plotly.express as px
from sqlitedb.read import read_data_from_sqlite
from sqlitedb.models import TickerInfo, SP500Holdings

def get_sp500_data():
    sp500_data = read_data_from_sqlite(SP500Holdings)
    ticker_info = read_data_from_sqlite(TickerInfo)
    ticker_info = ticker_info[ticker_info['Ticker'].isin(sp500_data['Ticker'])]
   
    return ticker_info

def clean_data(data):
    data = data[(data['Sector']!='N/A') & (data['Industry']!='N/A')]
    data = data[data['PERatio'].notnull()]
    return data

def prepare_data():
    data = get_sp500_data()
    data = clean_data(data)
    return data
# data = pd.read_csv(r'C:\development\repo\stock_analytics\charts\sp500_sample_data.csv')

def create_bar_chart(data):
    avg_pe_sector = data.groupby('Sector')['PERatio'].mean().reset_index()
    avg_pe_sector = avg_pe_sector.sort_values('PERatio', ascending=False)
    avg_pe_sector = avg_pe_sector.round(1)
    fig = px.bar(avg_pe_sector, x='Sector', y='PERatio',
                 title='Average PE Ratio by Sector',
                 labels={'PERatio': 'Average PE Ratio', 'Sector': 'Sector'},
                 text='PERatio',
                 color='Sector')  # Use 'Sector' to set different colors for each bar

    fig.update_layout(xaxis_title="Sector", yaxis_title="Average PE Ratio")
    fig.show()


if __name__ == '__main__':
    # data = prepare_data()
    # data.to_csv('./data/sp500_pe_data.csv', index=False)
    data = pd.read_csv('./data/sp500_pe_data.csv')
    create_bar_chart(data)