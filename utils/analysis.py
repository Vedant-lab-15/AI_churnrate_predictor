import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any, Optional
import json
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score

# Descriptive statistics analysis
def descriptive_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate descriptive statistics for numeric columns."""
    numeric_df = df.select_dtypes(include=['number'])
    if len(numeric_df.columns) == 0:
        return {"error": "No numeric columns found in the dataset"}
    
    stats = numeric_df.describe().round(2).to_dict()
    
    # Add additional statistics
    for col in numeric_df.columns:
        stats[col]['skew'] = numeric_df[col].skew().round(2)
        stats[col]['kurtosis'] = numeric_df[col].kurtosis().round(2)
    
    return stats

# Distribution analysis
def distribution_analysis(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Analyze the distribution of a column."""
    if column not in df.columns:
        return {"error": f"Column '{column}' not found in the dataset"}
    
    result = {}
    
    if pd.api.types.is_numeric_dtype(df[column]):
        # Numeric column
        result['type'] = 'numeric'
        result['stats'] = {
            'min': float(df[column].min()),
            'max': float(df[column].max()),
            'mean': float(df[column].mean()),
            'median': float(df[column].median()),
            'std': float(df[column].std()),
            'skew': float(df[column].skew()),
            'kurtosis': float(df[column].kurtosis())
        }
        
        # Calculate histogram data
        hist_data = np.histogram(df[column].dropna(), bins='auto')
        result['histogram'] = {
            'counts': hist_data[0].tolist(),
            'bin_edges': hist_data[1].tolist()
        }
        
    else:
        # Categorical column
        result['type'] = 'categorical'
        value_counts = df[column].value_counts().reset_index()
        value_counts.columns = ['value', 'count']
        
        result['value_counts'] = value_counts.to_dict('records')
        
    return result

# Correlation analysis
def correlation_analysis(df: pd.DataFrame, method: str = 'pearson') -> Dict[str, Any]:
    """Calculate correlation between numeric columns."""
    numeric_df = df.select_dtypes(include=['number'])
    if len(numeric_df.columns) < 2:
        return {"error": "Need at least 2 numeric columns for correlation analysis"}
    
    corr_matrix = numeric_df.corr(method=method).round(2)
    
    # Convert to format suitable for heatmap visualization
    corr_data = []
    for i, row_name in enumerate(corr_matrix.index):
        for j, col_name in enumerate(corr_matrix.columns):
            corr_data.append({
                'row': row_name,
                'column': col_name,
                'correlation': corr_matrix.iloc[i, j]
            })
    
    return {
        'correlation_matrix': corr_matrix.to_dict(),
        'correlation_data': corr_data,
        'method': method
    }

# Time series analysis
def time_series_analysis(df: pd.DataFrame, date_column: str, value_column: str) -> Dict[str, Any]:
    """Analyze time series data."""
    if date_column not in df.columns or value_column not in df.columns:
        return {"error": f"Columns '{date_column}' or '{value_column}' not found in the dataset"}
    
    # Ensure date column is datetime type
    try:
        df[date_column] = pd.to_datetime(df[date_column])
    except:
        return {"error": f"Could not convert '{date_column}' to datetime"}
    
    # Sort by date
    df_sorted = df.sort_values(by=date_column)
    
    # Resample to different frequencies
    result = {}
    
    # Original time series data
    ts_data = df_sorted[[date_column, value_column]].dropna()
    result['original'] = ts_data.to_dict('records')
    
    # Daily aggregation
    if len(ts_data) > 1:
        try:
            df_daily = ts_data.set_index(date_column).resample('D').mean()
            result['daily'] = df_daily.reset_index().to_dict('records')
            
            # Weekly aggregation
            df_weekly = ts_data.set_index(date_column).resample('W').mean()
            result['weekly'] = df_weekly.reset_index().to_dict('records')
            
            # Monthly aggregation
            df_monthly = ts_data.set_index(date_column).resample('M').mean()
            result['monthly'] = df_monthly.reset_index().to_dict('records')
            
            # Calculate trend (simple moving average)
            window_size = max(2, len(ts_data) // 10)  # Dynamic window size
            df_trend = ts_data.set_index(date_column)
            df_trend['trend'] = df_trend[value_column].rolling(window=window_size).mean()
            result['trend'] = df_trend.reset_index().to_dict('records')
        except Exception as e:
            result['error'] = f"Error in resampling: {str(e)}"
    
    return result

# Group analysis
def group_analysis(df: pd.DataFrame, group_column: str, value_column: str, agg_func: str = 'mean') -> Dict[str, Any]:
    """Analyze data grouped by a categorical column."""
    if group_column not in df.columns or value_column not in df.columns:
        return {"error": f"Columns '{group_column}' or '{value_column}' not found in the dataset"}
    
    # Check if value column is numeric
    if not pd.api.types.is_numeric_dtype(df[value_column]):
        return {"error": f"Value column '{value_column}' must be numeric"}
    
    # Group data
    try:
        if agg_func == 'mean':
            grouped = df.groupby(group_column)[value_column].mean()
        elif agg_func == 'sum':
            grouped = df.groupby(group_column)[value_column].sum()
        elif agg_func == 'count':
            grouped = df.groupby(group_column)[value_column].count()
        elif agg_func == 'min':
            grouped = df.groupby(group_column)[value_column].min()
        elif agg_func == 'max':
            grouped = df.groupby(group_column)[value_column].max()
        else:
            return {"error": f"Unsupported aggregation function: {agg_func}"}
        
        # Calculate additional statistics
        group_stats = df.groupby(group_column)[value_column].agg(['mean', 'std', 'count']).reset_index()
        stats_dict = group_stats.to_dict('records')
        
        # Prepare data for visualization
        grouped_data = grouped.reset_index()
        grouped_data.columns = [group_column, agg_func]
        
        return {
            'grouped_data': grouped_data.to_dict('records'),
            'group_stats': stats_dict,
            'aggregation': agg_func
        }
        
    except Exception as e:
        return {"error": f"Error in grouping: {str(e)}"}

# Outlier analysis
def outlier_analysis(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Analyze outliers in a column."""
    if column not in df.columns:
        return {"error": f"Column '{column}' not found in the dataset"}
    
    # Check if column is numeric
    if not pd.api.types.is_numeric_dtype(df[column]):
        return {"error": f"Column '{column}' must be numeric for outlier analysis"}
    
    # Calculate statistics
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Identify outliers
    outliers_iqr = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    
    # Z-score method
    z_scores = (df[column] - df[column].mean()) / df[column].std()
    outliers_zscore = df[abs(z_scores) > 3]
    
    return {
        'stats': {
            'Q1': float(Q1),
            'median': float(df[column].median()),
            'Q3': float(Q3),
            'IQR': float(IQR),
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'mean': float(df[column].mean()),
            'std': float(df[column].std())
        },
        'outliers_iqr': {
            'count': len(outliers_iqr),
            'percentage': round((len(outliers_iqr) / len(df)) * 100, 2),
            'values': outliers_iqr[column].tolist() if len(outliers_iqr) < 100 else outliers_iqr[column].tolist()[:100]
        },
        'outliers_zscore': {
            'count': len(outliers_zscore),
            'percentage': round((len(outliers_zscore) / len(df)) * 100, 2),
            'values': outliers_zscore[column].tolist() if len(outliers_zscore) < 100 else outliers_zscore[column].tolist()[:100]
        }
    }

# Missing values analysis
def missing_values_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze missing values in the dataset."""
    # Calculate missing values per column
    missing = pd.DataFrame({
        'column': df.columns,
        'count': df.isna().sum().values,
        'percentage': (df.isna().sum().values / len(df) * 100).round(2)
    })
    
    # Sort by number of missing values
    missing = missing.sort_values('count', ascending=False)
    
    # Calculate overall statistics
    total_cells = np.prod(df.shape)
    total_missing = df.isna().sum().sum()
    
    return {
        'per_column': missing.to_dict('records'),
        'overall': {
            'total_cells': int(total_cells),
            'total_missing': int(total_missing),
            'percentage': round(total_missing / total_cells * 100, 2)
        }
    }

# Clustering analysis
def clustering_analysis(df: pd.DataFrame, columns: List[str], n_clusters: int = 3) -> Dict[str, Any]:
    """Perform cluster analysis on selected columns."""
    # Check if all columns exist
    for col in columns:
        if col not in df.columns:
            return {"error": f"Column '{col}' not found in the dataset"}
    
    # Check if all columns are numeric
    df_subset = df[columns]
    if not all(pd.api.types.is_numeric_dtype(df_subset[col]) for col in columns):
        return {"error": "All columns must be numeric for clustering analysis"}
    
    # Handle missing values
    df_clean = df_subset.dropna()
    if len(df_clean) < 10:
        return {"error": "Too few complete rows for clustering analysis"}
    
    # Scale data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df_clean)
    
    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(scaled_data)
    
    # Add cluster labels to dataframe
    df_result = df_clean.copy()
    df_result['cluster'] = clusters
    
    # Calculate cluster statistics
    cluster_stats = []
    for i in range(n_clusters):
        cluster_df = df_result[df_result['cluster'] == i]
        stats = {}
        for col in columns:
            stats[col] = {
                'mean': float(cluster_df[col].mean()),
                'median': float(cluster_df[col].median()),
                'min': float(cluster_df[col].min()),
                'max': float(cluster_df[col].max()),
                'std': float(cluster_df[col].std())
            }
        cluster_stats.append({
            'cluster': i,
            'count': len(cluster_df),
            'percentage': round(len(cluster_df) / len(df_result) * 100, 2),
            'stats': stats
        })
    
    # Perform PCA for visualization if more than 2 dimensions
    if len(columns) > 2:
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(scaled_data)
        df_pca = pd.DataFrame({
            'pca1': pca_result[:, 0],
            'pca2': pca_result[:, 1],
            'cluster': clusters
        })
        pca_explained_variance = pca.explained_variance_ratio_
        
        return {
            'pca_data': df_pca.to_dict('records'),
            'pca_explained_variance': pca_explained_variance.tolist(),
            'cluster_stats': cluster_stats,
            'n_clusters': n_clusters,
            'centroids': kmeans.cluster_centers_.tolist()
        }
    else:
        # For 1-2 dimensions, return original data with cluster labels
        vis_data = df_result.reset_index().to_dict('records')
        return {
            'data': vis_data,
            'cluster_stats': cluster_stats,
            'n_clusters': n_clusters,
            'centroids': kmeans.cluster_centers_.tolist()
        }

# Prediction analysis (simple ML)
def prediction_analysis(df: pd.DataFrame, target_column: str, feature_columns: List[str], 
                       test_size: float = 0.2) -> Dict[str, Any]:
    """Perform simple prediction analysis."""
    # Check if all columns exist
    for col in feature_columns + [target_column]:
        if col not in df.columns:
            return {"error": f"Column '{col}' not found in the dataset"}
    
    # Check if all feature columns are numeric
    for col in feature_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return {"error": f"Feature column '{col}' must be numeric"}
    
    # Handle missing values
    df_clean = df[feature_columns + [target_column]].dropna()
    if len(df_clean) < 20:  # Minimum sample size for ML
        return {"error": "Too few complete rows for prediction analysis"}
    
    X = df_clean[feature_columns]
    y = df_clean[target_column]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    result = {}
    
    # Check if target is numeric or categorical
    if pd.api.types.is_numeric_dtype(y):
        # Regression
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        result['model_type'] = 'regression'
        result['metrics'] = {
            'mse': float(mse),
            'rmse': float(rmse),
            'r2': float(r2)
        }
        
    else:
        # Classification
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        try:
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
        except:
            precision = recall = f1 = None
        
        result['model_type'] = 'classification'
        result['metrics'] = {
            'accuracy': float(accuracy),
        }
        
        if precision is not None:
            result['metrics']['precision'] = float(precision)
            result['metrics']['recall'] = float(recall)
            result['metrics']['f1'] = float(f1)
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    result['feature_importance'] = feature_importance.to_dict('records')
    
    return result