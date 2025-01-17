from email.message import EmailMessage
import logging
from typing import Optional
import os
import smtplib
from sqlitedb.read import read_data_from_sqlite
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from sqlitedb.models import StocksPrice
from dotenv import load_dotenv
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # Your email address
EMAIL_PASSWORD = os.getenv(
    "EMAIL_PASSWORD"
)  # Your email password or app-specific password


logger = logging.getLogger('stock_analytics')

def send_email(
    recipient: str,
    subject: str,
    body: str,
    report_path: Optional[str] = None,
    html_content: Optional[str] = None,
) -> None:
    logger.info(f"Sending email to {recipient} with subject '{subject}'.")
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
    if html_content:
        msg.add_alternative(html_content, subtype="html")
    print(f"Error sending email: {EMAIL_ADDRESS} {EMAIL_PASSWORD}")
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
        logger.info("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {EMAIL_ADDRESS} {EMAIL_PASSWORD}")
        logger.error(f"Error sending email: {e}")


def format_worksheet(workbook, worksheet, combined_df):
    logger.debug("Formatting worksheet.")
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
            
            

def get_neighbour_days(start_date) -> list[datetime]:
    logger.debug(f"Getting neighbour days for start_date {start_date}.")
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

def  fetch_stock_data(
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
        logger.error(f"Error fetching data for {ticker}: {e}")
        raise
    # df.index = pd.to_datetime(df.index, utc=True)  # Set utc=True
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df["Ticker"] = ticker
    try:
        df['PERatio'] = stock.info['trailingPE']
    except:
        df['PERatio'] = pd.NA
    
    try:
        df['ForwardPERatio'] = stock.info['forwardPE']
    except:
        df['ForwardPERatio'] = pd.NA
    if "Stock Splits" in df.columns:
        df = df.rename(columns={"Stock Splits": "StockSplits"})
    return df


def read_tickers(model) -> list:
    logger.info(f"Fetching underlying tickers for {model}.")
    """
    Fetch the list of index underlying tickers from sqlite
        list: List of ticker symbols.
    """

    try:
        table = read_data_from_sqlite(model)
    except Exception as e:
        logger.error(f"Error fetching data from sqlite: {e}")
        raise e
    tickers = table["Ticker"].tolist()
    return tickers


def get_all_tickers():
    all_tickers = read_data_from_sqlite(StocksPrice, columns_to_select=['Ticker'], is_distinct=True)
    return set(all_tickers["Ticker"].unique())

if __name__ == "__main__":
    res = get_all_tickers()
    print(res)