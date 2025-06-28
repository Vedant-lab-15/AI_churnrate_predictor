import streamlit as st
import pandas as pd
import numpy as np
from utils.data_processing import get_column_statistics, detect_outliers
from utils.visualization import plot_histogram, plot_box, plot_bar, plot_outliers, plot_missing_values

from utils.data_processing import preprocess_dataframe_for_arrow

def render_explore_page():
    """Render the data exploration page."""
    st.header("🔍 Explore Your Data")
    
    # Check if data is loaded
    if 'current_data' not in st.session_state or st.session_state.current_data is None:
        st.warning("Please upload a dataset first!")
        if st.button("Go to Upload Page"):
            st.session_state.page = "upload"
            st.experimental_rerun()
        return
    
    # Get the data
    df = st.session_state.current_data
    file_name = st.session_state.file_name
    
    # Preprocess dataframe for Arrow compatibility
    df = preprocess_dataframe_for_arrow(df)
    
    st.markdown(f"Exploring dataset: **{file_name}**")
    
    # Create tabs for different exploration views
    tabs = st.tabs(["📊 Overview", "📋 Data Viewer", "🧮 Column Stats", "⚠️ Missing Values", "🔎 Insights"])
    
    # Overview tab
    with tabs[0]:
        render_overview_tab(df)
    
    # Data viewer tab
    with tabs[1]:
        render_data_viewer_tab(df)
    
    # Column stats tab
    with tabs[2]:
        render_column_stats_tab(df)
    
    # Missing values tab
    with tabs[3]:
        render_missing_values_tab(df)
    
    # Insights tab
    with tabs[4]:
        render_insights_tab(df)

def render_overview_tab(df):
    """Render the overview tab content."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Dataset Summary")
        summary = st.session_state.data_summary
        
        # Display summary metrics
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        with metrics_col1:
            st.metric("Rows", summary['n_rows'])
        with metrics_col2:
            st.metric("Columns", summary['n_columns'])
        with metrics_col3:
            st.metric("Memory Usage", f"{summary['memory_usage']} MB")
        
        # Column types summary
        column_type_counts = pd.Series(summary['column_types']).value_counts()
        st.markdown("### Column Types Distribution")
        st.bar_chart(column_type_counts)
        
    with col2:
        st.subheader("Data Quality")
        
        # Missing values summary
        missing_values = summary['missing_values']
        columns_with_missing = [col for col, pct in missing_values.items() if pct > 0]
        
        if columns_with_missing:
            st.markdown(f"**{len(columns_with_missing)}** columns have missing values")
            
            # Show columns with highest missing percentages
            missing_df = pd.DataFrame({
                'Column': columns_with_missing,
                'Missing %': [missing_values[col] for col in columns_with_missing]
            }).sort_values('Missing %', ascending=False)
            
            st.dataframe(missing_df.head(5), use_container_width=True)
            
            # Show missing values chart
            st.markdown("### Missing Values Distribution")
            fig = plot_missing_values(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No missing values found in the dataset.")
    
    st.markdown("---")
    
    # Dataset preview
    st.subheader("Data Preview")
    st.dataframe(df.head(5), use_container_width=True)
    
    # Column information
    st.subheader("Column Information")
    col_info = pd.DataFrame({
        'Column': df.columns,
        'Type': [df[col].dtype for col in df.columns],
        'Non-Null Count': [df[col].count() for col in df.columns],
        'Missing Count': [df[col].isna().sum() for col in df.columns],
        'Unique Values': [df[col].nunique() for col in df.columns]
    })
    st.dataframe(col_info, use_container_width=True)

def render_data_viewer_tab(df):
    """Render the data viewer tab content."""
    st.subheader("Data Viewer")
    
    # Options for viewing
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        rows_to_show = st.number_input("Rows to display", min_value=5, max_value=100, value=10)
    with col2:
        sort_by = st.selectbox("Sort by", ["None"] + df.columns.tolist())
    with col3:
        if sort_by != "None":
            sort_order = st.radio("Sort order", ["Ascending", "Descending"], horizontal=True)
    
    # Apply filters
    filtered_df = df.copy()
    
    # Filters expander
    with st.expander("Add filters"):
        # Allow filtering for each column
        filter_cols = st.multiselect("Select columns to filter", df.columns.tolist())
        
        applied_filters = False
        for col in filter_cols:
            st.markdown(f"**Filter for {col}**")
            
            if pd.api.types.is_numeric_dtype(df[col]):
                # Numeric filter
                min_val, max_val = float(df[col].min()), float(df[col].max())
                filter_range = st.slider(f"Range for {col}", min_val, max_val, (min_val, max_val))
                filtered_df = filtered_df[(filtered_df[col] >= filter_range[0]) & (filtered_df[col] <= filter_range[1])]
                applied_filters = True
            
            elif pd.api.types.is_categorical_dtype(df[col]) or df[col].nunique() < 20:
                # Categorical filter
                categories = df[col].dropna().unique().tolist()
                selected_cats = st.multiselect(f"Values for {col}", categories, default=categories)
                if selected_cats:
                    filtered_df = filtered_df[filtered_df[col].isin(selected_cats)]
                    applied_filters = True
            
            else:
                # Text filter
                text_filter = st.text_input(f"Text contains (for {col})", "")
                if text_filter:
                    filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(text_filter, case=False, na=False)]
                    applied_filters = True
    
    # Show filter summary if filters applied
    if applied_filters:
        st.info(f"Showing {len(filtered_df)} of {len(df)} rows after filtering")
    
    # Sort data if requested
    if sort_by != "None":
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=(sort_order == "Ascending"))
    
    # Display the data
    st.dataframe(filtered_df.head(rows_to_show), use_container_width=True)
    
    # Export options
    st.markdown("### Export Data")
    export_cols = st.columns([1, 1, 1])
    with export_cols[0]:
        if st.button("Export to CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"exported_data.csv",
                mime="text/csv"
            )
    with export_cols[1]:
        if st.button("Export to Excel"):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False)
            st.download_button(
                label="Download Excel",
                data=buffer.getvalue(),
                file_name=f"exported_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

def render_column_stats_tab(df):
    """Render the column statistics tab content."""
    st.subheader("Column Statistics")
    
    # Select column to analyze
    col_to_analyze = st.selectbox("Select a column to analyze", df.columns.tolist())
    
    # Get column type and statistics
    col_type = df[col_to_analyze].dtype
    col_stats = get_column_statistics(df, col_to_analyze)
    
    col1, col2 = st.columns([1, 1])
    
    # Column information
    with col1:
        st.markdown("### Column Info")
        info_df = pd.DataFrame({
            'Metric': ['Type', 'Count', 'Missing Values', 'Missing %', 'Unique Values'],
            'Value': [
                str(col_type),
                col_stats['count'],
                col_stats['missing'],
                f"{col_stats['missing_pct']}%",
                col_stats['unique_values']
            ]
        })
        st.dataframe(info_df, use_container_width=True, hide_index=True)
    
    # Type-specific statistics
    with col2:
        st.markdown("### Statistics")
        
        if pd.api.types.is_numeric_dtype(df[col_to_analyze]):
            stats_df = pd.DataFrame({
                'Metric': ['Min', 'Max', 'Mean', 'Median', 'Std Dev', 'Skewness', 'Outliers'],
                'Value': [
                    col_stats['min'],
                    col_stats['max'],
                    col_stats['mean'],
                    col_stats['median'],
                    col_stats['std'],
                    col_stats['skew'],
                    f"{col_stats['outliers_count']} ({col_stats['outliers_pct']}%)"
                ]
            })
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
        elif pd.api.types.is_datetime64_any_dtype(df[col_to_analyze]):
            stats_df = pd.DataFrame({
                'Metric': ['Min (Earliest)', 'Max (Latest)', 'Range (Days)'],
                'Value': [
                    col_stats['min'],
                    col_stats['max'],
                    col_stats['range_days']
                ]
            })
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
        elif 'top_values' in col_stats:
            st.markdown("### Top Values")
            top_values = col_stats['top_values']
            items = list(top_values.items())
            items_df = pd.DataFrame({
                'Value': [str(k) for k, v in items],
                'Count': [v for k, v in items],
                'Percentage': [f"{(v / col_stats['count']) * 100:.1f}%" for k, v in items]
            })
            st.dataframe(items_df, use_container_width=True, hide_index=True)
    
    # Data visualization
    st.markdown("### Visualizations")
    
    if pd.api.types.is_numeric_dtype(df[col_to_analyze]):
        # For numeric columns
        viz_type = st.radio(
            "Select visualization type",
            ["Histogram", "Box Plot", "Outlier Analysis"],
            horizontal=True
        )
        
        if viz_type == "Histogram":
            bins = st.slider("Number of bins", 5, 100, 20)
            fig = plot_histogram(df, col_to_analyze, bins=bins)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "Box Plot":
            fig = plot_box(df, col_to_analyze)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "Outlier Analysis":
            fig = plot_outliers(df, col_to_analyze)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                # Show outliers
                st.markdown("### Outlier Values")
                outliers = detect_outliers(df, col_to_analyze)
                if len(outliers) > 0:
                    outlier_df = df.iloc[outliers][[col_to_analyze]]
                    st.dataframe(outlier_df, use_container_width=True)
                else:
                    st.info("No outliers detected")
    
    elif pd.api.types.is_categorical_dtype(df[col_to_analyze]) or df[col_to_analyze].nunique() < 20:
        # For categorical columns
        fig = plot_bar(df, col_to_analyze)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        # For text columns
        st.info("This column appears to be text data. Statistical visualizations are not available.")
        
        # Show sample values
        st.markdown("### Sample Values")
        st.dataframe(df[col_to_analyze].sample(min(10, len(df))), use_container_width=True)

def render_missing_values_tab(df):
    """Render the missing values tab content."""
    st.subheader("Missing Values Analysis")
    
    # Calculate missing values statistics
    missing_values = pd.DataFrame({
        'Column': df.columns,
        'Missing Count': df.isna().sum().values,
        'Missing Percentage': (df.isna().sum().values / len(df) * 100).round(2)
    }).sort_values('Missing Count', ascending=False)
    
    # Overall summary
    total_cells = np.prod(df.shape)
    total_missing = df.isna().sum().sum()
    missing_pct = total_missing / total_cells * 100
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Missing Values", f"{total_missing:,}")
    with col2:
        st.metric("Total Data Points", f"{total_cells:,}")
    with col3:
        st.metric("Overall Missing Percentage", f"{missing_pct:.2f}%")
    
    # Missing values visualization
    st.markdown("### Missing Values by Column")
    fig = plot_missing_values(df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No missing values found in the dataset.")
    
    # Missing values table
    st.markdown("### Missing Values Details")
    # Filter to only show columns with missing values
    missing_values_filtered = missing_values[missing_values['Missing Count'] > 0]
    if not missing_values_filtered.empty:
        st.dataframe(missing_values_filtered, use_container_width=True, hide_index=True)
    else:
        st.success("No missing values found in the dataset.")
    
    # Missing values handling options
    st.markdown("### Handle Missing Values")
    
    if total_missing > 0:
        st.markdown("Select a column and handling method to preview results:")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            missing_col = st.selectbox("Column with missing values", 
                                      missing_values_filtered['Column'].tolist() if not missing_values_filtered.empty else [])
        with col2:
            handling_method = st.selectbox("Handling method", 
                                          ["Drop rows", "Fill with mean", "Fill with median", 
                                           "Fill with mode", "Fill with constant"])
        
        if handling_method and missing_col:
            # Preview result
            df_preview = df.copy()
            missing_count_before = df_preview[missing_col].isna().sum()
            
            if handling_method == "Drop rows":
                df_preview = df_preview.dropna(subset=[missing_col])
                st.warning(f"This will remove {missing_count_before} rows with missing values in '{missing_col}'")
            
            elif handling_method == "Fill with mean":
                if pd.api.types.is_numeric_dtype(df_preview[missing_col]):
                    mean_val = df_preview[missing_col].mean()
                    df_preview[missing_col] = df_preview[missing_col].fillna(mean_val)
                    st.info(f"Missing values will be replaced with the mean: {mean_val:.2f}")
                else:
                    st.error("Mean fill is only applicable to numeric columns")
            
            elif handling_method == "Fill with median":
                if pd.api.types.is_numeric_dtype(df_preview[missing_col]):
                    median_val = df_preview[missing_col].median()
                    df_preview[missing_col] = df_preview[missing_col].fillna(median_val)
                    st.info(f"Missing values will be replaced with the median: {median_val:.2f}")
                else:
                    st.error("Median fill is only applicable to numeric columns")
            
            elif handling_method == "Fill with mode":
                mode_val = df_preview[missing_col].mode()[0]
                df_preview[missing_col] = df_preview[missing_col].fillna(mode_val)
                st.info(f"Missing values will be replaced with the most frequent value: {mode_val}")
            
            elif handling_method == "Fill with constant":
                const_val = st.text_input("Constant value to fill with", "0")
                if const_val:
                    # Try to convert to appropriate type
                    try:
                        if pd.api.types.is_numeric_dtype(df_preview[missing_col]):
                            const_val = float(const_val)
                        df_preview[missing_col] = df_preview[missing_col].fillna(const_val)
                        st.info(f"Missing values will be replaced with: {const_val}")
                    except ValueError:
                        st.error("Please enter a valid value")
            
            # Show preview
            st.markdown("### Preview After Handling Missing Values")
            st.dataframe(df_preview.head(5), use_container_width=True)
            
            # Apply to actual data if requested
            if st.button("Apply to dataset"):
                if handling_method == "Drop rows":
                    st.session_state.current_data = st.session_state.current_data.dropna(subset=[missing_col])
                
                elif handling_method == "Fill with mean" and pd.api.types.is_numeric_dtype(st.session_state.current_data[missing_col]):
                    mean_val = st.session_state.current_data[missing_col].mean()
                    st.session_state.current_data[missing_col] = st.session_state.current_data[missing_col].fillna(mean_val)
                
                elif handling_method == "Fill with median" and pd.api.types.is_numeric_dtype(st.session_state.current_data[missing_col]):
                    median_val = st.session_state.current_data[missing_col].median()
                    st.session_state.current_data[missing_col] = st.session_state.current_data[missing_col].fillna(median_val)
                
                elif handling_method == "Fill with mode":
                    mode_val = st.session_state.current_data[missing_col].mode()[0]
                    st.session_state.current_data[missing_col] = st.session_state.current_data[missing_col].fillna(mode_val)
                
                elif handling_method == "Fill with constant":
                    try:
                        if pd.api.types.is_numeric_dtype(st.session_state.current_data[missing_col]):
                            const_val = float(const_val)
                        st.session_state.current_data[missing_col] = st.session_state.current_data[missing_col].fillna(const_val)
                    except ValueError:
                        st.error("Please enter a valid value")
                
                st.success(f"Successfully applied {handling_method} to column '{missing_col}'")
                st.experimental_rerun()
    else:
        st.success("No missing values found in the dataset.")

def render_insights_tab(df):
    """Render the insights tab content."""
    st.subheader("Automated Data Insights")
    
    # Generate insights based on data
    with st.spinner("Generating insights..."):
        insights = generate_insights(df)
    
    # Display insights
    for category, category_insights in insights.items():
        st.markdown(f"### {category}")
        
        for insight in category_insights:
            with st.container():
                st.info(insight['description'])
                
                # Show visualization if available
                if 'visualization' in insight:
                    viz_type = insight['visualization']['type']
                    
                    if viz_type == 'bar' and 'column' in insight['visualization']:
                        col = insight['visualization']['column']
                        fig = plot_bar(df, col)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == 'histogram' and 'column' in insight['visualization']:
                        col = insight['visualization']['column']
                        fig = plot_histogram(df, col)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)

def generate_insights(df):
    """Generate automated insights about the data."""
    insights = {
        "Summary Insights": [],
        "Data Quality Insights": [],
        "Distribution Insights": [],
        "Outlier Insights": []
    }
    
    # Summary insights
    insights["Summary Insights"].append({
        "description": f"This dataset contains {df.shape[0]} rows and {df.shape[1]} columns."
    })
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime']).columns.tolist()
    
    insights["Summary Insights"].append({
        "description": f"The dataset has {len(numeric_cols)} numeric columns, {len(categorical_cols)} categorical/text columns, and {len(datetime_cols)} datetime columns."
    })
    
    # Data quality insights
    missing_counts = df.isna().sum()
    cols_with_missing = missing_counts[missing_counts > 0]
    
    if not cols_with_missing.empty:
        insights["Data Quality Insights"].append({
            "description": f"Found {len(cols_with_missing)} columns with missing values. The column with most missing values is '{cols_with_missing.idxmax()}' ({cols_with_missing.max()} missing values, {cols_with_missing.max() / len(df) * 100:.1f}%)."
        })
    else:
        insights["Data Quality Insights"].append({
            "description": "No missing values found in this dataset, which is excellent for data quality!"
        })
    
    # Distribution insights
    if numeric_cols:
        # Find most skewed numeric column
        skewness = df[numeric_cols].skew().abs()
        if not skewness.empty and not skewness.isna().all():
            most_skewed = skewness.idxmax()
            skew_value = skewness.max()
            
            skew_direction = "right" if df[most_skewed].skew() > 0 else "left"
            insights["Distribution Insights"].append({
                "description": f"The column '{most_skewed}' shows a strong {skew_direction}-skewed distribution (skewness = {df[most_skewed].skew():.2f}). This might affect statistical analyses that assume normal distribution.",
                "visualization": {"type": "histogram", "column": most_skewed}
            })
    
    # Categorical distribution insights
    if categorical_cols:
        for col in categorical_cols[:2]:  # Limit to 2 categorical columns
            value_counts = df[col].value_counts()
            if len(value_counts) > 0:
                top_value = value_counts.index[0]
                top_percentage = value_counts.iloc[0] / len(df) * 100
                
                if top_percentage > 50:
                    insights["Distribution Insights"].append({
                        "description": f"In the '{col}' column, the value '{top_value}' appears in {top_percentage:.1f}% of rows, which indicates a significant imbalance.",
                        "visualization": {"type": "bar", "column": col}
                    })
    
    # Outlier insights
    if numeric_cols:
        for col in numeric_cols[:3]:  # Limit to 3 numeric columns
            outliers = detect_outliers(df, col)
            outlier_percentage = len(outliers) / len(df) * 100
            
            if outlier_percentage > 5:
                insights["Outlier Insights"].append({
                    "description": f"The column '{col}' contains {len(outliers)} outliers ({outlier_percentage:.1f}% of the data). These might need special handling for certain analyses."
                })
    
    return insights