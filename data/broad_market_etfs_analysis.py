import pandas as pd
from jinja2 import Template

# HTML template for the report with placeholders for data
HTML_TEMPLATE = """
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
        .percentage { display: inline-block; width: 100px; text-align: right; }
        .header { text-align: center; }  /* Center align the header */
    </style>
    <title>Broad Market Monitoring Report</title>
</head>
<body>
    <h1 class="header">{{ report_date }} Broad Market Monitoring Report</h1>
    {% for asset_class, items in data.items() %}
        <h2>{{ asset_class }}</h2>
        {% for item in items %}
        <div class="card">
            <h2>{{ item['Sector'] }}</h2>
            <p><strong>{{ item['Name'] }} ({{ item['Ticker'] }})</p>
            <!-- Highlight positive/negative returns with appropriate class -->
            <p><strong>1 Day Return:</strong> <span class="percentage {{ 'positive' if item['1d_return'] > 0 else 'negative' }}">{{ '%.2f%%' % (item['1d_return'] * 100) }}</span></p>
            <p><strong>5 Day Return:</strong> <span class="percentage {{ 'positive' if item['5d_return'] > 0 else 'negative' }}">{{ '%.2f%%' % (item['5d_return'] * 100) }}</span></p>
            <p><strong>1 Month Return:</strong> <span class="percentage {{ 'positive' if item['1mo_return'] > 0 else 'negative' }}">{{ '%.2f%%' % (item['1mo_return'] * 100) }}</span></p>
            <p><strong>2 Month Return:</strong> <span class="percentage {{ 'positive' if item['2mo_return'] > 0 else 'negative' }}">{{ '%.2f%%' % (item['2mo_return'] * 100) }}</span></p>
            <p><strong>6 Month Return:</strong> <span class="percentage {{ 'positive' if item['6mo_return'] > 0 else 'negative' }}">{{ '%.2f%%' % (item['6mo_return'] * 100) }}</span></p>
            <p><strong>1 Year Return:</strong> <span class="percentage {{ 'positive' if item['1y_return'] > 0 else 'negative' }}">{{ '%.2f%%' % (item['1y_return'] * 100) }}</span></p>
        </div>
        {% endfor %}
    {% endfor %}
</body>
</html>
"""

def sort_asset_class(data: dict) ->dict:
    pre_defined_order = ['Market-Wide Indicators','Equities', 'Bonds', 'Commodities', 'Currency', 'Diversifiers',  'Alternative Assets','Defensive Sectors','Real Estate','International Markets'  ]
    sorted_data = {k: data.get(k, None) for k in pre_defined_order}
    return sorted_data

def generate_broad_market_monitoring_report_html(data:pd.DataFrame, report_date: str) ->str:

    # Group data by "Asset Class" to organize cards by category
    data.to_csv('data/broad_market_etfs.csv', index=False)
    data_grouped = data.groupby("Asset_Class").apply(lambda x: x.to_dict(orient="records")).to_dict()
    data_grouped = sort_asset_class(data_grouped)
    template = Template(HTML_TEMPLATE)
    html_content = template.render(data=data_grouped, report_date=report_date)

    # Save the rendered HTML content to a file
    output_file = "./reports/broad_market_report.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    return html_content

    
if __name__ == "__main__":
    data = pd.read_csv('data/broad_market_etfs.csv')
    report_date = "2025-01-09"
    generate_broad_market_monitoring_report_html(data, report_date)
