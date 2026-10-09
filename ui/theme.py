import streamlit as st

def apply_theme():
    st.set_page_config(
        page_title="IntelliResolve",
        page_icon="IR",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        '''
        <style>
        :root {
            --ir-bg: #0b1020;
            --ir-surface: #111827;
            --ir-surface-2: #172033;
            --ir-border: #2a3852;
            --ir-text: #f8fafc;
            --ir-muted: #cbd5e1;
            --ir-accent: #60a5fa;
            --ir-success: #34d399;
            --ir-warning: #fbbf24;
            --ir-danger: #fb7185;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background: var(--ir-bg) !important;
            color: var(--ir-text) !important;
        }

        [data-testid="stHeader"] {
            background: var(--ir-bg) !important;
        }

        [data-testid="stSidebar"] {
            background: #080d19 !important;
            border-right: 1px solid var(--ir-border);
        }

        [data-testid="stSidebar"] * {
            color: var(--ir-text) !important;
        }

        .stMarkdown, .stText, label, p, span, div {
            color: var(--ir-text);
        }

        .ir-muted {
            color: var(--ir-muted) !important;
        }

        .ir-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: var(--ir-text) !important;
            margin-bottom: 0.2rem;
        }

        .ir-subtitle {
            font-size: 1rem;
            color: var(--ir-muted) !important;
            margin-bottom: 1.5rem;
        }

        .ir-card {
            background: var(--ir-surface) !important;
            border: 1px solid var(--ir-border);
            border-radius: 14px;
            padding: 18px;
            min-height: 125px;
        }

        .ir-card-title {
            color: var(--ir-muted) !important;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .ir-card-value {
            color: var(--ir-text) !important;
            font-size: 1.7rem;
            font-weight: 800;
            margin-top: 8px;
        }

        .ir-status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.8rem;
        }

        .ir-success { color: #052e1b !important; background: var(--ir-success); }
        .ir-warning { color: #3b2500 !important; background: var(--ir-warning); }
        .ir-danger { color: #3b0710 !important; background: var(--ir-danger); }

        .stButton > button {
            border-radius: 9px !important;
            min-height: 42px !important;
            font-weight: 700 !important;
        }

        input, textarea, select, [data-baseweb="input"],
        [data-baseweb="select"], [data-baseweb="textarea"] {
            color: var(--ir-text) !important;
            background: var(--ir-surface-2) !important;
        }

        input::placeholder, textarea::placeholder {
            color: #aebbd0 !important;
            opacity: 1 !important;
        }

        [data-baseweb="select"] * {
            color: var(--ir-text) !important;
        }

        [role="listbox"] {
            background: var(--ir-surface) !important;
        }

        [role="option"] {
            color: var(--ir-text) !important;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--ir-border);
            border-radius: 10px;
        }

        [data-testid="stMetric"] {
            background: var(--ir-surface);
            border: 1px solid var(--ir-border);
            padding: 14px;
            border-radius: 12px;
        }

        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"] {
            color: var(--ir-text) !important;
        }

        hr {
            border-color: var(--ir-border) !important;
        }

        a {
            color: var(--ir-accent) !important;
        }

        @media (max-width: 900px) {
            .ir-title { font-size: 1.7rem; }
            .ir-card { min-height: 100px; }
        }
        </style>
        ''',
        unsafe_allow_html=True,
    )
