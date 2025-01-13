import pandas as pd
import plotly.graph_objects as go
import os

# Read data from CSV
data = pd.read_csv('./data/sp500_pe_data.csv')

# Filter out rows with missing PE ratio values
data = data.round(2)

# Get the top 10 companies with the highest PE ratio
top_10_highest_pe = data.nlargest(10, 'PERatio')

# Get the top 10 companies with the lowest PE ratio
top_10_lowest_pe = data.nsmallest(10, 'PERatio')

# Calculate sector averages
sector_avg = data.groupby('Sector')['PERatio'].mean().round(2).sort_values(ascending=True)

# Create a bar chart for the top 10 companies with the highest PE ratio
fig_highest = go.Figure()
fig_highest.add_trace(go.Bar(
    y=top_10_highest_pe['CompanyName'],  # Switch to y-axis for horizontal bars
    x=top_10_highest_pe['PERatio'],      # Switch to x-axis for horizontal bars
    text=top_10_highest_pe['PERatio'].round(2),
    textposition='auto',
    orientation='h',                      # Set horizontal orientation
    marker_color='red',
    hovertemplate="Company: %{y}<br>PE Ratio: %{x}<br>Sector: " + top_10_highest_pe['Sector'] + "<extra></extra>"
))

# Update layout for better readability
fig_highest.update_layout(
    title={
        'text': 'Top 10 Companies with Highest PE Ratio',
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis_title='PE Ratio',
    yaxis_title=None,                     # Remove y-axis title
    yaxis={'categoryorder':'total ascending'},  # Sort bars
    height=500,
    margin=dict(l=20, r=20, t=40, b=20),
    showlegend=False
)

# Create a bar chart for the top 10 companies with the lowest PE ratio
fig_lowest = go.Figure()
fig_lowest.add_trace(go.Bar(
    y=top_10_lowest_pe['CompanyName'],    # Switch to y-axis for horizontal bars
    x=top_10_lowest_pe['PERatio'],        # Switch to x-axis for horizontal bars
    text=top_10_lowest_pe['PERatio'].round(2),
    textposition='auto',
    orientation='h',                       # Set horizontal orientation
    marker_color='green',
    hovertemplate="Company: %{y}<br>PE Ratio: %{x}<br>Sector: " + top_10_lowest_pe['Sector'] + "<extra></extra>"
))

# Update layout for better readability
fig_lowest.update_layout(
    title={
        'text': 'Top 10 Companies with Lowest PE Ratio',
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis_title='PE Ratio',
    yaxis_title=None,                      # Remove y-axis title
    yaxis={'categoryorder':'total ascending'},   # Sort bars
    height=500,
    margin=dict(l=20, r=20, t=40, b=20),
    showlegend=False
)

# Create sector average PE ratio chart
fig_sector = go.Figure()
fig_sector.add_trace(go.Bar(
    y=sector_avg.index,
    x=sector_avg.values,
    text=sector_avg.values,
    textposition='auto',
    orientation='h',
    marker_color='navy',
    hovertemplate="Sector: %{y}<br>Average PE: %{x:.1f}<extra></extra>"
))

fig_sector.update_layout(
    title={
        'text': 'Average PE Ratio by Sector',
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis_title='PE Ratio',
    yaxis_title=None,
    height=500,
    margin=dict(l=20, r=20, t=40, b=20),
    showlegend=False
)

# Ensure the output directory exists
output_dir = "C:/development/repo/stock_analytics/reports/PE_ratio"
os.makedirs(output_dir, exist_ok=True)

# Save the charts as HTML files
fig_highest.write_html(os.path.join(output_dir, "top_10_highest_pe.html"))
fig_lowest.write_html(os.path.join(output_dir, "top_10_lowest_pe.html"))
fig_sector.write_html(os.path.join(output_dir, "sector_pe_ratio.html"))

# Updated HTML template to match old version
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
        h1 {
            text-align: center;
            color: #333;
            padding: 20px 0;
            margin-bottom: 30px;
            border-bottom: 2px solid #ddd;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        iframe {
            display: block;
            background: white;
        }
    </style>
</head>
<body>
    <h1>PE Ratio Analysis Dashboard</h1>
    <div class="chart-container">
        <iframe src="sector_pe_ratio.html" width="100%" height="500px" style="border:none;"></iframe>
    </div>
    <div class="chart-container">
        <iframe src="top_10_highest_pe.html" width="100%" height="500px" style="border:none;"></iframe>
    </div>
    <div class="chart-container">
        <iframe src="top_10_lowest_pe.html" width="100%" height="500px" style="border:none;"></iframe>
    </div>
</body>
</html>
"""

# Save the combined HTML content to a file
output_file = os.path.join(output_dir, "pe_ratio_charts.html")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_template)

# Notify the user that the report generation is complete
print(f"HTML report generated: {output_file}")
