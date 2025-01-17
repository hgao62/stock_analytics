import pandas as pd
import plotly.graph_objects as go
import os

# Read and process data
data = pd.read_csv('./data/sp500_pe_data.csv')
data = data.dropna(subset=['PERatio']).round(2)

# Calculate statistics with explicit column names
sector_stats = data.groupby('Sector')['PERatio'].agg(['mean', 'max', 'min', 'count']).reset_index()
sector_stats.rename(columns={'mean': 'sector_mean', 'max': 'sector_max', 'min': 'sector_min'}, inplace=True)

industry_stats = data.groupby('Industry')['PERatio'].agg(['mean', 'max', 'min']).reset_index()
industry_stats.rename(columns={'mean': 'industry_mean', 'max': 'industry_max', 'min': 'industry_min'}, inplace=True)

# Sort sector stats
sector_stats = sector_stats.sort_values('sector_mean', ascending=True)

# Get top 10 companies
top_10_highest_pe = data.nlargest(10, 'PERatio')
top_10_lowest_pe = data.nsmallest(10, 'PERatio')

# Merge with sector and industry statistics
top_10_highest_pe = top_10_highest_pe.merge(
    sector_stats[['Sector', 'sector_mean', 'sector_max', 'sector_min']], 
    on='Sector', 
    how='left'
)
top_10_highest_pe = top_10_highest_pe.merge(
    industry_stats[['Industry', 'industry_mean', 'industry_max', 'industry_min']], 
    on='Industry', 
    how='left'
)

top_10_lowest_pe = top_10_lowest_pe.merge(
    sector_stats[['Sector', 'sector_mean', 'sector_max', 'sector_min']], 
    on='Sector', 
    how='left'
)
top_10_lowest_pe = top_10_lowest_pe.merge(
    industry_stats[['Industry', 'industry_mean', 'industry_max', 'industry_min']], 
    on='Industry', 
    how='left'
)

# Sort data
top_10_highest_pe = top_10_highest_pe.sort_values('PERatio', ascending=True)
top_10_lowest_pe = top_10_lowest_pe.sort_values('PERatio', ascending=False)

# Create sector average chart
fig_sector = go.Figure()
fig_sector.add_trace(go.Bar(
    name='Sector Average PE',
    y=sector_stats['Sector'],
    x=sector_stats['sector_mean'],
    text=sector_stats['sector_mean'].round(1),
    textposition='outside',
    orientation='h',
    marker=dict(
        color=sector_stats['sector_mean'],
        colorscale='RdYlBu',
        reversescale=True,
        showscale=True,
        colorbar=dict(
            title="PE Ratio",
            thickness=15,
            len=0.5,
            x=0.85,
            y=0.5
        )
    ),
    hovertemplate="<b>%{y}</b><br>Average PE: %{x:.1f}<br>Companies: " + sector_stats['count'].astype(str) + "<extra></extra>"
))

fig_sector.update_layout(
    title=dict(text="Average PE Ratio by Sector", x=0.5, y=0.95, font=dict(size=24)),
    height=600,
    margin=dict(l=180, r=100, t=80, b=40),
    xaxis=dict(title="PE Ratio", titlefont=dict(size=18), tickfont=dict(size=16)),
    yaxis=dict(title=None, tickfont=dict(size=16)),
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white'
)

# Create comparison bar charts for highest/lowest PE
def create_comparison_chart(data, title, color):
    fig = go.Figure()
    
    # Company PE bars
    fig.add_trace(go.Bar(
        name='Company PE',
        y=data['CompanyName'],
        x=data['PERatio'],
        text=data['PERatio'].round(1),
        textposition='auto',
        orientation='h',
        marker_color=color,
        width=0.4,
        hovertemplate="Company: %{y}<br>PE Ratio: %{x:.1f}<extra></extra>",
        textfont=dict(size=20)  # Increased font size
    ))
    
    # Sector average bars
    fig.add_trace(go.Bar(
        name='Sector Average',
        y=data['CompanyName'],
        x=data['sector_mean'],  # Updated column name
        text=data['sector_mean'].round(1),
        textposition='auto',
        orientation='h',
        marker_color='navy',
        width=0.4,
        hovertemplate="Sector: " + data['Sector'] + "<br>Sector Avg PE: %{x:.1f}<extra></extra>",
        textfont=dict(size=20)  # Increased font size
    ))
    
    fig.update_layout(
        title_text=title,
        title_x=0.5,
        barmode='group',
        height=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=20)  # Increased font size
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis_title="PE Ratio",
        yaxis_title=None
    )
    
    return fig

fig_highest = create_comparison_chart(top_10_highest_pe, "Top 10 Companies with Highest PE Ratio vs Sector Average", 'red')
fig_lowest = create_comparison_chart(top_10_lowest_pe, "Top 10 Companies with Lowest PE Ratio vs Sector Average", 'green')

# Create detailed tables
def create_pe_table(data, title):
    return go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Company Name</b>', '<b>Sector</b>', '<b>Industry</b>', '<b>PE Ratio</b>', 
                   '<b>Sector Avg PE</b>', '<b>Sector Max PE</b>', '<b>Sector Min PE</b>', 
                   '<b>Industry Avg PE</b>', '<b>Industry Max PE</b>', '<b>Industry Min PE</b>'],
            fill_color='darkblue',
            font=dict(color='white', size=18),  # Increased font size
            align='center',
            line_color='black'
        ),
        cells=dict(
            values=[
                [f'<b>{val}</b>' for val in data.CompanyName],
                data.Sector,
                data.Industry,
                [f'<b>{val}</b>' for val in data.PERatio],
                data['sector_mean'],     # Updated column names
                data['sector_max'],
                data['sector_min'],
                data['industry_mean'],
                data['industry_max'],
                data['industry_min']
            ],
            fill=dict(color=['lightgrey', 'white', 'white', 'white', 'white', 'white', 'white', 'white', 'white', 'white']),
            font=dict(
                color=['black', 'black', 'black', 'red' if 'Highest' in title else 'green', 
                       'black', 'black', 'black', 'black', 'black', 'black'],
                size=[18, 18, 18, 20, 18, 18, 18, 18, 18, 18],  # Increased font size
                family='Arial'
            ),
            align='center',
            line_color='black'
        )
    )]).update_layout(title=title, height=1000)

top_10_highest_pe = top_10_highest_pe.sort_values('PERatio', ascending=False)
top_10_highest_pe = top_10_highest_pe.round(1)
top_10_lowest_pe = top_10_lowest_pe.round(1)
top_10_lowest_pe = top_10_lowest_pe.sort_values('PERatio', ascending=True)
table_highest = create_pe_table(top_10_highest_pe, "Top 10 Companies with Highest PE Ratio")
table_lowest = create_pe_table(top_10_lowest_pe, "Top 10 Companies with Lowest PE Ratio")

# Save all files
output_dir = "C:/development/repo/stock_analytics/reports/PE_ratio"
os.makedirs(output_dir, exist_ok=True)

# Save individual files
files_to_save = {
    "sector_pe_ratio.html": fig_sector,
    "top_10_highest_pe.html": fig_highest,
    "top_10_lowest_pe.html": fig_lowest,
    "top_10_highest_pe_table.html": table_highest,
    "top_10_lowest_pe_table.html": table_lowest
}

for filename, fig in files_to_save.items():
    fig.write_html(os.path.join(output_dir, filename))

# Create unified dashboard HTML
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PE Ratio Analysis Dashboard</title>
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
        .section-title {
            text-align: center;
            font-size: 28px;
            color: #333;
            margin: 40px 0 20px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
        }
        .chart-container, .table-container {
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
    
    <!-- Charts Section -->
    <div class="chart-container">
        <iframe src="sector_pe_ratio.html" width="100%" height="700px" style="border:none;"></iframe>
    </div>
    <div class="chart-container">
        <iframe src="top_10_highest_pe.html" width="100%" height="600px" style="border:none;"></iframe>
         <iframe src="top_10_highest_pe_table.html" width="100%" height="1000px" style="border:none;"></iframe>
    </div>
    <div class="chart-container">
        <iframe src="top_10_lowest_pe.html" width="100%" height="600px" style="border:none;"></iframe>
        <iframe src="top_10_lowest_pe_table.html" width="100%" height="1000px" style="border:none;"></iframe>
    </div>

    <!-- Tables Section -->
    <h2 class="section-title">Detailed Analysis</h2>
    <div class="table-container">
        <iframe src="top_10_highest_pe_table.html" width="100%" height="1000px" style="border:none;"></iframe>
    </div>
    <div class="table-container">
        <iframe src="top_10_lowest_pe_table.html" width="100%" height="1000px" style="border:none;"></iframe>
    </div>
</body>
</html>
"""

# Save the unified dashboard
with open(os.path.join(output_dir, "pe_ratio_dashboard.html"), "w", encoding="utf-8") as f:
    f.write(html_template)

print("PE Ratio Analysis Dashboard generated successfully!")
