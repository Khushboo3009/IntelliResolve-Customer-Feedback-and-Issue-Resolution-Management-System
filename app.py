import streamlit as st

from db.init_db import initialize_database
from services.auth_service import (
    authenticate_user,
    create_and_send_otp,
    verify_otp,
    create_employee,
    get_departments,
)
from styles.theme import apply_theme


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="IntelliResolve",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DATABASE
# ============================================================

@st.cache_resource
def setup_database():
    try:
        initialize_database()
        return True
    except Exception as exc:
        st.error("Unable to initialize the IntelliResolve database.")
        st.exception(exc)
        return False


if not setup_database():
    st.stop()


# ============================================================
# THEME
# ============================================================

apply_theme()


# ============================================================
# SESSION STATE
# ============================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "signup_verified" not in st.session_state:
    st.session_state.signup_verified = False

if "signup_email" not in st.session_state:
    st.session_state.signup_email = ""

if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>
/* =========================================================
   HIDE STREAMLIT DEFAULT PAGE NAVIGATION
   ========================================================= */

[data-testid="stSidebarNav"] {
    display: none !important;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

[data-testid="stSidebar"] {
    background: #081220 !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}

[data-testid="stSidebar"] > div:first-child {
    background: #081220 !important;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1rem !important;
    padding-left: 0.65rem !important;
    padding-right: 0.65rem !important;
}


/* =========================================================
   SIDEBAR TEXT
   ========================================================= */

[data-testid="stSidebar"] p {
    color: #E2E8F0 !important;
}


/* =========================================================
   SIDEBAR NAVIGATION LINKS
   ========================================================= */

[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
    border-radius: 8px !important;
    padding: 0.38rem 0.55rem !important;
    margin: 2px 0 !important;
    color: #E2E8F0 !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}

[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
    background: #18263A !important;
    color: #FFFFFF !important;
}


/* =========================================================
   SIDEBAR SECTION TITLES
   ========================================================= */

.ir-section {
    color: #94A3B8 !important;
    font-size: 0.67rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.08em !important;
    margin-top: 1rem !important;
    margin-bottom: 0.3rem !important;
}


/* =========================================================
   SIDEBAR BRAND
   ========================================================= */

.ir-brand-title {
    color: #FFFFFF !important;
    font-size: 1.35rem !important;
    font-weight: 800 !important;
    margin-bottom: 0 !important;
}

.ir-brand-subtitle {
    color: #94A3B8 !important;
    font-size: 0.68rem !important;
    margin-top: 0 !important;
}


/* =========================================================
   USER CARD
   ========================================================= */

.ir-user-card {
    background: #062D2D !important;
    border-radius: 10px !important;
    padding: 0.8rem !important;
}

.ir-user-status {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}


/* =========================================================
   LOGIN PAGE
   ========================================================= */

.ir-login-logo {
    text-align: center;
    font-size: 4rem;
    line-height: 1;
    margin-top: 1rem;
    margin-bottom: 0.4rem;
}

.ir-login-title {
    text-align: center;
    color: #FFFFFF !important;
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.15;
}

.ir-login-subtitle {
    text-align: center;
    color: #94A3B8 !important;
    font-size: 0.95rem;
    margin-top: 0.6rem;
    margin-bottom: 1.5rem;
}


/* =========================================================
   LOGIN FORM
   ========================================================= */

.ir-login-form {
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button {
    border-radius: 10px !important;
    min-height: 44px !important;
}


/* =========================================================
   INPUT LABELS
   ========================================================= */

[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stDateInput"] label {
    color: #E2E8F0 !important;
    font-weight: 600 !important;
}


/* =========================================================
   HEADER / FOOTER
   ========================================================= */

header {
    background: transparent !important;
}

footer {
    visibility: hidden !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HIDE SIDEBAR ON LOGIN
# ============================================================

def hide_sidebar_before_login():

    st.markdown(
        """
<style>
[data-testid="stSidebar"] {
    display: none !important;
}

[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

header {
    visibility: hidden !important;
}
</style>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# LOGIN BRAND
# ============================================================

def render_login_brand():

    st.markdown(
        '<div class="ir-login-logo">🧠</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="ir-login-title">IntelliResolve</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="ir-login-subtitle">'
        'Adaptive Cross-Industry Feedback Intelligence '
        '&amp; Operations Platform'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    hide_sidebar_before_login()

    render_login_brand()

    signin, signup = st.tabs(
        [
            "🔐 Employee Sign In",
            "👤 Employee Sign Up",
        ]
    )


    # ========================================================
    # SIGN IN
    # ========================================================

    with signin:

        left, center, right = st.columns([1, 1, 1])

        with center:

            st.markdown("### Welcome Back")

            email = st.text_input(
                "Official Email",
                placeholder="employee@company.com",
                key="login_email",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )

            if st.button(
                "Sign In",
                width="stretch",
                type="primary",
                key="login_button",
            ):

                clean_email = email.strip().lower()

                if not clean_email:

                    st.warning(
                        "Please enter your email."
                    )

                elif not password:

                    st.warning(
                        "Please enter your password."
                    )

                else:

                    try:

                        user = authenticate_user(
                            clean_email,
                            password,
                        )

                        if user:

                            st.session_state.user = user

                            st.session_state.signup_verified = False
                            st.session_state.signup_email = ""
                            st.session_state.otp_sent = False

                            st.rerun()

                        else:

                            st.error(
                                "Invalid email or password."
                            )

                    except Exception as exc:

                        st.error(
                            "Unable to sign in."
                        )

                        st.exception(exc)


    # ========================================================
    # SIGN UP
    # ========================================================

    with signup:

        left, center, right = st.columns([1, 1, 1])

        with center:

            st.markdown("### Employee Registration")

            full_name = st.text_input(
                "Full Name",
                key="su_name",
            )

            email = st.text_input(
                "Official Email",
                key="su_email",
            )

            password = st.text_input(
                "Create Password",
                type="password",
                key="su_pass",
            )

            confirm = st.text_input(
                "Confirm Password",
                type="password",
                key="su_confirm",
            )


            # ------------------------------------------------
            # DEPARTMENTS
            # ------------------------------------------------

            try:

                departments = get_departments()

            except Exception as exc:

                departments = []

                st.error(
                    "Unable to load departments."
                )

                st.exception(exc)


            if departments:

                department = st.selectbox(
                    "Department",
                    departments,
                    format_func=lambda item: item.name,
                    key="su_department",
                )

            else:

                department = None

                st.warning(
                    "No departments are available."
                )


            # ------------------------------------------------
            # SEND OTP
            # ------------------------------------------------

            if st.button(
                "Send OTP",
                width="stretch",
                key="send_otp_button",
            ):

                clean_email = email.strip().lower()

                if not full_name.strip():

                    st.warning(
                        "Please enter your full name."
                    )

                elif not clean_email:

                    st.warning(
                        "Please enter your official email."
                    )

                elif not password:

                    st.warning(
                        "Please create a password."
                    )

                elif password != confirm:

                    st.error(
                        "Passwords do not match."
                    )

                elif department is None:

                    st.error(
                        "Please select a department."
                    )

                else:

                    try:

                        create_and_send_otp(
                            clean_email,
                            "signup",
                        )

                        st.session_state.signup_email = (
                            clean_email
                        )

                        st.session_state.otp_sent = True

                        st.success(
                            "OTP has been sent to your email."
                        )

                    except Exception as exc:

                        st.error(
                            "Unable to send OTP."
                        )

                        st.exception(exc)


            # ------------------------------------------------
            # VERIFY OTP
            # ------------------------------------------------

            if st.session_state.otp_sent:

                otp = st.text_input(
                    "Enter OTP",
                    key="otp_box",
                    max_chars=6,
                )

                if st.button(
                    "Verify OTP",
                    width="stretch",
                    key="verify_otp_button",
                ):

                    clean_email = (
                        st.session_state.signup_email
                        or email.strip().lower()
                    )

                    if not otp.strip():

                        st.warning(
                            "Please enter the OTP."
                        )

                    else:

                        try:

                            verified = verify_otp(
                                clean_email,
                                otp.strip(),
                                "signup",
                            )

                            if verified:

                                st.session_state.signup_verified = True

                                st.success(
                                    "Email verified successfully."
                                )

                            else:

                                st.error(
                                    "Invalid or expired OTP."
                                )

                        except Exception as exc:

                            st.error(
                                "Unable to verify OTP."
                            )

                            st.exception(exc)


            # ------------------------------------------------
            # CREATE ACCOUNT
            # ------------------------------------------------

            if st.session_state.signup_verified:

                st.success(
                    "Email verified. "
                    "You can now create your employee account."
                )

                if st.button(
                    "Create Employee Account",
                    width="stretch",
                    type="primary",
                    key="create_employee_button",
                ):

                    if department is None:

                        st.error(
                            "Please select a department."
                        )

                    else:

                        try:

                            clean_email = (
                                st.session_state.signup_email
                                or email.strip().lower()
                            )

                            create_employee(
                                full_name.strip(),
                                clean_email,
                                password,
                                department.id,
                            )

                            st.success(
                                "Employee account created successfully. "
                                "You can now sign in."
                            )

                            st.session_state.signup_verified = False
                            st.session_state.signup_email = ""
                            st.session_state.otp_sent = False

                        except Exception as exc:

                            st.error(
                                "Unable to create the employee account."
                            )

                            st.exception(exc)


# ============================================================
# SIDEBAR BRAND
# ============================================================

def render_sidebar_brand():

    # IMPORTANT:
    # Do NOT use multiline HTML here.
    # Native Streamlit components prevent raw HTML
    # from appearing in the sidebar.

    st.markdown("## 🧠 IntelliResolve")

    st.caption(
        "Feedback Intelligence Platform"
    )


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def render_sidebar_navigation():

    # ========================================================
    # MAIN
    # ========================================================

    st.markdown(
        '<div class="ir-section">MAIN</div>',
        unsafe_allow_html=True,
    )

    st.page_link(
        "app.py",
        label="Home",
        icon="🏠",
    )


    # ========================================================
    # DATA & INTELLIGENCE
    # ========================================================

    st.markdown(
        '<div class="ir-section">DATA & INTELLIGENCE</div>',
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/1_Data_Ingestion.py",
        label="Data Ingestion",
        icon="📥",
    )

    st.page_link(
        "pages/2_Feedback_Analysis.py",
        label="Feedback Analysis",
        icon="💬",
    )

    st.page_link(
        "pages/7_Predictive_Intelligence.py",
        label="Predictive Intelligence",
        icon="📈",
    )


    # ========================================================
    # ISSUE RESOLUTION
    # ========================================================

    st.markdown(
        '<div class="ir-section">ISSUE RESOLUTION</div>',
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/3_Issue_Management.py",
        label="Issue Management",
        icon="⚠️",
    )

    st.page_link(
        "pages/5_Investigation.py",
        label="Investigation",
        icon="🔍",
    )

    st.page_link(
        "pages/8_Interventions.py",
        label="Interventions",
        icon="🛠️",
    )

    st.page_link(
        "pages/9_Intervention_Outcomes.py",
        label="Intervention Outcomes",
        icon="🎯",
    )


    # ========================================================
    # OPERATIONS
    # ========================================================

    st.markdown(
        '<div class="ir-section">OPERATIONS</div>',
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/4_Operations_Control.py",
        label="Operations Control",
        icon="⚙️",
    )

    st.page_link(
        "pages/6_Operations_Dashboard.py",
        label="Operations Dashboard",
        icon="📊",
    )

    st.page_link(
        "pages/SLA_Escalations.py",
        label="SLA & Escalations",
        icon="⏰",
    )

    st.page_link(
        "pages/Alerts.py",
        label="Alerts",
        icon="🚨",
    )


    # ========================================================
    # RECORDS
    # ========================================================

    st.markdown(
        '<div class="ir-section">RECORDS</div>',
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/10_History.py",
        label="History",
        icon="🕘",
    )


# ============================================================
# SIDEBAR USER
# ============================================================

def render_sidebar_user():

    user = st.session_state.user

    full_name = user.get(
        "full_name",
        "Employee",
    )

    role = user.get(
        "role",
        "Department User",
    )

    department = user.get(
        "department",
        "N/A",
    )

    st.markdown("---")

    # Native Streamlit only.
    # No HTML here.

    st.markdown(
        "### 👤 Employee Logged In"
    )

    st.markdown(
        f"**{full_name}**"
    )

    st.caption(
        f"Role: {role}"
    )

    st.caption(
        f"Department: {department}"
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

    with st.sidebar:

        render_sidebar_brand()

        st.divider()

        render_sidebar_navigation()

        render_sidebar_user()

        st.divider()

        if st.button(
            "🚪 Sign Out",
            width="stretch",
            key="logout_button",
        ):

            st.session_state.user = None

            st.session_state.signup_verified = False
            st.session_state.signup_email = ""
            st.session_state.otp_sent = False

            st.rerun()


# ============================================================
# HOME PAGE
# ============================================================

def home():

    user = st.session_state.user

    full_name = user.get(
        "full_name",
        "Employee",
    )

    role = user.get(
        "role",
        "Department User",
    )

    department = user.get(
        "department",
        "N/A",
    )

    st.title(
        "Executive Operations Center"
    )

    st.write(
        f"Welcome, **{full_name}**."
    )

    st.info(
        "IntelliResolve provides a connected workflow for "
        "feedback analysis, issue detection, investigation, "
        "interventions, operational monitoring and outcomes."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Role",
            role,
        )

    with col2:

        st.metric(
            "Department",
            department,
        )

    with col3:

        st.metric(
            "Account Status",
            "Active",
        )


# ============================================================
# START APPLICATION
# ============================================================

if st.session_state.user is None:

    login_page()

else:

    render_sidebar()

    home()