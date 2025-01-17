import pandas as pd
import plotly.graph_objects as go
import os

# Read data from CSV
data = pd.read_csv('./data/sp500_pe_data.csv')

# Filter out rows with missing PE ratio values
data = data.round(2)

# Calculate sector averages
sector_avg = data.groupby('Sector')['PERatio'].agg(['mean', 'count']).reset_index()
sector_avg['mean'] = sector_avg['mean'].round(2)

# Sort sector averages by mean PE ratio (descending)
sector_avg = sector_avg.sort_values('mean', ascending=True)

# Define sector colors
sector_colors = {
    'Technology': '#2E86C1',
    'Healthcare': '#27AE60',
    'Financial Services': '#8E44AD',
    'Consumer Cyclical': '#E74C3C',
    'Industrials': '#F39C12',
    'Communication Services': '#16A085',
    'Consumer Defensive': '#2C3E50',
    'Energy': '#E67E22',
    'Basic Materials': '#9B59B6',
    'Real Estate': '#C0392B',
    'Utilities': '#1ABC9C'
}

# Create sector average PE ratio chart with updated styling
fig_sector = go.Figure()
fig_sector.add_trace(go.Bar(
    name='Sector Average PE',
    y=sector_avg['Sector'],
    x=sector_avg['mean'],
    text=sector_avg['mean'].round(1),
    textposition='outside',  # Changed to outside
    orientation='h',
    marker=dict(
        color=sector_avg['mean'],  # Color based on value
        colorscale='RdYlBu',      # Red-Yellow-Blue color scale
        reversescale=True,        # Reverse the color scale
        showscale=True,           # Show the color scale
        colorbar=dict(
            title="PE Ratio",
            thickness=15,
            len=0.5,
            x=0.85,
            y=0.5
        )
    ),
    hovertemplate="<b>%{y}</b><br>Average PE: %{x:.1f}<br>Companies: " + sector_avg['count'].astype(str) + "<extra></extra>"
))

# Update sector chart layout with increased height
fig_sector.update_layout(
    title=dict(
        text="Average PE Ratio by Sector",
        x=0.5,
        y=0.95,
        font=dict(size=20)
    ),
    height=600,  # Increased from 500 to 700
    margin=dict(l=180, r=100, t=80, b=40),
    xaxis=dict(
        title="PE Ratio",
        titlefont=dict(size=14),
        tickfont=dict(size=12)
    ),
    yaxis=dict(
        title=None,
        tickfont=dict(size=12)
    ),
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white'
)

# Get the top 10 companies with the highest PE ratio
top_10_highest_pe = data.nlargest(10, 'PERatio')
# Merge with sector averages
top_10_highest_pe = top_10_highest_pe.merge(sector_avg[['Sector', 'mean']], on='Sector', how='left')

# Sort highest PE data by PE ratio (descending)
top_10_highest_pe = top_10_highest_pe.sort_values('PERatio', ascending=True)

# Get the top 10 companies with the lowest PE ratio
top_10_lowest_pe = data.nsmallest(10, 'PERatio')
# Merge with sector averages
top_10_lowest_pe = top_10_lowest_pe.merge(sector_avg[['Sector', 'mean']], on='Sector', how='left')

# Sort lowest PE data by PE ratio (ascending)
top_10_lowest_pe = top_10_lowest_pe.sort_values('PERatio', ascending=False)

# Create bar chart for highest PE ratios
fig_highest = go.Figure()

# Add bars for company PE ratios
fig_highest.add_trace(go.Bar(
    name='Company PE',
    y=top_10_highest_pe['CompanyName'],
    x=top_10_highest_pe['PERatio'],
    text=top_10_highest_pe['PERatio'].round(1),
    textposition='auto',
    orientation='h',
    marker_color='red',
    width=0.4,
    hovertemplate="Company: %{y}<br>PE Ratio: %{x:.1f}<extra></extra>"
))

# Add bars for sector averages
fig_highest.add_trace(go.Bar(
    name='Sector Average',
    y=top_10_highest_pe['CompanyName'],
    x=top_10_highest_pe['mean'],
    text=top_10_highest_pe['mean'].round(1),
    textposition='auto',
    orientation='h',
    marker_color='navy',
    width=0.4,
    hovertemplate="Sector: " + top_10_highest_pe['Sector'] + "<br>Sector Avg PE: %{x:.1f}<extra></extra>"
))

# Update layout for highest PE ratio figure
fig_highest.update_layout(
    title_text="Top 10 Companies with Highest PE Ratio vs Sector Average",
    title_x=0.5,
    barmode='group',
    height=600,
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    margin=dict(l=20, r=20, t=60, b=20),
    xaxis_title="PE Ratio",
    yaxis_title=None
)

# Create bar chart for lowest PE ratios
fig_lowest = go.Figure()

# Add bars for company PE ratios
fig_lowest.add_trace(go.Bar(
    name='Company PE',
    y=top_10_lowest_pe['CompanyName'],
    x=top_10_lowest_pe['PERatio'],
    text=top_10_lowest_pe['PERatio'].round(1),
    textposition='auto',
    orientation='h',
    marker_color='green',
    width=0.4,
    hovertemplate="Company: %{y}<br>PE Ratio: %{x:.1f}<extra></extra>"
))

# Add bars for sector averages
fig_lowest.add_trace(go.Bar(
    name='Sector Average',
    y=top_10_lowest_pe['CompanyName'],
    x=top_10_lowest_pe['mean'],
    text=top_10_lowest_pe['mean'].round(1),
    textposition='auto',
    orientation='h',
    marker_color='navy',
    width=0.4,
    hovertemplate="Sector: " + top_10_lowest_pe['Sector'] + "<br>Sector Avg PE: %{x:.1f}<extra></extra>"
))

# Update layout for lowest PE ratio figure
fig_lowest.update_layout(
    title_text="Top 10 Companies with Lowest PE Ratio vs Sector Average",
    title_x=0.5,
    barmode='group',
    height=600,
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    margin=dict(l=20, r=20, t=60, b=20),
    xaxis_title="PE Ratio",
    yaxis_title=None
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
        <iframe src="sector_pe_ratio.html" width="100%" height="700px" style="border:none;"></iframe>
    </div>
    <div class="chart-container">
        <iframe src="top_10_highest_pe.html" width="100%" height="600px" style="border:none;"></iframe>
    </div>
    <div class="chart-container">
        <iframe src="top_10_lowest_pe.html" width="100%" height="600px" style="border:none;"></iframe>
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
