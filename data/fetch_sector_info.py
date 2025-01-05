from yahoo_data import fetch_index_underlying
import pandas as pd
import yfinance as yf
from sqlitedb.write import write_data_to_sqlite
from sqlitedb.models import NASDAQHoldings
# sp500_tickers = fetch_index_underlying()
nasdaq_tickers = pd.read_csv('data/static_data/qqq_holdings.csv')['Ticker'].tolist()
output = []
for ticker in nasdaq_tickers:
    record = {}
    res = yf.Ticker(ticker)
    record['Ticker'] = ticker
    try:
        record['Sector'] = res.info['sector']
    except:
        record['Sector'] = 'N/A'
    try:
        record['Industry'] = res.info['industry']
    except:
        record['Industry'] = 'N/A'
        
    try:
        record['CompanyName'] = res.info['longName']
    except:
        record['CompanyName'] = 'N/A'
    output.append(record)
df = pd.DataFrame(output,index=False)
write_data_to_sqlite(NASDAQHoldings,df)
