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
        h1 { font-size: 28px; margin-bottom: 20px; }
        h2 { font-size: 20px; color: #333; margin-top: 30px; }
        table { 
            width: auto; 
            border-collapse: collapse; 
            margin-top: 10px; 
            table-layout: fixed;
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 4px 8px; 
            text-align: center;
        }
        th { background-color: #f4f4f4; font-weight: bold; }
        .ticker { color: #1e90ff; font-weight: bold; } /* Ticker styling */
        .positive { color: green; }
        .negative { color: red; }
        .separator { border-top: 2px dashed yellow; margin: 20px 0; }
        .header {
            text-align: center;
        }
        .name-column {
            max-width: 200px;
            min-width: 150px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .return-column {
            width: 60px;
            white-space: nowrap;
            padding: 4px;
        }
        .ticker-column {
            width: 50px;
            white-space: nowrap;
            color: #1e90ff; 
            font-weight: bold; 
        }
    </style>
    <title>Broad Market Monitoring Report</title>
</head>
<body>
    <h1 class="header">{{ report_date }}</h1>
    <h1 class="header">Broad Market Monitoring Report</h1>
    {% for asset_class, items in data.items() %}
        <h2>{{ asset_class }}</h2>
        <table>
            <thead>
                <tr>
                    <th class="ticker-column">Ticker</th>
                    <th class="name-column">Name</th>
                    <th class="return-column">1 Day</th>
                    <th class="return-column">3 Day</th>
                    <th class="return-column">5 Day</th>
                    <th class="return-column">1 Month</th>
                    <th class="return-column">2 Month</th>
                    <th class="return-column">6 Month</th>
                    <th class="return-column">1 Year</th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                <tr>
                    <td class="ticker-column">{{ item['Ticker'] }}</td>
                    <td class="name-column">{{ item['Name'] }}</td>
                    <td class="return-column {{ 'positive' if item['1d_return'] > 0 else 'negative' }}">
                        {{ '%.2f%%' % (item['1d_return'] * 100) }}
                    </td>
                    <td class="return-column {{ 'positive' if item['3d_return'] > 0 else 'negative' }}">
                        {{ '%.2f%%' % (item['3d_return'] * 100) }}
                    </td>
                    <td class="return-column {{ 'positive' if item['5d_return'] > 0 else 'negative' }}">
                        {{ '%.2f%%' % (item['5d_return'] * 100) }}
                    </td>
                    <td class="return-column {{ 'positive' if item['1mo_return'] > 0 else 'negative' }}">
                        {{ '%.2f%%' % (item['1mo_return'] * 100) }}
                    </td>
                    <td class="return-column {{ 'positive' if item['2mo_return'] > 0 else 'negative' }}">
                        {{ '%.2f%%' % (item['2mo_return'] * 100) }}
                    </td>
                    <td class="return-column {{ 'positive' if item['6mo_return'] > 0 else 'negative' }}">
                        {{ '%.2f%%' % (item['6mo_return'] * 100) }}
                    </td>
                    <td class="return-column {{ 'positive' if item['1y_return'] > 0 else 'negative' }}">
                        {{ '%.2f%%' % (item['1y_return'] * 100) }}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    {% endfor %}
</body>
</html>
"""

HTML_TEMPLATE2 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { font-size: 28px; margin-bottom: 20px; }
        h2 { font-size: 20px; color: #333; margin-top: 30px; }
        table { 
            width: auto; 
            border-collapse: collapse; 
            margin-top: 10px; 
            table-layout: fixed;
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 4px 8px; 
            text-align: center;
        }
        th { background-color: #f4f4f4; font-weight: bold; }
        .ticker { color: #1e90ff; font-weight: bold; } /* Ticker styling */
        .positive { color: green; }
        .negative { color: red; }
        .separator { border-top: 2px dashed yellow; margin: 20px 0; }
        .header {
            text-align: center;
        }
        .name-column {
            max-width: 200px;
            min-width: 150px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .return-column {
            width: 60px;
            white-space: nowrap;
            padding: 4px;
        }
        .ticker-column {
            width: 50px;
            white-space: nowrap;
            color: #1e90ff; 
            font-weight: bold; 
        }
    </style>
    <title>Broad Market Monitoring Report</title>
</head>
<body>
    <h1 class="header">{{ report_date }}</h1>
    <h1 class="header">{{report_name}} Report</h1>
    {% for period, items in data.items() %}
        <h2>{{ period}} Returns</h2>
        <table>
            <thead>
                <tr>
                    <th class="ticker-column">Ticker</th>
                    <th class="name-column">Company Name</th>
                    <th class="name-column">Sector</th>
                    <th class="name-column">Industry</th>
                    <th class="return-column">{{period}}_return</th>
                    <th class="return-column">{{period}}_SP500_return</th>
                    <th class="return-column">Threshold</th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                <tr>
                    <td class="ticker-column">{{ item['Ticker'] }}</td>
                    <td class="name-column">{{ item['CompanyName'] }}</td>
                    <td class="name-column">{{ item['Sector'] }}</td>
                    <td class="name-column">{{ item['Industry'] }}</td>
                    <td class="return-column {{ 'positive' if item[period + '_return'] > 0 else 'negative' }}">
                        {{ '%.2f%%' % (item[period + '_return'] * 100) }}
                    </td>
                      <td class="return-column {{ 'positive' if item[period +'_SP500_return'] > 0 else 'negative' }}">
                        {{ '%.2f%%' % (item[period + '_SP500_return'] * 100) }}
                    </td>
                    <td class="name-column">{{ item['Threshold'] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
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

def generate_market_scanner_html_report(data, report_date,report_name):
    template = Template(HTML_TEMPLATE2)
    html_content = template.render(data=data, report_date=report_date, report_name=report_name)
    output_file = f"./reports/{report_name}.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    return html_content
    
if __name__ == "__main__":
    data = pd.read_csv('data/broad_market_etfs.csv')
    report_date = "2025-01-09"
    res = generate_broad_market_monitoring_report_html(data, report_date)