
from sqlitedb.models import SP500Holdings, StocksPrice, NASDAQHoldings,TickerInfo
from data.yahoo_data import fetch_stock_data
from sqlitedb.write import write_data_to_sqlite
from data.utilities import read_tickers,get_all_tickers
import pandas as  pd
import yfinance as yf

def load_nasdaq_data(sp500_tickers):
    nasdaq_tickers = read_tickers(NASDAQHoldings)
    nasdaq_tickers = [
        ticker for ticker in nasdaq_tickers if ticker not in sp500_tickers
    ]
    for each_ticker in nasdaq_tickers:
        try:
            df = fetch_stock_data(each_ticker, "1y")
            df["IndexName"] = "nasdaq"
            df = df.rename(columns={"Stock Splits": "StockSplits"})
            write_data_to_sqlite(StocksPrice, df)
        except Exception as e:
            print(f"Error fetching data for {each_ticker}: {e}")
            continue



def load_sp500_data():
    sp500_tickers = read_tickers(SP500Holdings)
    for each_ticker in sp500_tickers:
        df = fetch_stock_data(each_ticker, "1y")
        df["IndexName"] = "sp500"
        write_data_to_sqlite(StocksPrice, df)


def initial_laod():
    load_sp500_data()
    sp500_tickers = read_tickers(SP500Holdings)
    load_nasdaq_data(sp500_tickers)


def populate_pe_ratio():
    sp500_tickers = get_all_tickers()
    dfs = []
    for each_ticker in sp500_tickers:
        record = {}
        ticker_obj =  yf.Ticker(each_ticker)
        try:
           
            pe = ticker_obj.info['trailingPE']
 
        except Exception as e:
            pe = pd.NA
            
        try:
            forward_pe = ticker_obj.info['forwardPE']
        except Exception as e:
            forward_pe = pd.NA
            
        try:
            record['Sector'] = ticker_obj.info['sector']
        except:
            record['Sector'] = 'N/A'
        
        try:
            record['Industry'] = ticker_obj.info['industry']
        except:
            record['Industry'] = 'N/A'
            
        try:
            record['CompanyName'] = ticker_obj.info['longName']
        except:
            record['CompanyName'] = 'N/A'
            
        try:
            record['MarketCap'] = ticker_obj.info['marketCap'] 
        except:
            record['MarketCap'] = pd.NA
        
        try:
            record['Dividend'] = ticker_obj.info['dividendYield']
        except:
            record['Dividend'] = pd.NA
        
        try:
            record['ROE'] = ticker_obj.info['returnOnEquity']   
        except: 
            record['ROE'] = pd.NA
            
        try:
            record['ROA'] = ticker_obj.info['returnOnAssets']
        except:
            record['ROA'] = pd.NA
            
        record['Ticker'] = each_ticker
        record['PERatio'] = pe
        record['ForwardPERatio'] = forward_pe
        dfs.append(record)
    df = pd.DataFrame(dfs)
    df['LastUpdated'] = pd.Timestamp.now().date()
    write_data_to_sqlite(TickerInfo, df)
if __name__ == "__main__":
    populate_pe_ratio()