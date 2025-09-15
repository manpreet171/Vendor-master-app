import streamlit as st

def format_currency(value):
    """Format a value as currency"""
    if value is None:
        return "N/A"
    return f"${value:.2f}"

def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app"""
    st.markdown("""
    <style>
        .main {
            padding: 1rem;
        }
        .stProgress > div > div > div > div {
            background-color: #4CAF50;
        }
        .success-message {
            padding: 1rem;
            background-color: #d4edda;
            color: #155724;
            border-radius: 0.25rem;
            margin-bottom: 1rem;
        }
        .error-message {
            padding: 1rem;
            background-color: #f8d7da;
            color: #721c24;
            border-radius: 0.25rem;
            margin-bottom: 1rem;
        }
        .info-message {
            padding: 1rem;
            background-color: #d1ecf1;
            color: #0c5460;
            border-radius: 0.25rem;
            margin-bottom: 1rem;
        }
        .warning-message {
            padding: 1rem;
            background-color: #fff3cd;
            color: #856404;
            border-radius: 0.25rem;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
