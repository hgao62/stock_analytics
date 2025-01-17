import pandas as pd
from typing import List
from data.broad_market_etfs_analysis import generate_broad_market_monitoring_report_html,generate_market_scanner_html_report
from data.utilities import format_worksheet
import logging

logger = logging.getLogger('stock_analytics')
def prepare_report_data( 
    df: pd.DataFrame ,                   
    lookback_periods: List[str],
    increase_thresholds: List[float],
    decrease_thresholds: List[float],

    columns: List[str],
    ) -> List[dict]:
    final_output_data = {}
    for period in lookback_periods:
        final_output_columns = columns + [
            f"{period}_return",
            f"{period}_SP500_return",
        ]
        period_data = filter_data_by_thresholds(
            increase_thresholds, decrease_thresholds,period, df, final_output_columns, 
        )

        if period_data:
            combined_df = pd.concat(period_data)
            combined_df = combined_df.sort_values(
                by=f"{period}_return", ascending=False
            )
            
            final_output_data[period] = combined_df.to_dict(orient="records")
    return final_output_data
    

def generate_html_report(df: pd.DataFrame,
    lookback_periods: list,
    increase_thresholds: list,
    decrease_thresholds: list,
    report_date_str: str,
    columns: List[str],
    report_name: str) ->None:


    report_data = prepare_report_data(
        df,
        lookback_periods,
        increase_thresholds,
        decrease_thresholds,
        columns,
    )
    df.to_csv(f"data/{report_name}.csv")
    html_content = generate_market_scanner_html_report(report_data,report_date_str,report_name)
    logger.info(f"Report generated successfully: {report_name}")
    return html_content
    
def filter_data_by_thresholds(
    increase_thresholds,
    decrease_thresholds,
    period: str,
    df: pd.DataFrame,
    final_output_columns: list[str],
) -> pd.DataFrame:
    """
    Filter dataframe based on provided thresholds and period returns.
    This function filters a DataFrame based on threshold values for a given period's returns,
    creating categories/buckets of data that fall within specified threshold ranges.
    Args:
        thresholds (list[float]): List of threshold values to filter the data
        period (str): Time period to analyze returns (e.g., 'daily', 'weekly', 'monthly')
        df (pd.DataFrame): Input DataFrame containing return data
        final_output_columns (list[str]): List of columns to include in the output DataFrame
        threshold_type (str): Type of threshold being applied (e.g., 'Return', 'Gain', 'Loss')
    Returns:
        pd.DataFrame: Filtered DataFrame containing only rows that meet the threshold criteria,
                     with an additional 'Threshold' column indicating the range.
    Example:
        >>> thresholds = [0.05, 0.10, 0.15]
        >>> filter_data_by_thresholds(thresholds, 'daily', df, ['Date', 'Close'], 'Return')
        Returns DataFrame with rows where daily returns fall within specified threshold ranges
    """
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
    return period_data
    
def generate_excel_report(
    df: pd.DataFrame,
    lookback_periods: list,
    increase_thresholds: list,
    decrease_thresholds: list,
    report_date_str: str,
    columns: List[str],
    report_name: str,
) -> None:
    logger.info("Generating report.")
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

           
            increase_df = filter_data_by_thresholds(
                increase_thresholds, period, df, final_output_columns, "Increase"
            )
            period_data.append(increase_df)

            decrease_df = filter_data_by_thresholds(
                decrease_thresholds, period, df, final_output_columns, "Decrease"
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
                    logger.error(
                        f"Error formatting worksheet for period {period}: {e}"
                    )

    logger.info(f"Report generated successfully: {report_filename}")


def generate_watch_list_report(
    df: pd.DataFrame, report_date_str: str, report_name: str
) -> None:
    logger.info("Generating watchlist report.")
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
            logger.error(f"Error formatting worksheet  {e}")

    logger.info(f"Watchlist Report generated successfully: {report_filename}")



