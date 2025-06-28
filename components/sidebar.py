import streamlit as st
import pandas as pd
import os
import io
import numpy as np
from utils.data_processing import load_data, get_data_preview, get_data_summary, suggest_analysis_types

def render_sidebar():
    """Render the sidebar with navigation and options."""
    with st.sidebar:
        st.subheader("📋 Navigation")
        
        # Main navigation
        page = st.radio(
            "Select a page",
            ["🏠 Home", "📤 Upload Data", "🔍 Explore Data", "📊 Analyze Data", "📝 Generate Report"],
            index=0
        )
        
        st.markdown("---")
        
        # Current dataset information
        if 'current_data' in st.session_state and st.session_state.current_data is not None:
            df = st.session_state.current_data
            st.subheader("📊 Current Dataset")
            st.info(f"**Rows:** {df.shape[0]} | **Columns:** {df.shape[1]}")
            
            # Dataset options
            if st.button("❌ Clear Dataset"):
                st.session_state.current_data = None
                st.session_state.file_name = None
                st.session_state.data_summary = None
                st.session_state.suggested_analyses = None
                st.experimental_rerun()
        
        # Help section
        with st.expander("❓ Help"):
            st.markdown("""
            **How to use EasyAnalytics:**
            1. Upload your data file (CSV or Excel)
            2. Explore and understand your data
            3. Run analyses with a few clicks
            4. Generate insights automatically
            5. Create and export reports
            
            Need more help? Check out our [documentation](https://github.com/your-repo/EasyAnalytics).
            """)
        
        st.markdown("---")
        st.markdown("© 2023 EasyAnalytics")
        
    return page.split(" ")[1].lower()

def render_upload_page():
    """Render the data upload page."""
    st.header("📤 Upload Your Data")
    
    st.markdown("""
    Upload your data file (CSV or Excel) to start analysis. 
    Your data will be processed directly in your browser and won't be stored on any server.
    """)
    
    # File upload
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            # Determine file type and load
            file_name = uploaded_file.name
            file_extension = os.path.splitext(file_name)[1].lower()
            
            if file_extension == ".csv":
                # Options for CSV
                with st.expander("CSV Import Options"):
                    delimiter = st.selectbox("Delimiter", options=[",", ";", "\t", "|"], index=0)
                    encoding = st.selectbox("Encoding", options=["utf-8", "latin1", "iso-8859-1"], index=0)
                
                df = pd.read_csv(uploaded_file, delimiter=delimiter, encoding=encoding)
            elif file_extension in [".xlsx", ".xls"]:
                # Options for Excel
                with st.expander("Excel Import Options"):
                    sheet_name = st.text_input("Sheet Name (leave blank for first sheet)", "")
                
                if sheet_name.strip() == "":
                    df = pd.read_excel(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            
            # Store the data in session state
            st.session_state.current_data = df
            st.session_state.file_name = file_name
            
            # Get data summary
            data_summary = get_data_summary(df)
            st.session_state.data_summary = data_summary
            
            # Get suggested analyses
            suggested_analyses = suggest_analysis_types(df)
            st.session_state.suggested_analyses = suggested_analyses
            
            # Display success message
            st.success(f"Successfully loaded {file_name} with {df.shape[0]} rows and {df.shape[1]} columns!")
            
            # Preview data
            st.subheader("Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Quick stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", df.shape[0])
            with col2:
                st.metric("Columns", df.shape[1])
            with col3:
                missing_percentage = (df.isna().sum().sum() / (df.shape[0] * df.shape[1])) * 100
                st.metric("Missing Values", f"{missing_percentage:.2f}%")
            
            # Column information
            st.subheader("Column Information")
            column_info = pd.DataFrame({
                "Column": df.columns,
                "Type": [str(df[col].dtype) for col in df.columns],
                "Missing": [df[col].isna().sum() for col in df.columns],
                "Unique Values": [df[col].nunique() for col in df.columns]
            })
            st.dataframe(column_info, use_container_width=True)
            
            # Next steps
            st.markdown("---")
            st.markdown("### Next Steps")
            col1, col2 = st.columns(2)
            with col1:
                st.button("🔍 Explore Data", key="goto_explore", 
                         on_click=lambda: st.session_state.update({"page": "explore"}))
            with col2:
                st.button("📊 Analyze Data", key="goto_analyze",
                         on_click=lambda: st.session_state.update({"page": "analyze"}))
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    else:
        # Sample data option
        st.markdown("---")
        st.markdown("### Or try with sample data")
        
        sample_data_option = st.selectbox(
            "Select a sample dataset",
            ["None", "Iris Flower Dataset", "Titanic Passengers", "Housing Prices", "Sales Data"]
        )
        
        if sample_data_option != "None" and st.button("Load Sample Data"):
            if sample_data_option == "Iris Flower Dataset":
                df = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv")
                file_name = "iris.csv"
            elif sample_data_option == "Titanic Passengers":
                df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
                file_name = "titanic.csv"
            elif sample_data_option == "Housing Prices":
                df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/housing.csv")
                file_name = "housing.csv"
            elif sample_data_option == "Sales Data":
                # Create sample sales data
                data = {
                    'Date': pd.date_range(start='2020-01-01', periods=100, freq='D'),
                    'Product': ['Product A', 'Product B', 'Product C', 'Product D'] * 25,
                    'Region': ['North', 'South', 'East', 'West', 'Central'] * 20,
                    'Sales': np.random.randint(100, 1000, size=100),
                    'Quantity': np.random.randint(1, 50, size=100),
                    'Discount': np.random.choice([0, 0.1, 0.2, 0.3, 0.4], size=100),
                    'Profit': np.random.randint(-100, 500, size=100)
                }
                df = pd.DataFrame(data)
                file_name = "sales_sample.csv"
            
            # Store the data in session state
            st.session_state.current_data = df
            st.session_state.file_name = file_name
            
            # Get data summary
            data_summary = get_data_summary(df)
            st.session_state.data_summary = data_summary
            
            # Get suggested analyses
            suggested_analyses = suggest_analysis_types(df)
            st.session_state.suggested_analyses = suggested_analyses
            
            st.experimental_rerun()  # Rerun to show the loaded data
        
        # Show tips for preparing data
        with st.expander("Tips for preparing your data"):
            st.markdown("""
            **Best practices for data preparation:**
            - Make sure your first row contains column headers
            - Remove any blank rows at the beginning
            - Check that dates are in a consistent format
            - Ensure numeric columns don't contain text values
            - Consider cleaning your data before uploading for better results
            """)
