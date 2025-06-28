import streamlit as st

def render_header():
    """Render the header for EasyAnalytics application."""
    st.set_page_config(
        page_title="EasyAnalytics - Data Analysis Made Simple",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main header
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://img.icons8.com/fluency/96/000000/combo-chart.png", width=80)
    with col2:
        st.title("EasyAnalytics")
        st.markdown("### Data Analysis Made Simple for Everyone")
    
    st.markdown("---")

    # Custom CSS for better styling
    st.markdown("""
    <style>
        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Header styling */
        h1 {
            color: #1E88E5;
            font-weight: bold;
        }
        
        h3 {
            color: #424242;
            margin-top: -0.5rem;
        }
        
        /* Card styling */
        div.stCard {
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 5px;
            font-weight: bold;
        }
        
        /* Table styling */
        .dataframe {
            font-family: Arial, sans-serif;
            font-size: 14px;
            border-collapse: collapse;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #f1f1f1;
            border-radius: 5px;
            padding: 10px 20px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1E88E5;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)