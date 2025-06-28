import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional

# Configure plot styles
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams['font.size'] = 12

# Helper function for consistent chart theming
def apply_theme(fig):
    """Apply a consistent theme to Plotly figures"""
    fig.update_layout(
        plot_bgcolor='white',
        font=dict(
            family="Arial, sans-serif",
            size=12,
        ),
        margin=dict(l=60, r=40, t=40, b=60),
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#EEEEEE')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#EEEEEE')
    return fig

# Basic distribution visualizations
def plot_histogram(df: pd.DataFrame, column: str, bins: int = None, kde: bool = True):
    """Plot histogram for a numeric column"""
    if not pd.api.types.is_numeric_dtype(df[column]):
        st.error(f"Column '{column}' must be numeric to plot a histogram")
        return None
    
    nbins_value = bins if bins is not None else None
    
    fig = px.histogram(df, x=column, nbins=nbins_value, marginal='box', 
                     title=f'Distribution of {column}')
    return apply_theme(fig)

def plot_box(df: pd.DataFrame, column: str, group_by: Optional[str] = None):
    """Plot box plot for a numeric column, optionally grouped by a categorical column"""
    if not pd.api.types.is_numeric_dtype(df[column]):
        st.error(f"Column '{column}' must be numeric to plot a box plot")
        return None
    
    if group_by is not None and group_by not in df.columns:
        st.error(f"Column '{group_by}' not found in the dataset")
        return None
    
    if group_by is None:
        fig = px.box(df, y=column, title=f'Box Plot of {column}')
    else:
        fig = px.box(df, x=group_by, y=column, 
                   title=f'Box Plot of {column} grouped by {group_by}', 
                   color=group_by)
    
    return apply_theme(fig)

def plot_bar(df: pd.DataFrame, column: str, limit: int = 10):
    """Plot bar chart for a categorical column"""
    if column not in df.columns:
        st.error(f"Column '{column}' not found in the dataset")
        return None
    
    # Get value counts and limit to top N
    value_counts = df[column].value_counts().reset_index()
    value_counts.columns = [column, 'count']
    
    if len(value_counts) > limit:
        top_values = value_counts.head(limit-1)
        others_sum = pd.DataFrame({column: ['Others'], 
                                 'count': [value_counts['count'][limit-1:].sum()]})
        value_counts = pd.concat([top_values, others_sum])
    
    fig = px.bar(value_counts, x=column, y='count', 
                title=f'Frequency of {column} values', 
                text='count')
    
    fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    
    return apply_theme(fig)

# Correlation visualizations
def plot_correlation_matrix(df: pd.DataFrame, method: str = 'pearson'):
    """Plot correlation matrix heatmap"""
    numeric_df = df.select_dtypes(include=['number'])
    
    if len(numeric_df.columns) < 2:
        st.error("Need at least 2 numeric columns for correlation analysis")
        return None
    
    corr_matrix = numeric_df.corr(method=method).round(2)
    
    # Create heatmap with Plotly
    fig = px.imshow(corr_matrix, 
                  text_auto=True, 
                  color_continuous_scale='RdBu_r',
                  title=f'{method.capitalize()} Correlation Matrix')
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
    )
    
    return apply_theme(fig)

def plot_scatter(df: pd.DataFrame, x_col: str, y_col: str, color_col: Optional[str] = None):
    """Plot scatter plot between two numeric columns"""
    if x_col not in df.columns or y_col not in df.columns:
        st.error(f"Columns '{x_col}' or '{y_col}' not found in the dataset")
        return None
    
    if not pd.api.types.is_numeric_dtype(df[x_col]) or not pd.api.types.is_numeric_dtype(df[y_col]):
        st.error("Both columns must be numeric for scatter plot")
        return None
    
    if color_col is not None and color_col not in df.columns:
        st.error(f"Column '{color_col}' not found in the dataset")
        return None
    
    if color_col is None:
        fig = px.scatter(df, x=x_col, y=y_col, 
                       title=f'Scatter Plot: {y_col} vs {x_col}',
                       opacity=0.7)
    else:
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                       title=f'Scatter Plot: {y_col} vs {x_col}, colored by {color_col}',
                       opacity=0.7)
    
    # Add trend line
    if color_col is None and pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col]):
        fig.update_layout(showlegend=False)
        fig.add_traces(
            px.scatter(
                df, x=x_col, y=y_col, trendline="ols"
            ).data[1]
        )
    
    return apply_theme(fig)

# Time series visualizations
def plot_time_series(df: pd.DataFrame, date_column: str, value_column: str, 
                    agg_freq: Optional[str] = None, title: Optional[str] = None):
    """Plot time series data"""
    if date_column not in df.columns or value_column not in df.columns:
        st.error(f"Columns '{date_column}' or '{value_column}' not found in the dataset")
        return None
    
    # Ensure date column is datetime type
    try:
        df[date_column] = pd.to_datetime(df[date_column])
    except:
        st.error(f"Could not convert '{date_column}' to datetime")
        return None
    
    # Sort by date
    df_sorted = df.sort_values(by=date_column)
    
    # Aggregate if specified
    if agg_freq is not None:
        try:
            df_agg = df_sorted.set_index(date_column).resample(agg_freq).mean().reset_index()
        except:
            st.error(f"Could not resample with frequency '{agg_freq}'")
            return None
    else:
        df_agg = df_sorted
    
    chart_title = title or f'Time Series: {value_column} over time'
    
    fig = px.line(df_agg, x=date_column, y=value_column, 
                title=chart_title,
                markers=True)
    
    # If we have many points, remove markers
    if len(df_agg) > 50:
        fig.update_traces(mode='lines')
    
    return apply_theme(fig)

# Group analysis visualizations
def plot_group_bar(df: pd.DataFrame, group_column: str, value_column: str, 
                  agg_func: str = 'mean', horizontal: bool = False):
    """Plot bar chart for grouped data"""
    if group_column not in df.columns or value_column not in df.columns:
        st.error(f"Columns '{group_column}' or '{value_column}' not found in the dataset")
        return None
    
    if not pd.api.types.is_numeric_dtype(df[value_column]):
        st.error(f"Value column '{value_column}' must be numeric")
        return None
    
    # Group data
    try:
        if agg_func == 'mean':
            grouped = df.groupby(group_column)[value_column].mean().reset_index()
        elif agg_func == 'sum':
            grouped = df.groupby(group_column)[value_column].sum().reset_index()
        elif agg_func == 'count':
            grouped = df.groupby(group_column)[value_column].count().reset_index()
        elif agg_func == 'min':
            grouped = df.groupby(group_column)[value_column].min().reset_index()
        elif agg_func == 'max':
            grouped = df.groupby(group_column)[value_column].max().reset_index()
        else:
            st.error(f"Unsupported aggregation function: {agg_func}")
            return None
    except Exception as e:
        st.error(f"Error in grouping: {str(e)}")
        return None
    
    title = f'{agg_func.capitalize()} of {value_column} by {group_column}'
    
    if horizontal:
        fig = px.bar(grouped, y=group_column, x=value_column, 
                   title=title,
                   orientation='h',
                   text=value_column)
    else:
        fig = px.bar(grouped, x=group_column, y=value_column, 
                   title=title,
                   text=value_column)
    
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    
    return apply_theme(fig)

# Outlier visualizations
def plot_outliers(df: pd.DataFrame, column: str):
    """Plot box plot highlighting outliers"""
    if column not in df.columns:
        st.error(f"Column '{column}' not found in the dataset")
        return None
    
    if not pd.api.types.is_numeric_dtype(df[column]):
        st.error(f"Column '{column}' must be numeric for outlier analysis")
        return None
    
    # Calculate statistics for outlier detection
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Create data for plotting
    outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
    
    # Create a box plot
    fig = go.Figure()
    
    # Add box plot
    fig.add_trace(go.Box(
        y=df[column],
        name=column,
        boxpoints='outliers',
        jitter=0.3,
        pointpos=-1.8,
        marker_color='rgb(7,40,89)',
        marker_size=5,
        line_width=2
    ))
    
    # Highlight outliers with different markers
    if outlier_mask.sum() > 0:
        fig.add_trace(go.Scatter(
            y=df.loc[outlier_mask, column],
            mode='markers',
            name='Outliers',
            marker=dict(
                color='red',
                size=8,
                symbol='circle',
                line=dict(color='black', width=1)
            ),
            hovertemplate='Value: %{y}<extra></extra>'
        ))
    
    fig.update_layout(
        title=f'Box Plot with Outliers Highlighted - {column}',
        xaxis_title='',
        yaxis_title=column,
    )
    
    return apply_theme(fig)

# Missing value visualizations
def plot_missing_values(df: pd.DataFrame):
    """Plot missing values heatmap"""
    # Calculate missing values percentage
    missing_pct = df.isna().mean().sort_values(ascending=False) * 100
    columns_with_missing = missing_pct[missing_pct > 0].index.tolist()
    
    if not columns_with_missing:
        st.info("No missing values found in the dataset")
        return None
    
    # Create dataframe for heatmap
    missing_df = pd.DataFrame({'column': columns_with_missing,
                             'percent_missing': missing_pct[columns_with_missing].values})
    
    fig = px.bar(missing_df, x='column', y='percent_missing',
                title='Percentage of Missing Values by Column',
                labels={'percent_missing': '% Missing', 'column': 'Column'},
                text_auto='.1f')
    
    fig.update_traces(marker_color='#FFA07A', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45)
    
    return apply_theme(fig)

# Cluster analysis visualization
def plot_clusters(df_pca: pd.DataFrame, n_clusters: int):
    """Plot clusters from PCA results"""
    if 'pca1' not in df_pca.columns or 'pca2' not in df_pca.columns or 'cluster' not in df_pca.columns:
        st.error("PCA data not in expected format")
        return None
    
    fig = px.scatter(df_pca, x='pca1', y='pca2', color='cluster',
                   title=f'Cluster Analysis - {n_clusters} clusters',
                   labels={'pca1': 'Principal Component 1', 'pca2': 'Principal Component 2'},
                   color_discrete_sequence=px.colors.qualitative.G10)
    
    return apply_theme(fig)

# Feature importance visualization
def plot_feature_importance(feature_importance: List[Dict]):
    """Plot feature importance from ML model"""
    df = pd.DataFrame(feature_importance)
    
    if 'feature' not in df.columns or 'importance' not in df.columns:
        st.error("Feature importance data not in expected format")
        return None
    
    # Sort by importance
    df = df.sort_values('importance')
    
    fig = px.bar(df, y='feature', x='importance', 
               title='Feature Importance',
               orientation='h')
    
    return apply_theme(fig)