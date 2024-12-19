def fetch_top_gainers(exchange: str, threshold: float):
    # Example logic to filter stocks
    tickers = ['AAPL', 'MSFT', 'GOOG']  # Replace with dynamic list
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        yearly_return = (hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0] * 100
        if yearly_return > threshold:
            data.append({
                'Ticker': ticker,
                '1-Year % Change': round(yearly_return, 2)
            })
    return pd.DataFrame(data)