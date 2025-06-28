import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import base64

# Helper functions for chart creation
def create_bar_chart(df, x_col, y_col, agg_func):
    """Create a bar chart for the report."""
    if agg_func == "sum":
        data = df.groupby(x_col)[y_col].sum().reset_index()
    elif agg_func == "mean":
        data = df.groupby(x_col)[y_col].mean().reset_index()
    
    title = f"{agg_func.capitalize()} of {y_col} by {x_col}"
    fig = px.bar(data, x=x_col, y=y_col, title=title)
    fig.update_layout(xaxis_title=x_col, yaxis_title=y_col)
    return fig

def create_count_bar_chart(df, x_col):
    """Create a count-based bar chart."""
    data = df[x_col].value_counts().reset_index()
    data.columns = [x_col, 'count']
    
    title = f"Count of {x_col}"
    fig = px.bar(data, x=x_col, y='count', title=title)
    fig.update_layout(xaxis_title=x_col, yaxis_title='Count')
    return fig

def create_line_chart(df, x_col, y_col):
    """Create a line chart for the report."""
    # Ensure x_col is datetime
    df_copy = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_copy[x_col]):
        df_copy[x_col] = pd.to_datetime(df_copy[x_col], errors='coerce')
    
    # Sort by date
    df_copy = df_copy.sort_values(x_col)
    
    title = f"{y_col} over time"
    fig = px.line(df_copy, x=x_col, y=y_col, title=title)
    fig.update_layout(xaxis_title=x_col, yaxis_title=y_col)
    return fig

def create_scatter_plot(df, x_col, y_col, color_col):
    """Create a scatter plot for the report."""
    title = f"Scatter Plot of {y_col} vs {x_col}"
    
    if color_col:
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=title)
    else:
        fig = px.scatter(df, x=x_col, y=y_col, title=title)
    
    fig.update_layout(xaxis_title=x_col, yaxis_title=y_col)
    return fig

def create_histogram(df, col_name, bins):
    """Create a histogram for the report."""
    title = f"Distribution of {col_name}"
    fig = px.histogram(df, x=col_name, nbins=bins, title=title)
    fig.update_layout(xaxis_title=col_name, yaxis_title='Count')
    return fig

def create_box_plot(df, y_col, x_col):
    """Create a box plot for the report."""
    if x_col:
        title = f"Box Plot of {y_col} by {x_col}"
        fig = px.box(df, x=x_col, y=y_col, title=title)
    else:
        title = f"Box Plot of {y_col}"
        fig = px.box(df, y=y_col, title=title)
    
    return fig

def create_pie_chart(df, cat_col, value_col):
    """Create a pie chart for the report."""
    if value_col:
        data = df.groupby(cat_col)[value_col].sum().reset_index()
        values = value_col
        title = f"Distribution of {value_col} by {cat_col}"
    else:
        data = df[cat_col].value_counts().reset_index()
        data.columns = [cat_col, 'count']
        values = 'count'
        title = f"Distribution of {cat_col}"
    
    fig = px.pie(data, names=cat_col, values=values, title=title)
    return fig

def generate_html_report(report_items, df, file_name):
    """Generate an HTML report from the report items."""
    # Start with HTML header
    report_date = datetime.now().strftime("%Y-%m-%d")
    
    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Data Analysis Report - {file_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #3498db; margin-top: 30px; }}
            h3 {{ color: #2980b9; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #3498db; color: white; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .metric {{ display: inline-block; background: #f8f9fa; padding: 15px; margin: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
            .metric-label {{ font-size: 14px; color: #7f8c8d; }}
            .plot {{ width: 100%; height: auto; margin: 20px 0; }}
            footer {{ margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; color: #7f8c8d; font-size: 12px; }}
        </style>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <div class="container">
            <h1>Data Analysis Report - {file_name}</h1>
            <p><em>Generated on {report_date}</em></p>
            <hr>
    """
    
    # Add each report item
    for item in report_items:
        if item["type"] == "text":
            if item["text_type"] == "Title":
                html += f"<h2>{item['content']}</h2>\n"
            elif item["text_type"] == "Subtitle":
                html += f"<h3>{item['content']}</h3>\n"
            else:  # Paragraph
                html += f"<p>{item['content']}</p>\n"
        
        elif item["type"] == "dataset_summary":
            summary = item["summary"]
            
            html += f"""<h2>Dataset Summary</h2>
            <div>
                <div class="metric">
                    <div class="metric-value">{summary["n_rows"]}</div>
                    <div class="metric-label">Rows</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary["n_columns"]}</div>
                    <div class="metric-label">Columns</div>
                </div>
            </div>
            
            <h3>Column Types</h3>
            <table>
                <tr>
                    <th>Column</th>
                    <th>Type</th>
                </tr>
            """
            
            for col, dtype in summary["column_types"].items():
                html += f"<tr><td>{col}</td><td>{dtype}</td></tr>\n"
            
            html += "</table>\n"
            
            # Missing values
            if isinstance(summary["missing_values"], dict) and summary["missing_values"]:
                html += f"""<h3>Missing Values</h3>
                <table>
                    <tr>
                        <th>Column</th>
                        <th>Missing Values</th>
                    </tr>
                """
                
                for col, missing in summary["missing_values"].items():
                    html += f"<tr><td>{col}</td><td>{missing}</td></tr>\n"
                
                html += "</table>\n"
        
        elif item["type"] == "data_preview":
            preview_df = df.head(item["rows"])
            
            html += f"<h2>Data Preview</h2>\n"
            html += "<table>\n"
            
            # Add table header
            html += "<tr>\n"
            for col in preview_df.columns:
                html += f"<th>{col}</th>\n"
            html += "</tr>\n"
            
            # Add table rows
            for _, row in preview_df.iterrows():
                html += "<tr>\n"
                for val in row:
                    html += f"<td>{val}</td>\n"
                html += "</tr>\n"
            
            html += "</table>\n"
        
        elif item["type"] == "chart":
            fig = item["figure"]
            # Convert Plotly figure to HTML
            chart_html = fig.to_html(full_html=False)
            html += f"<div class='plot'>{chart_html}</div>\n"
        
        elif item["type"] == "analysis_result":
            analysis = item["analysis"]
            html += f"<h2>Analysis Result: {analysis['type']}</h2>\n"
            html += f"<p><strong>Time:</strong> {analysis['timestamp']}</p>\n"
            html += f"<p><strong>Columns:</strong> {', '.join(analysis['columns'])}</p>\n"
            html += "<p>Analysis details are available in the analysis section of the application.</p>\n"
        
        html += "<hr>\n"
    
    # Add footer and close HTML
    html += f"""<footer>
            Report generated by EasyAnalytics on {report_date}.
            </footer>
        </div>
    </body>
    </html>
    """
    
    return html