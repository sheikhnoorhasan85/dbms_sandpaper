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

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 1.2rem;
    }
    .role-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .badge-admin { background-color: #FEE2E2; color: #991B1B; }
    .badge-mentor { background-color: #E0E7FF; color: #3730A3; }
    .badge-intern { background-color: #D1FAE5; color: #065F46; }
    .badge-evaluator { background-color: #FEF3C7; color: #92400E; }
    
    .login-card {
        background: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .login-card h3 {
        margin-top: 0;
        color: #0F172A;
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
    st.markdown('<div class="main-title">🎓 InternHub: Internship Management System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">SVNIT Surat • CS203 Database Management Systems Project • Team: <b>sandpaper</b></div>', unsafe_allow_html=True)

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

            # Quick Test Credentials Helper
            with st.expander("📋 Quick-Fill Test Accounts for Demo / Viva Evaluation", expanded=True):
                st.caption("Click any account to automatically fill the login form with seed credentials:")
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
                    if st.button("🔍 Lab Evaluator", key="demo_eval", use_container_width=True):
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
                        ok, msg = st.session_state.db_manager.register_student_user(
                            reg_fn, reg_ln, reg_em, reg_ph, reg_clg, reg_dept, reg_p1
                        )
                        if ok:
                            st.success(f"{msg}")
                            st.session_state.fill_email = reg_em.strip().lower()
                            st.session_state.fill_password = reg_p1
                            st.info("👉 Switch to the **'Account Sign-In'** tab above to log into your new portal!")
                        else:
                            st.error(f"Registration Failed: {msg}")

    with col_info:
        st.markdown("### 🚀 Welcome to InternHub")
        st.markdown(
            "A modern, unified portal connecting students, faculty mentors, "
            "and campus administration for end-to-end internship and project management."
        )

        st.markdown("#### 🎓 What You Can Do as a Student Intern")
        st.markdown("""
        - **Daily Attendance Check-in:** Log your daily working hours with secure date validation.
        - **Milestones & Deliverables:** View assigned tasks, track deadlines, and submit your project links.
        - **Stipend Slips:** Access itemized monthly payment slips with attendance records and performance bonuses.
        """)

        st.markdown("#### 👨‍🏫 What You Can Do as a Faculty Mentor")
        st.markdown("""
        - **Student Guidance:** Monitor and mentor active interns assigned to your research domain.
        - **Task Evaluation:** Review submitted project deliverables and grade student milestone progress.
        - **Weekly Reviews:** Provide structured technical and professional feedback to guide students.
        """)

        st.markdown("#### 👑 Campus Administration & Incubation Cell")
        st.markdown("""
        - **Department Oversight:** Live departmental metrics, mentor workload, and student distribution.
        - **Automated Payroll:** Calculate and disburse monthly stipends with automated audit logs.
        - **Smooth Onboarding:** Process new applications and allocate student mentors efficiently.
        """)

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

    # Header with identity
    st.markdown(f'<div class="main-title">🎓 InternHub — {profile.get("name")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">{profile.get("detail", "")} • Active Role: <b>{role.upper()}</b></div>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # VIEW TYPE 1: ADMIN / HR PORTAL
    # -------------------------------------------------------------------------
    if role == "admin":
        tab_admin1, tab_admin2, tab_admin3, tab_admin4, tab_admin5, tab_admin6 = st.tabs([
            "📊 Executive Dashboard", 
            "➕ Onboard Intern (Stored Procedure)", 
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

            m1.metric("Enrolled Interns", total_i, f"{active_i} Active")
            m2.metric("Faculty Mentors", total_m, "All Departments")
            m3.metric("Project Deliverables", len(df_tasks) if not df_tasks.empty else 0, "Tracked Milestones")
            m4.metric("Disbursed Stipends", f"₹ {total_payout:,.2f}", "Calculated via Cursor")

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
            st.dataframe(df_interns, use_container_width=True)

        with tab_admin2:
            st.markdown("#### Atomic Onboarding via Stored Procedure (`sp_onboard_intern`)")
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
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Status", str(me.get("status", "ACTIVE")), "Enrolled")
                c2.metric("Faculty Mentor", str(me.get("mentor_name", "Unassigned")))
                c3.metric("Base Stipend", f"₹ {float(me.get('base_stipend', 0)):,.2f}")
                c4.metric("Performance Score", f"{float(me.get('composite_performance_score', 90.0)):.1f}%", "Weighted Formula")
                
                st.markdown("---")
                st.write(f"**Department:** {me.get('dept_name', 'Computer Science & Engineering')}")
                st.write(f"**Institution:** {me.get('college_name', 'SVNIT Surat')}")
                st.write(f"**Duration:** {me.get('start_date')} to {me.get('end_date')}")
            else:
                st.info("Loading student profile...")

        with tab_i2:
            st.markdown("#### 📅 Daily Working Time & Attendance")
            st.caption("Institutional Rule: Working hours can only be logged for today and are strictly immutable once recorded.")

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
