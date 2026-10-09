import streamlit as st

def page_header(title: str, subtitle: str):
    st.markdown(f'<div class="ir-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ir-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def card(title: str, value: str, description: str = ""):
    st.markdown(
        f'''
        <div class="ir-card">
            <div class="ir-card-title">{title}</div>
            <div class="ir-card-value">{value}</div>
            <div class="ir-muted">{description}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

def status_badge(text: str, kind: str = "success"):
    css = {
        "success": "ir-success",
        "warning": "ir-warning",
        "danger": "ir-danger",
    }.get(kind, "ir-success")
    st.markdown(
        f'<span class="ir-status {css}">{text}</span>',
        unsafe_allow_html=True,
    )
