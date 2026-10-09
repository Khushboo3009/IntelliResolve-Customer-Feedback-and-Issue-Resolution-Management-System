import streamlit as st

def app_header(page_title: str):

    st.markdown("""
    <div style="padding:15px 0 25px 0;">
        <h1 style="color:#F8FAFC;margin-bottom:0;">
            🧠 IntelliResolve
        </h1>
        <p style="color:#94A3B8;font-size:18px;">
        Intelligent Customer Feedback & Resolution System
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"## {page_title}")
    st.divider()