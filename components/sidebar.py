import streamlit as st
import pandas as pd
import os
import numpy as np
from utils.data_processing import get_data_summary, suggest_analysis_types

# Maps display label -> route key used in app.py
NAV_PAGES = {
    "🏠 Home": "home",
    "📤 Upload Data": "upload",
    "🔍 Explore Data": "explore",
    "📊 Analyze Data": "analyze",
    "📝 Generate Report": "report",
}


def render_sidebar():
    """Render the sidebar navigation and return the current page key."""
    with st.sidebar:
        st.subheader("📋 Navigation")

        selected_label = st.radio(
            "Select a page",
            list(NAV_PAGES.keys()),
            index=0,
        )

        st.markdown("---")

        # Show current dataset info if one is loaded
        if "current_data" in st.session_state and st.session_state.current_data is not None:
            df = st.session_state.current_data
            st.subheader("📊 Current Dataset")
            st.info(f"**File:** {st.session_state.file_name}\n\n**Rows:** {df.shape[0]} | **Cols:** {df.shape[1]}")

            if st.button("❌ Clear Dataset"):
                st.session_state.current_data = None
                st.session_state.file_name = None
                st.session_state.data_summary = None
                st.session_state.suggested_analyses = None
                st.rerun()

        with st.expander("❓ How to use"):
            st.markdown(
                """
                1. **Upload** a CSV or Excel file
                2. **Explore** to understand your data
                3. **Analyze** to run statistical analyses
                4. **Report** to build and export insights
                """
            )

        st.markdown("---")
        st.markdown("© 2024 EasyAnalytics")

    return NAV_PAGES[selected_label]


def render_upload_page():
    """Render the data upload page."""
    st.header("📤 Upload Your Data")

    st.markdown(
        "Upload a CSV or Excel file to get started. "
        "Your data stays in your browser session and is never stored on any server."
    )

    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None:
        try:
            file_name = uploaded_file.name
            file_extension = os.path.splitext(file_name)[1].lower()

            if file_extension == ".csv":
                with st.expander("CSV Import Options"):
                    delimiter = st.selectbox("Delimiter", options=[",", ";", "\t", "|"], index=0)
                    encoding = st.selectbox("Encoding", options=["utf-8", "latin1", "iso-8859-1"], index=0)
                df = pd.read_csv(uploaded_file, delimiter=delimiter, encoding=encoding)

            elif file_extension in [".xlsx", ".xls"]:
                with st.expander("Excel Import Options"):
                    sheet_name = st.text_input("Sheet name (leave blank for first sheet)", "")
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name.strip() or 0)

            else:
                st.error("Unsupported file format.")
                return

            _store_dataset(df, file_name)

            st.success(f"Loaded **{file_name}** — {df.shape[0]:,} rows × {df.shape[1]} columns")
            _show_upload_preview(df)

        except Exception as e:
            st.error(f"Could not load file: {e}")

    else:
        _render_sample_data_section()


def _store_dataset(df: pd.DataFrame, file_name: str):
    """Save dataset and derived metadata into session state."""
    st.session_state.current_data = df
    st.session_state.file_name = file_name
    st.session_state.data_summary = get_data_summary(df)
    st.session_state.suggested_analyses = suggest_analysis_types(df)


def _show_upload_preview(df: pd.DataFrame):
    """Show a quick preview and column info after upload."""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", f"{df.shape[0]:,}")
    with col2:
        st.metric("Columns", df.shape[1])
    with col3:
        missing_pct = (df.isna().sum().sum() / df.size) * 100
        st.metric("Missing Values", f"{missing_pct:.2f}%")

    st.subheader("Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("Column Information")
    col_info = pd.DataFrame(
        {
            "Column": df.columns,
            "Type": [str(df[c].dtype) for c in df.columns],
            "Missing": [df[c].isna().sum() for c in df.columns],
            "Unique Values": [df[c].nunique() for c in df.columns],
        }
    )
    st.dataframe(col_info, use_container_width=True)

    st.markdown("---")
    st.markdown("### What's next?")
    st.markdown("Use the sidebar to **Explore** or **Analyze** your data.")


def _render_sample_data_section():
    """Let users load a built-in sample dataset."""
    st.markdown("---")
    st.markdown("### No file? Try a sample dataset")

    sample_options = {
        "None": None,
        "Iris Flowers": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
        "Titanic Passengers": "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv",
        "Sales Data (generated)": None,
    }

    choice = st.selectbox("Select a sample dataset", list(sample_options.keys()))

    if choice != "None" and st.button("Load Sample Data"):
        try:
            if choice == "Sales Data (generated)":
                df = _generate_sales_data()
                file_name = "sales_sample.csv"
            else:
                df = pd.read_csv(sample_options[choice])
                file_name = f"{choice.lower().replace(' ', '_')}.csv"

            _store_dataset(df, file_name)
            st.rerun()

        except Exception as e:
            st.error(f"Could not load sample data: {e}")

    with st.expander("Tips for preparing your data"):
        st.markdown(
            """
            - First row should be column headers
            - Remove blank rows at the top
            - Use a consistent date format throughout
            - Numeric columns shouldn't contain text like "N/A" — use empty cells instead
            """
        )


def _generate_sales_data() -> pd.DataFrame:
    """Generate a simple synthetic sales dataset."""
    rng = np.random.default_rng(42)
    n = 200
    return pd.DataFrame(
        {
            "Date": pd.date_range(start="2023-01-01", periods=n, freq="D"),
            "Product": rng.choice(["Product A", "Product B", "Product C", "Product D"], n),
            "Region": rng.choice(["North", "South", "East", "West"], n),
            "Sales": rng.integers(100, 1000, n),
            "Quantity": rng.integers(1, 50, n),
            "Discount": rng.choice([0.0, 0.1, 0.2, 0.3], n),
            "Profit": rng.integers(-100, 500, n),
        }
    )
