import pandas as pd
import numpy as np

def load_data(file_path: str) -> pd.DataFrame:
    """Load data from CSV or Excel file."""
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format")

def get_data_preview(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Return the first n rows of the dataframe."""
    return df.head(n)

def get_data_summary(df: pd.DataFrame) -> dict:
    """Generate summary statistics and info about the dataframe."""
    summary = {
        'n_rows': df.shape[0],
        'n_columns': df.shape[1],
        'memory_usage': round(df.memory_usage(deep=True).sum() / (1024 ** 2), 2),  # in MB
        'column_types': df.dtypes.apply(lambda x: str(x)).to_dict(),
        'missing_values': (df.isna().sum() / len(df) * 100).round(2).to_dict()
    }
    return summary

def suggest_analysis_types(df: pd.DataFrame) -> list:
    """Suggest analysis types based on dataframe characteristics."""
    suggestions = []
    if df.select_dtypes(include=['number']).shape[1] > 0:
        suggestions.append('descriptive_statistics')
        suggestions.append('distribution_analysis')
        suggestions.append('correlation_analysis')
        suggestions.append('outlier_analysis')
        suggestions.append('group_analysis')
        suggestions.append('clustering_analysis')
        suggestions.append('prediction_analysis')
    if df.select_dtypes(include=['datetime']).shape[1] > 0:
        suggestions.append('time_series_analysis')
    if df.isna().sum().sum() > 0:
        suggestions.append('missing_values_analysis')
    return suggestions

def preprocess_dataframe_for_arrow(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the dataframe to ensure columns 'Type' and 'Value' have consistent and Arrow-compatible types.
    - Convert 'Type' column to string type.
    - Convert 'Value' column to a consistent type (string if mixed types).
    """
    df_copy = df.copy()
    
    if 'Type' in df_copy.columns:
        df_copy['Type'] = df_copy['Type'].astype(str)
    
    if 'Value' in df_copy.columns:
        # Check if 'Value' column has mixed types
        if df_copy['Value'].apply(lambda x: isinstance(x, (int, float, type(None)))).all():
            # All numeric or None, convert to float
            df_copy['Value'] = pd.to_numeric(df_copy['Value'], errors='coerce')
        else:
            # Mixed types, convert all to string
            df_copy['Value'] = df_copy['Value'].astype(str)
    
    return df_copy

def get_column_statistics(df: pd.DataFrame, column: str) -> dict:
    """Calculate statistics for a specific column in the dataframe."""
    col_data = df[column]
    stats = {
        'count': col_data.count(),
        'missing': col_data.isna().sum(),
        'missing_pct': round((col_data.isna().sum() / len(col_data)) * 100, 2),
        'unique_values': col_data.nunique()
    }
    
    if pd.api.types.is_numeric_dtype(col_data):
        stats.update({
            'min': col_data.min(),
            'max': col_data.max(),
            'mean': col_data.mean(),
            'median': col_data.median(),
            'std': col_data.std(),
            'skew': col_data.skew(),
            'outliers_count': len(detect_outliers(df, column)),
            'outliers_pct': round((len(detect_outliers(df, column)) / len(col_data)) * 100, 2)
        })
    elif pd.api.types.is_datetime64_any_dtype(col_data):
        stats.update({
            'min': col_data.min(),
            'max': col_data.max(),
            'range_days': (col_data.max() - col_data.min()).days
        })
    else:
        # For categorical or text columns, get top values
        top_values = col_data.value_counts().head(5).to_dict()
        stats['top_values'] = top_values
    
    return stats

def detect_outliers(df: pd.DataFrame, column: str) -> list:
    """Detect outliers in a numeric column using the IQR method."""
    col_data = df[column]
    if not pd.api.types.is_numeric_dtype(col_data):
        return []
    
    Q1 = col_data.quantile(0.25)
    Q3 = col_data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)].index.tolist()
    return outliers
