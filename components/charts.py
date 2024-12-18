import plotly.graph_objects as go
import pandas as pd

def create_stock_price_chart(df: pd.DataFrame, title: str = "Stock Price Over Time") -> go.Figure:
    """
    Creates a line chart for stock prices over time.
    
    Parameters:
        df (pd.DataFrame): DataFrame with 'date' and 'value' columns.
        title (str): Title for the chart.
    
    Returns:
        go.Figure: A Plotly figure object.
    """
    fig = go.Figure()

    # Add line trace for stock prices
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['value'],
        mode='lines',
        name='Stock Price',
        line=dict(color='blue')
    ))

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        hovermode="x unified"
    )
    return fig

def create_volume_chart(df: pd.DataFrame, title: str = "Trading Volume Over Time") -> go.Figure:
    """
    Creates a bar chart for trading volume over time.
    
    Parameters:
        df (pd.DataFrame): DataFrame with 'date' and 'volume' columns.
        title (str): Title for the chart.
    
    Returns:
        go.Figure: A Plotly figure object.
    """
    if 'volume' not in df.columns:
        raise ValueError("DataFrame must contain a 'volume' column for this chart.")
    
    fig = go.Figure()

    # Add bar trace for volume
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['volume'],
        name='Volume',
        marker_color='orange'
    ))

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Volume",
        template="plotly_white",
        hovermode="x unified"
    )
    return fig
