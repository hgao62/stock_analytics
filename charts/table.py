import pandas as pd
import plotly.graph_objects as go
import os

# Read data from CSV
data = pd.read_csv('./data/sp500_pe_data.csv')

# Filter out rows with missing PE ratio values
data = data.dropna(subset=['PERatio'])

# Calculate sector and industry statistics
sector_stats = data.groupby('Sector')['PERatio'].agg(['mean', 'max', 'min']).reset_index()
industry_stats = data.groupby('Industry')['PERatio'].agg(['mean', 'max', 'min']).reset_index()

# Get the top 10 companies with the highest PE ratio
top_10_highest_pe = data.nlargest(10, 'PERatio')

# Get the top 10 companies with the lowest PE ratio
top_10_lowest_pe = data.nsmallest(10, 'PERatio')

# Merge the sector and industry stats with the top 10 companies
top_10_highest_pe = top_10_highest_pe.merge(sector_stats, on='Sector', suffixes=('', '_sector'))
top_10_highest_pe = top_10_highest_pe.merge(industry_stats, on='Industry', suffixes=('', '_industry'))

top_10_lowest_pe = top_10_lowest_pe.merge(sector_stats, on='Sector', suffixes=('', '_sector'))
top_10_lowest_pe = top_10_lowest_pe.merge(industry_stats, on='Industry', suffixes=('', '_industry'))

# Round numbers to 1 decimal place
data['PERatio'] = data['PERatio'].round(1)
sector_stats[['mean', 'max', 'min']] = sector_stats[['mean', 'max', 'min']].round(1)
industry_stats[['mean', 'max', 'min']] = industry_stats[['mean', 'max', 'min']].round(1)
top_10_highest_pe[['PERatio', 'mean', 'max', 'min', 'mean_industry', 'max_industry', 'min_industry']] = top_10_highest_pe[['PERatio', 'mean', 'max', 'min', 'mean_industry', 'max_industry', 'min_industry']].round(1)
top_10_lowest_pe[['PERatio', 'mean', 'max', 'min', 'mean_industry', 'max_industry', 'min_industry']] = top_10_lowest_pe[['PERatio', 'mean', 'max', 'min', 'mean_industry', 'max_industry', 'min_industry']].round(1)

# Create a table for the top 10 companies with the highest PE ratio
fig_highest = go.Figure(data=[go.Table(
    header=dict(values=['<b>Company Name</b>', '<b>Sector</b>', '<b>Industry</b>', '<b>PE Ratio</b>', '<b>Sector Avg PE</b>', '<b>Sector Max PE</b>', '<b>Sector Min PE</b>', '<b>Industry Avg PE</b>', '<b>Industry Max PE</b>', '<b>Industry Min PE</b>'],
                fill_color='darkblue',
                font=dict(color='white', size=14),
                align='center',
                line_color='black'),
    cells=dict(values=[[f'<b>{val}</b>' for val in top_10_highest_pe.CompanyName], 
                      top_10_highest_pe.Sector, top_10_highest_pe.Industry, 
                      [f'<b>{val}</b>' for val in top_10_highest_pe.PERatio], 
                      top_10_highest_pe['mean'], top_10_highest_pe['max'], top_10_highest_pe['min'], 
                      top_10_highest_pe['mean_industry'], top_10_highest_pe['max_industry'], top_10_highest_pe['min_industry']],
               fill=dict(color=['lightgrey', 'white', 'white', 'white', 'white', 'white', 'white', 'white', 'white', 'white']),
               font=dict(color=['black', 'black', 'black', 'darkred', 'black', 'black', 'black', 'black', 'black', 'black'], 
                        size=[13, 13, 13, 15, 13, 13, 13, 13, 13, 13],
                        family='Arial'),
               align='center',
               line_color='black'))
])

# Create a table for the top 10 companies with the lowest PE ratio
fig_lowest = go.Figure(data=[go.Table(
    header=dict(values=['<b>Company Name</b>', '<b>Sector</b>', '<b>Industry</b>', '<b>PE Ratio</b>', '<b>Sector Avg PE</b>', '<b>Sector Max PE</b>', '<b>Sector Min PE</b>', '<b>Industry Avg PE</b>', '<b>Industry Max PE</b>', '<b>Industry Min PE</b>'],
                fill_color='darkblue',
                font=dict(color='white', size=14),
                align='center',
                line_color='black'),
    cells=dict(values=[[f'<b>{val}</b>' for val in top_10_lowest_pe.CompanyName], 
                      top_10_lowest_pe.Sector, top_10_lowest_pe.Industry, 
                      [f'<b>{val}</b>' for val in top_10_lowest_pe.PERatio], 
                      top_10_lowest_pe['mean'], top_10_lowest_pe['max'], top_10_lowest_pe['min'], 
                      top_10_lowest_pe['mean_industry'], top_10_lowest_pe['max_industry'], top_10_lowest_pe['min_industry']],
               fill=dict(color=['lightgrey', 'white', 'white', 'white', 'white', 'white', 'white', 'white', 'white', 'white']),
               font=dict(color=['black', 'black', 'black', 'green', 'black', 'black', 'black', 'black', 'black', 'black'],
                        size=[13, 13, 13, 15, 13, 13, 13, 13, 13, 13],
                        family='Arial'),
               align='center',
               line_color='black'))
])

# Update layout for the highest PE ratio table
fig_highest.update_layout(
    title='Top 10 Companies with Highest PE Ratio',
    height=1000  # Increase height to accommodate all rows
)

# Update layout for the lowest PE ratio table
fig_lowest.update_layout(
    title='Top 10 Companies with Lowest PE Ratio',
    height=1000  # Increase height to accommodate all rows
)

# Ensure the output directory exists
output_dir = "C:/development/repo/stock_analytics/reports/PE_ratio"
os.makedirs(output_dir, exist_ok=True)

# Save the tables as HTML files
fig_highest.write_html(os.path.join(output_dir, "top_10_highest_pe_table.html"))
fig_lowest.write_html(os.path.join(output_dir, "top_10_lowest_pe_table.html"))

# Update HTML template to include both charts and tables in a unified dashboard
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PE Ratio Analysis</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1, h2 {
            text-align: center;
            color: #333;
        }
        h1 {
            padding: 20px 0;
            margin-bottom: 30px;
            border-bottom: 2px solid #ddd;
        }
        h2 {
            margin-top: 40px;
            font-size: 24px;
        }
        .chart-container, .table-container {
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .section-title {
            text-align: center;
            font-size: 28px;
            color: #333;
            margin: 40px 0 20px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
        }
        iframe {
            display: block;
            background: white;
        }
    </style>
</head>
<body>
    <h1>PE Ratio Analysis Dashboard</h1>
    
    <!-- Visualizations Section -->
    <h2 class="section-title">PE Ratio Charts</h2>
    <div class="chart-container">
        <iframe src="sector_pe_ratio.html" width="100%" height="700px" style="border:none;"></iframe>
    </div>
    <div class="chart-container">
        <iframe src="top_10_highest_pe.html" width="100%" height="600px" style="border:none;"></iframe>
    </div>
    <div class="chart-container">
        <iframe src="top_10_lowest_pe.html" width="100%" height="600px" style="border:none;"></iframe>
    </div>

    <!-- Tables Section -->
    <h2 class="section-title">PE Ratio Detailed Tables</h2>
    <div class="table-container">
        <iframe src="top_10_highest_pe_table.html" width="100%" height="1000px" style="border:none;"></iframe>
    </div>
    <div class="table-container">
        <iframe src="top_10_lowest_pe_table.html" width="100%" height="1000px" style="border:none;"></iframe>
    </div>
</body>
</html>
"""

# Update the output filename to indicate it's the main dashboard
output_file = os.path.join(output_dir, "pe_ratio_dashboard.html")

# Save the combined HTML content to a file
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_template)

# Notify the user that the report generation is complete
print(f"HTML report generated: {output_file}")
