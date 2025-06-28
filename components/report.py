import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import base64
from .report_utils import (
    create_bar_chart, create_count_bar_chart, create_line_chart,
    create_scatter_plot, create_histogram, create_box_plot, create_pie_chart,
    generate_html_report
)

def render_report_page():
    """Render the report generation page."""
    st.header("📝 Generate Report")
    
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
    
    # Initialize report state if needed
    if 'report_items' not in st.session_state:
        st.session_state.report_items = []
    
    # Create columns for report building
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Report Builder")
        
        # Add different types of content to the report
        add_item_type = st.selectbox(
            "Add to report",
            ["Text/Title", "Dataset Summary", "Data Preview", "Chart", "Analysis Result"],
            key="add_item_type"
        )
        
        # Different options based on selected type
        if add_item_type == "Text/Title":
            text_type = st.selectbox("Text type", ["Title", "Subtitle", "Paragraph"])
            text_content = st.text_area("Content")
            
            if st.button("Add to Report") and text_content:
                st.session_state.report_items.append({
                    "type": "text",
                    "text_type": text_type,
                    "content": text_content
                })
                st.success("Added to report!")
        
        elif add_item_type == "Dataset Summary":
            if st.button("Add Dataset Summary"):
                # Get data summary
                data_summary = {}
                data_summary["n_rows"] = len(df)
                data_summary["n_columns"] = len(df.columns)
                data_summary["column_types"] = {col: str(dtype) for col, dtype in df.dtypes.items()}
                
                # Get missing values summary
                missing_values = {}
                for col in df.columns:
                    missing_count = df[col].isna().sum()
                    missing_pct = (missing_count / len(df)) * 100
                    if missing_count > 0:
                        missing_values[col] = {
                            "count": missing_count,
                            "percentage": missing_pct
                        }
                
                data_summary["missing_values"] = missing_values
                
                st.session_state.report_items.append({
                    "type": "dataset_summary",
                    "content": data_summary
                })
                st.success("Added dataset summary to report!")
        
        elif add_item_type == "Data Preview":
            if st.button("Add Data Preview"):
                preview_data = df.head(10).to_dict('records')
                st.session_state.report_items.append({
                    "type": "data_preview",
                    "content": preview_data
                })
                st.success("Added data preview to report!")
        
        elif add_item_type == "Chart":
            chart_types = [
                "Bar Chart", "Count Bar Chart", "Line Chart", "Scatter Plot",
                "Histogram", "Box Plot", "Pie Chart"
            ]
            selected_chart = st.selectbox("Select chart type", chart_types)
            
            if st.button("Add Chart"):
                # Placeholder for chart generation logic
                st.warning("Chart generation not implemented yet.")
        
        elif add_item_type == "Analysis Result":
            if st.button("Add Analysis Result"):
                # Placeholder for analysis result logic
                st.warning("Analysis result addition not implemented yet.")
    
    with col2:
        st.subheader("Report Preview")
        
        if not st.session_state.report_items:
            st.info("No items added to the report yet.")
        else:
            for i, item in enumerate(st.session_state.report_items):
                if item["type"] == "text":
                    if item["text_type"] == "Title":
                        st.title(item["content"])
                    elif item["text_type"] == "Subtitle":
                        st.subheader(item["content"])
                    else:
                        st.write(item["content"])
                elif item["type"] == "dataset_summary":
                    summary = item["content"]
                    st.markdown(f"**Rows:** {summary['n_rows']}")
                    st.markdown(f"**Columns:** {summary['n_columns']}")
                    st.markdown("**Column Types:**")
                    for col, dtype in summary["column_types"].items():
                        st.markdown(f"- {col}: {dtype}")
                    if summary["missing_values"]:
                        st.markdown("**Missing Values:**")
                        for col, miss_info in summary["missing_values"].items():
                            st.markdown(f"- {col}: {miss_info['count']} ({miss_info['percentage']:.2f}%)")
                elif item["type"] == "data_preview":
                    st.dataframe(pd.DataFrame(item["content"]))
                else:
                    st.write(f"Unsupported report item type: {item['type']}")
