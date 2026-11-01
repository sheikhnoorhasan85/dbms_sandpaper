"""
InternHub - Multi-Role Web Application Interface
Course: CS203 Database Management Systems (B.Tech CSE Sem-III, SVNIT Surat)
Team: sandpaper
Title: InternHub
Features:
- Role-Based Access Control (Admin, Mentor, Intern, Evaluator)
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
    initial_sidebar_state="expanded"
)

# Custom Styling — High-Trust Academic & Enterprise UI/UX Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --primary: #4F46E5;
        --primary-hover: #4338CA;
        --primary-light: #EEF2FF;
        --accent-sky: #0EA5E9;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --purple: #8B5CF6;
        --bg-canvas: #F8FAFC;
        --bg-card: #FFFFFF;
        --border-subtle: #E2E8F0;
        --text-main: #0F172A;
        --text-body: #334155;
        --text-muted: #64748B;
    }

    /* Base Font & Unified Canvas Layout (Locked to high-trust synced palette) */
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Synchronized Clean Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
        box-shadow: 1px 0 3px rgba(0, 0, 0, 0.02) !important;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {
        color: #1E293B !important;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3.5rem;
        max-width: 1320px;
    }

    /* Typography Hierarchy */
    h1 {
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        letter-spacing: -0.025em !important;
    }
    h2 {
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        color: #1E293B !important;
        letter-spacing: -0.02em !important;
    }
    h3 {
        font-size: 1.35rem !important;
        font-weight: 600 !important;
        color: #1E293B !important;
    }
    h4, h5 {
        font-weight: 600 !important;
        color: #334155 !important;
    }
    p, span, label {
        font-size: 0.9375rem;
        color: #334155;
    }

    /* Smooth Buttons & Elevation */
    .stButton > button, button[kind="primary"], button[kind="secondary"] {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid transparent !important;
    }
    button[kind="primary"], .stButton > button[kind="primary"] {
        background-color: #4F46E5 !important;
        color: #FFFFFF !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    }
    button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover {
        background-color: #4338CA !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
    }
    /* Secondary & Outline Buttons */
    button[kind="secondary"], .stButton > button:not([kind="primary"]) {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03) !important;
    }
    button[kind="secondary"]:hover, .stButton > button:not([kind="primary"]):hover {
        background-color: #F8FAFC !important;
        border-color: #94A3B8 !important;
        color: #4F46E5 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06) !important;
    }
    .stButton > button:focus {
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2) !important;
    }

    /* Synchronized Form Fields & Inputs */
    input, textarea, select {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
    }
    div[data-baseweb="input"] > div, 
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div {
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        transition: all 0.15s ease-in-out !important;
        color: #0F172A !important;
    }
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        color: #0F172A !important;
        background-color: transparent !important;
    }
    div[data-baseweb="input"] > div:focus-within, 
    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="textarea"] > div:focus-within {
        border-color: #4F46E5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
    }

    /* Dropdown Menus & Popovers */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
    }
    li[role="option"] {
        color: #0F172A !important;
        font-size: 0.9rem !important;
        padding: 8px 12px !important;
    }
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: #EEF2FF !important;
        color: #4F46E5 !important;
    }

    /* Synchronized Clean Form Cards */
    div[data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 24px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
    }

    /* Synchronized Clean Expanders */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03) !important;
        margin-bottom: 12px !important;
    }
    div[data-testid="stExpander"] details {
        background-color: #FFFFFF !important;
    }
    div[data-testid="stExpander"] summary {
        color: #0F172A !important;
        font-weight: 600 !important;
    }
    div[data-testid="stExpander"] summary:hover {
        color: #4F46E5 !important;
    }

    /* Markdown Text & Code Styling */
    .stMarkdown p, .stMarkdown li {
        color: #334155 !important;
        line-height: 1.6 !important;
    }
    .stMarkdown strong {
        color: #0F172A !important;
    }
    code {
        background: #EEF2FF !important;
        color: #4338CA !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-size: 0.85em !important;
        border: 1px solid #C7D2FE !important;
    }
    pre code {
        border: none !important;
    }

    /* Alerts / Callouts */
    div[data-testid="stAlert"] {
        border-radius: 10px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    }

    /* Synchronized Clean Metric Containers */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
    }
    div[data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.72rem !important;
    }

    /* Synchronized Clean Dataframes */
    div[data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 4px !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04) !important;
    }

    /* Clean Pill-Style Route Tabs */
    .stTabs {
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 6px 8px !important;
        gap: 6px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        color: #64748B !important;
        border-radius: 8px !important;
        background-color: transparent !important;
        border: none !important;
        transition: all 0.15s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #4F46E5 !important;
        background-color: #F1F5F9 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #4F46E5 !important;
        background-color: #EEF2FF !important;
        border: none !important;
        box-shadow: 0 1px 2px rgba(79, 70, 229, 0.1) !important;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
        border-radius: 16px;
        padding: 36px 36px;
        color: #FFFFFF;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 24px;
        flex-wrap: wrap;
    }
    .hero-content {
        flex: 1 1 500px;
    }
    .hero-trust-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 14px;
    }
    .trust-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #E0E7FF;
        letter-spacing: 0.02em;
    }
    .hero-title {
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        line-height: 1.25 !important;
        margin-bottom: 10px !important;
    }
    .hero-gradient-text {
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #C7D2FE;
        line-height: 1.55;
        max-width: 620px;
        margin: 0;
    }
    .hero-glass-preview {
        flex: 0 1 360px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(12px);
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        padding: 18px 20px;
        box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.2);
        color: #0F172A;
    }
    .glass-header {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 14px;
        padding-bottom: 8px;
        border-bottom: 1px solid #E2E8F0;
    }
    .glass-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }
    .glass-dot.red { background: #EF4444; }
    .glass-dot.yellow { background: #F59E0B; }
    .glass-dot.green { background: #10B981; }
    .glass-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #475569;
        margin-left: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .glass-stats-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }
    .glass-stat {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px 12px;
    }
    .glass-val {
        font-size: 1.15rem;
        font-weight: 700;
        color: #4F46E5;
        display: block;
    }
    .glass-lbl {
        font-size: 0.72rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    /* Top Sticky Navbar */
    .top-navbar {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 12px 20px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        flex-wrap: wrap;
        gap: 12px;
    }
    .navbar-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .navbar-logo {
        font-size: 1.5rem;
    }
    .navbar-brand {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
    }
    .navbar-chip {
        background: #EEF2FF;
        color: #4F46E5;
        border: 1px solid #C7D2FE;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 9999px;
    }
    .navbar-center {
        display: flex;
        gap: 8px;
    }
    .nav-pill {
        font-size: 0.85rem;
        font-weight: 500;
        color: #64748B;
        padding: 6px 14px;
        border-radius: 9999px;
        background: transparent;
        transition: all 0.15s ease;
    }
    .nav-pill.active {
        background: #EEF2FF;
        color: #4F46E5;
        font-weight: 600;
    }
    .navbar-right {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .user-avatar-pill {
        display: flex;
        align-items: center;
        gap: 10px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 9999px;
        padding: 4px 14px 4px 6px;
    }
    .avatar-circle {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #4F46E5;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .avatar-info {
        display: flex;
        flex-direction: column;
    }
    .avatar-name {
        font-size: 0.82rem;
        font-weight: 600;
        color: #0F172A;
        line-height: 1.2;
    }

    /* KPI / Stat Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
        border-color: #CBD5E1;
    }
    .kpi-top {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }
    .kpi-icon-box {
        width: 42px;
        height: 42px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        flex-shrink: 0;
    }
    .kpi-lbl {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
    }
    .kpi-val {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }

    /* Status Badges */
    .role-badge, .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .badge-admin { background-color: #F3E8FF; color: #6B21A8; border: 1px solid #E9D5FF; }
    .badge-mentor { background-color: #EEF2FF; color: #3730A3; border: 1px solid #C7D2FE; }
    .badge-intern { background-color: #E0F2FE; color: #0369A1; border: 1px solid #BAE6FD; }
    .badge-evaluator { background-color: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
    .badge-active { background-color: #DCFCE7; color: #15803D; border: 1px solid #BBF7D0; }
    .badge-pending { background-color: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
    .badge-danger { background-color: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }

    /* Modern Clean Container Cards */
    .content-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 22px 24px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 16px;
    }

    /* Demo Login Pills Card */
    .demo-pill-card {
        border: 2px dashed #C7D2FE;
        background: #FFFFFF;
        border-radius: 12px;
        padding: 18px 20px;
        margin-top: 18px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
    }
    .demo-tag {
        display: inline-block;
        background: #EEF2FF;
        color: #4F46E5;
        border: 1px solid #C7D2FE;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }
    .demo-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
    }
    .demo-desc {
        font-size: 0.8rem;
        color: #64748B;
        margin-bottom: 12px;
    }

    /* Search & Multi-Filter Bar */
    .filter-bar-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Reusable UI Helpers (KPI Cards & Top Navbar)
# -----------------------------------------------------------------------------
def render_kpi_card(title: str, value: str, delta: str = "", icon: str = "📊", scheme: str = "indigo"):
    bg_colors = {
        "indigo": ("#EEF2FF", "#4F46E5"),
        "sky": ("#E0F2FE", "#0284C7"),
        "emerald": ("#DCFCE7", "#10B981"),
        "amber": ("#FEF3C7", "#D97706"),
        "purple": ("#F3E8FF", "#8B5CF6"),
        "crimson": ("#FEE2E2", "#EF4444"),
    }
    bg_icon, icon_color = bg_colors.get(scheme, ("#EEF2FF", "#4F46E5"))
    delta_html = f'<div style="font-size: 0.8rem; font-weight: 500; color: #64748B; margin-top: 2px;">{delta}</div>' if delta else ""
    
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-top">
            <div class="kpi-icon-box" style="background-color: {bg_icon}; color: {icon_color};">
                {icon}
            </div>
            <div class="kpi-lbl">{title}</div>
        </div>
        <div class="kpi-val">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def render_top_navbar(role: str, profile: dict):
    role_badges = {
        "admin": ('badge-admin', '👑 HR / Administrator'),
        "mentor": ('badge-mentor', '👨‍🏫 Faculty Mentor'),
        "intern": ('badge-intern', '🎓 Student Intern'),
        "evaluator": ('badge-evaluator', '🔍 Academic Evaluator')
    }
    b_class, b_label = role_badges.get(role, ('badge-admin', role.capitalize()))
    name = profile.get("name", "User")
    parts = name.split()
    initials = (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")) if parts else "IH"
    initials = initials.upper()

    col_nav, col_btn = st.columns([5.5, 1])
    with col_nav:
        st.markdown(f"""
        <div class="top-navbar">
            <div class="navbar-left">
                <span class="navbar-logo">🎓</span>
                <span class="navbar-brand">InternHub</span>
                <span class="navbar-chip">SVNIT Surat</span>
            </div>
            <div class="navbar-center">
                <span class="nav-pill active">Dashboard Overview</span>
                <span class="nav-pill">Milestone Tasks</span>
                <span class="nav-pill">Relational Logic</span>
            </div>
            <div class="navbar-right">
                <div class="user-avatar-pill">
                    <div class="avatar-circle">{initials}</div>
                    <div class="avatar-info">
                        <span class="avatar-name">{name}</span>
                        <span class="role-badge {b_class}">{b_label}</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_btn:
        st.write("")
        if st.button("🚪 Sign Out", key="top_sign_out_btn", use_container_width=True):
            logout()

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
    st.session_state.user_role = None  # "admin", "mentor", "intern", "evaluator"
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
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/database.png", width=56)
    st.markdown("### **InternHub Portal**")
    st.caption("Team: **sandpaper** • CS203 SVNIT Surat")
    
    # User Profile Widget if logged in
    if st.session_state.authenticated:
        role = st.session_state.user_role
        prof = st.session_state.user_profile
        
        st.markdown("---")
        badge_class = f"badge-{role}"
        role_label = {
            "admin": "👑 HR / Admin",
            "mentor": "👨‍🏫 Faculty Mentor",
            "intern": "🎓 Student Intern",
            "evaluator": "🔍 Professor / Evaluator"
        }.get(role, role.capitalize())
        
        st.markdown(f'<span class="role-badge {badge_class}">{role_label}</span>', unsafe_allow_html=True)
        st.markdown(f"**{prof.get('name', 'User')}**")
        if "detail" in prof and prof["detail"]:
            st.caption(prof["detail"])
            
        if st.button("🚪 Log Out / Switch Role", use_container_width=True):
            logout()
            
        st.markdown("---")
    
    # Database Engine Status
    st.markdown("#### ⚙️ Database Engine")
    eng = st.session_state.db_manager.active_engine
    if eng == "mysql":
        st.success(f"🟢 **Engine:** MySQL Workbench ({st.session_state.db_manager.database})")
    else:
        st.info("☁️ **Engine:** Autonomous Relational Cloud Engine (SQLite)")
        st.caption("Zero-setup interactive mode with all 8 tables and procedures.")

    # Engine Switcher Expander
    with st.expander("Database Connection Settings"):
        eng_choice = st.radio("Active Engine:", ["Autonomous Cloud Engine (SQLite)", "MySQL Server (Local/Remote)"], 
                              index=0 if eng == "sqlite" else 1)
        if eng_choice == "MySQL Server (Local/Remote)":
            m_host = st.text_input("Host", value=st.session_state.db_manager.host)
            m_port = st.number_input("Port", value=st.session_state.db_manager.port, step=1)
            m_user = st.text_input("User", value=st.session_state.db_manager.user)
            m_pass = st.text_input("Password", type="password", value=st.session_state.db_manager.password)
            m_db = st.text_input("Database", value=st.session_state.db_manager.database)
            
            if st.button("Connect MySQL", use_container_width=True):
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
            if eng != "sqlite":
                if st.button("Switch to Cloud SQLite", use_container_width=True):
                    st.session_state.db_manager.set_engine("sqlite")
                    st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.75rem; color: #94A3B8;">
        Academic Year: 2026-27<br>
        SVNIT Surat • CS203 Project
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# SCREEN 1: LOGIN / ROLE SELECTOR (If not authenticated)
# =============================================================================
if not st.session_state.authenticated:
    # 1. Hero Banner Component Pattern
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-content">
            <div class="hero-trust-badges">
                <span class="trust-badge">🏛️ SVNIT Surat</span>
                <span class="trust-badge">⚡ CS203 DBMS Project</span>
                <span class="trust-badge">🛡️ Role-Based Access Control</span>
                <span class="trust-badge">🔒 SHA-256 Verified Auth</span>
            </div>
            <h1 class="hero-title">
                Unified Internship & <span class="hero-gradient-text">Mentorship Management</span>
            </h1>
            <p class="hero-subtitle">
                A high-trust enterprise database platform orchestrating student onboarding, mentor quotas, tamper-proof attendance, and automated cursor-driven payroll for academic engineering departments.
            </p>
        </div>
        <div class="hero-glass-preview">
            <div class="glass-header">
                <span class="glass-dot red"></span>
                <span class="glass-dot yellow"></span>
                <span class="glass-dot green"></span>
                <span class="glass-title">Database Engine Status: Online</span>
            </div>
            <div class="glass-stats-grid">
                <div class="glass-stat">
                    <span class="glass-val">9 Tables</span>
                    <span class="glass-lbl">BCNF Relational</span>
                </div>
                <div class="glass-stat">
                    <span class="glass-val">4 Portals</span>
                    <span class="glass-lbl">PoLP Isolation</span>
                </div>
                <div class="glass-stat">
                    <span class="glass-val">100%</span>
                    <span class="glass-lbl">Tamper-Proof Time</span>
                </div>
                <div class="glass-stat">
                    <span class="glass-val">Cursor</span>
                    <span class="glass-lbl">Batch Payroll</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_login, col_info = st.columns([1.1, 1.4], gap="large")

    with col_login:
        tab_login, tab_register = st.tabs(["🔐 Account Sign-In", "📝 Student Registration"])

        with tab_login:
            st.markdown("##### 🔐 Sign In with Database Credentials")
            st.caption("Authenticated securely against the relational `users` table via SHA-256 password hash verification.")

            # Initialize fill session states if not present
            if "fill_email" not in st.session_state:
                st.session_state.fill_email = "admin@svnit.ac.in"
            if "fill_password" not in st.session_state:
                st.session_state.fill_password = "admin123"

            with st.form("db_login_form"):
                login_email = st.text_input("Institutional / Registered Email", value=st.session_state.fill_email)
                login_password = st.text_input("Password", type="password", value=st.session_state.fill_password)
                submit_login = st.form_submit_button("Sign In to Database Portal 🚀", use_container_width=True)

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

            # Demo Login Pills (Pattern: Dashed-border highlight card with one-click buttons)
            st.markdown("""
            <div class="demo-pill-card">
                <span class="demo-tag">⚡ DEMO & VIVA EVALUATION</span>
                <div class="demo-title">One-Click Quick Sign-In Pills</div>
                <div class="demo-desc">Select any role to automatically fill verified institutional credentials:</div>
            </div>
            """, unsafe_allow_html=True)
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                if st.button("👑 HR Admin", key="demo_admin", use_container_width=True):
                    st.session_state.fill_email = "admin@svnit.ac.in"
                    st.session_state.fill_password = "admin123"
                    st.rerun()
                if st.button("👨‍🏫 Mentor (Dr. Rajesh)", key="demo_mentor", use_container_width=True):
                    st.session_state.fill_email = "rajesh.sharma@svnit.ac.in"
                    st.session_state.fill_password = "password123"
                    st.rerun()
            with t_col2:
                if st.button("🎓 Intern (Aarav Shah)", key="demo_intern", use_container_width=True):
                    st.session_state.fill_email = "aarav.shah@example.com"
                    st.session_state.fill_password = "password123"
                    st.rerun()
                if st.button("🔍 Academic Evaluator", key="demo_eval", use_container_width=True):
                    st.session_state.fill_email = "evaluator@svnit.ac.in"
                    st.session_state.fill_password = "admin123"
                    st.rerun()

        with tab_register:
            st.markdown("##### 📝 Student Intern Account Registration")
            st.caption("Executes `sp_register_student_user` creating synchronized rows across `interns` and `users` tables within an atomic transaction.")

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
                            st.info("👉 Switch to the **'Account Sign-In'** tab above to log into your new portal!")
                        else:
                            st.error(f"Registration Failed: {msg}")

    with col_info:
        st.markdown("""
        <div class="content-card" style="margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="background: #E0F2FE; color: #0284C7; width: 36px; height: 36px; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.15rem; font-weight: bold;">🎓</span>
                <span style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">For Enrolled Student Interns</span>
            </div>
            <div style="font-size: 0.88rem; color: #475569; line-height: 1.6;">
                • <b>Interactive Mentor Selection:</b> Explore available research supervisors, inspect live slot availability, and submit preferences.<br>
                • <b>Daily Attendance Check-In:</b> Single-click check-in for today's hours protected by database tampering triggers.<br>
                • <b>Milestone Submissions & Stipends:</b> Upload project links and view itemized monthly disbursement slips.
            </div>
        </div>

        <div class="content-card" style="margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="background: #EEF2FF; color: #4F46E5; width: 36px; height: 36px; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.15rem; font-weight: bold;">👨‍🏫</span>
                <span style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">For Faculty Project Mentors</span>
            </div>
            <div style="font-size: 0.88rem; color: #475569; line-height: 1.6;">
                • <b>Research Supervision:</b> Row-level isolation displaying only interns under your research guidance.<br>
                • <b>Deliverable Grading:</b> Score project submissions with trigger checks (0–100 scale).<br>
                • <b>Weekly Reviews & Overrides:</b> Submit structured feedback and make supervisor attendance adjustments with audit logs.
            </div>
        </div>

        <div class="content-card" style="margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="background: #F3E8FF; color: #8B5CF6; width: 36px; height: 36px; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.15rem; font-weight: bold;">👑</span>
                <span style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">For Campus Administration & Incubation</span>
            </div>
            <div style="font-size: 0.88rem; color: #475569; line-height: 1.6;">
                • <b>Institutional Analytics:</b> Departmental metrics, budget tracking, and real-time mentor quota monitoring.<br>
                • <b>Verification & Allocation:</b> Review student applications with student-preferred mentors pre-selected.<br>
                • <b>Automated Payroll:</b> Execute cursor batch payroll computation and inspect immutable system audit logs.
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("ℹ️ SVNIT CS203 DBMS Project & Architecture Notes (For Evaluators)"):
            st.markdown("""
            **Technical Implementation Highlights:**
            - **Authentication Model:** Relational `users` table with SHA-256 cryptographic password hashing.
            - **Role-Based Access Control (RBAC):** Strict role-based isolation (Admin, Mentor, Intern, Evaluator) enforcing the Principle of Least Privilege (PoLP).
            - **Tamper-Proof Working Time:** Database trigger `trg_prevent_attendance_tampering` prevents student hours modification once submitted.
            - **Transactional Registration:** Stored procedure `sp_register_student_user` uses an atomic `START TRANSACTION ... COMMIT` across `interns`, `users`, and `audit_logs`.
            - **Cursor-Based Payroll:** Stored procedure `sp_generate_monthly_stipend` executes explicit cursor loops for pro-rated stipend calculation.
            - **Relational Design:** 9 tables normalized up to BCNF with cascading foreign keys, check constraints, and audit logging.
            """)
            c_m1, c_m2, c_m3 = st.columns(3)
            c_m1.metric("Database Auth", "users Table", "SHA-256")
            c_m2.metric("Tamper Protection", "DB Trigger", "Immutable")
            c_m3.metric("Normalization", "3NF & BCNF", "Zero Redundancy")


# =============================================================================
# SCREEN 2: LOGGED IN VIEWS (Different views per user type)
# =============================================================================
else:
    role = st.session_state.user_role
    profile = st.session_state.user_profile

    # Top Sticky Navbar Component Pattern
    render_top_navbar(role, profile)

    # -------------------------------------------------------------------------
    # VIEW TYPE 1: ADMIN / HR PORTAL
    # -------------------------------------------------------------------------
    if role == "admin":
        tab_admin1, tab_admin2, tab_admin3, tab_admin4, tab_admin5, tab_admin6 = st.tabs([
            "📊 Executive Dashboard", 
            "➕ Verify & Onboard Interns", 
            "💰 Monthly Stipend Run (Cursor)", 
            "👥 Faculty Mentors & Quotas", 
            "🛠️ Attendance Corrections (Override)",
            "📜 System Audit Trail"
        ])

        with tab_admin1:
            st.markdown("#### Institutional Overview & Real-time Metrics")
            df_interns = run_db_query("SELECT * FROM vw_intern_master_summary;", fallback_func=mock_data.get_mock_interns)
            df_mentors = run_db_query("SELECT * FROM vw_mentor_workload;", fallback_func=mock_data.get_mock_mentors)
            df_tasks = run_db_query("SELECT * FROM tasks;", fallback_func=mock_data.get_mock_tasks)
            df_stipends = run_db_query("SELECT * FROM stipend_payments;", fallback_func=mock_data.get_mock_stipends)

            m1, m2, m3, m4 = st.columns(4)
            total_i = len(df_interns) if not df_interns.empty else 0
            active_i = len(df_interns[df_interns['status'] == 'ACTIVE']) if not df_interns.empty and 'status' in df_interns.columns else 0
            total_m = len(df_mentors) if not df_mentors.empty else 0
            total_payout = df_stipends['net_amount'].sum() if not df_stipends.empty and 'net_amount' in df_stipends.columns else 0.0

            with m1:
                render_kpi_card("Enrolled Interns", str(total_i), f"{active_i} Active Students", icon="👥", scheme="indigo")
            with m2:
                render_kpi_card("Faculty Mentors", str(total_m), "Across 5 Departments", icon="👨‍🏫", scheme="sky")
            with m3:
                render_kpi_card("Project Deliverables", str(len(df_tasks) if not df_tasks.empty else 0), "Tracked Milestones", icon="📋", scheme="purple")
            with m4:
                render_kpi_card("Disbursed Stipends", f"₹ {total_payout:,.0f}", "Cursor Computed", icon="💰", scheme="emerald")

            st.markdown("---")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown("##### Department-wise Intern Distribution")
                if not df_interns.empty and 'dept_name' in df_interns.columns:
                    st.bar_chart(df_interns['dept_name'].value_counts())
            with col_d2:
                st.markdown("##### Mentor Workload & Capacity Utilization")
                if not df_mentors.empty:
                    st.dataframe(df_mentors[['mentor_name', 'dept_name', 'current_active_interns', 'max_capacity', 'capacity_status']], use_container_width=True)

            st.markdown("##### Master Intern Relational View (`vw_intern_master_summary`)")
            
            # Embedded Search & Multi-Filter Bar Pattern
            st.markdown('<div class="filter-bar-container">', unsafe_allow_html=True)
            fc1, fc2, fc3, fc4 = st.columns([1.8, 1.2, 1.2, 0.8])
            with fc1:
                adm_sq = st.text_input("🔍 Search Interns", placeholder="Filter by name or email...", key="adm_srch")
            with fc2:
                all_depts = ["All Departments"] + (sorted(df_interns['dept_name'].dropna().unique().tolist()) if not df_interns.empty and 'dept_name' in df_interns.columns else [])
                adm_dept = st.selectbox("Department Filter", all_depts, key="adm_d_flt")
            with fc3:
                adm_stat = st.selectbox("Status Filter", ["All Statuses", "ACTIVE", "APPLIED", "COMPLETED", "TERMINATED"], key="adm_st_flt")
            with fc4:
                st.write("")
                st.write("")
                if st.button("Clear ✕", key="adm_clr_btn", use_container_width=True):
                    st.session_state.adm_srch = ""
                    st.session_state.adm_d_flt = "All Departments"
                    st.session_state.adm_st_flt = "All Statuses"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            df_admin_view = df_interns.copy()
            if not df_admin_view.empty:
                if adm_sq.strip():
                    q = adm_sq.strip().lower()
                    df_admin_view = df_admin_view[
                        df_admin_view['intern_name'].str.lower().str.contains(q, na=False) |
                        df_admin_view['intern_email'].str.lower().str.contains(q, na=False)
                    ]
                if adm_dept != "All Departments":
                    df_admin_view = df_admin_view[df_admin_view['dept_name'] == adm_dept]
                if adm_stat != "All Statuses":
                    df_admin_view = df_admin_view[df_admin_view['status'] == adm_stat]

            st.dataframe(df_admin_view, use_container_width=True)

        with tab_admin2:
            st.markdown("#### 📋 Verify Student Registrations & Onboard Interns")
            st.caption("Review self-registered student applications, allocate faculty mentors (verifying quotas), or onboard interns directly.")

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

            st.markdown("##### 1. Pending Student Self-Registrations Awaiting Verification")
            if not df_pending.empty:
                st.warning(f"🔔 **{len(df_pending)} student application(s) awaiting verification and mentor allocation.**")
                disp_cols = ['intern_id', 'student_name', 'email', 'college_name', 'dept_name', 'requested_mentor']
                st.dataframe(df_pending[disp_cols], use_container_width=True)

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
                        btn_approve = st.form_submit_button("Verify & Allocate Mentor ✅", use_container_width=True)
                    with col_v2:
                        btn_reject = st.form_submit_button("Reject Application ❌", use_container_width=True)

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
            st.markdown("##### 2. Direct Onboarding via Stored Procedure (`sp_onboard_intern`)")
            st.caption("Validates department and mentor quota triggers at the database level before inserting.")

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

                if st.form_submit_button("Execute sp_onboard_intern 🚀", use_container_width=True):
                    try:
                        new_id, msg = st.session_state.db_manager.call_sp_onboard_intern(
                            fn, ln, em, ph, clg, d_id, m_id, str(s_dt), str(e_dt), stip
                        )
                        st.success(f"Procedure executed: {msg} (Assigned Intern ID: #{new_id})")
                    except Exception as ex:
                        st.error(f"Database Constraint/Trigger Error: {ex}")

        with tab_admin3:
            st.markdown("#### Automated Batch Payroll via Stored Procedure with CURSOR")
            st.caption("Iterates over active interns, verifies calendar attendance, computes pro-rated compensation, and awards performance bonuses.")

            with st.form("admin_stipend_form"):
                cs1, cs2, cs3 = st.columns(3)
                with cs1:
                    pay_m = st.selectbox("Billing Month", list(range(1, 13)), index=8, format_func=lambda m: datetime.date(2026, m, 1).strftime('%B'))
                with cs2:
                    pay_y = st.number_input("Billing Year", value=2026, step=1)
                with cs3:
                    w_days = st.number_input("Standard Working Days in Month", value=22, min_value=1, max_value=31)

                if st.form_submit_button("Run Cursor Payroll Routine 💵", use_container_width=True):
                    try:
                        cnt, tot = st.session_state.db_manager.call_sp_generate_stipend(pay_m, pay_y, w_days)
                        st.success(f"Cursor batch completed! Processed {cnt} intern(s). Total Disbursed: ₹ {tot:,.2f}")
                    except Exception as ex:
                        st.error(f"Execution Error: {ex}")

            st.markdown("##### Disbursed Stipend Payments (`stipend_payments`)")
            df_pay = run_db_query("SELECT * FROM stipend_payments ORDER BY payment_id DESC;", fallback_func=mock_data.get_mock_stipends)
            st.dataframe(df_pay, use_container_width=True)

        with tab_admin4:
            st.markdown("#### Faculty Mentors & Quota Monitoring (`vw_mentor_workload`)")
            df_m = run_db_query("SELECT * FROM vw_mentor_workload;", fallback_func=mock_data.get_mock_mentors)
            st.dataframe(df_m, use_container_width=True)

        with tab_admin5:
            st.markdown("#### 🛠️ Supervisor Attendance Hours Adjustment")
            st.caption("Policy Rule: Interns cannot modify logged hours. Only HR Administrators and Mentors can adjust hours with an audit justification.")

            df_all_att = run_db_query("""
                SELECT a.att_id, a.intern_id, i.first_name || ' ' || i.last_name AS intern_name, a.att_date, a.status, a.hours_logged, a.remarks
                FROM attendance a
                JOIN interns i ON a.intern_id = i.intern_id
                ORDER BY a.att_date DESC
            """)

            if not df_all_att.empty:
                st.dataframe(df_all_att, use_container_width=True)

                with st.form("admin_adjust_hours_form"):
                    att_rec_map = {f"Record #{r['att_id']}: {r['intern_name']} on {r['att_date']} (Current: {r['hours_logged']} hrs)": r['att_id'] for _, r in df_all_att.iterrows()}
                    selected_rec_key = st.selectbox("Select Attendance Record to Adjust:", list(att_rec_map.keys()))
                    selected_att_id = att_rec_map[selected_rec_key]

                    c_ad1, c_ad2 = st.columns(2)
                    with c_ad1:
                        new_hrs = st.number_input("Corrected Hours Logged (0.0 - 24.0)", min_value=0.0, max_value=24.0, value=8.0, step=0.5, key="admin_hrs_in")
                    with c_ad2:
                        adjust_reason = st.text_input("Mandatory Adjustment Reason", placeholder="e.g. Verified lab project overtime / Correction", key="admin_reason_in")

                    if st.form_submit_button("Execute sp_adjust_attendance_hours ⚙️", use_container_width=True):
                        if not adjust_reason.strip():
                            st.error("Please provide a valid reason for adjusting logged attendance.")
                        else:
                            ok, msg = st.session_state.db_manager.adjust_attendance_hours(
                                selected_att_id, new_hrs, adjust_reason, profile['name']
                            )
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
            else:
                st.info("No attendance records found.")

        with tab_admin6:
            st.markdown("#### System Audit Trail (`audit_logs`)")
            st.caption("Captures all database triggers, status changes, attendance adjustments, and administrative operations.")
            df_a = run_db_query("SELECT * FROM audit_logs ORDER BY log_id DESC;", fallback_func=mock_data.get_mock_audit_logs)
            st.dataframe(df_a, use_container_width=True)

    # -------------------------------------------------------------------------
    # VIEW TYPE 2: FACULTY MENTOR PORTAL
    # -------------------------------------------------------------------------
    elif role == "mentor":
        m_id = profile["id"]
        st.info(f"👨‍🏫 Welcome, **{profile['name']}**. You are viewing only the student interns and deliverables assigned to your research supervision.")

        tab_m1, tab_m2, tab_m3, tab_m4, tab_m5 = st.tabs([
            "👥 My Supervised Interns", 
            "📝 Assign New Task", 
            "🎯 Evaluate & Score Submissions", 
            "⭐ Submit Weekly Review",
            "🛠️ Adjust Intern Hours (Override)"
        ])

        with tab_m1:
            st.markdown(f"#### Active Interns Under Your Mentorship")
            df_my_interns = run_db_query("SELECT * FROM vw_intern_master_summary WHERE mentor_name LIKE ? OR intern_id IN (SELECT intern_id FROM interns WHERE mentor_id = ?)", (f"%{profile['name'].split()[-1]}%", m_id), fallback_func=mock_data.get_mock_interns)
            
            # Mentor KPI Stat Cards Component Pattern
            km1, km2, km3, km4 = st.columns(4)
            active_cnt = len(df_my_interns[df_my_interns['status'] == 'ACTIVE']) if not df_my_interns.empty and 'status' in df_my_interns.columns else 0
            tasks_cnt = int(df_my_interns['total_tasks'].sum()) if not df_my_interns.empty and 'total_tasks' in df_my_interns.columns else 0
            appr_cnt = int(df_my_interns['approved_tasks'].sum()) if not df_my_interns.empty and 'approved_tasks' in df_my_interns.columns else 0
            
            with km1:
                render_kpi_card("Active Interns", str(active_cnt), "Supervised Students", icon="🎓", scheme="indigo")
            with km2:
                render_kpi_card("Total Tasks", str(tasks_cnt), "Project Milestones", icon="📋", scheme="sky")
            with km3:
                render_kpi_card("Approved Submissions", str(appr_cnt), "Graded Deliverables", icon="✅", scheme="emerald")
            with km4:
                render_kpi_card("Supervision Capacity", f"{active_cnt}/3", "Slots Utilized", icon="🟢", scheme="amber")

            st.markdown("---")
            st.dataframe(df_my_interns, use_container_width=True)

        with tab_m2:
            st.markdown("#### Assign New Deliverable / Project Milestone")
            with st.form("mentor_assign_task_form"):
                # Get this mentor's interns
                df_assigned = run_db_query("SELECT intern_id, first_name || ' ' || last_name AS name FROM interns WHERE mentor_id = ?", (m_id,))
                intern_map = {f"#{row['intern_id']} - {row['name']}": row['intern_id'] for _, row in df_assigned.iterrows()} if not df_assigned.empty else {"#1 - Aarav Shah": 1}

                t_intern = st.selectbox("Target Intern", list(intern_map.keys()))
                t_title = st.text_input("Milestone Title", "Design BCNF Normalization Schema")
                t_desc = st.text_area("Requirements & Scope", "Analyze the functional dependencies and produce the relational mapping.")
                t_dead = st.date_input("Deadline", datetime.date(2026, 11, 20))

                if st.form_submit_button("Assign Deliverable 📝"):
                    try:
                        q = "INSERT INTO tasks (intern_id, assigned_by, title, description, deadline, status) VALUES (?, ?, ?, ?, ?, 'TODO')"
                        st.session_state.db_manager.execute_dml(q, (intern_map[t_intern], m_id, t_title, t_desc, str(t_dead)))
                        st.success(f"Task '{t_title}' successfully assigned!")
                    except Exception as ex:
                        st.error(f"Error: {ex}")

        with tab_m3:
            st.markdown("#### Review & Score Submitted Deliverables")
            st.caption("Database Trigger `trg_validate_task_approval` validates that approved tasks must be scored between 0 and 100.")
            
            df_pending = run_db_query("""
                SELECT t.task_id, i.first_name || ' ' || i.last_name AS intern_name, t.title, t.status, t.submission_url, t.score
                FROM tasks t
                JOIN interns i ON t.intern_id = i.intern_id
                WHERE t.assigned_by = ?
            """, (m_id,), fallback_func=mock_data.get_mock_tasks)
            
            st.dataframe(df_pending, use_container_width=True)

            with st.form("grade_task_form"):
                t_id_input = st.number_input("Task ID to Grade", min_value=1, value=int(df_pending['task_id'].iloc[0]) if not df_pending.empty else 1)
                new_status = st.selectbox("Update Status", ["APPROVED", "REJECTED", "IN_PROGRESS"])
                new_score = st.slider("Score (0.0 to 100.0)", 0.0, 100.0, 92.5, 0.5)

                if st.form_submit_button("Update Task Evaluation"):
                    try:
                        score_val = new_score if new_status == "APPROVED" else None
                        q = "UPDATE tasks SET status = ?, score = ? WHERE task_id = ?"
                        st.session_state.db_manager.execute_dml(q, (new_status, score_val, t_id_input))
                        st.success(f"Task #{t_id_input} updated to {new_status} with score {score_val}!")
                    except Exception as ex:
                        st.error(f"Validation Error: {ex}")

        with tab_m4:
            st.markdown("#### Submit Weekly Performance Review")
            st.caption("Enforces `UNIQUE(intern_id, week_number)` constraint.")

            with st.form("mentor_weekly_review_form"):
                df_assigned = run_db_query("SELECT intern_id, first_name || ' ' || last_name AS name FROM interns WHERE mentor_id = ?", (m_id,))
                intern_map = {f"#{row['intern_id']} - {row['name']}": row['intern_id'] for _, row in df_assigned.iterrows()} if not df_assigned.empty else {"#1 - Aarav Shah": 1}

                rev_intern = st.selectbox("Intern", list(intern_map.keys()))
                rev_week = st.slider("Academic Week Number", 1, 16, 5)
                cr1, cr2 = st.columns(2)
                with cr1:
                    r_tech = st.slider("Technical Skill Rating (1.0 - 5.0)", 1.0, 5.0, 4.6, 0.1)
                with cr2:
                    r_soft = st.slider("Soft Skills & Punctuality (1.0 - 5.0)", 1.0, 5.0, 4.4, 0.1)
                r_notes = st.text_area("Remarks / Feedback", "Demonstrated high technical competence in indexing and transaction isolation.")

                if st.form_submit_button("Submit Evaluation ⭐"):
                    try:
                        q = """
                            INSERT INTO performance_reviews (intern_id, mentor_id, review_date, week_number, technical_rating, softskills_rating, feedback)
                            VALUES (?, ?, DATE('now'), ?, ?, ?, ?)
                        """
                        st.session_state.db_manager.execute_dml(q, (intern_map[rev_intern], m_id, rev_week, r_tech, r_soft, r_notes))
                        st.success(f"Evaluation for Week {rev_week} recorded successfully!")
                    except Exception as ex:
                        st.error(f"Database Constraint Error (e.g., Duplicate week review): {ex}")

        with tab_m5:
            st.markdown("#### 🛠️ Supervisor Attendance Hours Adjustment")
            st.caption("Policy Rule: Interns cannot edit working hours. Supervisors can adjust records using `sp_adjust_attendance_hours`, which logs an immutable audit event.")

            df_mentor_att = run_db_query("""
                SELECT a.att_id, a.intern_id, i.first_name || ' ' || i.last_name AS intern_name, a.att_date, a.status, a.hours_logged, a.remarks
                FROM attendance a
                JOIN interns i ON a.intern_id = i.intern_id
                WHERE i.mentor_id = ?
                ORDER BY a.att_date DESC
            """, (m_id,))

            if not df_mentor_att.empty:
                st.dataframe(df_mentor_att, use_container_width=True)

                with st.form("mentor_adjust_hours_form"):
                    att_rec_map = {f"Record #{r['att_id']}: {r['intern_name']} on {r['att_date']} (Current: {r['hours_logged']} hrs)": r['att_id'] for _, r in df_mentor_att.iterrows()}
                    selected_rec_key = st.selectbox("Select Attendance Record to Adjust:", list(att_rec_map.keys()))
                    selected_att_id = att_rec_map[selected_rec_key]

                    c_adj1, c_adj2 = st.columns(2)
                    with c_adj1:
                        new_hrs = st.number_input("Corrected Hours Logged (0.0 - 24.0)", min_value=0.0, max_value=24.0, value=8.0, step=0.5, key="m_hrs_in")
                    with c_adj2:
                        adjust_reason = st.text_input("Mandatory Adjustment Reason", placeholder="e.g. Lab overtime verified / System correction", key="m_reason_in")

                    if st.form_submit_button("Submit Hours Adjustment ⚙️", use_container_width=True):
                        if not adjust_reason.strip():
                            st.error("Please provide a valid reason for adjusting logged attendance.")
                        else:
                            ok, msg = st.session_state.db_manager.adjust_attendance_hours(
                                selected_att_id, new_hrs, adjust_reason, profile['name']
                            )
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
            else:
                st.info("No attendance records logged yet for your supervised interns.")

    # -------------------------------------------------------------------------
    # VIEW TYPE 3: STUDENT INTERN PORTAL
    # -------------------------------------------------------------------------
    elif role == "intern":
        i_id = profile["id"]
        st.info(f"🎓 Welcome, **{profile['name']}**. Here is your personalized internship tracking dashboard.")

        tab_i1, tab_i2, tab_i3, tab_i4 = st.tabs([
            "👤 My Profile & Summary", 
            "📅 Log Daily Attendance", 
            "📁 My Assigned Tasks & Submissions", 
            "💵 My Monthly Stipend Slips"
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
                with c1:
                    render_kpi_card("Enrollment Status", status_val, "Enrolled" if status_val == "ACTIVE" else "Pending Review", icon="📌", scheme="emerald" if status_val == "ACTIVE" else "amber")
                with c2:
                    render_kpi_card("Faculty Mentor", pref_mentor, "Assigned Supervisor" if status_val == "ACTIVE" else "Preference", icon="👨‍🏫", scheme="sky")
                with c3:
                    render_kpi_card("Monthly Base Stipend", f"₹ {float(me.get('base_stipend', 0)):,.0f}", "Base Compensation", icon="💵", scheme="indigo")
                with c4:
                    render_kpi_card("Performance Score", f"{float(me.get('composite_performance_score', 90.0)):.1f}%", "Weighted Formula", icon="🏆", scheme="purple")
                
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
                                    slot_badge = f"<span style='color: #15803D; font-weight: 600;'>🟢 {rm['slots_available']} of {rm['max_capacity']} Slots Available</span>"
                                else:
                                    slot_badge = "<span style='color: #B91C1C; font-weight: 600;'>🔴 Quota Full (0 Slots Open)</span>"

                                is_current_pick = f"<span style='background: #FEF3C7; color: #92400E; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;'>YOUR CURRENT PICK</span>" if pref_mentor == rm['mentor_name'] else ""

                                st.markdown(f"""
                                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <div style="font-weight: 700; color: #0F172A; font-size: 0.95rem;">👨‍🏫 {rm['mentor_name']}</div>
                                        {is_current_pick}
                                    </div>
                                    <div style="font-size: 0.82rem; color: #475569; margin-top: 2px;"><b>Designation:</b> {rm['designation']}</div>
                                    <div style="font-size: 0.82rem; color: #475569;"><b>Department:</b> {rm['dept_name']}</div>
                                    <div style="font-size: 0.82rem; margin-top: 6px;">{slot_badge}</div>
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

                            submit_pref = st.form_submit_button("Submit Mentor Preference 🎯", use_container_width=True)
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
            st.markdown("#### 📅 Daily Working Time & Attendance")
            st.caption("Institutional Rule: Working hours can only be logged for today and are strictly immutable once recorded.")

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

                    st.warning("⚠️ **Policy Notice**: Students cannot modify their working hours or attendance date once recorded. If an error occurred or an adjustment is required, please contact your faculty mentor or HR administrator.")
                else:
                    st.markdown(f"##### Log Attendance for Today: **{today_date.strftime('%A, %B %d, %Y')}**")
                    with st.form("intern_att_form"):
                        st.text_input("Calendar Date (Locked to Today)", value=today_str, disabled=True)
                        att_st = st.selectbox("Attendance Status", ["PRESENT", "WORK_FROM_HOME", "ON_LEAVE", "ABSENT"])
                        att_hrs = st.slider("Hours Worked Today (0.0 - 12.0)", 0.0, 12.0, 8.0, 0.5)
                        att_rmk = st.text_input("Daily Work Summary / Activity Log", "Worked on database assignment modules")

                        if st.form_submit_button("Record Today's Attendance 📅", use_container_width=True):
                            try:
                                q = "INSERT INTO attendance (intern_id, att_date, status, hours_logged, remarks) VALUES (?, ?, ?, ?, ?)"
                                st.session_state.db_manager.execute_dml(q, (i_id, today_str, att_st, att_hrs, att_rmk))
                                st.success(f"Attendance recorded for {today_str} as {att_st} ({att_hrs} hrs)! Record is now locked.")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Database Validation Error: {ex}")

            st.markdown("---")
            st.markdown("##### 📜 My Verified Attendance History (Read-Only)")
            st.caption("All attendance records are securely stored and verified against the unique composite key `(intern_id, att_date)`.")
            df_my_att = run_db_query(
                "SELECT att_id, att_date, status, hours_logged, remarks FROM attendance WHERE intern_id = ? ORDER BY att_date DESC",
                (i_id,)
            )
            st.dataframe(df_my_att, use_container_width=True)

        with tab_i3:
            st.markdown("#### My Deliverables & Work Submissions")
            df_my_tasks = run_db_query("SELECT task_id, title, deadline, status, score, submission_url FROM tasks WHERE intern_id = ?", (i_id,), fallback_func=mock_data.get_mock_tasks)
            st.dataframe(df_my_tasks, use_container_width=True)

            with st.form("submit_work_form"):
                st.markdown("##### Submit Completed Work Link")
                t_sub_id = st.number_input("Task ID", min_value=1, value=int(df_my_tasks['task_id'].iloc[0]) if not df_my_tasks.empty else 1)
                sub_url = st.text_input("Deliverable URL (GitHub / Google Drive / Report Link)", "https://github.com/sandpaper/internhub/task-submission")

                if st.form_submit_button("Submit Work 🚀"):
                    try:
                        q = "UPDATE tasks SET status = 'SUBMITTED', submission_url = ? WHERE task_id = ? AND intern_id = ?"
                        st.session_state.db_manager.execute_dml(q, (sub_url, t_sub_id, i_id))
                        st.success(f"Task #{t_sub_id} submitted for mentor review!")
                    except Exception as ex:
                        st.error(f"Submission Error: {ex}")

        with tab_i4:
            st.markdown("#### Monthly Stipend Disbursement Statements")
            df_my_stip = run_db_query("SELECT pay_month, pay_year, days_present, total_working_days, calculated_stipend, bonus, net_amount, payment_status, processed_date FROM stipend_payments WHERE intern_id = ? ORDER BY payment_id DESC", (i_id,), fallback_func=mock_data.get_mock_stipends)
            st.dataframe(df_my_stip, use_container_width=True)

    # -------------------------------------------------------------------------
    # VIEW TYPE 4: EVALUATOR / PROFESSOR PORTAL (Full inspection mode)
    # -------------------------------------------------------------------------
    elif role == "evaluator":
        st.info("🔍 **Academic Evaluation Mode Active**. You have complete administrative oversight across all database tables, procedural code, triggers, and query consoles.")

        tab_e1, tab_e2, tab_e3, tab_e4 = st.tabs([
            "🏢 All Institutional Portals", 
            "⚡ SQL Workbench Console", 
            "📐 Relational ER Diagram", 
            "🎓 Viva & Rubric Checklist"
        ])

        with tab_e1:
            st.markdown("#### Switch into any user perspective directly:")
            c_p1, c_p2, c_p3 = st.columns(3)
            with c_p1:
                if st.button("Preview as HR Admin", use_container_width=True):
                    login_as("admin", {"name": "HR Directorate", "detail": "Incubation Cell", "id": 1})
            with c_p2:
                if st.button("Preview as Mentor (Dr. Rajesh Sharma)", use_container_width=True):
                    login_as("mentor", {"name": "Dr. Rajesh Sharma", "detail": "Associate Professor (CSE)", "id": 1})
            with c_p3:
                if st.button("Preview as Intern (Aarav Shah)", use_container_width=True):
                    login_as("intern", {"name": "Aarav Shah", "detail": "Student • SVNIT Surat", "id": 1})

            st.markdown("---")
            st.markdown("##### Complete Relational Database Tables Overview:")
            table_list = ["departments", "mentors", "interns", "tasks", "attendance", "performance_reviews", "stipend_payments", "audit_logs", "users"]
            sel_t = st.selectbox("Inspect Table:", table_list)
            df_t = run_db_query(f"SELECT * FROM {sel_t};")
            st.dataframe(df_t, use_container_width=True)

        with tab_e2:
            st.markdown("#### Interactive SQL Query Runner")
            presets = {
                "Master Intern Summary (View)": "SELECT * FROM vw_intern_master_summary;",
                "Mentor Workload & Capacity Utilization (View)": "SELECT * FROM vw_mentor_workload;",
                "Recent Audit Trail Events": "SELECT * FROM audit_logs ORDER BY log_id DESC LIMIT 10;",
                "Tasks with Evaluated Scores": "SELECT * FROM tasks WHERE status = 'APPROVED';"
            }
            sel_preset = st.selectbox("Preset Academic Queries:", list(presets.keys()))
            custom_q = st.text_area("SQL Statement (SELECT only):", value=presets[sel_preset], height=100)
            if st.button("Execute Query ⚡"):
                res = run_db_query(custom_q)
                st.dataframe(res, use_container_width=True)

        with tab_e3:
            st.markdown("#### Relational Entity-Relationship (ER) Model")
            st.markdown("""
            ```mermaid
            erDiagram
                DEPARTMENT ||--|{ MENTOR : "employs (1:N)"
                DEPARTMENT ||--o{ INTERN : "hosts (1:N)"
                MENTOR ||--o{ INTERN : "supervises (1:N)"
                MENTOR ||--o{ TASK : "assigns (1:N)"
                INTERN ||--o{ TASK : "receives (1:N)"
                INTERN ||--o{ ATTENDANCE : "logs (1:N)"
                MENTOR ||--o{ PERFORMANCE_REVIEW : "evaluates (1:N)"
                INTERN ||--o{ PERFORMANCE_REVIEW : "assessed_in (1:N)"
                INTERN ||--o{ STIPEND_PAYMENT : "receives (1:N)"
                INTERN ||--o{ AUDIT_LOG : "monitored_by (1:N)"
            ```
            """)

        with tab_e4:
            st.markdown("#### CS203 Rubric Verification Matrix")
            rubric_df = pd.DataFrame([
                {"Phase": "Phase A", "Topic": "Requirements Analysis", "Status": "Complete (Admin, Mentor, Intern specs in PROJECT_REPORT.md)"},
                {"Phase": "Phase B", "Topic": "Conceptual Design (ER)", "Status": "Complete (Mermaid + Crow's foot + Cardinalities)"},
                {"Phase": "Phase C", "Topic": "Logical Design & Normalization", "Status": "Complete (Proven up to BCNF with Functional Dependencies)"},
                {"Phase": "Phase D", "Topic": "Physical Design & Procedural Programs", "Status": "Complete (DDL, Triggers, Cursors in Stored Procedures)"},
                {"Phase": "Phase E", "Topic": "Web Application Implementation", "Status": "Complete (Role-Based Multi-View Streamlit App)"},
                {"Phase": "Phase F", "Topic": "Demonstration & Viva Preparation", "Status": "Complete (25+ Q&A Defense Guide in VIVA_QUESTIONS.md)"}
            ])
            st.dataframe(rubric_df, use_container_width=True)
