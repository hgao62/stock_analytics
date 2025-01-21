import pandas as pd
import plotly.graph_objects as go
import os

def generate_combined_performance_chart(file_path: str) -> None:
    """
    Generate a combined time series chart for account performance data.

    Parameters:
        file_path (str): The path to the CSV file containing performance data.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Extract the chart name from the file path
    chart_name = os.path.splitext(os.path.basename(file_path))[0]

    # Read the performance data from CSV
    df = pd.read_csv(file_path)

    # Convert date format from YYYYMMDD to a proper date column
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')

    # Convert Cumulative Performance Data to percentage
    df['Cumulative performance data'] = df['Cumulative performance data'] * 100

    # Create a combined time series chart
    fig = go.Figure()

    # Add Net Present Value trace
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Net present value'],
        mode='lines',
        name='Net Present Value',
        line=dict(color='blue')
    ))

    # Add Cumulative Performance Data trace
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Cumulative performance data'],
        mode='lines',
        name='Cumulative Performance Data',
        line=dict(color='red'),
        yaxis='y2'
    ))

    # Update layout for better readability
    fig.update_layout(
        title=dict(text=f'{chart_name} - Net Present Value and Cumulative Performance Data Over Time', x=0.5, y=0.95, font=dict(size=24)),
        xaxis_title='Date',
        yaxis=dict(
            title='Net Present Value',
            tickfont=dict(size=14)
        ),
        yaxis2=dict(
            title='Cumulative Performance Data (%)',
            overlaying='y',
            side='right',
            tickfont=dict(size=14)
        ),
        xaxis=dict(
            tickformat='%b %Y',  # Format x-axis to show months
            tickfont=dict(size=14),
            dtick="M1"  # Set tick interval to 1 month
        ),
        legend=dict(font=dict(size=16))
    )

    # Ensure the output directory exists
    output_dir = "C:/development/repo/stock_analytics/reports/IB"
    os.makedirs(output_dir, exist_ok=True)

    # Save the combined chart as an HTML file
    output_file = os.path.join(output_dir, f"{chart_name}_combined_performance.html")
    fig.write_html(output_file)

    print(f"Combined chart saved to {output_dir}")

# Example usage
file_path = "C:/development/repo/stock_analytics/ib/data/U11570761_1Y_performance.csv"
# file_path = "C:/development/repo/stock_analytics/ib/data/U9978141_2Y_performance.csv"
generate_combined_performance_chart(file_path)
