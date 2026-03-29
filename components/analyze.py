import streamlit as st
import pandas as pd
import numpy as np
from utils.analysis import (
    descriptive_statistics, correlation_analysis, distribution_analysis,
    time_series_analysis, group_analysis, outlier_analysis, missing_values_analysis,
    clustering_analysis, prediction_analysis
)
from utils.visualization import (
    plot_histogram, plot_correlation_matrix, plot_scatter, plot_time_series,
    plot_group_bar, plot_outliers, plot_clusters, plot_feature_importance
)
import plotly.express as px
import io
from datetime import datetime
from utils.data_processing import preprocess_dataframe_for_arrow

def render_analyze_page():
    """Render the data analysis page."""
    st.header("📊 Analyze Your Data")
    
    # Check if data is loaded
    if 'current_data' not in st.session_state or st.session_state.current_data is None:
        st.warning("Please upload a dataset first!")
        if st.button("Go to Upload Page"):
            st.rerun()
        return
    
    # Get the data
    df = st.session_state.current_data
    
    # Preprocess dataframe for Arrow compatibility
    df = preprocess_dataframe_for_arrow(df)
    
    file_name = st.session_state.file_name
    
    st.markdown(f"Analyzing dataset: **{file_name}**")
    
    # Create columns for analysis selection
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Analysis Types")
        
        # Get suggested analyses
        suggested_analyses = st.session_state.get('suggested_analyses', [])
        
        # Analysis selection
        analysis_types = {
            "descriptive": "📊 Descriptive Statistics",
            "distribution": "📈 Distribution Analysis",
            "correlation": "🔄 Correlation Analysis",
            "time_series": "⏱️ Time Series Analysis",
            "group": "👥 Group Analysis",
            "outlier": "⚠️ Outlier Analysis",
            "missing": "❓ Missing Values Analysis",
            "cluster": "🔮 Clustering Analysis",
            "prediction": "🎯 Prediction Analysis"
        }
        
        # Show recommendations if available
        if suggested_analyses:
            st.info("Recommended analyses based on your data:")
            for analysis in suggested_analyses:
                if analysis == 'descriptive_statistics':
                    st.markdown(f"✓ {analysis_types['descriptive']}")
                elif analysis == 'distribution_analysis':
                    st.markdown(f"✓ {analysis_types['distribution']}")
                elif analysis == 'correlation_analysis':
                    st.markdown(f"✓ {analysis_types['correlation']}")
                elif analysis == 'time_series_analysis':
                    st.markdown(f"✓ {analysis_types['time_series']}")
                elif analysis == 'group_analysis':
                    st.markdown(f"✓ {analysis_types['group']}")
                elif analysis == 'outlier_analysis':
                    st.markdown(f"✓ {analysis_types['outlier']}")
                elif analysis == 'missing_values_analysis':
                    st.markdown(f"✓ {analysis_types['missing']}")
            
            st.markdown("---")
        
        # Analysis type selection
        selected_analysis = st.radio(
            "Select Analysis Type",
            list(analysis_types.keys()),
            format_func=lambda x: analysis_types[x],
            key="analysis_type"
        )
        
        # History of analyses
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
        
        with st.expander("Analysis History"):
            if not st.session_state.analysis_history:
                st.info("No analyses run yet.")
            else:
                for i, analysis in enumerate(st.session_state.analysis_history):
                    st.markdown(f"**{i+1}. {analysis['type']}** - {analysis['timestamp']}")
        
        # Option to clear history
        if st.session_state.analysis_history and st.button("Clear History"):
            st.session_state.analysis_history = []
            st.success("Analysis history cleared!")
            st.rerun()
    
    with col2:
        st.subheader(f"{analysis_types[selected_analysis]}")
        
        if selected_analysis == "descriptive":
            render_descriptive_analysis(df)
        elif selected_analysis == "distribution":
            render_distribution_analysis(df)
        elif selected_analysis == "correlation":
            render_correlation_analysis(df)
        elif selected_analysis == "time_series":
            render_time_series_analysis(df)
        elif selected_analysis == "group":
            render_group_analysis(df)
        elif selected_analysis == "outlier":
            render_outlier_analysis(df)
        elif selected_analysis == "missing":
            render_missing_values_analysis(df)
        elif selected_analysis == "cluster":
            render_clustering_analysis(df)
        elif selected_analysis == "prediction":
            render_prediction_analysis(df)

def save_to_analysis_history(analysis_type, columns):
    """Save the current analysis to history."""
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    st.session_state.analysis_history.append({
        'type': analysis_type,
        'columns': columns,
        'timestamp': timestamp
    })

def render_descriptive_analysis(df):
    """Render descriptive statistics analysis."""
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.warning("No numeric columns found in the dataset. Descriptive statistics requires numeric data.")
        return
    
    # Options for analysis
    col1, col2 = st.columns(2)
    
    with col1:
        selected_cols = st.multiselect(
            "Select columns for analysis",
            numeric_cols,
            default=numeric_cols[:min(5, len(numeric_cols))]
        )
    
    # Run analysis
    if not selected_cols:
        st.warning("Please select at least one column for analysis.")
        return
    
    # Calculate statistics
    with st.spinner("Calculating descriptive statistics..."):
        stats_result = descriptive_statistics(df[selected_cols])
    
    if "error" in stats_result:
        st.error(f"Error in analysis: {stats_result['error']}")
        return
    
    # Display results
    st.subheader("Statistical Summary")
    
    # Convert dictionary to DataFrame for better display
    stats_df = pd.DataFrame(stats_result).T
    st.dataframe(stats_df, use_container_width=True)
    
    # Create visualizations
    st.subheader("Visualizations")
    
    for col in selected_cols:
        st.markdown(f"#### Distribution of {col}")
        fig = plot_histogram(df, col)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Save to analysis history
    save_to_analysis_history("Descriptive Statistics", selected_cols)

def render_distribution_analysis(df):
    """Render distribution analysis."""
    # Get columns
    all_cols = df.columns.tolist()
    
    # Options for analysis
    col1, col2 = st.columns(2)
    
    with col1:
        selected_col = st.selectbox(
            "Select column for analysis",
            all_cols
        )
    
    # Run analysis
    if not selected_col:
        st.warning("Please select a column for analysis.")
        return
    
    # Calculate distribution
    with st.spinner("Analyzing distribution..."):
        dist_result = distribution_analysis(df, selected_col)
    
    if "error" in dist_result:
        st.error(f"Error in analysis: {dist_result['error']}")
        return
    
    # Display results
    st.subheader("Distribution Analysis")
    
    # Different display based on column type
    if dist_result['type'] == 'numeric':
        # Show statistics
        stats = dist_result['stats']
        stats_df = pd.DataFrame({
            'Metric': list(stats.keys()),
            'Value': list(stats.values())
        })
        
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        # Show histogram
        fig = plot_histogram(df, selected_col)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            
    else:  # Categorical
        # Show value counts
        value_counts = pd.DataFrame(dist_result['value_counts'])
        value_counts['percentage'] = value_counts['count'] / value_counts['count'].sum() * 100
        value_counts['percentage'] = value_counts['percentage'].round(2).astype(str) + '%'
        
        st.dataframe(value_counts, use_container_width=True)
        
        # Show bar chart
        from utils.visualization import plot_bar
        fig = plot_bar(df, selected_col)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Save to analysis history
    save_to_analysis_history("Distribution Analysis", [selected_col])

def render_correlation_analysis(df):
    """Render correlation analysis."""
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns for correlation analysis. Your dataset doesn't have enough numeric columns.")
        return
    
    # Options for analysis
    col1, col2 = st.columns(2)
    
    with col1:
        selected_cols = st.multiselect(
            "Select columns for correlation analysis",
            numeric_cols,
            default=numeric_cols[:min(5, len(numeric_cols))]
        )
    
    with col2:
        corr_method = st.selectbox(
            "Correlation method",
            ["pearson", "spearman", "kendall"],
            index=0,
            help="Pearson measures linear correlation, Spearman and Kendall measure rank correlation"
        )
    
    # Run analysis
    if len(selected_cols) < 2:
        st.warning("Please select at least two columns for correlation analysis.")
        return
    
    # Calculate correlation
    with st.spinner("Calculating correlation matrix..."):
        corr_result = correlation_analysis(df[selected_cols], method=corr_method)
    
    if "error" in corr_result:
        st.error(f"Error in analysis: {corr_result['error']}")
        return
    
    # Display results
    st.subheader("Correlation Matrix")
    
    # Show correlation heatmap
    fig = plot_correlation_matrix(df[selected_cols], method=corr_method)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Save to analysis history
    save_to_analysis_history("Correlation Analysis", selected_cols)

def render_time_series_analysis(df):
    """Render time series analysis."""
    # Check if there are datetime columns
    datetime_cols = [col for col in df.columns if pd.api.types.is_datetime64_dtype(df[col])]
    date_like_cols = [col for col in df.columns if df[col].dtype == 'object' and 
                     pd.to_datetime(df[col], errors='coerce').notna().any()]
    
    if not datetime_cols and not date_like_cols:
        st.warning("No datetime columns found. Please convert a column to datetime format first.")
        
        # Offer conversion option
        potential_date_cols = st.multiselect(
            "Select columns that might contain dates",
            df.select_dtypes(include=['object']).columns.tolist()
        )
        
        if potential_date_cols and st.button("Convert to Datetime"):
            df_copy = st.session_state.current_data.copy()
            for col in potential_date_cols:
                try:
                    df_copy[col] = pd.to_datetime(df_copy[col])
                    st.success(f"Successfully converted '{col}' to datetime!")
                except Exception as e:
                    st.error(f"Could not convert '{col}' to datetime: {str(e)}")
            
            st.session_state.current_data = df_copy
            st.rerun()
            
        return
    
    # Prepare date column options
    date_columns = datetime_cols + date_like_cols
    
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.warning("No numeric columns found for time series analysis.")
        return
    
    # Options for analysis
    col1, col2 = st.columns(2)
    
    with col1:
        date_column = st.selectbox(
            "Select date/time column",
            date_columns
        )
    
    with col2:
        value_column = st.selectbox(
            "Select value column to analyze",
            numeric_cols
        )
    
    # Run analysis
    if not date_column or not value_column:
        st.warning("Please select both date and value columns for analysis.")
        return
    
    # Calculate time series analysis
    with st.spinner("Analyzing time series data..."):
        ts_result = time_series_analysis(df, date_column, value_column)
    
    if "error" in ts_result:
        st.error(f"Error in analysis: {ts_result['error']}")
        return
    
    # Display results
    st.subheader("Time Series Analysis")
    
    # Plot time series
    fig = plot_time_series(df, date_column, value_column)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Save to analysis history
    save_to_analysis_history("Time Series Analysis", [date_column, value_column])

def render_group_analysis(df):
    """Render group analysis."""
    # Get categorical and numeric columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not categorical_cols:
        st.warning("No categorical columns found for grouping.")
        return
    
    if not numeric_cols:
        st.warning("No numeric columns found for value analysis.")
        return
    
    # Options for analysis
    col1, col2, col3 = st.columns(3)
    
    with col1:
        group_column = st.selectbox(
            "Select grouping column",
            categorical_cols
        )
    
    with col2:
        value_column = st.selectbox(
            "Select value column to analyze",
            numeric_cols
        )
    
    with col3:
        agg_func = st.selectbox(
            "Aggregation function",
            ["mean", "sum", "count", "min", "max"]
        )
    
    # Run analysis
    if not group_column or not value_column:
        st.warning("Please select both grouping and value columns for analysis.")
        return
    
    # Calculate group analysis
    with st.spinner("Calculating group statistics..."):
        group_result = group_analysis(df, group_column, value_column, agg_func)
    
    if "error" in group_result:
        st.error(f"Error in analysis: {group_result['error']}")
        return
    
    # Display results
    st.subheader("Group Analysis Results")
    
    # Show group statistics
    grouped_data = pd.DataFrame(group_result["grouped_data"])
    st.dataframe(grouped_data, use_container_width=True)
    
    # Visualization
    st.subheader("Visualization")
    
    # Check if there are too many groups
    horizontal = len(grouped_data) > 10
    
    fig = plot_group_bar(df, group_column, value_column, agg_func, horizontal=horizontal)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Save to analysis history
    save_to_analysis_history("Group Analysis", [group_column, value_column])

def render_outlier_analysis(df):
    """Render outlier analysis."""
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.warning("No numeric columns found for outlier analysis.")
        return
    
    # Options for analysis
    col1, col2 = st.columns(2)
    
    with col1:
        selected_col = st.selectbox(
            "Select column for outlier analysis",
            numeric_cols
        )
    
    # Run analysis
    if not selected_col:
        st.warning("Please select a column for outlier analysis.")
        return
    
    # Calculate outlier analysis
    with st.spinner("Analyzing outliers..."):
        outlier_result = outlier_analysis(df, selected_col)
    
    if "error" in outlier_result:
        st.error(f"Error in analysis: {outlier_result['error']}")
        return
    
    # Display results
    st.subheader("Outlier Analysis Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### IQR Method")
        st.info(f"Found {outlier_result['outliers_iqr']['count']} outliers ({outlier_result['outliers_iqr']['percentage']}% of data)")
        
        # Show boxplot
        fig = plot_outliers(df, selected_col)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Z-Score Method")
        st.info(f"Found {outlier_result['outliers_zscore']['count']} outliers ({outlier_result['outliers_zscore']['percentage']}% of data)")
    
    # Save to analysis history
    save_to_analysis_history("Outlier Analysis", [selected_col])

def render_missing_values_analysis(df):
    """Render missing values analysis."""
    # Calculate missing values analysis
    with st.spinner("Analyzing missing values..."):
        missing_result = missing_values_analysis(df)
    
    # Display results
    st.subheader("Missing Values Analysis")
    
    # Overall stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Missing", f"{missing_result['overall']['total_missing']:,}")
    with col2:
        st.metric("Total Cells", f"{missing_result['overall']['total_cells']:,}")
    with col3:
        st.metric("Missing Percentage", f"{missing_result['overall']['percentage']:.2f}%")
    
    # Show missing values chart
    st.subheader("Missing Values by Column")
    fig = plot_missing_values(df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Save to analysis history
    save_to_analysis_history("Missing Values Analysis", [])

def render_clustering_analysis(df):
    """Render clustering analysis."""
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns for clustering analysis.")
        return
    
    # Options for analysis
    col1, col2 = st.columns(2)
    
    with col1:
        selected_cols = st.multiselect(
            "Select columns for clustering",
            numeric_cols,
            default=numeric_cols[:min(3, len(numeric_cols))]
        )
    
    with col2:
        n_clusters = st.slider(
            "Number of clusters",
            min_value=2,
            max_value=10,
            value=3
        )
    
    # Run analysis
    if len(selected_cols) < 2:
        st.warning("Please select at least two columns for clustering analysis.")
        return
    
    # Calculate clustering
    with st.spinner("Performing cluster analysis..."):
        cluster_result = clustering_analysis(df, selected_cols, n_clusters)
    
    if "error" in cluster_result:
        st.error(f"Error in analysis: {cluster_result['error']}")
        return
    
    # Display results
    st.subheader("Clustering Results")
    
    # Show cluster visualization
    if 'pca_data' in cluster_result:
        st.info(f"PCA was applied to reduce dimensions to 2D for visualization. Explained variance: {sum(cluster_result['pca_explained_variance']):.2%}")
        
        # Plot clusters
        fig = plot_clusters(pd.DataFrame(cluster_result['pca_data']), n_clusters)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Show cluster statistics
    st.subheader("Cluster Statistics")
    
    for cluster_stat in cluster_result['cluster_stats']:
        cluster_num = cluster_stat['cluster']
        count = cluster_stat['count']
        percentage = cluster_stat['percentage']
        
        with st.expander(f"Cluster {cluster_num} ({count} points, {percentage:.1f}%)"):
            stats_data = []
            for col, metrics in cluster_stat['stats'].items():
                row = {'Column': col}
                row.update(metrics)
                stats_data.append(row)
            
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, use_container_width=True)
    
    # Save to analysis history
    save_to_analysis_history("Clustering Analysis", selected_cols)

def render_prediction_analysis(df):
    """Render prediction analysis."""
    # Get columns
    all_cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns for prediction analysis.")
        return
    
    # Options for analysis
    col1, col2 = st.columns(2)
    
    with col1:
        target_col = st.selectbox(
            "Select target column to predict",
            all_cols
        )
    
    with col2:
        test_size = st.slider(
            "Test set size (%)",
            min_value=10,
            max_value=50,
            value=20
        ) / 100
    
    # Select feature columns
    feature_cols = st.multiselect(
        "Select feature columns (predictors)",
        [col for col in numeric_cols if col != target_col],
        default=[col for col in numeric_cols[:min(5, len(numeric_cols))] if col != target_col]
    )
    
    # Run analysis
    if not target_col or len(feature_cols) < 1:
        st.warning("Please select target and at least one feature column for prediction.")
        return
    
    # Calculate prediction
    with st.spinner("Building and evaluating prediction model..."):
        pred_result = prediction_analysis(df, target_col, feature_cols, test_size)
    
    if "error" in pred_result:
        st.error(f"Error in analysis: {pred_result['error']}")
        return
    
    # Display results
    st.subheader("Prediction Model Results")
    
    model_type = pred_result['model_type']
    st.info(f"Model Type: {'Regression' if model_type == 'regression' else 'Classification'}")
    
    # Show model metrics
    st.markdown("### Model Performance")
    
    metrics = pred_result['metrics']
    metrics_df = pd.DataFrame({
        'Metric': list(metrics.keys()),
        'Value': list(metrics.values())
    })
    
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    # Show feature importance
    st.markdown("### Feature Importance")
    
    fig = plot_feature_importance(pred_result['feature_importance'])
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Feature importance table
    importance_df = pd.DataFrame(pred_result['feature_importance'])
    importance_df['importance'] = importance_df['importance'].round(4)
    st.dataframe(importance_df, use_container_width=True, hide_index=True)
    
    # Save to analysis history
    save_to_analysis_history("Prediction Analysis", [target_col] + feature_cols)