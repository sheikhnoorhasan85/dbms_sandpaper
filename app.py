"""
InternHub - Multi-Role Web Application Interface
Course: CS203 Database Management Systems (B.Tech CSE Sem-III, SVNIT Surat)
Team: sandpaper
Title: InternHub
Features:
- Role-Based Access Control (Admin, Mentor, Intern)
- Tailored Views per User Type
- Dual-Engine Support (MySQL Workbench & Autonomous Cloud Relational Engine)
- Ready for Public Cloud Deployment
"""

import streamlit as st
import pandas as pd
import datetime
import os

from db_helper import DatabaseManager
import mock_data

# Page configuration
st.set_page_config(
    page_title="InternHub | DBMS Project (Team sandpaper)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling (Formal Enterprise Theme & Top Navigation System)
st.markdown("""
<style>
    /* Permanently hide Streamlit sidebar and collapse control across ALL views */
    [data-testid="stSidebar"], 
    [data-testid="collapsedControl"],
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* Global Light Theme Canvas */
    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
    }

    /* Main Container Width & Formal Spacing */
    .main .block-container {
        max-width: 1320px !important;
        padding-top: 1.25rem !important;
        padding-bottom: 3rem !important;
        margin: 0 auto !important;
    }

    /* Formal Top Navbar Container Card */
    div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
        padding: 0.55rem 1rem !important;
        margin-bottom: 0.85rem !important;
    }

    /* Top Taskbar on Landing Page */
    .landing-taskbar {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }

    /* Formal Enterprise Feature Cards */
    .feature-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }
    .feature-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.06);
    }

    .pill-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 500;
        background: #F1F5F9;
        color: #475569;
        border: 1px solid #E2E8F0;
        margin-right: 6px;
        margin-top: 6px;
    }

    /* Universal Buttons - Formal, Crisp & Aligned */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        padding: 0.42rem 1rem !important;
        border: 1px solid #CBD5E1 !important;
        background: #FFFFFF !important;
        color: #1E293B !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
        transition: all 0.15s ease-in-out !important;
        line-height: 1.35 !important;
        min-height: 2.25rem !important;
    }
    .stButton > button:hover {
        border-color: #4F46E5 !important;
        color: #4F46E5 !important;
        background: #F8FAFC !important;
        box-shadow: 0 2px 5px rgba(79, 70, 229, 0.12) !important;
    }
    .stButton > button:active {
        transform: scale(0.98) !important;
        background: #F1F5F9 !important;
    }

    /* Sign Out Button Specific Style (Discreet, Formal Red Hover) */
    div[data-testid="stVerticalBlockBorderWrapper"] .stButton > button {
        border: 1px solid #E2E8F0 !important;
        color: #475569 !important;
        font-weight: 500 !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] .stButton > button:hover {
        border-color: #FCA5A5 !important;
        color: #DC2626 !important;
        background: #FEF2F2 !important;
        box-shadow: 0 1px 3px rgba(220, 38, 38, 0.1) !important;
    }

    /* Primary Action Submit Buttons */
    .stFormSubmitButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.5rem 1.25rem !important;
        background: #4F46E5 !important;
        color: #FFFFFF !important;
        border: 1px solid #4338CA !important;
        box-shadow: 0 1px 3px rgba(79, 70, 229, 0.25) !important;
        transition: all 0.15s ease-in-out !important;
        line-height: 1.35 !important;
        min-height: 2.35rem !important;
    }
    .stFormSubmitButton > button:hover {
        background: #4338CA !important;
        border-color: #3730A3 !important;
        box-shadow: 0 3px 8px rgba(79, 70, 229, 0.3) !important;
        color: #FFFFFF !important;
    }
    .stFormSubmitButton > button:active {
        transform: scale(0.98) !important;
        background: #3730A3 !important;
    }

    /* Form Inputs & Selects */
    div[data-baseweb="input"] {
        border-radius: 8px !important;
        background-color: #FFFFFF !important;
        border-color: #E2E8F0 !important;
        transition: all 0.15s ease !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #4F46E5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
    }
    div[data-baseweb="select"] > div {
        border-radius: 8px !important;
        border-color: #E2E8F0 !important;
    }

    /* Formal Enterprise Underline Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px !important;
        background-color: transparent !important;
        padding: 0 !important;
        border-bottom: 1px solid #E2E8F0 !important;
        margin-bottom: 1.25rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0 !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        color: #64748B !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        background-color: transparent !important;
        transition: all 0.15s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #0F172A !important;
        border-bottom-color: #CBD5E1 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #4F46E5 !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #4F46E5 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* KPI Metric Cards - Clean Formal Box */
    div[data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03) !important;
        transition: border-color 0.15s ease !important;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #CBD5E1 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.55rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        color: #64748B !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Database Manager Initialization
# -----------------------------------------------------------------------------
if "db_manager" not in st.session_state:
    st.session_state.db_manager = DatabaseManager(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "internhub_db"),
        engine_mode="auto"
    )

# -----------------------------------------------------------------------------
# Session State: Authentication & Role Management
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None  # "admin", "mentor", "intern"
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}

def logout():
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_profile = {}
    st.rerun()

def login_as(role: str, profile: dict):
    st.session_state.authenticated = True
    st.session_state.user_role = role
    st.session_state.user_profile = profile
    st.rerun()

# -----------------------------------------------------------------------------
# Helper: Query execution with fallback
# -----------------------------------------------------------------------------
def run_db_query(query: str, params: tuple = None, fallback_func=None):
    try:
        return st.session_state.db_manager.execute_query(query, params)
    except Exception as e:
        if fallback_func:
            return fallback_func()
        return pd.DataFrame()

# -----------------------------------------------------------------------------
# Top Taskbar Functions (Unified Formal Navigation Bar)
# -----------------------------------------------------------------------------
def render_landing_taskbar():
    st.markdown("""
    <div class="landing-taskbar">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="background: #4F46E5; width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; color: #ffffff; flex-shrink: 0;">
                🎓
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-weight: 700; font-size: 1.15rem; color: #0F172A; letter-spacing: -0.01em;">InternHub</span>
                    <span style="background: #EEF2FF; color: #4F46E5; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; border: 1px solid #C7D2FE;">SVNIT SURAT</span>
                </div>
                <div style="font-size: 0.75rem; color: #64748B;">Academic Internship Management System</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #ECFDF5; border: 1px solid #A7F3D0; padding: 4px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; color: #065F46;">
                <span style="width: 7px; height: 7px; background: #10B981; border-radius: 50%; display: inline-block;"></span>
                <span>Cloud Relational Engine Active</span>
            </div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 4px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; color: #475569;">
                Team sandpaper
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_authenticated_taskbar(role: str, profile: dict):
    role_labels = {
        "admin": "Administrator",
        "mentor": "Faculty Mentor",
        "intern": "Student Intern"
    }
    role_title = role_labels.get(role, role.capitalize())
    badge_style = {
        "admin": "background: #EEF2FF; color: #4338CA; border: 1px solid #C7D2FE;",
        "mentor": "background: #F0F9FF; color: #0284C7; border: 1px solid #BAE6FD;",
        "intern": "background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0;"
    }.get(role, "background: #F1F5F9; color: #475569; border: 1px solid #E2E8F0;")
    
    eng = st.session_state.db_manager.active_engine
    eng_label = "MySQL Server" if eng == "mysql" else "Cloud SQLite"
    eng_color = "#10B981" if eng == "mysql" else "#0284C7"
    eng_bg = "#ECFDF5" if eng == "mysql" else "#F0F9FF"
    eng_border = "#A7F3D0" if eng == "mysql" else "#BAE6FD"

    with st.container(border=True):
        col_brand, col_engine, col_user, col_action = st.columns(
            [2.5, 2.2, 3.8, 1.2], 
            vertical_alignment="center"
        )
        with col_brand:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background: #4F46E5; width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.15rem; color: #ffffff; flex-shrink: 0;">
                    🎓
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; line-height: 1.2;">InternHub</div>
                    <div style="font-size: 0.74rem; color: #64748B; font-weight: 500;">SVNIT Surat</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_engine:
            st.markdown(f"""
            <div style="display: inline-flex; align-items: center; gap: 6px; background: {eng_bg}; border: 1px solid {eng_border}; padding: 4px 10px; border-radius: 9999px; font-size: 0.76rem; font-weight: 600; color: #334155;">
                <span style="width: 7px; height: 7px; background: {eng_color}; border-radius: 50%; display: inline-block;"></span>
                <span>Engine: {eng_label}</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col_user:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 8px; justify-content: flex-end;">
                <div style="text-align: right;">
                    <div style="font-weight: 600; font-size: 0.88rem; color: #0F172A; line-height: 1.2;">{profile.get('name', 'User')}</div>
                    <div style="font-size: 0.74rem; color: #64748B;">{profile.get('email', '')}</div>
                </div>
                <span style="{badge_style} font-size: 0.72rem; font-weight: 700; padding: 3px 8px; border-radius: 6px; letter-spacing: 0.02em; white-space: nowrap;">
                    {role_title}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
        with col_action:
            if st.button("Sign Out", key="topbar_signout", use_container_width=True):
                logout()

# =============================================================================
# SCREEN 1: LOGIN / ROLE SELECTOR (If not authenticated)
# =============================================================================
if not st.session_state.authenticated:
    # Top Taskbar for Landing Page
    render_landing_taskbar()

    col_login, col_info = st.columns([1.15, 1.35], gap="large")

    with col_login:
        # Quick-Fill Test Accounts Strip (Formal 1-click pills)
        st.markdown("""
        <div style="font-size: 0.76rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
            ⚡ Quick Demo Logins
        </div>
        """, unsafe_allow_html=True)
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            if st.button("Administrator", key="demo_admin", use_container_width=True):
                st.session_state.fill_email = "admin@svnit.ac.in"
                st.session_state.fill_password = "admin123"
                st.rerun()
        with t_col2:
            if st.button("Faculty Mentor", key="demo_mentor", use_container_width=True):
                st.session_state.fill_email = "rajesh.sharma@svnit.ac.in"
                st.session_state.fill_password = "password123"
                st.rerun()
        with t_col3:
            if st.button("Student Intern", key="demo_intern", use_container_width=True):
                st.session_state.fill_email = "aarav.shah@example.com"
                st.session_state.fill_password = "password123"
                st.rerun()
        with t_col2:
            if st.button("👨‍🏫 Mentor", key="demo_mentor", use_container_width=True):
                st.session_state.fill_email = "rajesh.sharma@svnit.ac.in"
                st.session_state.fill_password = "password123"
                st.rerun()
        with t_col3:
            if st.button("🎓 Intern", key="demo_intern", use_container_width=True):
                st.session_state.fill_email = "aarav.shah@example.com"
                st.session_state.fill_password = "password123"
                st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Register Student"])

        with tab_login:
            # Initialize fill session states if not present
            if "fill_email" not in st.session_state:
                st.session_state.fill_email = "admin@svnit.ac.in"
            if "fill_password" not in st.session_state:
                st.session_state.fill_password = "admin123"

            with st.form("db_login_form"):
                login_email = st.text_input("Institutional Email", value=st.session_state.fill_email)
                login_password = st.text_input("Password", type="password", value=st.session_state.fill_password)
                submit_login = st.form_submit_button("Sign In to Portal 🚀", use_container_width=True)

                if submit_login:
                    if not login_email.strip() or not login_password.strip():
                        st.error("Please enter both email and password.")
                    else:
                        user = st.session_state.db_manager.authenticate_user(login_email, login_password)
                        if user:
                            role_lower = user["role"].lower()
                            profile = {
                                "id": user["reference_id"] if user["reference_id"] is not None else user["user_id"],
                                "user_id": user["user_id"],
                                "name": user["full_name"],
                                "email": user["email"],
                                "role": user["role"],
                                "detail": f"{user['role']} Account • {user['email']}"
                            }
                            st.success(f"Welcome back, {user['full_name']}!")
                            login_as(role_lower, profile)
                        else:
                            st.error("Invalid credentials or account inactive. Please check your email and password.")

        with tab_register:
            st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #0F172A; margin-bottom: 8px;'>New Student Account Registration</div>", unsafe_allow_html=True)

            with st.form("student_registration_form"):
                rc1, rc2 = st.columns(2)
                with rc1:
                    reg_fn = st.text_input("First Name *", placeholder="e.g. Yash")
                with rc2:
                    reg_ln = st.text_input("Last Name *", placeholder="e.g. Trivedi")

                reg_clg = st.text_input("University / Institute *", value="SVNIT Surat")
                reg_dept = st.selectbox("Department *", [1, 2, 3, 4, 5], format_func=lambda x: f"Dept #{x}: {['CSE','AIDS','ECE','IT','ROBO'][x-1]}")

                # Optional initial mentor preference
                df_reg_mentors = run_db_query("SELECT mentor_id, (first_name || ' ' || last_name) AS name, designation, dept_id FROM mentors")
                reg_mentor_choices = [("None", "Decide Later in Student Dashboard (Recommended)")]
                if not df_reg_mentors.empty:
                    for _, rm in df_reg_mentors.iterrows():
                        reg_mentor_choices.append((str(rm['mentor_id']), f"Mentor #{rm['mentor_id']}: {rm['name']} ({rm['designation']})"))

                selected_reg_mentor = st.selectbox(
                    "Preferred Faculty Mentor (Optional):",
                    options=[c[0] for c in reg_mentor_choices],
                    format_func=lambda x: dict(reg_mentor_choices)[x]
                )

                rc3, rc4 = st.columns(2)
                with rc3:
                    reg_em = st.text_input("Student Email *", placeholder="e.g. yash.t@example.com")
                with rc4:
                    reg_ph = st.text_input("Phone Number *", placeholder="+91 9876543210")

                rc5, rc6 = st.columns(2)
                with rc5:
                    reg_p1 = st.text_input("Choose Password *", type="password", placeholder="Min 6 characters")
                with rc6:
                    reg_p2 = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password")

                reg_submit = st.form_submit_button("Create Student Account 🚀", use_container_width=True)

                if reg_submit:
                    if not reg_fn.strip() or not reg_ln.strip() or not reg_em.strip() or not reg_p1.strip():
                        st.error("Please fill in all mandatory fields.")
                    elif "@" not in reg_em or "." not in reg_em:
                        st.error("Please enter a valid email address.")
                    elif len(reg_p1) < 6:
                        st.error("Password must be at least 6 characters long.")
                    elif reg_p1 != reg_p2:
                        st.error("Passwords do not match. Please re-enter carefully.")
                    else:
                        pref_m_id = None if selected_reg_mentor == "None" else int(selected_reg_mentor)
                        ok, msg = st.session_state.db_manager.register_student_user(
                            reg_fn, reg_ln, reg_em, reg_ph, reg_clg, reg_dept, reg_p1, pref_m_id
                        )
                        if ok:
                            st.success(f"{msg}")
                            st.session_state.fill_email = reg_em.strip().lower()
                            st.session_state.fill_password = reg_p1
                            st.info("👉 Switch to the **'Sign In'** tab above to access your new portal!")
                        else:
                            st.error(f"Registration Failed: {msg}")

    with col_info:
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <span style="background: #EEF2FF; color: #4F46E5; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.05em; border: 1px solid #C7D2FE;">Academic & Research Portal</span>
            <h2 style="font-size: 1.85rem; font-weight: 800; color: #0F172A; margin: 12px 0 8px 0; line-height: 1.25;">Empowering Academic Internships</h2>
            <p style="font-size: 0.95rem; color: #64748B; margin: 0; line-height: 1.55;">
                A unified, role-governed platform connecting student scholars, faculty research supervisors, and campus incubation administration at SVNIT Surat.
            </p>
        </div>

        <div class="feature-card">
            <div style="display: flex; gap: 14px; align-items: flex-start;">
                <div style="background: #EEF2FF; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; flex-shrink: 0; border: 1px solid #C7D2FE;">
                    🎓
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1rem; color: #0F172A;">Student Intern Workspace</div>
                    <div style="font-size: 0.88rem; color: #475569; margin-top: 4px; line-height: 1.45;">
                        Track assigned deliverables, submit project URLs, check in daily working hours, and review monthly stipend slips.
                    </div>
                    <div style="margin-top: 8px;">
                        <span class="pill-tag">Daily Attendance</span>
                        <span class="pill-tag">Deliverables</span>
                        <span class="pill-tag">Stipend Slips</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="feature-card">
            <div style="display: flex; gap: 14px; align-items: flex-start;">
                <div style="background: #E0F2FE; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; flex-shrink: 0; border: 1px solid #BAE6FD;">
                    👨‍🏫
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1rem; color: #0F172A;">Faculty Mentorship Portal</div>
                    <div style="font-size: 0.88rem; color: #475569; margin-top: 4px; line-height: 1.45;">
                        Supervise research scholars, assign project milestones, and score submitted deliverables with live quota tracking.
                    </div>
                    <div style="margin-top: 8px;">
                        <span class="pill-tag">Milestone Grading</span>
                        <span class="pill-tag">Research Supervision</span>
                        <span class="pill-tag">Quota Management</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="feature-card">
            <div style="display: flex; gap: 14px; align-items: flex-start;">
                <div style="background: #ECFDF5; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; flex-shrink: 0; border: 1px solid #A7F3D0;">
                    👑
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1rem; color: #0F172A;">Campus Administration & Incubation</div>
                    <div style="font-size: 0.88rem; color: #475569; margin-top: 4px; line-height: 1.45;">
                        Review applicant registrations, verify faculty quotas, oversee institutional KPIs, and execute automated stipend payroll.
                    </div>
                    <div style="margin-top: 8px;">
                        <span class="pill-tag">Applicant Verification</span>
                        <span class="pill-tag">Automated Payroll</span>
                        <span class="pill-tag">Executive Analytics</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# SCREEN 2: LOGGED IN VIEWS (Different views per user type)
# =============================================================================
else:
    role = st.session_state.user_role
    profile = st.session_state.user_profile

    # Top Taskbar with user identity & quick logout
    render_authenticated_taskbar(role, profile)

    # Collapsible Database Connection & Engine Configuration
    with st.expander("⚙️ Database Engine & Connection Settings", expanded=False):
        c_eng1, c_eng2 = st.columns([1, 2])
        with c_eng1:
            eng = st.session_state.db_manager.active_engine
            eng_choice = st.radio(
                "Active Relational Engine:", 
                ["Autonomous Relational Engine (SQLite)", "MySQL Server (Local/Remote)"], 
                index=0 if eng == "sqlite" else 1
            )
        with c_eng2:
            if eng_choice == "MySQL Server (Local/Remote)":
                m_c1, m_c2 = st.columns(2)
                with m_c1:
                    m_host = st.text_input("Host", value=st.session_state.db_manager.host)
                    m_port = st.number_input("Port", value=st.session_state.db_manager.port, step=1)
                    m_user = st.text_input("User", value=st.session_state.db_manager.user)
                with m_c2:
                    m_pass = st.text_input("Password", type="password", value=st.session_state.db_manager.password)
                    m_db = st.text_input("Database", value=st.session_state.db_manager.database)
                    if st.button("Connect MySQL Server", use_container_width=True):
                        st.session_state.db_manager.host = m_host
                        st.session_state.db_manager.port = int(m_port)
                        st.session_state.db_manager.user = m_user
                        st.session_state.db_manager.password = m_pass
                        st.session_state.db_manager.database = m_db
                        ok, msg = st.session_state.db_manager.set_engine("mysql")
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(f"Connection failed: {msg}")
            else:
                st.info("Operating on Autonomous Relational Engine (SQLite) with pre-seeded datasets, stored procedures, and triggers.")
                if eng != "sqlite":
                    if st.button("Switch to Cloud SQLite Engine", use_container_width=True):
                        st.session_state.db_manager.set_engine("sqlite")
                        st.rerun()

    # -------------------------------------------------------------------------
    # VIEW TYPE 1: ADMIN / HR PORTAL
    # -------------------------------------------------------------------------
    if role == "admin":
        tab_admin1, tab_admin2, tab_admin3, tab_admin4 = st.tabs([
            "Executive Dashboard", 
            "Verify & Onboard Interns", 
            "Monthly Stipend Payroll", 
            "Faculty Mentors & Quotas"
        ])

        with tab_admin1:
            st.markdown("#### Institutional Overview & Real-Time Metrics")
            df_interns = run_db_query("SELECT * FROM vw_intern_master_summary;", fallback_func=mock_data.get_mock_interns)
            df_mentors = run_db_query("SELECT * FROM vw_mentor_workload;", fallback_func=mock_data.get_mock_mentors)
            df_tasks = run_db_query("SELECT * FROM tasks;", fallback_func=mock_data.get_mock_tasks)
            df_stipends = run_db_query("SELECT * FROM stipend_payments;", fallback_func=mock_data.get_mock_stipends)

            m1, m2, m3, m4 = st.columns(4)
            total_i = len(df_interns) if not df_interns.empty else 0
            active_i = len(df_interns[df_interns['status'] == 'ACTIVE']) if not df_interns.empty and 'status' in df_interns.columns else 0
            total_m = len(df_mentors) if not df_mentors.empty else 0
            total_payout = df_stipends['net_amount'].sum() if not df_stipends.empty and 'net_amount' in df_stipends.columns else 0.0

            m1.metric("Enrolled Interns", total_i, f"{active_i} Active")
            m2.metric("Faculty Mentors", total_m, "All Departments")
            m3.metric("Project Deliverables", len(df_tasks) if not df_tasks.empty else 0, "Tracked Milestones")
            m4.metric("Disbursed Stipends", f"₹ {total_payout:,.2f}", "Calculated via Payroll")

            st.markdown("---")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown("##### Department-wise Intern Distribution")
                if not df_interns.empty and 'dept_name' in df_interns.columns:
                    st.bar_chart(df_interns['dept_name'].value_counts())
            with col_d2:
                st.markdown("##### Mentor Workload & Capacity Utilization")
                if not df_mentors.empty:
                    st.dataframe(df_mentors[['mentor_name', 'dept_name', 'current_active_interns', 'max_capacity', 'capacity_status']], use_container_width=True, hide_index=True)

            st.markdown("##### Master Intern Relational View")
            st.dataframe(df_interns, use_container_width=True, hide_index=True)

        with tab_admin2:
            st.markdown("#### Verify Student Registrations & Onboard Interns")

            # Sub-section 1: Pending Self-Registrations
            df_pending = run_db_query("""
                SELECT i.intern_id, (i.first_name || ' ' || i.last_name) AS student_name, 
                       i.email, i.phone, i.college_name, d.dept_name, i.dept_id, i.mentor_id,
                       IFNULL(m.first_name || ' ' || m.last_name, 'Not Selected') AS requested_mentor,
                       IFNULL(m.designation, '') AS requested_mentor_title,
                       i.status
                FROM interns i
                JOIN departments d ON i.dept_id = d.dept_id
                LEFT JOIN mentors m ON i.mentor_id = m.mentor_id
                WHERE i.status = 'APPLIED'
                ORDER BY i.intern_id DESC
            """)

            st.markdown("##### 1. Pending Student Registrations Awaiting Verification")
            if not df_pending.empty:
                st.warning(f"🔔 **{len(df_pending)} student application(s) awaiting verification and mentor allocation.**")
                disp_cols = ['intern_id', 'student_name', 'email', 'college_name', 'dept_name', 'requested_mentor']
                st.dataframe(df_pending[disp_cols], use_container_width=True, hide_index=True)

                with st.form("verify_student_app_form"):
                    st.markdown("###### Verify & Assign Faculty Mentor")
                    app_map = {
                        f"#{r['intern_id']}: {r['student_name']} ({r['dept_name']} • Pref: {r['requested_mentor']})": {
                            "id": r['intern_id'],
                            "name": r['student_name'],
                            "pref_id": r['mentor_id'],
                            "pref_name": r['requested_mentor'],
                            "pref_title": r['requested_mentor_title']
                        }
                        for _, r in df_pending.iterrows()
                    }
                    selected_app_label = st.selectbox("Select Pending Student:", list(app_map.keys()))
                    selected_info = app_map[selected_app_label]
                    selected_intern_id = selected_info["id"]

                    if selected_info["pref_id"] is not None:
                        st.info(f"💡 **Student's Requested Preference:** Mentor #{selected_info['pref_id']} — {selected_info['pref_name']} ({selected_info['pref_title']})")
                    else:
                        st.caption("ℹ️ This student has not chosen a preferred mentor yet. You can assign any available faculty mentor.")

                    # Mentors list with open capacity slots from vw_mentor_workload
                    df_mentors_wl = run_db_query("SELECT mentor_id, mentor_name, designation, dept_name, slots_available, max_capacity FROM vw_mentor_workload")
                    mentor_options = {}
                    default_idx = 0
                    m_idx = 0
                    for _, r in df_mentors_wl.iterrows():
                        slots_txt = f"{r['slots_available']} slots open" if r['slots_available'] > 0 else "FULL"
                        is_pref = " ⭐ [STUDENT'S CHOICE]" if selected_info["pref_id"] == r['mentor_id'] else ""
                        lbl = f"Mentor #{r['mentor_id']}: {r['mentor_name']} ({r['dept_name']} • {slots_txt}){is_pref}"
                        mentor_options[lbl] = r['mentor_id']
                        if selected_info["pref_id"] == r['mentor_id']:
                            default_idx = m_idx
                        m_idx += 1

                    selected_mentor_label = st.selectbox(
                        "Assign Faculty Mentor (Quota Checked):",
                        options=list(mentor_options.keys()),
                        index=default_idx
                    )
                    selected_mentor_id = mentor_options[selected_mentor_label]

                    alloc_stipend = st.number_input("Approved Monthly Base Stipend (₹):", value=15000.0, step=1000.0)

                    col_v1, col_v2 = st.columns(2)
                    with col_v1:
                        btn_approve = st.form_submit_button("Verify & Allocate Mentor", use_container_width=True)
                    with col_v2:
                        btn_reject = st.form_submit_button("Reject Application", use_container_width=True)

                    if btn_approve:
                        ok, msg = st.session_state.db_manager.verify_and_allocate_intern(
                            selected_intern_id, selected_mentor_id, alloc_stipend, profile['name']
                        )
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(f"Approval Failed (Database Constraint / Quota): {msg}")

                    if btn_reject:
                        ok, msg = st.session_state.db_manager.reject_intern_application(
                            selected_intern_id, "Incomplete or unverified academic documentation", profile['name']
                        )
                        if ok:
                            st.warning(msg)
                            st.rerun()
                        else:
                            st.error(f"Rejection Failed: {msg}")
            else:
                st.info("✅ All student registrations are verified! No pending applications.")

            st.markdown("---")
            st.markdown("##### 2. Direct Intern Onboarding")
            st.caption("Onboard new interns directly with departmental allocation and faculty mentor assignment.")

            with st.form("admin_onboard_form"):
                ca1, ca2 = st.columns(2)
                with ca1:
                    fn = st.text_input("First Name", "Aayush")
                    ln = st.text_input("Last Name", "Patel")
                    em = st.text_input("Email", "aayush.p@example.com")
                    ph = st.text_input("Phone", "+91 9825000099")
                    clg = st.text_input("Institute / University", "SVNIT Surat")
                with ca2:
                    d_id = st.selectbox("Department", [1, 2, 3, 4, 5], format_func=lambda x: f"Dept #{x}: {['CSE','AIDS','ECE','IT','ROBO'][x-1]}")
                    m_id = st.selectbox("Assign Faculty Mentor", [1, 2, 3, 4, 5, 6], format_func=lambda x: f"Mentor #{x} (Check quota)")
                    s_dt = st.date_input("Start Date", datetime.date(2026, 9, 1))
                    e_dt = st.date_input("End Date", datetime.date(2026, 12, 31))
                    stip = st.number_input("Monthly Stipend (₹)", value=20000.0, step=1000.0)

                if st.form_submit_button("Onboard Student Intern", use_container_width=True):
                    try:
                        new_id, msg = st.session_state.db_manager.call_sp_onboard_intern(
                            fn, ln, em, ph, clg, d_id, m_id, str(s_dt), str(e_dt), stip
                        )
                        st.success(f"Intern successfully onboarded: {msg} (Assigned Intern ID: #{new_id})")
                    except Exception as ex:
                        st.error(f"Database Constraint/Trigger Error: {ex}")

        with tab_admin3:
            st.markdown("#### Monthly Stipend Payroll Routine")
            st.caption("Calculate monthly student disbursements based on attendance records and performance bonuses.")

            with st.form("admin_stipend_form"):
                cs1, cs2, cs3 = st.columns(3)
                with cs1:
                    pay_m = st.selectbox("Billing Month", list(range(1, 13)), index=8, format_func=lambda m: datetime.date(2026, m, 1).strftime('%B'))
                with cs2:
                    pay_y = st.number_input("Billing Year", value=2026, step=1)
                with cs3:
                    w_days = st.number_input("Standard Working Days in Month", value=22, min_value=1, max_value=31)

                if st.form_submit_button("Run Monthly Payroll Routine", use_container_width=True):
                    try:
                        cnt, tot = st.session_state.db_manager.call_sp_generate_stipend(pay_m, pay_y, w_days)
                        st.success(f"Payroll batch completed! Processed {cnt} intern(s). Total Disbursed: ₹ {tot:,.2f}")
                    except Exception as ex:
                        st.error(f"Execution Error: {ex}")

            st.markdown("##### Disbursed Stipend Statements")
            df_pay = run_db_query("SELECT * FROM stipend_payments ORDER BY payment_id DESC;", fallback_func=mock_data.get_mock_stipends)
            st.dataframe(df_pay, use_container_width=True, hide_index=True)

        with tab_admin4:
            st.markdown("#### Faculty Supervision & Capacity Quotas")
            df_m = run_db_query("SELECT * FROM vw_mentor_workload;", fallback_func=mock_data.get_mock_mentors)
            st.dataframe(df_m, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # VIEW TYPE 2: FACULTY MENTOR PORTAL
    # -------------------------------------------------------------------------
    elif role == "mentor":
        m_id = profile["id"]
        st.info(f"Welcome, **{profile['name']}**. Active portal for research supervision.")

        tab_m1, tab_m2, tab_m3 = st.tabs([
            "Supervised Interns", 
            "Assign Milestone", 
            "Evaluate Submissions"
        ])

        with tab_m1:
            st.markdown("#### Active Interns Under Supervision")
            df_my_interns = run_db_query("SELECT * FROM vw_intern_master_summary WHERE mentor_name LIKE ? OR intern_id IN (SELECT intern_id FROM interns WHERE mentor_id = ?)", (f"%{profile['name'].split()[-1]}%", m_id), fallback_func=mock_data.get_mock_interns)
            st.dataframe(df_my_interns, use_container_width=True, hide_index=True)

        with tab_m2:
            st.markdown("#### Assign New Project Milestone")
            with st.form("mentor_assign_task_form"):
                # Get this mentor's interns
                df_assigned = run_db_query("SELECT intern_id, first_name || ' ' || last_name AS name FROM interns WHERE mentor_id = ?", (m_id,))
                intern_map = {f"#{row['intern_id']} - {row['name']}": row['intern_id'] for _, row in df_assigned.iterrows()} if not df_assigned.empty else {"#1 - Aarav Shah": 1}

                t_intern = st.selectbox("Target Intern", list(intern_map.keys()))
                t_title = st.text_input("Milestone Title", "Design BCNF Normalization Schema")
                t_desc = st.text_area("Requirements & Scope", "Analyze the functional dependencies and produce the relational mapping.")
                t_dead = st.date_input("Deadline", datetime.date(2026, 11, 20))

                if st.form_submit_button("Assign Milestone", use_container_width=True):
                    try:
                        q = "INSERT INTO tasks (intern_id, assigned_by, title, description, deadline, status) VALUES (?, ?, ?, ?, ?, 'TODO')"
                        st.session_state.db_manager.execute_dml(q, (intern_map[t_intern], m_id, t_title, t_desc, str(t_dead)))
                        st.success(f"Task '{t_title}' successfully assigned!")
                    except Exception as ex:
                        st.error(f"Error: {ex}")

        with tab_m3:
            st.markdown("#### Review & Score Submitted Deliverables")
            df_pending = run_db_query("""
                SELECT t.task_id, i.first_name || ' ' || i.last_name AS intern_name, t.title, t.status, t.submission_url, t.score
                FROM tasks t
                JOIN interns i ON t.intern_id = i.intern_id
                WHERE t.assigned_by = ?
            """, (m_id,), fallback_func=mock_data.get_mock_tasks)
            
            st.dataframe(df_pending, use_container_width=True, hide_index=True)

            with st.form("grade_task_form"):
                t_id_input = st.number_input("Task ID to Grade", min_value=1, value=int(df_pending['task_id'].iloc[0]) if not df_pending.empty else 1)
                new_status = st.selectbox("Update Status", ["APPROVED", "REJECTED", "IN_PROGRESS"])
                new_score = st.slider("Score (0.0 to 100.0)", 0.0, 100.0, 92.5, 0.5)

                if st.form_submit_button("Update Task Evaluation", use_container_width=True):
                    try:
                        score_val = new_score if new_status == "APPROVED" else None
                        q = "UPDATE tasks SET status = ?, score = ? WHERE task_id = ?"
                        st.session_state.db_manager.execute_dml(q, (new_status, score_val, t_id_input))
                        st.success(f"Task #{t_id_input} updated to {new_status} with score {score_val}!")
                    except Exception as ex:
                        st.error(f"Validation Error: {ex}")

    # -------------------------------------------------------------------------
    # VIEW TYPE 3: STUDENT INTERN PORTAL
    # -------------------------------------------------------------------------
    elif role == "intern":
        i_id = profile["id"]
        st.info(f"Welcome, **{profile['name']}**. Student Academic Workspace.")

        tab_i1, tab_i2, tab_i3, tab_i4 = st.tabs([
            "Profile & Mentorship", 
            "Daily Attendance", 
            "Deliverables & Submissions", 
            "Monthly Stipend Slips"
        ])

        with tab_i1:
            st.markdown("#### Internship Details")
            df_me = run_db_query("SELECT * FROM vw_intern_master_summary WHERE intern_id = ?", (i_id,), fallback_func=mock_data.get_mock_interns)
            if not df_me.empty:
                me = df_me.iloc[0]
                status_val = str(me.get("status", "ACTIVE"))
                pref_mentor = str(me.get("mentor_name", "Unassigned"))

                if status_val == "APPLIED":
                    if pref_mentor != "Unassigned":
                        st.success(f"⏳ **Mentor Preference Submitted:** You have requested **{pref_mentor}** ({me.get('mentor_designation', '')}). Your application is currently awaiting Admin verification & quota approval.")
                    else:
                        st.warning("⚠️ **Action Required: Choose Your Preferred Faculty Mentor.** Please review the available research supervisors below and select your preferred mentor to proceed with your application.")
                elif status_val == "TERMINATED":
                    st.error("❌ **Application Inactive / Rejected:** Please contact the incubation office for details.")

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Status", status_val, "Enrolled" if status_val == "ACTIVE" else "Pending Review")
                c2.metric("Faculty Mentor", pref_mentor, "Assigned" if status_val == "ACTIVE" else "Preference")
                c3.metric("Base Stipend", f"₹ {float(me.get('base_stipend', 0)):,.2f}")
                c4.metric("Performance Score", f"{float(me.get('composite_performance_score', 90.0)):.1f}%", "Weighted Formula")
                
                st.markdown("---")
                st.write(f"**Department:** {me.get('dept_name', 'Computer Science & Engineering')}")
                st.write(f"**Institution:** {me.get('college_name', 'SVNIT Surat')}")
                st.write(f"**Duration:** {me.get('start_date')} to {me.get('end_date')}")

                # If status is APPLIED, show the Options Available for the Intern
                if status_val == "APPLIED":
                    st.markdown("---")
                    st.markdown("### 🎯 Explore Mentorship Options Available for You")
                    st.caption("Browse faculty mentors, their research specializations, and current capacity slots. Choose your preferred supervisor for Admin approval:")

                    df_all_mentors = run_db_query("""
                        SELECT mentor_id, mentor_name, dept_name, designation, 
                               max_capacity, current_active_interns, slots_available, capacity_status
                        FROM vw_mentor_workload
                        ORDER BY dept_name, mentor_id
                    """)

                    if not df_all_mentors.empty:
                        m_cols = st.columns(2)
                        for idx, (_, rm) in enumerate(df_all_mentors.iterrows()):
                            with m_cols[idx % 2]:
                                if rm['slots_available'] > 0:
                                    slot_badge = f"<span style='color: #15803D; font-weight: 600; font-size: 0.82rem;'>🟢 {rm['slots_available']} of {rm['max_capacity']} Slots Available</span>"
                                else:
                                    slot_badge = "<span style='color: #B91C1C; font-weight: 600; font-size: 0.82rem;'>🔴 Quota Full (0 Slots Open)</span>"

                                is_current_pick = f"<span style='background: #FEF3C7; color: #92400E; padding: 2px 8px; border-radius: 9999px; font-size: 0.72rem; font-weight: 700;'>CURRENT PICK</span>" if pref_mentor == rm['mentor_name'] else ""

                                st.markdown(f"""
                                <div class="feature-card" style="margin-bottom: 12px; padding: 14px 16px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div style="font-weight: 700; color: #0F172A; font-size: 0.95rem;">👨‍🏫 {rm['mentor_name']}</div>
                                        {is_current_pick}
                                    </div>
                                    <div style="font-size: 0.82rem; color: #475569; margin-top: 2px;"><b>Designation:</b> {rm['designation']}</div>
                                    <div style="font-size: 0.82rem; color: #475569;"><b>Department:</b> {rm['dept_name']}</div>
                                    <div style="margin-top: 6px;">{slot_badge}</div>
                                </div>
                                """, unsafe_allow_html=True)

                        st.markdown("##### 📝 Submit / Update Your Mentor Preference")
                        with st.form("intern_choose_mentor_form"):
                            m_choice_dict = {}
                            for _, rm in df_all_mentors.iterrows():
                                slots_note = f"({rm['slots_available']} open slots)" if rm['slots_available'] > 0 else "(Full - waitlist)"
                                lbl = f"Mentor #{rm['mentor_id']}: {rm['mentor_name']} — {rm['dept_name']} {slots_note}"
                                m_choice_dict[lbl] = rm['mentor_id']

                            sel_lbl = st.selectbox("Select Preferred Faculty Mentor:", list(m_choice_dict.keys()))
                            sel_m_id = m_choice_dict[sel_lbl]
                            project_interest = st.text_input("Area of Interest / Learning Objective (Optional):", placeholder="e.g. Relational indexing, Distributed DBMS, Microservices")

                            submit_pref = st.form_submit_button("Submit Mentor Preference", use_container_width=True)
                            if submit_pref:
                                ok, msg = st.session_state.db_manager.set_intern_preferred_mentor(
                                    i_id, sel_m_id, profile['name']
                                )
                                if ok:
                                    st.success(f"{msg}")
                                    st.rerun()
                                else:
                                    st.error(f"Error submitting preference: {msg}")
            else:
                st.info("Loading student profile...")

        with tab_i2:
            st.markdown("#### Daily Attendance & Working Hours")

            df_status = run_db_query("SELECT status FROM interns WHERE intern_id = ?", (i_id,))
            current_status = df_status.iloc[0]['status'] if not df_status.empty else 'ACTIVE'

            if current_status == 'APPLIED':
                st.info("⏳ **Verification Required:** Attendance logging will unlock once the administrator verifies your application and assigns your Faculty Mentor.")
            else:
                today_date = datetime.date.today()
                today_str = today_date.isoformat()

                # Check if attendance for today already exists in DB
                df_today = run_db_query(
                    "SELECT att_id, att_date, status, hours_logged, remarks FROM attendance WHERE intern_id = ? AND att_date = ?",
                    (i_id, today_str)
                )

                if not df_today.empty:
                    today_record = df_today.iloc[0]
                    st.success(f"🔒 **Today's Attendance Recorded & Locked ({today_str})**")
                    
                    c_t1, c_t2, c_t3 = st.columns(3)
                    c_t1.metric("Status", str(today_record.get('status', 'PRESENT')))
                    c_t2.metric("Working Hours Logged", f"{float(today_record.get('hours_logged', 8.0)):.1f} hrs")
                    c_t3.metric("Policy Status", "Locked (Immutable)", "Tamper Protected")
                    
                    if today_record.get('remarks'):
                        st.info(f"**Remarks:** {today_record.get('remarks')}")

                    st.warning("⚠️ **Policy Notice**: Working hours are recorded once per day and are strictly locked to ensure verifiable institutional records. For corrections, please contact your faculty mentor or administrator.")
                else:
                    st.markdown(f"##### Log Attendance for Today: **{today_date.strftime('%A, %B %d, %Y')}**")
                    with st.form("intern_att_form"):
                        st.text_input("Calendar Date (Locked to Today)", value=today_str, disabled=True)
                        att_st = st.selectbox("Attendance Status", ["PRESENT", "WORK_FROM_HOME", "ON_LEAVE", "ABSENT"])
                        att_hrs = st.slider("Hours Worked Today (0.0 - 12.0)", 0.0, 12.0, 8.0, 0.5)
                        att_rmk = st.text_input("Daily Work Summary / Activity Log", "Worked on database assignment modules")

                        if st.form_submit_button("Record Today's Attendance", use_container_width=True):
                            try:
                                q = "INSERT INTO attendance (intern_id, att_date, status, hours_logged, remarks) VALUES (?, ?, ?, ?, ?)"
                                st.session_state.db_manager.execute_dml(q, (i_id, today_str, att_st, att_hrs, att_rmk))
                                st.success(f"Attendance recorded for {today_str} as {att_st} ({att_hrs} hrs)! Record is now locked.")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Database Validation Error: {ex}")

            st.markdown("---")
            st.markdown("##### Verified Attendance Records")
            df_my_att = run_db_query(
                "SELECT att_id, att_date, status, hours_logged, remarks FROM attendance WHERE intern_id = ? ORDER BY att_date DESC",
                (i_id,)
            )
            st.dataframe(df_my_att, use_container_width=True, hide_index=True)

        with tab_i3:
            st.markdown("#### Assigned Deliverables & Submissions")
            df_my_tasks = run_db_query("SELECT task_id, title, deadline, status, score, submission_url FROM tasks WHERE intern_id = ?", (i_id,), fallback_func=mock_data.get_mock_tasks)
            st.dataframe(df_my_tasks, use_container_width=True, hide_index=True)

            with st.form("submit_work_form"):
                st.markdown("##### Submit Completed Work Link")
                t_sub_id = st.number_input("Task ID", min_value=1, value=int(df_my_tasks['task_id'].iloc[0]) if not df_my_tasks.empty else 1)
                sub_url = st.text_input("Deliverable URL (GitHub / Google Drive / Report Link)", "https://github.com/sandpaper/internhub/task-submission")

                if st.form_submit_button("Submit Deliverable", use_container_width=True):
                    try:
                        q = "UPDATE tasks SET status = 'SUBMITTED', submission_url = ? WHERE task_id = ? AND intern_id = ?"
                        st.session_state.db_manager.execute_dml(q, (sub_url, t_sub_id, i_id))
                        st.success(f"Task #{t_sub_id} submitted for mentor review!")
                    except Exception as ex:
                        st.error(f"Submission Error: {ex}")

        with tab_i4:
            st.markdown("#### Monthly Stipend Disbursement Statements")
            df_my_stip = run_db_query("SELECT pay_month, pay_year, days_present, total_working_days, calculated_stipend, bonus, net_amount, payment_status, processed_date FROM stipend_payments WHERE intern_id = ? ORDER BY payment_id DESC", (i_id,), fallback_func=mock_data.get_mock_stipends)
            st.dataframe(df_my_stip, use_container_width=True, hide_index=True)
