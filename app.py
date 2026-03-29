import streamlit as st
from components.header import render_header
from components.sidebar import render_sidebar, render_upload_page
from components.explore import render_explore_page
from components.analyze import render_analyze_page
from components.report import render_report_page


def main():
    render_header()
    current_page = render_sidebar()

    if current_page == "home":
        st.markdown(
            """
            ## Welcome to EasyAnalytics 👋

            Upload your data and let the app do the heavy lifting — no coding required.

            **Here's how it works:**
            1. **Upload** your CSV or Excel file
            2. **Explore** your data with automatic summaries and quality checks
            3. **Analyze** with one-click statistical and ML-powered analyses
            4. **Report** — build and export a clean HTML report

            Use the sidebar to get started.
            """
        )
    elif current_page == "upload":
        render_upload_page()
    elif current_page == "explore":
        render_explore_page()
    elif current_page == "analyze":
        render_analyze_page()
    elif current_page == "report":
        render_report_page()
    else:
        st.error("Page not found. Please select a valid page from the sidebar.")


if __name__ == "__main__":
    main()
