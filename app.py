import streamlit as st
from components.header import render_header
from components.sidebar import render_sidebar, render_upload_page
from components.explore import render_explore_page
from components.analyze import render_analyze_page
from components.report import render_report_page

def main():
    # Render the header
    render_header()
    
    # Render the sidebar and get the current page
    current_page = render_sidebar()
    
    # Route to the selected page
    if current_page == "home":
        st.write("Welcome to EasyAnalytics! Use the sidebar to navigate through the app.")
    elif current_page == "upload":
        render_upload_page()
    elif current_page == "explore":
        render_explore_page()
    elif current_page == "analyze":
        render_analyze_page()
    elif current_page == "generate":
        render_report_page()
    else:
        st.error("Page not found. Please select a valid page from the sidebar.")

if __name__ == "__main__":
    main()
