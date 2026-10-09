import streamlit as st


def apply_theme():

    st.markdown(
        """
<style>

/* ============================================================
   FONT
   ============================================================ */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');


/* ============================================================
   GLOBAL APPLICATION
   ============================================================ */

html,
body,
[class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(
        180deg,
        #07111F 0%,
        #0B1728 100%
    );
    color: #F8FAFC;
}


/* ============================================================
   MAIN CONTENT
   ============================================================ */

.main {
    background: transparent;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

[data-testid="stSidebar"] {
    background: #081220 !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}

[data-testid="stSidebar"] > div {
    background: #081220 !important;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}


/* Sidebar text */

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #E2E8F0;
}


/* ============================================================
   SIDEBAR NAVIGATION
   ============================================================ */

[data-testid="stSidebarNav"] {
    padding-top: 0.5rem;
}

[data-testid="stSidebarNav"] a {
    color: #E2E8F0 !important;
    border-radius: 8px;
    font-weight: 500;
}

[data-testid="stSidebarNav"] a:hover {
    background: #18263A !important;
    color: #FFFFFF !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: #2C3D56 !important;
    color: #FFFFFF !important;
    font-weight: 700;
}


/* ============================================================
   SIDEBAR CUSTOM NAVIGATION
   ============================================================ */

[data-testid="stSidebar"] .stPageLink a {
    color: #E2E8F0 !important;
    text-decoration: none !important;
    border-radius: 8px;
    padding: 0.35rem 0.5rem;
}

[data-testid="stSidebar"] .stPageLink a:hover {
    background: #18263A !important;
    color: #FFFFFF !important;
}


/* ============================================================
   HEADINGS
   ============================================================ */

h1 {
    color: #FFFFFF !important;
    font-weight: 800 !important;
}

h2 {
    color: #F1F5F9 !important;
    font-weight: 700 !important;
}

h3 {
    color: #F1F5F9 !important;
    font-weight: 700 !important;
}

h4 {
    color: #E2E8F0 !important;
    font-weight: 600 !important;
}


/* ============================================================
   NORMAL TEXT
   ============================================================ */

.stApp p {
    color: #CBD5E1;
}

.stApp small {
    color: #94A3B8;
}


/* ============================================================
   LABELS
   ============================================================ */

.stApp label {
    color: #E2E8F0 !important;
    font-weight: 500 !important;
}


/* ============================================================
   TEXT INPUT
   ============================================================ */

.stTextInput input {
    background-color: #101B2C !important;
    color: #FFFFFF !important;

    border: 1px solid #334863 !important;
    border-radius: 10px !important;

    min-height: 42px;
}


/* Text input focus */

.stTextInput input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 1px #3B82F6 !important;
}


/* Placeholder */

.stTextInput input::placeholder {
    color: #64748B !important;
    opacity: 1 !important;
}


/* ============================================================
   PASSWORD INPUT
   ============================================================ */

.stTextInput input[type="password"] {
    color: #FFFFFF !important;
}


/* ============================================================
   TEXT AREA
   ============================================================ */

.stTextArea textarea {
    background-color: #101B2C !important;
    color: #FFFFFF !important;

    border: 1px solid #334863 !important;
    border-radius: 10px !important;
}

.stTextArea textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 1px #3B82F6 !important;
}

.stTextArea textarea::placeholder {
    color: #64748B !important;
    opacity: 1 !important;
}


/* ============================================================
   SELECTBOX
   IMPORTANT: Do NOT use .stSelectbox div
   ============================================================ */

div[data-testid="stSelectbox"] {
    width: 100%;
}


/* Selectbox visible field */

div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #101B2C !important;

    color: #FFFFFF !important;

    border: 1px solid #334863 !important;
    border-radius: 10px !important;

    min-height: 42px;
}


/* Selectbox selected text */

div[data-testid="stSelectbox"]
div[data-baseweb="select"]
span {
    color: #FFFFFF !important;
}


/* Selectbox input */

div[data-testid="stSelectbox"]
div[data-baseweb="select"]
input {
    color: #FFFFFF !important;
}


/* Selectbox placeholder */

div[data-testid="stSelectbox"]
div[data-baseweb="select"]
input::placeholder {
    color: #94A3B8 !important;
    opacity: 1 !important;
}


/* Selectbox arrow */

div[data-testid="stSelectbox"]
svg {
    fill: #CBD5E1 !important;
    color: #CBD5E1 !important;
}


/* Selectbox focus */

div[data-testid="stSelectbox"]
div[data-baseweb="select"]:focus-within > div {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 1px #3B82F6 !important;
}


/* ============================================================
   SELECTBOX DROPDOWN POPUP
   ============================================================ */

div[data-baseweb="popover"] {
    background-color: #101B2C !important;
}

div[data-baseweb="popover"] > div {
    background-color: #101B2C !important;
}


/* Dropdown list */

ul[data-testid="stSelectboxVirtualDropdown"] {
    background-color: #101B2C !important;
}


/* Dropdown options */

div[role="option"] {
    background-color: #101B2C !important;
    color: #F8FAFC !important;
}


/* Dropdown option text */

div[role="option"] span {
    color: #F8FAFC !important;
}


/* Dropdown hover */

div[role="option"]:hover {
    background-color: #243752 !important;
}


/* Selected dropdown option */

div[role="option"][aria-selected="true"] {
    background-color: #263D5D !important;
    color: #FFFFFF !important;
}


/* ============================================================
   DATE INPUT
   ============================================================ */

div[data-testid="stDateInput"] input {
    background-color: #101B2C !important;
    color: #FFFFFF !important;

    border: 1px solid #334863 !important;
    border-radius: 10px !important;
}

div[data-testid="stDateInput"] input::placeholder {
    color: #94A3B8 !important;
}

div[data-testid="stDateInput"] input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 1px #3B82F6 !important;
}


/* ============================================================
   NUMBER INPUT
   ============================================================ */

.stNumberInput input {
    background-color: #101B2C !important;
    color: #FFFFFF !important;

    border: 1px solid #334863 !important;
    border-radius: 10px !important;
}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    background: #2563EB !important;
    color: #FFFFFF !important;

    border: none !important;
    border-radius: 10px !important;

    min-height: 44px;

    font-weight: 600 !important;

    transition:
        background 0.2s ease,
        transform 0.2s ease;
}

.stButton > button:hover {
    background: #1D4ED8 !important;
    color: #FFFFFF !important;

    transform: translateY(-1px);
}

.stButton > button:focus {
    color: #FFFFFF !important;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.35) !important;
}


/* ============================================================
   DOWNLOAD BUTTON
   ============================================================ */

.stDownloadButton > button {
    background: #1E3A5F !important;
    color: #FFFFFF !important;

    border: 1px solid #365477 !important;
    border-radius: 10px !important;

    font-weight: 600 !important;
}

.stDownloadButton > button:hover {
    background: #284C75 !important;
}


/* ============================================================
   TABS
   ============================================================ */

.stTabs [role="tab"] {
    color: #CBD5E1 !important;
    font-weight: 600 !important;
}

.stTabs [role="tab"]:hover {
    color: #FFFFFF !important;
}

.stTabs [aria-selected="true"] {
    color: #FFFFFF !important;
    border-bottom: 3px solid #2563EB !important;
}


/* ============================================================
   METRIC CARDS
   ============================================================ */

[data-testid="metric-container"] {
    background: #111C2E !important;

    border: 1px solid rgba(255,255,255,0.06);

    border-radius: 18px;

    padding: 18px;
}

[data-testid="metric-container"] label {
    color: #94A3B8 !important;
}

[data-testid="metric-container"]
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;

    font-size: 30px;

    font-weight: 700;
}

[data-testid="metric-container"]
[data-testid="stMetricDelta"] {
    color: #CBD5E1 !important;
}


/* ============================================================
   DATAFRAME
   ============================================================ */

[data-testid="stDataFrame"] {
    border-radius: 14px;

    overflow: hidden;

    border: 1px solid rgba(255,255,255,0.08);
}


/* ============================================================
   EXPANDERS
   ============================================================ */

[data-testid="stExpander"] {
    background: #101B2C !important;

    border: 1px solid #24344C !important;

    border-radius: 12px !important;
}

[data-testid="stExpander"] summary {
    color: #F8FAFC !important;
}

[data-testid="stExpander"] summary span {
    color: #F8FAFC !important;
}


/* ============================================================
   ALERTS
   ============================================================ */

div[data-testid="stAlert"] {
    border-radius: 10px;
}


/* Success */

div[data-testid="stAlert"][data-baseweb="notification"] {
    color: #F8FAFC;
}


/* ============================================================
   SUCCESS / ERROR / WARNING / INFO
   ============================================================ */

.stSuccess {
    background: #052E22 !important;
    color: #D1FAE5 !important;
}

.stError {
    background: #3A1111 !important;
    color: #FECACA !important;
}

.stWarning {
    background: #3B2A10 !important;
    color: #FDE68A !important;
}

.stInfo {
    background: #0F2A43 !important;
    color: #BFDBFE !important;
}


/* ============================================================
   CHECKBOX
   ============================================================ */

.stCheckbox label {
    color: #E2E8F0 !important;
}


/* ============================================================
   RADIO BUTTON
   ============================================================ */

.stRadio label {
    color: #E2E8F0 !important;
}


/* ============================================================
   MULTISELECT
   ============================================================ */

div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
    background-color: #101B2C !important;
    color: #FFFFFF !important;

    border: 1px solid #334863 !important;
    border-radius: 10px !important;
}

div[data-testid="stMultiSelect"] span {
    color: #FFFFFF !important;
}


/* Multiselect dropdown */

div[data-testid="stMultiSelect"] div[role="option"] {
    background-color: #101B2C !important;
    color: #FFFFFF !important;
}


/* ============================================================
   FILE UPLOADER
   ============================================================ */

[data-testid="stFileUploader"] {
    width: 100% !important;
    background: #101B2C !important;
    border: 1px dashed #4B6385 !important;
    border-radius: 14px !important;
    padding: 4px !important;
}

/* Main uploader area */
[data-testid="stFileUploader"] section {
    background: #101B2C !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 18px !important;
}

/* Upload label */
[data-testid="stFileUploader"] label {
    color: #F8FAFC !important;
    font-weight: 600 !important;
}

/* All uploader text */
[data-testid="stFileUploader"] section p {
    color: #CBD5E1 !important;
    opacity: 1 !important;
}

/* Small helper text:
   200MB per file • CSV, XLSX, XLS, JSON
*/
[data-testid="stFileUploader"] section small {
    color: #94A3B8 !important;
    opacity: 1 !important;
    font-size: 13px !important;
}

/* Upload button */
[data-testid="stFileUploader"] section button {
    background: #FFFFFF !important;
    color: #111827 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    min-height: 40px !important;
    padding: 6px 18px !important;
    font-weight: 600 !important;
}

/* Upload button text */
[data-testid="stFileUploader"] section button span {
    color: #111827 !important;
    opacity: 1 !important;
}

/* Upload button hover */
[data-testid="stFileUploader"] section button:hover {
    background: #F1F5F9 !important;
    color: #0F172A !important;
    border-color: #94A3B8 !important;
}

/* Upload icon */
[data-testid="stFileUploader"] section button svg {
    color: #111827 !important;
    fill: #111827 !important;
}

/* Drag and drop / uploader instructions */
[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] {
    color: #CBD5E1 !important;
}

[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p {
    color: #CBD5E1 !important;
    opacity: 1 !important;
}

/* Uploaded file name */
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] {
    color: #F8FAFC !important;
    opacity: 1 !important;
}

/* Uploaded file information */
[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
    color: #E2E8F0 !important;
}

/* Remove inherited opacity */
[data-testid="stFileUploader"] * {
    opacity: 1 !important;
}

/* ============================================================
   SLIDER
   ============================================================ */

.stSlider label {
    color: #E2E8F0 !important;
}


/* ============================================================
   DIVIDERS
   ============================================================ */

hr {
    border-color: rgba(255,255,255,0.08) !important;
}


/* ============================================================
   LINKS
   ============================================================ */

a {
    color: #60A5FA !important;
}

a:hover {
    color: #93C5FD !important;
}


/* ============================================================
   SCROLLBAR
   ============================================================ */

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #081220;
}

::-webkit-scrollbar-thumb {
    background: #334863;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #4B6385;
}


/* ============================================================
   HIDE STREAMLIT MENU
   ============================================================ */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* ============================================================
   HEADER
   ============================================================ */

header {
    background: transparent !important;
}


/* ============================================================
   TOOLTIP
   ============================================================ */

[data-testid="stTooltipContent"] {
    background: #18263A !important;
    color: #FFFFFF !important;
}


/* ============================================================
   POPOVERS
   ============================================================ */

div[data-baseweb="popover"] {
    background-color: #101B2C !important;
    color: #FFFFFF !important;
}


/* ============================================================
   CHAT / EMPTY COMPONENT BACKGROUND FIX
   ============================================================ */

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    background: transparent;
}


/* ============================================================
   MOBILE / SMALL SCREEN
   ============================================================ */

@media (max-width: 768px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    h1 {
        font-size: 2rem !important;
    }

    h2 {
        font-size: 1.5rem !important;
    }

    h3 {
        font-size: 1.25rem !important;
    }

}

</style>
""",
        unsafe_allow_html=True,
    )