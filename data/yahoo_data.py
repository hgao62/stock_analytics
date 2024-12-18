import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


import pandas as pd

def fetch_sp500_tickers() -> list:
    """
    Fetch the list of S&P 500 tickers by scraping Wikipedia.
    Returns:
        list: List of ticker symbols.
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    try:
        table = pd.read_csv("sp500.csv")
    except Exception as e:
        table = pd.read_html(url, match="Symbol")[0]  # Automatically parses HTML tables
    tickers = table["Symbol"].tolist()
    return tickers


def fetch_stock_data(ticker: str, period: str) -> pd.DataFrame:
    """
    Fetch historical stock data for a specific ticker from Yahoo Finance.
    
    Parameters:
        ticker (str): Stock ticker symbol.
        period (str): Period string for Yahoo Finance API (e.g., '1mo', '3mo', '1y').
    
    Returns:
        pd.DataFrame: DataFrame with historical stock data.
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    df.index = pd.to_datetime(df.index)
    return df

def get_neighbour_days(start_date)->list[datetime]:
    """
    Get the previous and next day of the start date
    """
    res = []
    for i in range(1,4):
        adjust_start_date_backwards = start_date - timedelta(days= i)
        adjust_start_date_forwards = start_date + timedelta(days= i)
        res.append(adjust_start_date_backwards)
        res.append(adjust_start_date_forwards)
    return res

def calculate_returns(df: pd.DataFrame, periods: list, period_days, ticker: str) -> dict:
    """
    Calculate returns for specified periods.
    
    Parameters:
        df (pd.DataFrame): DataFrame with an 'Adj Close' column.
        periods (list): List of periods for which to calculate returns.
        period_days (dict): Dictionary mapping periods to days.
        ticker (str): Stock ticker symbol.
    
    Returns:
        dict: Dictionary of returns for each period.
    """
    returns = {"Ticker": ticker}
    for period in periods:
        try:
            start_date = df.index[-1] - timedelta(days=period_days[period])
        except Exception as e:
            print(e)
        
        # Normalize dates to ignore timezone and other attributes
        start_date_normalized = start_date.normalize()
        df.index = df.index.normalize()
        
        if start_date_normalized in df.index:
            returns[f"{period}_return"] = round((df['Close'].iloc[-1] / df.loc[start_date_normalized, 'Close'] - 1), 4)
        else:
            # If start date is not in the data, calculate the return using the closest available date
            neighbour_days = get_neighbour_days(start_date_normalized)
            for day in neighbour_days:
                if day in df.index:
                    returns[f"{period}_return"] = round((df['Close'].iloc[-1] / df.loc[day, 'Close'] - 1), 4)
                    break
            else:
                returns[f"{period}_return"] = 0
    return returns

def screen_top_gainers(tickers: list, lookback_periods: list) -> pd.DataFrame:
    """
    Screen top gainers for a list of tickers over specified lookback periods.
    
    Parameters:
        tickers (list): List of stock tickers.
        lookback_periods (list): List of periods for which to calculate returns.
    
    Returns:
        pd.DataFrame: DataFrame with returns for each ticker and time period.
    """
    results = []
    
    # Convert periods to days for comparison
    period_days = {
        '1d':1,
        '5d':5,
        '14d':14,
        '21d':21,
        '1mo': 30,
        '2mo': 60,
        '3mo': 90,
        '4mo': 120,
        '5mo': 150,
        '6mo': 180,
        '1y': 365,
        # '2y': 730,
        # '5y': 1825
    }
    longest_period = max(lookback_periods, key=lambda x: period_days[x])

    for ticker in tickers:
        try:
            df = fetch_stock_data(ticker, longest_period)
            df.to_csv(f"data/{ticker}.csv")
            returns = calculate_returns(df, lookback_periods,period_days, ticker)
            results.append(returns)
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            continue

    # Convert results to a DataFrame
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(by=f"{lookback_periods[0]}_return", ascending=False)
    return result_df


def get_top_gainers():
    """
    Fetch and screen top gainers for S&P 500 stocks.
    """
    sp500_tickers = fetch_sp500_tickers()
    # sp500_tickers = ['GOOGL', 'AAPL', 'AMZN', 'MSFT', 'TSLA', 'NVDA', 'META']
    # sp500_tickers = ['GOOGL']
    # Define periods for Yahoo Finance API: this month (1mo), past 3 months (3mo), past 1 year (1y), past 5 years (5y)
    lookback_periods = ['1mo', '3mo', '1y',  '5y']
    lookback_periods = ['1d','5d','14d','21d','1mo','2mo','3mo','4mo','5mo','6mo','1y']
    top_gainers = screen_top_gainers(sp500_tickers, lookback_periods)
    return top_gainers


if __name__ == "__main__":
    # Run the top gainers function
    df_top_gainers = get_top_gainers()
    df_top_gainers.to_csv("data/top_gainers.csv", index=False)
    print(df_top_gainers.head())
