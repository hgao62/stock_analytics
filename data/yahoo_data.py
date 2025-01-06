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
    Users
)
from sqlitedb.delete import truncate_table
from sqlitedb.update import update_data_in_sqlite
from data.watchlist import get_user_tickers
# load environment variable
load_dotenv()
# Email configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # Your email address
EMAIL_PASSWORD = os.getenv(
    "EMAIL_PASSWORD"
)  # Your email password or app-specific password

# Ensure the 'logs' directory exists
os.makedirs("logs", exist_ok=True)

# Set up logging configuration
logging.basicConfig(
    filemode="a",
    filename="logs/yahoo_data.log",  # Log file path
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s- %(filename)s:%(lineno)s  - %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S",  # Date format
)

logging.info("Environment variables loaded.")
logging.info(f"Email address: {EMAIL_ADDRESS}. Email password: {EMAIL_PASSWORD}")

TODAY = datetime.now()
REPORT_DATE = TODAY.strftime("%Y-%m-%d")


def read_tickers(model) -> list:
    logging.info(f"Fetching underlying tickers for {model}.")
    """
    Fetch the list of index underlying tickers from sqlite
        list: List of ticker symbols.
    """

    try:
        table = read_data_from_sqlite(model)
    except Exception as e:
        logging.error(f"Error fetching data from sqlite: {e}")
        raise e
    tickers = table["Ticker"].tolist()
    return tickers


def fetch_stock_data(
    ticker: str,
    period: Optional[str] = None,
    start_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """
    Fetch historical stock data for a specific ticker from Yahoo Finance.

    Parameters:
        ticker (str): Stock ticker symbol.
        period (Optional[str]): Period string for Yahoo Finance API (e.g., '1mo', '3mo', '1y').
        start_date (Optional[str]): Start date for fetching data.
        end_date (Optional[str]): End date for fetching data.

    Returns:
        pd.DataFrame: DataFrame with historical stock data.
    """
    stock = yf.Ticker(ticker)
    try:
        if start_date and end_date:
            df = stock.history(start=start_date, end=end_date)
        else:
            df = stock.history(period=period)
    except Exception as e:
        logging.error(f"Error fetching data for {ticker}: {e}")
        raise
    # df.index = pd.to_datetime(df.index, utc=True)  # Set utc=True
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df["Ticker"] = ticker
    return df


def get_neighbour_days(start_date) -> list[datetime]:
    logging.debug(f"Getting neighbour days for start_date {start_date}.")
    """
    Get the previous and next day of the start date
    """
    res = []
    for i in range(1, 4):
        adjust_start_date_backwards = start_date - timedelta(days=i)
        adjust_start_date_forwards = start_date + timedelta(days=i)
        res.append(adjust_start_date_backwards)
        res.append(adjust_start_date_forwards)
    return res


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
            start_date = (report_date - timedelta(days=period_days[period])).date()
        except Exception as e:
            logging.error(
                f"Error calculating start_date for {ticker} during {period}: {e}"
            )
            print(f"Error calculating start_date for {ticker} during {period}: {e}")
            returns[f"{period}_return"] = 0
            continue  # Skip to the next period

        # Convert start_date to pandas Timestamp and normalize
        # start_date_normalized = pd.Timestamp(start_date).normalize().tz_localize('UTC')
        # Normalize dates to ignore timezone and other attributes

        report_date_price = df[df["Date"] == report_date.date()]["Close"].values[0]
        if start_date in df["Date"].values:
            try:

                lookback_date_price = df[df["Date"] == start_date]["Close"].values[0]
                returns[f"{period}_return"] = round(
                    (report_date_price / lookback_date_price - 1), 4
                )
            except Exception as e:
                logging.error(
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
                        logging.error(
                            f"Error calculating return for {ticker} on {adj_lookback_date} during {period}: {e}"
                        )
                        returns[f"{period}_return"] = pd.NA
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
        "1d": 1,
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
    sp500_df = fetch_stock_data("^GSPC", longest_period)
    sp500_returns = calculate_returns(sp500_df, lookback_periods, period_days, "S&P500")

    for ticker in tickers:
        try:
            df = fetch_stock_data(ticker, longest_period)
            df.to_csv(f"data/{ticker}.csv")
            returns = calculate_returns(df, lookback_periods, period_days, ticker)
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
    result_df = result_df.sort_values(
        by=f"{lookback_periods[0]}_return", ascending=False
    )
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
        if col.endswith("_return"):
            worksheet.set_column(
                idx,
                idx,
                10,
                workbook.add_format({"num_format": "0.00%"}),  # Set wider column width
            )
            # Apply conditional formatting with explicit min, mid, and max types
            worksheet.conditional_format(
                1,
                idx,
                len(combined_df),
                idx,
                {
                    "type": "3_color_scale",
                    "min_type": "num",
                    "min_value": combined_df[col].min(),
                    "mid_type": "num",
                    "mid_value": 0,
                    "max_type": "num",
                    "max_value": combined_df[col].max(),
                    "min_color": "#FF0000",  # Red for negative returns
                    "mid_color": "#FFFFFF",  # White for zero return
                    "max_color": "#00FF00",  # Green for positive returns
                },
            )
        else:
            worksheet.set_column(
                idx,
                idx,
                10)  # Set wider column width
            
            

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


def generate_report(
    df: pd.DataFrame,
    lookback_periods: list,
    increase_thresholds: list,
    decrease_thresholds: list,
    report_date_str: str,
    columns: List[str],
    report_name: str,
) -> None:
    logging.info("Generating report.")
    """
    Generate a report showing the increase and decrease for each threshold for all lookback periods.
    
    Parameters:
        df (pd.DataFrame): DataFrame with returns for each ticker and time period.
        lookback_periods (list): List of periods for which to calculate returns.
        increase_thresholds (list): List of increase thresholds.
        decrease_thresholds (list): List of decrease thresholds.
    """
    report_filename = f"reports/{report_name}_{report_date_str}.xlsx"

    with pd.ExcelWriter(report_filename, engine="xlsxwriter") as writer:

        for period in lookback_periods:
            final_output_columns = columns + [
                f"{period}_return",
                f"{period}_SP500_return",
            ]
            period_data = []

            for i, threshold in enumerate(increase_thresholds):
                if i < len(increase_thresholds) - 1:
                    next_threshold = increase_thresholds[i + 1]
                    increase_df = df[
                        (df[f"{period}_return"] > threshold)
                        & (df[f"{period}_return"] <= next_threshold)
                    ]
                else:
                    increase_df = df[df[f"{period}_return"] > threshold]

                if not increase_df.empty:
                    increase_df = increase_df[final_output_columns]
                    increase_df["Threshold"] = (
                        f"{threshold * 100}% < Increase <= {next_threshold * 100}%"
                        if i < len(increase_thresholds) - 1
                        else f"Increase > {threshold * 100}%"
                    )
                    period_data.append(increase_df)

            for i, threshold in enumerate(decrease_thresholds):
                if i < len(decrease_thresholds) - 1:
                    next_threshold = decrease_thresholds[i + 1]
                    decrease_df = df[
                        (df[f"{period}_return"] < -threshold)
                        & (df[f"{period}_return"] >= -next_threshold)
                    ]
                else:
                    decrease_df = df[df[f"{period}_return"] < -threshold]

                if not decrease_df.empty:
                    decrease_df = decrease_df[final_output_columns]
                    decrease_df["Threshold"] = (
                        f"{-next_threshold * 100}% <= Decrease < {-threshold * 100}%"
                        if i < len(decrease_thresholds) - 1
                        else f"Decrease < {-threshold * 100}%"
                    )
                    period_data.append(decrease_df)

            if period_data:
                combined_df = pd.concat(period_data)
                combined_df = combined_df.sort_values(
                    by=f"{period}_return", ascending=False
                )
                combined_df.to_excel(writer, sheet_name=period, index=False)

                # Format the worksheet
                workbook = writer.book
                worksheet = writer.sheets[period]
                try:
                    format_worksheet(workbook, worksheet, combined_df)
                except Exception as e:
                    logging.error(
                        f"Error formatting worksheet for period {period}: {e}"
                    )

    logging.info(f"Report generated successfully: {report_filename}")


def generate_watch_list_report(
    df: pd.DataFrame, report_date_str: str, report_name: str
) -> None:
    logging.info("Generating watchlist report.")
    """
    Generate a report showing the increase and decrease for each threshold for all lookback periods.
    
    Parameters:
        df (pd.DataFrame): DataFrame with returns for each ticker and time period.
        lookback_periods (list): List of periods for which to calculate returns.
        increase_thresholds (list): List of increase thresholds.
        decrease_thresholds (list): List of decrease thresholds.
    """
    beginning_cols = ["Ticker", "CompanyName", "Sector", "Industry"]
    output_columns = beginning_cols + [c for c in df.columns if c not in beginning_cols]
    df = df[output_columns]
    report_filename = f"reports/{report_name}_{report_date_str}.xlsx"

    with pd.ExcelWriter(report_filename, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="watchlist", index=False)
        # Format the worksheet
        workbook = writer.book
        worksheet = writer.sheets["watchlist"]
        try:
            format_worksheet(workbook, worksheet, df)
        except Exception as e:
            logging.error(f"Error formatting worksheet  {e}")

    logging.info(f"Watchlist Report generated successfully: {report_filename}")


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
        records_to_update = {k: v for k, v in new_records.items() if k in ["Close"]}
        update_data_in_sqlite(
            model,
            records_to_update,
            filters={"Ticker": ticker, "Date": start_date},
        )
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
        update_data_in_sqlite(
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
) -> pd.DataFrame:
    logging.info(f"Running get_top_gainers in '{mode}' mode.")
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
            logging.error(f"Error fetching data for {ticker}: {e}")
            print(f"Error fetching data for {ticker}: {e}")
            continue
        print(f"Processed {count} tickers.")
    # Convert results to a DataFrame
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(
        by=f"{lookback_periods[0]}_return", ascending=False
    )
    logging.info("Completed getting top gainers.")
    return result_df


def send_email(
    recipient: str,
    subject: str,
    body: str,
    report_path: Optional[str] = None,
) -> None:
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
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient
    msg.set_content(body)

    if report_path:
        # Attach the report
        with open(report_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(report_path)
        msg.add_attachment(
            file_data,
            maintype="application",
            subtype="octet-stream",
            filename=file_name,
        )

    # Send the email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")


def generate_market_scanner_report(
    sp500_tickers,
    lookback_periods: list,
    increase_thresholds: list,
    decrease_thresholds: list,
    args,
    current_date,
    report_name: str,
    all_tickers: List[str],
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

    report_path = f"reports/{report_name}_{current_date_str}.xlsx"
    column_output = [
        "Ticker",
        "CompanyName",
        "Sector",
        "Industry",
    ]
    generate_report(
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
        subject=f"Stock Analysis Report {current_date_str}",
        body=f"Please find the attached {report_name} report for {current_date_str}.",
        report_path=report_path,
    )
    logging.info(
        f"Market scanner Report for {current_date_str} generated and emailed successfully."
    )


def get_all_tickers():
    all_tickers = read_data_from_sqlite(StocksPrice)
    return set(all_tickers["Ticker"].unique())


def generate_watchlist_report(
    tickers, lookback_periods: list, args, current_date, all_tickers: List[str] = None
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
    report_name = "Watchlist Report"
    report_path = f"reports/{report_name}_{current_date_str}.xlsx"

    generate_watch_list_report(top_gainers, current_date_str, report_name)

    send_email(
        recipient=args.recipient,
        subject=f"{report_name} {current_date_str}",
        body=f"Please find the attached {report_name} report for {current_date_str}.",
        report_path=report_path,
    )
    logging.info(
        f"Watchlist Report for {current_date_str} generated and emailed successfully."
    )


    
def main():
    logging.info("Script started.")
    parser = argparse.ArgumentParser(description="Stock Analytics Script")
    parser.add_argument(
        "--mode",
        choices=["initial", "daily", "rerun"],
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

    logging.info(
        f"Parameters received - Mode: {args.mode}, Recipient: {args.recipient}, Start Date: {args.start_date}, End Date: {args.end_date}"
    )

    increase_thresholds = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 1, 2]
    decrease_thresholds = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 1, 2]
    lookback_periods = [
        "1d",
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
    logging.info(f"Fetched {len(sp500_tickers)} S&P 500 tickers.")

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
        )
        generate_watchlist_report(
            watchlist_tickers, lookback_periods, args, current_date, all_tickers
        )

    logging.info("Script completed successfully.")


def load_sp500_data():
    sp500_tickers = read_tickers(SP500Holdings)
    for each_ticker in sp500_tickers:
        df = fetch_stock_data(each_ticker, "1y")
        df["IndexName"] = "sp500"
        write_data_to_sqlite(StocksPrice, df)


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


def initial_laod():
    load_sp500_data()
    sp500_tickers = read_tickers(SP500Holdings)
    load_nasdaq_data(sp500_tickers)


# TODO 1. add sector to the report
# TODO 2. add company name to the report
if __name__ == "__main__":

    alert_emails = os.getenv("ALERT_EMAILS").split(",")
    # load_nasdaq_data(sp500_tickers )
    try:
        main()
    except Exception as e:
        send_email(
            recipient=alert_emails,
            subject="Stock Analysis Report - Error",
            body=f"An error occurred while running the stock analysis script. {str(e)}",
        )
