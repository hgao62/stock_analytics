import pandas as pd
import plotly.express as px
import os

def generate_portfolio_allocation_chart(account_id: str, allocation_type: str) -> None:
    """
    Generate a portfolio allocation chart for the given account ID and allocation type.

    Parameters:
        account_id (str): The account ID for which to generate the chart.
        allocation_type (str): The type of allocation data ('assetClass', 'sector', 'group').
    """
    # Read the portfolio allocation data from CSV
    file_path = f'ib/data/{account_id}_{allocation_type}_allocation.csv'
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path)

    # Create a pie chart for portfolio allocation
    fig = px.pie(df, names=allocation_type, values='amount', title=f'Portfolio Allocation by {allocation_type.capitalize()} for Account {account_id}')

    # Update layout for better readability
    fig.update_layout(
        title=dict(text=f'Portfolio Allocation by {allocation_type.capitalize()} for Account {account_id}', x=0.5, y=0.95, font=dict(size=24)),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=16)
        )
    )

    # Ensure the output directory exists
    output_dir = "C:/development/repo/stock_analytics/reports/IB"
    os.makedirs(output_dir, exist_ok=True)

    # Save the chart as an HTML file
    output_file = os.path.join(output_dir, f"{account_id}_{allocation_type}_portfolio_allocation.html")
    fig.write_html(output_file)

    print(f"Portfolio allocation chart generated: {output_file}")

def main():
    account_id = 'U11570761'  # Replace with the actual account ID
    allocation_types = ['assetClass', 'sector', 'group']
    for allocation_type in allocation_types:
        generate_portfolio_allocation_chart(account_id, allocation_type)

if __name__ == "__main__":
    main()
