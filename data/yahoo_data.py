import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import smtplib
from email.message import EmailMessage
import argparse

import pandas as pd
from pandas import ExcelWriter
import logging  # Import the logging module
from dotenv import load_dotenv
from typing import Optional

#load environment variable
load_dotenv()
# Email configuration
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')  # Your email address
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # Your email password or app-specific password 

# Ensure the 'logs' directory exists
os.makedirs('logs', exist_ok=True)

# Set up logging configuration
logging.basicConfig(
    filemode='a',
    filename='logs/yahoo_data.log',  # Log file path
    level=logging.INFO,               # Log level
    format='%(asctime)s - %(levelname)s- %(filename)s:%(lineno)s  - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S'       # Date format
)

logging.info("Environment variables loaded.")
logging.info(f"Email address: {EMAIL_ADDRESS}. Email password: {EMAIL_PASSWORD}")

TODAY = datetime.now()
REPORT_DATE = TODAY.strftime("%Y%m%d")
def fetch_sp500_tickers() -> list:
    logging.info("Fetching S&P 500 tickers.")
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
    try:
        df = stock.history(period=period)
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {e}")
        raise
    df.index = pd.to_datetime(df.index, utc=True)  # Set utc=True
    return df

def get_neighbour_days(start_date)->list[datetime]:
    logging.debug(f"Getting neighbour days for start_date {start_date}.")
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
            logging.error(f"Error calculating start_date for {ticker} during {period}: {e}")
            print(f"Error calculating start_date for {ticker} during {period}: {e}")
            returns[f"{period}_return"] = 0
            continue  # Skip to the next period
        
        # Convert start_date to pandas Timestamp and normalize
        start_date_normalized = pd.Timestamp(start_date).normalize()
        # Normalize dates to ignore timezone and other attributes
        df.index = df.index.normalize()
        
        if start_date_normalized in df.index:
            try:
                returns[f"{period}_return"] = round((df['Close'].iloc[-1] / df.loc[start_date_normalized, 'Close'] - 1), 4)
            except Exception as e:
                logging.error(f"Error calculating return for {ticker} during {period}: {e}")
                print(f"Error calculating return for {ticker} during {period}: {e}")
                returns[f"{period}_return"] = 0
        else:
            # If start date is not in the data, calculate the return using the closest available date
            neighbour_days = get_neighbour_days(start_date_normalized)
            for day in neighbour_days:
                if day in df.index:
                    try:
                        returns[f"{period}_return"] = round((df['Close'].iloc[-1] / df.loc[day, 'Close'] - 1), 4)
                        break
                    except Exception as e:
                        logging.error(f"Error calculating return for {ticker} on {day} during {period}: {e}")
                        print(f"Error calculating return for {ticker} on {day} during {period}: {e}")
                        continue
            else:
                returns[f"{period}_return"] = 0
    return returns

def screen_top_gainers(tickers: list, lookback_periods: list) -> pd.DataFrame:
    logging.info("Screening top gainers.")
    """
    Screen top gainers for a list of tickers over specified lookback periods,
    including S&P 500 returns for each period.
    
    Parameters:
        tickers (list): List of stock tickers.
        lookback_periods (list): List of periods for which to calculate returns.
    
    Returns:
        pd.DataFrame: DataFrame with returns for each ticker and time period,
                      including S&P 500 returns.
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

    # Fetch S&P 500 returns
    sp500_df = fetch_stock_data('^GSPC', longest_period)
    sp500_returns = calculate_returns(sp500_df, lookback_periods, period_days, 'S&P500')
    
    for ticker in tickers:
        try:
            df = fetch_stock_data(ticker, longest_period)
            df.to_csv(f"data/{ticker}.csv")
            returns = calculate_returns(df, lookback_periods,period_days, ticker)
            # Add S&P 500 returns to each ticker's returns
            for period in lookback_periods:
                returns[f"{period}_SP500_return"] = sp500_returns[f"{period}_return"]
            results.append(returns)
        except Exception as e:
            logging.error(f"Error fetching data for {ticker}: {e}")
            print(f"Error fetching data for {ticker}: {e}")
            continue

    # Convert results to a DataFrame
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(by=f"{lookback_periods[0]}_return", ascending=False)
    logging.info("Completed screening top gainers.")
    return result_df

def format_worksheet(workbook, worksheet, combined_df):
    logging.debug("Formatting worksheet.")
    """
    Format the worksheet with percentage format and conditional formatting.
    
    Parameters:
        workbook: The workbook object.
        worksheet: The worksheet object.
        combined_df: The combined DataFrame.
    """
    for idx, col in enumerate(combined_df.columns):
        if (col.endswith('_return')):
            worksheet.set_column(idx, idx, None, workbook.add_format({'num_format': '0.00%'}))
            # Apply conditional formatting with explicit min, mid, and max types
            worksheet.conditional_format(1, idx, len(combined_df), idx, {
                'type': '3_color_scale',
                'min_type': 'num',
                'min_value': combined_df[col].min(),
                'mid_type': 'num',
                'mid_value': 0,
                'max_type': 'num',
                'max_value': combined_df[col].max(),
                'min_color': "#FF0000",  # Red for negative returns
                'mid_color': "#FFFFFF",  # White for zero return
                'max_color': "#00FF00",  # Green for positive returns
            })

def generate_report(df: pd.DataFrame, lookback_periods: list, increase_thresholds: list, decrease_thresholds: list) -> None:
    logging.info("Generating report.")
    """
    Generate a report showing the increase and decrease for each threshold for all lookback periods.
    
    Parameters:
        df (pd.DataFrame): DataFrame with returns for each ticker and time period.
        lookback_periods (list): List of periods for which to calculate returns.
        increase_thresholds (list): List of increase thresholds.
        decrease_thresholds (list): List of decrease thresholds.
    """
    report_filename = f'reports/stock_analysis_report_{REPORT_DATE}.xlsx'
    with pd.ExcelWriter(report_filename, engine='xlsxwriter') as writer:


        for period in lookback_periods:
            period_data = []

            for i, threshold in enumerate(increase_thresholds):
                if i < len(increase_thresholds) - 1:
                    next_threshold = increase_thresholds[i + 1]
                    increase_df = df[(df[f"{period}_return"] > threshold) & (df[f"{period}_return"] <= next_threshold)]
                else:
                    increase_df = df[df[f"{period}_return"] > threshold]
                
                if not increase_df.empty:
                    increase_df = increase_df[['Ticker', f"{period}_return",f"{period}_SP500_return"]]
                    increase_df['Threshold'] = f"{threshold * 100}% < Increase <= {next_threshold * 100}%" if i < len(increase_thresholds) - 1 else f"Increase > {threshold * 100}%"
                    period_data.append(increase_df)

            for i, threshold in enumerate(decrease_thresholds):
                if i < len(decrease_thresholds) - 1:
                    next_threshold = decrease_thresholds[i + 1]
                    decrease_df = df[(df[f"{period}_return"] < -threshold) & (df[f"{period}_return"] >= -next_threshold)]
                else:
                    decrease_df = df[df[f"{period}_return"] < -threshold]
                
                if not decrease_df.empty:
                    decrease_df = decrease_df[['Ticker', f"{period}_return",f"{period}_SP500_return"]]
                    decrease_df['Threshold'] = f"{-next_threshold * 100}% <= Decrease < {-threshold * 100}%" if i < len(decrease_thresholds) - 1 else f"Decrease < {-threshold * 100}%"
                    period_data.append(decrease_df)

            if period_data:
                combined_df = pd.concat(period_data)
                combined_df = combined_df.sort_values(by=f"{period}_return", ascending=False)
                combined_df.to_excel(writer, sheet_name=period, index=False)

                # Format the worksheet
                workbook = writer.book
                worksheet = writer.sheets[period]
                try:
                    format_worksheet(workbook, worksheet, combined_df)
                except Exception as e:
                    logging.error(f"Error formatting worksheet for period {period}: {e}")

    logging.info(f"Report generated successfully: {report_filename}")

def get_top_gainers(tickers: list, lookback_periods: list, mode: str) -> pd.DataFrame:
    logging.info(f"Running get_top_gainers in '{mode}' mode.")
    """
    Screen top gainers for a list of tickers over specified lookback periods,
    including S&P 500 returns for each period.

    Parameters:
        tickers (list): List of stock tickers.
        lookback_periods (list): List of periods for which to calculate returns.
        mode (str): 'initial', 'daily', or 'rerun'

    Returns:
        pd.DataFrame: DataFrame with returns for each ticker and time period,
                      including S&P 500 returns.
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

    # Fetch S&P 500 returns
    if mode == 'initial':
        sp500_df = fetch_stock_data('^GSPC', longest_period)
        sp500_df.to_csv('data/SP500.csv')
    elif mode == 'daily':
        if os.path.exists('data/SP500.csv'):
            sp500_df = pd.read_csv('data/SP500.csv', index_col=0, parse_dates=True)
            # Ensure the index is datetime with UTC
            sp500_df.index = pd.to_datetime(sp500_df.index, utc=True)
            new_sp500_data = fetch_stock_data('^GSPC', '1d')
            if not new_sp500_data.empty:
                sp500_df = pd.concat([sp500_df, new_sp500_data])
                sp500_df.to_csv('data/SP500.csv')
        else:
            # If SP500.csv does not exist, perform initial load
            sp500_df = fetch_stock_data('^GSPC', longest_period)
            sp500_df.to_csv('data/SP500.csv')
    elif mode == 'rerun':
        if os.path.exists('data/SP500.csv'):
            sp500_df = pd.read_csv('data/SP500.csv', index_col=0, parse_dates=True)
            # Ensure the index is datetime with UTC
            sp500_df.index = pd.to_datetime(sp500_df.index, utc=True)
            today_str = TODAY.strftime('%Y-%m-%d')
            if today_str in sp500_df.index.strftime('%Y-%m-%d'):
                # Update the row where the index equals TODAY
                new_sp500_data = fetch_stock_data('^GSPC', '1d')
                if not new_sp500_data.empty:
                    sp500_df.loc[today_str] = new_sp500_data.loc[today_str]
                    sp500_df.to_csv('data/SP500.csv')
        else:
            print("SP500.csv not found. Please run in 'initial' or 'daily' mode first.")
            return pd.DataFrame()
    
    sp500_returns = calculate_returns(sp500_df, lookback_periods, period_days, 'S&P500')
    
    for ticker in tickers:
        try:
            if mode == 'initial':
                df = fetch_stock_data(ticker, longest_period)
                df.to_csv(f"data/{ticker}.csv")
            elif mode == 'daily':
                file_path = f"data/{ticker}.csv"
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                    # Ensure the index is datetime with UTC
                    df.index = pd.to_datetime(df.index, utc=True)
                    new_data = fetch_stock_data(ticker, '1d')
                    if not new_data.empty:
                        df = pd.concat([df, new_data])
                        df.to_csv(file_path)
                else:
                    # If ticker CSV does not exist, perform initial load
                    df = fetch_stock_data(ticker, longest_period)
                    df.to_csv(f"data/{ticker}.csv")
            elif mode == 'rerun':
                file_path = f"data/{ticker}.csv"
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                    # Ensure the index is datetime with UTC
                    df.index = pd.to_datetime(df.index, utc=True)
                    today_str = TODAY.strftime('%Y-%m-%d')
                    if today_str in df.index.strftime('%Y-%m-%d'):
                        # Update the row where the index equals TODAY
                        new_data = fetch_stock_data(ticker, '1d')
                        if not new_data.empty:
                            df.loc[today_str] = new_data.loc[today_str]
                            df.to_csv(file_path)
                else:
                    print(f"{file_path} not found. Please run in 'initial' or 'daily' mode first.")
                    continue

            # Simplify by removing redundant if-else
            returns = calculate_returns(df, lookback_periods, period_days, ticker)
            
            # Add S&P 500 returns to each ticker's returns
            for period in lookback_periods:
                returns[f"{period}_SP500_return"] = sp500_returns.get(f"{period}_return", 0)
            results.append(returns)
        except Exception as e:
            logging.error(f"Error fetching data for {ticker}: {e}")
            print(f"Error fetching data for {ticker}: {e}")
            continue

    # Convert results to a DataFrame
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(by=f"{lookback_periods[0]}_return", ascending=False)
    logging.info("Completed getting top gainers.")
    return result_df



def send_email( recipient: str, subject: str, body: str,report_path: Optional[str]=None,) -> None:
    logging.info(f"Sending email to {recipient} with subject '{subject}'.")
    """
    Send an email with the report attached.

    Parameters:
        report_path (str): Path to the report file.
        recipient (str): Recipient's email address.
        subject (str): Subject of the email.
        body (str): Body of the email.
    """
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient
    msg.set_content(body)

    if report_path:
        # Attach the report
        with open(report_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(report_path)
        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

    # Send the email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def main():
    logging.info("Script started.")
    parser = argparse.ArgumentParser(description='Stock Analytics Script')
    parser.add_argument('--mode', choices=['initial', 'daily', 'rerun'], required=True, help='Mode to run the process: initial, daily, or rerun')
    parser.add_argument('--recipient', type=str, required=True, help='Recipient email address')
    args = parser.parse_args()
    
    logging.info(f"Parameters received - Mode: {args.mode}, Recipient: {args.recipient}")
    
    increase_thresholds = [0.1, 0.2, 0.3, 0.4, 0.5,1,2]
    decrease_thresholds = [0.1, 0.2, 0.3, 0.4, 0.5,1,2]
    lookback_periods = ['1d','5d','14d','21d','1mo','2mo','3mo','4mo','5mo','6mo','1y']
    
  
    sp500_tickers = fetch_sp500_tickers()
    logging.info(f"Fetched {len(sp500_tickers)} S&P 500 tickers.")

    top_gainers = get_top_gainers(sp500_tickers, lookback_periods, mode=args.mode)
    
    if top_gainers.empty and args.mode == 'rerun':
        logging.warning("No data available to generate the report in 'rerun' mode.")
        print("No data available to generate the report in 'rerun' mode.")
        return

    generate_report(top_gainers, lookback_periods, increase_thresholds, decrease_thresholds)
    report_path = f'reports/stock_analysis_report_{REPORT_DATE}.xlsx'
    # Uncomment the following lines to enable email sending
    send_email(
        
        recipient=args.recipient,
        subject=f'Stock Analysis Report {REPORT_DATE}',
        body='Please find the attached stock analysis report.',
        report_path=report_path,
    )
    logging.info("Script completed successfully.")


# TODO 1. add sector to the report
# TODO 2. add company name to the report
if __name__ == "__main__":
    
    alert_emails = os.getenv('ALERT_EMAILS').split(',')
    # send_email(alert_emails, 'Stock Analysis Report - Started', 'The stock analysis script has started.')
    try:
        main()
    except Exception as e:
        send_email(
            recipient=alert_emails,
            subject='Stock Analysis Report - Error',
            body=f'An error occurred while running the stock analysis script. {str(e)}',
        )
        
