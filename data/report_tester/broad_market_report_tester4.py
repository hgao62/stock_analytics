import pandas as pd
from jinja2 import Template

# Sample data (replace with your Yahoo Finance API data or CSV input)
data = {
    "Ticker": ["SPY", "GLD", "TLT", "AAPL"],
    "Name": [
        "S&P 500 ETF",
        "SPDR Gold Shares",
        "iShares 20+ Year Treasury Bond ETF",
        "Apple Inc."
    ],
    "Asset Class": ["Equities", "Commodities", "Bonds", "Equities"],
    "1d_return": [-0.5, 0.53, 0.21, -0.3],
    "5d_return": [-1.2, 1.1, 0.5, -2.0],
    "1mo_return": [2.5, 3.0, -1.5, 5.0],
    "2mo_return": [5.0, 7.5, -2.0, 10.0],
    "6mo_return": [10.0, 15.0, 3.0, 20.0],
    "1yr_return": [15.0, 20.0, 5.0, 25.0],
}

# Convert the data dictionary into a Pandas DataFrame
df = pd.DataFrame(data)

# HTML template for the report with placeholders for data
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .card { border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 16px; width: 300px; display: inline-block; vertical-align: top; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); }
        .card h2 { margin: 0; font-size: 20px; color: #333; }
        .card p { margin: 5px 0; font-size: 14px; }
        .returns { margin-top: 10px; }
        .returns span { display: inline-block; width: 100px; }
        .positive { color: green; }
        .negative { color: red; }
        .ticker { color: lightblue; font-weight: bold; } /* Add this line */
        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 10px; /* Add more white space between cells horizontally */
        }
        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px dotted grey; /* Add dotted grey line */
        }
        tr {
            border-bottom: 1px dotted grey; /* Add dotted grey line */
        }
    </style>
    <title>Broad Market Monitoring Report</title>
</head>
<body>
    <h1>Broad Market Monitoring Report</h1>
    {% for asset_class, items in data.items() %}
        <h2>{{ asset_class }}</h2>
        <table>
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Name</th>
                    <th>1 Day</th>
                    <th>5 Day</th>
                    <th>1 Month</th>
                    <th>2 Month</th>
                    <th>6 Month</th>
                    <th>1 Year</th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                <tr>
                    <td class="ticker">{{ item['Ticker'] }}</td>
                    <td>{{ item['Name'] }}</td>
                    <td class="{{ 'positive' if item['1d_return'] > 0 else 'negative' }}">{{ item['1d_return'] }}%</td>
                    <td class="{{ 'positive' if item['5d_return'] > 0 else 'negative' }}">{{ item['5d_return'] }}%</td>
                    <td class="{{ 'positive' if item['1mo_return'] > 0 else 'negative' }}">{{ item['1mo_return'] }}%</td>
                    <td class="{{ 'positive' if item['2mo_return'] > 0 else 'negative' }}">{{ item['2mo_return'] }}%</td>
                    <td class="{{ 'positive' if item['6mo_return'] > 0 else 'negative' }}">{{ item['6mo_return'] }}%</td>
                    <td class="{{ 'positive' if item['1yr_return'] > 0 else 'negative' }}">{{ item['1yr_return'] }}%</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    {% endfor %}
</body>
</html>
"""

# Group data by "Asset Class" to organize cards by category
data_grouped = df.groupby("Asset Class").apply(lambda x: x.to_dict(orient="records")).to_dict()

# Use Jinja2 to render the HTML content
template = Template(html_template)
html_content = template.render(data=data_grouped)

# Save the rendered HTML content to a file
output_file = "broad_market_report.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

# Notify the user that the report generation is complete
print(f"HTML report generated: {output_file}")