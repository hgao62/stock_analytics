from yahoo_data import fetch_sp500_tickers
import pandas as pd
import yfinance as yf
sp500_tickers = fetch_sp500_tickers()
output = []
for ticker in sp500_tickers:
    record = {}
    res = yf.Ticker(ticker)
    record['ticker'] = ticker
    try:
        record['sector'] = res.info['sector']
    except:
        record['sector'] = 'N/A'
    try:
        record['industry'] = res.info['industry']
    except:
        record['industry'] = 'N/A'
        
    try:
        record['company_name'] = res.info['longName']
    except:
        record['company_name'] = 'N/A'
    output.append(record)
df = pd.DataFrame(output)
df.to_csv('data/sp500_stocks_sector_industry_info.csv')