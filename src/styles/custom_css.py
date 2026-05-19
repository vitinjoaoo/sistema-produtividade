import streamlit as st

def estilo():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #D1D9E6 !important;
        }

        /* CARDS */
        .metric-card {
            background-color: #D1D9E6 !important;
            padding: 20px;
            border-radius: 20px;
            box-shadow: 9px 9px 16px #A3B1C6, -9px -9px 16px #F0F5FF !important;
            color: #313945 !important;
        }

        /* INPUTS E FORMULÁRIOS */
        .stTextInput > div > div > input {
            background-color: #D1D9E6 !important;
            color: #313945 !important;
            border-radius: 10px !important;
            border: none !important;
            box-shadow: inset 2px 2px 5px #B8C2CC, inset -2px -2px 5px #F0F5FF !important;
        }

        .stButton > button {
            background-color: #D1D9E6 !important;
            box-shadow: 5px 5px 10px #B8C2CC, -5px -5px 10px #F0F5FF !important;
            color: #313945 !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
        }
        
        h1, h2, h3, p, span, label { color: #313945 !important; }
        </style>
    """, unsafe_allow_html=True)