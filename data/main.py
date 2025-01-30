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
from typing import Optional, List
from sqlitedb.read import read_data_from_sqlite
from sqlitedb.write import write_data_to_sqlite
from sqlitedb.models import (
    SP500Holdings,
    SP500StocksPrice,
    IndexPrice,
    WatchListTickers,
    NASDAQHoldings,
    StocksPrice,
    Users,
    BroadMarketETFList,
)
from data.broad_market_etfs_analysis import generate_broad_market_monitoring_report_html,generate_market_scanner_html_report
from sqlitedb.delete import truncate_table
from sqlitedb.update import upsert_data_in_sqlite
from data.watchlist import get_user_tickers
from data.utilities import send_email,format_worksheet,get_neighbour_days,fetch_stock_data,read_tickers,get_all_tickers
from data.report_generating import generate_html_report,generate_excel_report,generate_watch_list_report,generate_market_scanner_html_report
import traceback  
from extract_my_ib_return import load_positions

# Add this import
# load environment variable
load_dotenv()
# Email configuration

# Ensure the 'logs' directory exists
os.makedirs("logs", exist_ok=True)

# Set up logging configuration
logger = logging.getLogger('stock_analytics')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logs/yahoo_data.log')
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.info("Environment variables loaded.")

TODAY = datetime.now()
REPORT_DATE = TODAY.strftime("%Y-%m-%d")






def calculate_returns(
    df: pd.DataFrame, periods: list, period_days, ticker: str, report_date: pd.Timestamp
) -> dict:
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
            if period in ['1d', '3d', '5d']:
                # Use trading days for 1d, 3d, 5d periods
                start_date = report_date
                trading_days = 0
                while trading_days < period_days[period]:
                    start_date -= timedelta(days=1)
                    if start_date.weekday() < 5:  # Monday to Friday are trading days
                        trading_days += 1
                start_date = start_date.date()
            else:
                start_date = (report_date - timedelta(days=period_days[period])).date()
        except Exception as e:
            logger.error(
                f"Error calculating start_date for {ticker} during {period}: {e}"
            )
            print(f"Error calculating start_date for {ticker} during {period}: {e}")
            returns[f"{period}_return"] = 0
            continue  # Skip to the next period

        # Convert start_date to pandas Timestamp and normalize
        # start_date_normalized = pd.Timestamp(start_date).normalize().tz_localize('UTC')
        # Normalize dates to ignore timezone and other attributes
        report_date_data = df[df["Date"] == report_date.date()]["Close"]
        if report_date_data.empty:
            logger.error(f"No data found for {ticker} on {report_date.date()}")
            print(f"No data found for {ticker} on {report_date.date()}")
            raise Exception(f"No data found for {ticker} on {report_date.date()}")
        else:
            
            report_date_price = report_date_data.values[0]
        if start_date in df["Date"].values:
            try:

                lookback_date_price = df[df["Date"] == start_date]["Close"].values[0]
                returns[f"{period}_return"] = round(
                    (report_date_price / lookback_date_price - 1), 4
                )
            except Exception as e:
                logger.error(
                    f"Error calculating return for {ticker} during {period}: {e}"
                )
                print(f"Error calculating return for {ticker} during {period}: {e}")
                returns[f"{period}_return"] = 0
        else:
            # If start date is not in the data, calculate the return using the closest available date
            neighbour_days = get_neighbour_days(start_date)
            for adj_lookback_date in neighbour_days:
                if adj_lookback_date in df["Date"].values:
                    try:
                        lookback_date_price = df[df["Date"] == adj_lookback_date][
                            "Close"
                        ].values[0]
                        returns[f"{period}_return"] = round(
                            (report_date_price / lookback_date_price - 1), 4
                        )
                        break
                    except Exception as e:
                        logger.error(
                            f"Error calculating return for {ticker} on {adj_lookback_date} during {period}: {e}"
                        )
                        returns[f"{period}_return"] = pd.NA
                        continue
            else:
                returns[f"{period}_return"] = 0
    return returns


def enrich_with_sector_industry(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich the DataFrame with sector and industry information.

    Parameters:
        df (pd.DataFrame): DataFrame with stock data.
        info_path (str): Path to the CSV file containing sector and industry information.

    Returns:
        pd.DataFrame: Enriched DataFrame with sector and industry columns.
    """
    sp500_sector_df = read_data_from_sqlite(SP500Holdings)
    nasdq_sector_df = read_data_from_sqlite(NASDAQHoldings)
    combined_sector_df = pd.concat([sp500_sector_df, nasdq_sector_df])
    combined_sector_df = combined_sector_df.drop_duplicates(subset=["Ticker"])
    enriched_df = df.merge(combined_sector_df, on="Ticker", how="left")
    return enriched_df


from typing import List



enrich_mapping = {"^GSPC": "S&P 500", "^IXIC": "NASDAQ"}


def ticker_data_processing(
    mode: str,
    ticker: str,
    model,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
    longest_period: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fetch S&P 500 data based on the mode and date range.

    Parameters:
        mode (str): 'initial', 'daily', or 'rerun'
        start_date (Optional[pd.Timestamp]): Start date for rerun mode.
        end_date (Optional[pd.Timestamp]): End date for rerun mode.

    Returns:
        pd.DataFrame: DataFrame with S&P 500 data.
    """

    if mode == "initial":
        ticker_df = fetch_stock_data(ticker, longest_period)
        if ticker in enrich_mapping and model == IndexPrice:
            ticker_df["Name"] = enrich_mapping[ticker]
        write_data_to_sqlite(model, ticker_df)
    elif mode == "daily":
        new_ticker_df = fetch_stock_data(ticker, "1d")
        if ticker in enrich_mapping and model == IndexPrice:
            new_ticker_df["Name"] = enrich_mapping[ticker]
        if not new_ticker_df.empty:
            write_data_to_sqlite(model, new_ticker_df)
        ticker_df = read_data_from_sqlite(model, filters={"Ticker": ticker})
        ticker_df = ticker_df.sort_values(by="Date")
        # sp500_df.index = pd.to_datetime(sp500_df.index)
    elif mode == "rerun":
        new_ticker_df = fetch_stock_data(
            ticker, start_date=start_date, end_date=end_date
        )
        if ticker in enrich_mapping and model == IndexPrice:
            new_ticker_df["Name"] = enrich_mapping[ticker]
        new_records = new_ticker_df.to_dict(orient="records")[0]
        columns = ['Date','Ticker','Close','Name']
        records_to_update = {k: v for k, v in new_records.items() if k in columns}
        upsert_data_in_sqlite(
            model,
            records_to_update,
            filters={"Ticker": ticker, "Date": start_date},
        )
        ticker_df = read_data_from_sqlite(model, filters={"Ticker": ticker})
        ticker_df = ticker_df.sort_values(by="Date")
    elif mode == "db_rerun":
        ticker_df = read_data_from_sqlite(model, filters={"Ticker": ticker})
        ticker_df = ticker_df.sort_values(by="Date")
    return ticker_df


def fetch_sp500_data(
    mode: str,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """
    Fetch S&P 500 data based on the mode and date range.

    Parameters:
        mode (str): 'initial', 'daily', or 'rerun'
        start_date (Optional[pd.Timestamp]): Start date for rerun mode.
        end_date (Optional[pd.Timestamp]): End date for rerun mode.

    Returns:
        pd.DataFrame: DataFrame with S&P 500 data.
    """
    longest_period = "1y"  # Assuming '1y' is the longest period for S&P 500 data
    if mode == "initial":
        sp500_df = fetch_stock_data("^GSPC", longest_period)
        write_data_to_sqlite(SP500Holdings, sp500_df, clear_existing_data=True)

    elif mode == "daily":
        new_sp500_data = fetch_stock_data("^GSPC", "1d")
        if not new_sp500_data.empty:
            write_data_to_sqlite(SP500Holdings, new_sp500_data)
        sp500_df = read_data_from_sqlite(SP500Holdings)
        # sp500_df.index = pd.to_datetime(sp500_df.index)
    elif mode == "rerun":
        new_sp500_data = fetch_stock_data(
            "^GSPC", start_date=start_date, end_date=end_date
        )
        upsert_data_in_sqlite(
            SP500Holdings,
            new_sp500_data.to_dict(orient="records"),
            date_range={start_date, end_date},
        )

    return sp500_df


def get_top_gainers(
    tickers: list,
    lookback_periods: list,
    mode: str,
    all_tickers: List[str],
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
    benchmark_against_sp500: bool = True,
) -> pd.DataFrame:
    logger.info(f"Running get_top_gainers in '{mode}' mode.")
    """
    Screen top gainers for a list of tickers over specified lookback periods,
    including S&P 500 returns for each period.

    Parameters:
        tickers (list): List of stock tickers.
        lookback_periods (list): List of periods for which to calculate returns.
        mode (str): 'initial', 'daily', or 'rerun'
        start_date (Optional[str]): Start date for rerun mode.
        end_date (Optional[str]): End date for rerun mode.

    Returns:
        pd.DataFrame: DataFrame with returns for each ticker and time period,
                      including S&P 500 returns.
    """
    results = []

    # Convert periods to days for comparison
    period_days = {
        "1d": 1,
        "3d": 3,
        "5d": 5,
        "14d": 14,
        "21d": 21,
        "1mo": 30,
        "2mo": 60,
        "3mo": 90,
        "4mo": 120,
        "5mo": 150,
        "6mo": 180,
        "1y": 365,
        # '2y': 730,
        # '5y': 1825
    }
    
    longest_period = max(lookback_periods, key=lambda x: period_days[x])

    # Fetch S&P 500 returns
    if benchmark_against_sp500:
        sp500_df = ticker_data_processing(
            mode, "^GSPC", IndexPrice, start_date, end_date, longest_period
        )
        sp500_returns = calculate_returns(
            sp500_df, lookback_periods, period_days, "S&P500", start_date
        )
        nasdaq_df = ticker_data_processing(
            mode, "^IXIC", IndexPrice, start_date, end_date, longest_period
        )
        nasdaq_returns = calculate_returns(
            nasdaq_df, lookback_periods, period_days, "nasdaq", start_date
        )

    count = 0
    for ticker in tickers:
        count += 1
        try:
            if ticker not in all_tickers:
                ticker_df = ticker_data_processing(
                    "initial", ticker, StocksPrice, start_date, end_date, longest_period
                )
            else:
                ticker_df = ticker_data_processing(
                    mode, ticker, StocksPrice, start_date, end_date, longest_period
                )

            returns = calculate_returns(
                ticker_df, lookback_periods, period_days, ticker, start_date
            )
            if benchmark_against_sp500:
                for period in lookback_periods:
                    returns[f"{period}_SP500_return"] = sp500_returns.get(
                        f"{period}_return", 0
                    )
                for period in lookback_periods:
                    returns[f"{period}_nasdaq_return"] = nasdaq_returns.get(
                        f"{period}_return", 0
                    )
            results.append(returns)
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            print(f"Error fetching data for {ticker}: {e}")
            continue
        print(f"Processed {count} tickers.")
    # Convert results to a DataFrame
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(
        by=f"{lookback_periods[0]}_return", ascending=False
    )
    logger.info("Completed getting top gainers.")
    return result_df




def generate_market_scanner_report(
    sp500_tickers,
    lookback_periods: list,
    increase_thresholds: list,
    decrease_thresholds: list,
    args,
    current_date,
    report_name: str,
    all_tickers: List[str],
    format :str ='html'
) -> None:
    top_gainers = get_top_gainers(
        sp500_tickers,
        lookback_periods,
        mode=args.mode,
        all_tickers=all_tickers,
        start_date=current_date,
        end_date=current_date + timedelta(days=1),
    )

    if top_gainers.empty:
        raise Exception(f"No data available to generate the report for {current_date}")

    current_date_str = current_date.strftime("%Y-%m-%d")

    # Enrich top_gainers with sector and industry information
    top_gainers = enrich_with_sector_industry(top_gainers)
    column_output = [
            "Ticker",
            "CompanyName",
            "Sector",
            "Industry",
        ]
    if format == 'html':
        html_content = generate_html_report(top_gainers,
        lookback_periods,
        increase_thresholds,
        decrease_thresholds,
        current_date_str,
        column_output,
        report_name
    )
        send_email(
        recipient=args.recipient,
        subject=f"{report_name} Report {current_date_str}",
        body="",
        html_content=html_content,
    )
    elif format == 'excel':
        report_path = f"reports/{report_name}_{current_date_str}.xlsx"
        
        generate_excel_report(
            top_gainers,
            lookback_periods,
            increase_thresholds,
            decrease_thresholds,
            current_date_str,
            column_output,
            report_name,
        )
        send_email(
        recipient=args.recipient,
        subject=f"{report_name} Report {current_date_str}",
        body="",
        report_path=report_path,
    )
    
    logger.info(
        f"Market scanner Report for {current_date_str} generated and emailed successfully."
    )





def generate_user_specific_report(
    tickers, lookback_periods: list, args, current_date, report_name, all_tickers: List[str] = None
) -> None:

    top_gainers = get_top_gainers(
        tickers,
        lookback_periods,
        mode=args.mode,
        all_tickers=all_tickers,
        start_date=current_date,
        end_date=current_date + timedelta(days=1),
    )

    if top_gainers.empty and args.mode == "rerun":
        raise Exception(f"No data available to generate the report for {current_date}")

    current_date_str = current_date.strftime("%Y-%m-%d")

    # Enrich top_gainers with sector and industry information
    top_gainers = enrich_with_sector_industry(top_gainers)
    report_path = f"reports/{report_name}_{current_date_str}.xlsx"

    generate_watch_list_report(top_gainers, current_date_str, report_name)

    send_email(
        recipient=args.recipient,
        subject=f"{report_name} {current_date_str}",
        body=f"Please find the attached {report_name} report for {current_date_str}.",
        report_path=report_path,
    )
    logger.info(
        f"Watchlist Report for {current_date_str} generated and emailed successfully."
    )


def generate_broad_market_report(
    tickers, lookback_periods: list, args, current_date, all_tickers: List[str] = None
) -> None:

    top_gainers = get_top_gainers(
        tickers,
        lookback_periods,
        mode=args.mode,
        all_tickers=all_tickers,
        start_date=current_date,
        end_date=current_date + timedelta(days=1),
        benchmark_against_sp500=False,
    )

    if top_gainers.empty and args.mode == "rerun":
        raise Exception(f"No data available to generate the report for {current_date}")

    current_date_str = current_date.strftime("%Y-%m-%d")
    report_name = "Broad Market Monitoring Report"
    broad_market_etf_df = read_data_from_sqlite(BroadMarketETFList)
    enriched_top_gainers = pd.merge(top_gainers,broad_market_etf_df,how="left",on="Ticker")
    html_content = generate_broad_market_monitoring_report_html(enriched_top_gainers,current_date.strftime("%Y-%m-%d"))
    send_email(
        recipient=args.recipient,
        subject=f"{report_name} {current_date_str}",
        body=html_content ,
        html_content=html_content
    )
    logger.info(
        f"Watchlist Report for {current_date_str} generated and emailed successfully."
    )




    
def main():
    logger.info("Script started.")
    parser = argparse.ArgumentParser(description="Stock Analytics Script")
    parser.add_argument(
        "--mode",
        choices=["initial", "daily", "rerun","db_rerun"],
        required=True,
        help="Mode to run the process: initial, daily, or rerun",
    )
    parser.add_argument(
        "--recipient", type=str, required=True, help="Recipient email address"
    )
    parser.add_argument(
        "--start_date",
        type=str,
        help="Start date for rerun mode",
        default=TODAY.strftime("%Y-%m-%d"),
    )
    parser.add_argument(
        "--end_date",
        type=str,
        help="End date for rerun mode",
        default=TODAY.strftime("%Y-%m-%d"),
    )

    args = parser.parse_args()

    logger.info(
        f"Parameters received - Mode: {args.mode}, Recipient: {args.recipient}, Start Date: {args.start_date}, End Date: {args.end_date}"
    )

    increase_thresholds = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 1, 2]
    decrease_thresholds = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 1, 2]
    lookback_periods = [
        "1d",
        "3d",
        "5d",
        "14d",
        "21d",
        "1mo",
        "2mo",
        "3mo",
        "4mo",
        "5mo",
        "6mo",
        "1y",
    ]

    sp500_tickers = read_tickers(SP500Holdings)
    nasdaq_tickers = read_tickers(NASDAQHoldings)
    only_nasdaq_tickers = [
        ticker for ticker in nasdaq_tickers if ticker not in sp500_tickers
    ]
    watchlist_tickers = get_user_tickers("kobegao")
    ib_tickers = load_positions()
    broadmarket_etf_list = read_tickers(BroadMarketETFList)
    logger.info(f"Fetched {len(sp500_tickers)} S&P 500 tickers.")

    date_range = pd.date_range(start=args.start_date, end=args.end_date)
    all_tickers = get_all_tickers()
    for current_date in date_range:
        generate_market_scanner_report(
            sp500_tickers,
            lookback_periods,
            increase_thresholds,
            decrease_thresholds,
            args,
            current_date,
            report_name="SP500 Market Scanner",
            all_tickers=all_tickers,
            format='excel'
        )
        generate_market_scanner_report(
            only_nasdaq_tickers,
            lookback_periods,
            increase_thresholds,
            decrease_thresholds,
            args,
            current_date,
            report_name="NASDAQ Market Scanner",
            all_tickers=all_tickers,
            format='excel'
        )
        generate_user_specific_report(
            watchlist_tickers, lookback_periods, args, current_date, "Watchlist Report", all_tickers
        )
        generate_user_specific_report(
            ib_tickers, lookback_periods, args, current_date,"IB account return report", all_tickers
        )
        generate_broad_market_report(broadmarket_etf_list,lookback_periods,args,current_date,all_tickers)
    logger.info("Script completed successfully.")





# TODO 1. add sector to the report
# TODO 2. add company name to the report
if __name__ == "__main__":
 
    alert_emails = os.getenv("ALERT_EMAILS").split(",")

    try:
        main()
    except Exception as e:
        traceback_str = traceback.format_exc()
        logger.error(f"An error occurred while running the stock analysis script: {traceback_str}")
        send_email(
            recipient=alert_emails,
            subject="Stock Analysis Report - Error",
            body=f"An error occurred while running the stock analysis script.\n{traceback_str}",
        )
