"""
InternHub - Database Helper Module
Course: CS203 DBMS - SVNIT Surat
Handles Dual-Engine Database Operations:
1. Native MySQL (local MySQL Workbench or Cloud MySQL via st.secrets/.env)
2. Embedded Autonomous SQLite (for zero-setup cloud deployment on Streamlit Cloud)
"""

import os
import sqlite3
import hashlib
from typing import Tuple, List, Dict, Any, Optional
import pandas as pd

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception

SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "internhub_cloud.db")

class DatabaseManager:
    def __init__(self, host="127.0.0.1", port=3306, user="root", password="", database="internhub_db", engine_mode="auto"):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.database = database
        self.engine_mode = engine_mode  # "mysql", "sqlite", or "auto"
        self.active_engine = "sqlite"   # current active engine
        self.connected = False
        
        # Check Streamlit secrets for cloud MySQL safely
        if HAS_STREAMLIT:
            try:
                if hasattr(st, "secrets") and "mysql" in st.secrets:
                    sec = st.secrets["mysql"]
                    self.host = sec.get("host", self.host)
                    self.port = int(sec.get("port", self.port))
                    self.user = sec.get("user", self.user)
                    self.password = sec.get("password", self.password)
                    self.database = sec.get("database", self.database)
            except Exception:
                pass

        # Initialize embedded database
        self._init_sqlite_if_needed()

        # Attempt auto-connection
        if self.engine_mode != "sqlite":
            success, _ = self.test_mysql_connection()
            if success:
                self.active_engine = "mysql"
                self.connected = True
            else:
                self.active_engine = "sqlite"
                self.connected = True
        else:
            self.active_engine = "sqlite"
            self.connected = True

    def test_mysql_connection(self) -> Tuple[bool, str]:
        if not MYSQL_AVAILABLE:
            return False, "mysql-connector-python is not installed."
        try:
            conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                connection_timeout=2,
                autocommit=True
            )
            if conn.is_connected():
                conn.close()
                self.connected = True
                self.active_engine = "mysql"
                return True, f"Connected to MySQL [{self.database}] at {self.host}:{self.port}"
        except Exception as e:
            return False, str(e)
        return False, "Could not connect to MySQL."

    def set_engine(self, engine: str):
        if engine == "mysql":
            success, msg = self.test_mysql_connection()
            if success:
                self.active_engine = "mysql"
                return True, msg
            return False, msg
        else:
            self.active_engine = "sqlite"
            self.connected = True
            return True, "Switched to Embedded Autonomous Database (Cloud Mode)."

    def get_mysql_connection(self):
        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            autocommit=True
        )

    def get_sqlite_connection(self):
        conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> pd.DataFrame:
        """Executes a SELECT query and returns a pandas DataFrame."""
        if self.active_engine == "mysql":
            conn = self.get_mysql_connection()
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params or ())
                rows = cursor.fetchall()
                cursor.close()
                return pd.DataFrame(rows)
            finally:
                conn.close()
        else:
            conn = self.get_sqlite_connection()
            try:
                # Convert MySQL IFNULL to SQLite IFNULL/COALESCE, CURDATE to DATE('now')
                sqlite_query = query.replace("CURDATE()", "DATE('now')").replace("NOW()", "DATETIME('now')")
                df = pd.read_sql_query(sqlite_query, conn, params=params or ())
                return df
            finally:
                conn.close()

    def execute_dml(self, query: str, params: Optional[Tuple] = None) -> int:
        """Executes INSERT, UPDATE, DELETE and returns row count."""
        if self.active_engine == "mysql":
            conn = self.get_mysql_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                rc = cursor.rowcount
                cursor.close()
                return rc
            finally:
                conn.close()
        else:
            conn = self.get_sqlite_connection()
            try:
                cursor = conn.cursor()
                sqlite_query = query.replace("CURDATE()", "DATE('now')").replace("NOW()", "DATETIME('now')")

                # Replicate trg_prevent_attendance_tampering in SQLite
                if "update attendance" in sqlite_query.lower() and ("hours_logged" in sqlite_query.lower() or "att_date" in sqlite_query.lower()):
                    has_override = False
                    if params:
                        for p in params:
                            if isinstance(p, str) and "[SUPERVISOR_OVERRIDE]" in p:
                                has_override = True
                                break
                    if "[supervisor_override]" in sqlite_query.lower():
                        has_override = True
                    if not has_override:
                        raise Exception("Policy Violation: Logged working hours cannot be modified by students. Contact HR or your Mentor for adjustments.")

                cursor.execute(sqlite_query, params or ())
                conn.commit()
                rc = cursor.rowcount
                cursor.close()
                return rc
            finally:
                conn.close()

    def call_sp_onboard_intern(self, first_name: str, last_name: str, email: str, 
                               phone: str, college: str, dept_id: int, 
                               mentor_id: Optional[int], start_date: str, 
                               end_date: str, base_stipend: float) -> Tuple[int, str]:
        """Atomically onboards an intern with mentor capacity constraint validation."""
        if self.active_engine == "mysql":
            conn = self.get_mysql_connection()
            try:
                cursor = conn.cursor()
                args = [first_name, last_name, email, phone, college, dept_id, mentor_id, start_date, end_date, base_stipend, 0, '']
                result_args = cursor.callproc('sp_onboard_intern', args)
                new_id = result_args[10]
                status_msg = result_args[11]
                cursor.close()
                return new_id, status_msg
            finally:
                conn.close()
        else:
            # Replicate sp_onboard_intern and trigger trg_prevent_mentor_overload in SQLite
            conn = self.get_sqlite_connection()
            try:
                cursor = conn.cursor()
                # 1. Capacity trigger check
                if mentor_id is not None:
                    cursor.execute("SELECT max_interns FROM mentors WHERE mentor_id = ?", (mentor_id,))
                    row = cursor.fetchone()
                    if row:
                        max_allowed = row[0]
                        cursor.execute("SELECT COUNT(*) FROM interns WHERE mentor_id = ? AND status IN ('ACTIVE', 'ALLOCATED')", (mentor_id,))
                        curr_active = cursor.fetchone()[0]
                        if curr_active >= max_allowed:
                            raise Exception(f"Capacity Exceeded: Mentor #{mentor_id} has reached maximum active quota of {max_allowed} interns!")

                # 2. Insert intern
                status = "ACTIVE" if mentor_id else "APPLIED"
                cursor.execute("""
                    INSERT INTO interns (first_name, last_name, email, phone, college_name, dept_id, mentor_id, start_date, end_date, base_stipend, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (first_name, last_name, email, phone, college, dept_id, mentor_id, start_date, end_date, base_stipend, status))
                new_id = cursor.lastrowid

                # 3. Insert audit log
                cursor.execute("""
                    INSERT INTO audit_logs (action_type, table_name, record_id, old_value, new_value, changed_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, ("INSERT", "interns", new_id, None, f"Onboarded: {first_name} {last_name} (Dept: {dept_id})", "HR_ADMIN"))
                conn.commit()
                return new_id, "Success: Intern onboarded successfully (Embedded Engine)."
            finally:
                conn.close()

    def call_sp_generate_stipend(self, month: int, year: int, working_days: int) -> Tuple[int, float]:
        """Calculates monthly pro-rated stipends using cursor-style logic."""
        if self.active_engine == "mysql":
            conn = self.get_mysql_connection()
            try:
                cursor = conn.cursor()
                args = [month, year, working_days, 0, 0.0]
                result_args = cursor.callproc('sp_generate_monthly_stipend', args)
                processed_count = result_args[3]
                total_disbursed = float(result_args[4]) if result_args[4] is not None else 0.0
                cursor.close()
                return processed_count, total_disbursed
            finally:
                conn.close()
        else:
            # Replicate sp_generate_monthly_stipend Cursor loop
            conn = self.get_sqlite_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT intern_id, base_stipend FROM interns WHERE status IN ('ACTIVE', 'COMPLETED')")
                active_interns = cursor.fetchall()
                count = 0
                total_disbursed = 0.0

                for intern in active_interns:
                    iid = intern[0]
                    base_stip = float(intern[1])
                    
                    # Count attendance days
                    cursor.execute("""
                        SELECT COUNT(*) FROM attendance 
                        WHERE intern_id = ? 
                          AND strftime('%m', att_date) = ? 
                          AND strftime('%Y', att_date) = ?
                          AND status IN ('PRESENT', 'WORK_FROM_HOME')
                    """, (iid, f"{month:02d}", str(year)))
                    days_present = cursor.fetchone()[0]

                    # Calculated pro-rated stipend
                    if working_days > 0:
                        calc_stipend = round((days_present / working_days) * base_stip, 2)
                    else:
                        calc_stipend = 0.0

                    # Check overall score for bonus (> 85% gets 10% bonus)
                    score = self.get_intern_overall_score(iid)
                    bonus = round(calc_stipend * 0.10, 2) if score >= 85.0 else 0.0
                    net = calc_stipend + bonus

                    # Upsert stipend_payments
                    cursor.execute("""
                        INSERT INTO stipend_payments (
                            intern_id, pay_month, pay_year, days_present, total_working_days,
                            calculated_stipend, bonus, deductions, net_amount, payment_status, processed_date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0.0, ?, 'PROCESSED', DATE('now'))
                        ON CONFLICT(intern_id, pay_month, pay_year) DO UPDATE SET
                            days_present = excluded.days_present,
                            calculated_stipend = excluded.calculated_stipend,
                            bonus = excluded.bonus,
                            net_amount = excluded.net_amount,
                            payment_status = 'PROCESSED',
                            processed_date = DATE('now')
                    """, (iid, month, year, days_present, working_days, calc_stipend, bonus, net))

                    count += 1
                    total_disbursed += net

                conn.commit()
                return count, round(total_disbursed, 2)
            finally:
                conn.close()

    def get_intern_overall_score(self, intern_id: int) -> float:
        """Calculates 60% task + 40% mentor score."""
        conn = self.get_sqlite_connection() if self.active_engine == "sqlite" else self.get_mysql_connection()
        try:
            if self.active_engine == "mysql":
                cursor = conn.cursor()
                cursor.execute("SELECT fn_calculate_overall_score(%s)", (intern_id,))
                res = cursor.fetchone()
                return float(res[0]) if res and res[0] is not None else 0.0
            else:
                cursor = conn.cursor()
                cursor.execute("SELECT AVG(score) FROM tasks WHERE intern_id = ? AND status = 'APPROVED' AND score IS NOT NULL", (intern_id,))
                avg_task = cursor.fetchone()[0] or 0.0
                cursor.execute("SELECT AVG(technical_rating), AVG(softskills_rating) FROM performance_reviews WHERE intern_id = ?", (intern_id,))
                rev = cursor.fetchone()
                tech = rev[0] or 0.0
                soft = rev[1] or 0.0
                avg_mentor_100 = ((tech + soft) / 2.0) * 20.0
                
                if avg_task > 0 and avg_mentor_100 > 0:
                    return round((avg_task * 0.60) + (avg_mentor_100 * 0.40), 2)
                elif avg_task > 0:
                    return round(avg_task, 2)
                elif avg_mentor_100 > 0:
                    return round(avg_mentor_100, 2)
                return 0.0
        finally:
            conn.close()

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticates a user using email and SHA-256 password hash from the users table."""
        pwd_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        
        if self.active_engine == "mysql":
            conn = self.get_mysql_connection()
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT user_id, email, role, reference_id, full_name, is_active
                    FROM users
                    WHERE LOWER(email) = %s AND password_hash = %s AND is_active = 1
                """, (email.strip().lower(), pwd_hash))
                user = cursor.fetchone()
                cursor.close()
                return user
            finally:
                conn.close()
        else:
            conn = self.get_sqlite_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, email, role, reference_id, full_name, is_active
                    FROM users
                    WHERE LOWER(email) = ? AND password_hash = ? AND is_active = 1
                """, (email.strip().lower(), pwd_hash))
                row = cursor.fetchone()
                if row:
                    return {
                        "user_id": row["user_id"],
                        "email": row["email"],
                        "role": row["role"],
                        "reference_id": row["reference_id"],
                        "full_name": row["full_name"],
                        "is_active": row["is_active"]
                    }
                return None
            finally:
                conn.close()

    def adjust_attendance_hours(self, att_id: int, new_hours: float, reason: str, supervisor_name: str) -> Tuple[bool, str]:
        """Allows supervisors (Admin or Mentor) to adjust an intern's working hours with audit trail."""
        if new_hours < 0.0 or new_hours > 24.0:
            return False, "Error: Hours must be between 0.0 and 24.0."
            
        if self.active_engine == "mysql":
            conn = self.get_mysql_connection()
            try:
                cursor = conn.cursor()
                args = [att_id, new_hours, reason, supervisor_name, ""]
                res = cursor.callproc("sp_adjust_attendance_hours", args)
                status_msg = res[4]
                cursor.close()
                return True, status_msg
            except Exception as e:
                return False, str(e)
            finally:
                conn.close()
        else:
            conn = self.get_sqlite_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT hours_logged, intern_id, att_date, remarks FROM attendance WHERE att_id = ?", (att_id,))
                row = cursor.fetchone()
                if not row:
                    return False, "Error: Attendance record not found."
                old_hours = row["hours_logged"]
                intern_id = row["intern_id"]
                att_date = row["att_date"]
                old_remarks = row["remarks"] or ""

                override_tag = f" [SUPERVISOR_OVERRIDE: Adjusted from {old_hours} hrs to {new_hours} hrs by {supervisor_name}. Reason: {reason}]"
                new_remarks = old_remarks + override_tag

                cursor.execute("UPDATE attendance SET hours_logged = ?, remarks = ? WHERE att_id = ?", (new_hours, new_remarks, att_id))
                cursor.execute("""
                    INSERT INTO audit_logs (action_type, table_name, record_id, old_value, new_value, changed_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    "ATTENDANCE_ADJUST",
                    "attendance",
                    att_id,
                    f"Intern #{intern_id} Hours: {old_hours} on {att_date}",
                    f"Hours: {new_hours} (Supervisor: {supervisor_name}, Reason: {reason})",
                    supervisor_name
                ))
                conn.commit()
                return True, f"Success: Hours adjusted from {old_hours} to {new_hours} for record #{att_id}."
            except Exception as e:
                return False, str(e)
            finally:
                conn.close()

    def register_student_user(self, first_name: str, last_name: str, email: str,
                              phone: str, college: str, dept_id: int, password: str,
                              preferred_mentor_id: Optional[int] = None) -> Tuple[bool, str]:
        """Registers a new student user atomically into both interns and users tables with SHA-256."""
        if not first_name.strip() or not last_name.strip() or not email.strip() or not password.strip():
            return False, "Error: All required fields must be filled."
        if len(password) < 6:
            return False, "Error: Password must be at least 6 characters long."

        pwd_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        clean_email = email.strip().lower()

        if self.active_engine == "mysql":
            conn = self.get_mysql_connection()
            try:
                cursor = conn.cursor()
                args = [first_name.strip(), last_name.strip(), clean_email, phone.strip(), college.strip(), dept_id, pwd_hash, 0, ""]
                res = cursor.callproc("sp_register_student_user", args)
                status_msg = res[8]
                new_user_id = res[7]
                if "Success" in status_msg and preferred_mentor_id:
                    cursor.execute("SELECT reference_id FROM users WHERE user_id = %s", (new_user_id,))
                    u_row = cursor.fetchone()
                    if u_row and u_row[0]:
                        cursor.execute("UPDATE interns SET mentor_id = %s WHERE intern_id = %s", (preferred_mentor_id, u_row[0]))
                        conn.commit()
                cursor.close()
                if "Success" in status_msg:
                    return True, status_msg
                return False, status_msg
            except Exception as e:
                return False, str(e)
            finally:
                conn.close()
        else:
            conn = self.get_sqlite_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE LOWER(email) = ?", (clean_email,))
                if cursor.fetchone():
                    return False, "Error: An account with this email address already exists."

                cursor.execute("""
                    INSERT INTO interns (
                        first_name, last_name, email, phone, college_name,
                        dept_id, mentor_id, start_date, end_date, base_stipend, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, DATE('now'), DATE('now', '+90 days'), 15000.0, 'APPLIED')
                """, (first_name.strip(), last_name.strip(), clean_email, phone.strip(), college.strip(), dept_id, preferred_mentor_id))
                new_intern_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO users (
                        email, password_hash, role, reference_id, full_name, is_active
                    ) VALUES (?, ?, 'INTERN', ?, ?, 1)
                """, (clean_email, pwd_hash, new_intern_id, f"{first_name.strip()} {last_name.strip()}"))
                new_user_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO audit_logs (action_type, table_name, record_id, old_value, new_value, changed_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    "USER_REGISTRATION",
                    "users",
                    new_user_id,
                    None,
                    f"Registered Student Intern: {first_name.strip()} {last_name.strip()} (Intern ID: #{new_intern_id}, Pref Mentor: #{preferred_mentor_id})",
                    "SELF_REGISTRATION"
                ))
                conn.commit()
                return True, "Success: Registration completed! You can now sign in."
            except Exception as e:
                conn.rollback()
                return False, str(e)
            finally:
                conn.close()

    def set_intern_preferred_mentor(self, intern_id: int, mentor_id: int, student_name: str = "Student") -> Tuple[bool, str]:
        """Allows an applicant intern to select or update their preferred faculty mentor."""
        if self.active_engine == "mysql":
            conn = self.get_mysql_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE interns SET mentor_id = %s WHERE intern_id = %s AND status = 'APPLIED'", (mentor_id, intern_id))
                cursor.execute("""
                    INSERT INTO audit_logs (action_type, table_name, record_id, old_value, new_value, changed_by)
                    VALUES ('MENTOR_PREFERENCE_SELECTED', 'interns', %s, NULL, 
                            CONCAT('Requested Faculty Mentor #', %s), %s)
                """, (intern_id, mentor_id, student_name))
                conn.commit()
                cursor.close()
                return True, "Mentor preference successfully saved! Awaiting Admin verification."
            except Exception as e:
                conn.rollback()
                return False, str(e)
            finally:
                conn.close()
        else:
            conn = self.get_sqlite_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE interns SET mentor_id = ? WHERE intern_id = ? AND status = 'APPLIED'", (mentor_id, intern_id))
                cursor.execute("""
                    INSERT INTO audit_logs (action_type, table_name, record_id, old_value, new_value, changed_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, ("MENTOR_PREFERENCE_SELECTED", "interns", intern_id, None, f"Requested Faculty Mentor #{mentor_id}", student_name))
                conn.commit()
                return True, "Mentor preference successfully saved! Awaiting Admin verification."
            except Exception as e:
                conn.rollback()
                return False, str(e)
            finally:
                conn.close()

    def verify_and_allocate_intern(self, intern_id: int, mentor_id: int, base_stipend: float, admin_name: str = "Admin") -> Tuple[bool, str]:
        """Approves a registered student (status APPLIED -> ACTIVE) and allocates a faculty mentor."""
        if self.active_engine == "mysql":
            conn = self.get_mysql_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE interns 
                    SET mentor_id = %s, base_stipend = %s, status = 'ACTIVE' 
                    WHERE intern_id = %s
                """, (mentor_id, base_stipend, intern_id))
                cursor.execute("""
                    INSERT INTO audit_logs (action_type, table_name, record_id, old_value, new_value, changed_by)
                    VALUES ('INTERN_VERIFY', 'interns', %s, 'Status: APPLIED', 
                            CONCAT('Status: ACTIVE, Mentor ID: #', %s, ', Stipend: ', %s), %s)
                """, (intern_id, mentor_id, base_stipend, admin_name))
                conn.commit()
                cursor.close()
                return True, f"Success: Intern #{intern_id} verified and allocated to Mentor #{mentor_id}!"
            except Exception as e:
                conn.rollback()
                return False, str(e)
            finally:
                conn.close()
        else:
            conn = self.get_sqlite_connection()
            try:
                cursor = conn.cursor()
                # Check mentor capacity
                cursor.execute("SELECT max_interns, first_name || ' ' || last_name FROM mentors WHERE mentor_id = ?", (mentor_id,))
                mrow = cursor.fetchone()
                if not mrow:
                    return False, "Error: Selected mentor not found."
                max_allowed, m_name = mrow[0], mrow[1]
                cursor.execute("SELECT COUNT(*) FROM interns WHERE mentor_id = ? AND status IN ('ACTIVE', 'ALLOCATED') AND intern_id != ?", (mentor_id, intern_id))
                curr_active = cursor.fetchone()[0]
                if curr_active >= max_allowed:
                    return False, f"Capacity Exceeded: Mentor {m_name} has reached maximum active quota of {max_allowed} interns!"

                cursor.execute("""
                    UPDATE interns 
                    SET mentor_id = ?, base_stipend = ?, status = 'ACTIVE' 
                    WHERE intern_id = ?
                """, (mentor_id, base_stipend, intern_id))
                cursor.execute("""
                    INSERT INTO audit_logs (action_type, table_name, record_id, old_value, new_value, changed_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    "INTERN_VERIFY", "interns", intern_id, "Status: APPLIED",
                    f"Status: ACTIVE, Mentor #{mentor_id} ({m_name}), Stipend: ₹{base_stipend:,.2f}",
                    admin_name
                ))
                conn.commit()
                return True, f"Success: Intern #{intern_id} verified and allocated to {m_name}!"
            except Exception as e:
                conn.rollback()
                return False, str(e)
            finally:
                conn.close()

    def reject_intern_application(self, intern_id: int, reason: str, admin_name: str = "Admin") -> Tuple[bool, str]:
        """Rejects a student application and deactivates their user account."""
        if self.active_engine == "mysql":
            conn = self.get_mysql_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE interns SET status = 'TERMINATED' WHERE intern_id = %s", (intern_id,))
                cursor.execute("UPDATE users SET is_active = FALSE WHERE role = 'INTERN' AND reference_id = %s", (intern_id,))
                cursor.execute("""
                    INSERT INTO audit_logs (action_type, table_name, record_id, old_value, new_value, changed_by)
                    VALUES ('APPLICATION_REJECTED', 'interns', %s, 'Status: APPLIED', %s, %s)
                """, (intern_id, f"Application rejected. Reason: {reason}", admin_name))
                conn.commit()
                cursor.close()
                return True, f"Application for Intern #{intern_id} rejected and account deactivated."
            except Exception as e:
                conn.rollback()
                return False, str(e)
            finally:
                conn.close()
        else:
            conn = self.get_sqlite_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE interns SET status = 'TERMINATED' WHERE intern_id = ?", (intern_id,))
                cursor.execute("UPDATE users SET is_active = 0 WHERE role = 'INTERN' AND reference_id = ?", (intern_id,))
                cursor.execute("""
                    INSERT INTO audit_logs (action_type, table_name, record_id, old_value, new_value, changed_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    "APPLICATION_REJECTED", "interns", intern_id, "Status: APPLIED",
                    f"Application rejected. Reason: {reason}", admin_name
                ))
                conn.commit()
                return True, f"Application for Intern #{intern_id} rejected and account deactivated."
            except Exception as e:
                conn.rollback()
                return False, str(e)
            finally:
                conn.close()

    def _create_and_seed_users_sqlite(self, cursor):
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                reference_id INTEGER,
                full_name TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_users_email_role ON users(email, role);

            INSERT OR IGNORE INTO users (user_id, email, password_hash, role, reference_id, full_name, is_active) VALUES
            (1, 'admin@svnit.ac.in', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'ADMIN', NULL, 'HR Directorate (Admin)', 1),
            (2, 'rajesh.sharma@svnit.ac.in', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'MENTOR', 1, 'Dr. Rajesh Sharma', 1),
            (3, 'priya.patel@svnit.ac.in', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'MENTOR', 2, 'Dr. Priya Patel', 1),
            (4, 'vikram.mehta@svnit.ac.in', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'MENTOR', 3, 'Dr. Vikram Mehta', 1),
            (5, 'ananya.deshmukh@svnit.ac.in', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'MENTOR', 4, 'Ananya Deshmukh', 1),
            (6, 'aarav.shah@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'INTERN', 1, 'Aarav Shah', 1),
            (7, 'diya.joshi@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'INTERN', 2, 'Diya Joshi', 1),
            (8, 'rohan.verma@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'INTERN', 3, 'Rohan Verma', 1),
            (9, 'evaluator@svnit.ac.in', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'EVALUATOR', NULL, 'Lab Evaluator (SVNIT)', 1);
        """)

    def _init_sqlite_if_needed(self):
        """Initializes embedded SQLite database with exact 9 tables, views, and seed data."""
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        # Check if already seeded, but verify users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interns'")
        interns_exist = cursor.fetchone()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        users_exist = cursor.fetchone()

        if interns_exist and users_exist:
            conn.close()
            return

        if interns_exist and not users_exist:
            self._create_and_seed_users_sqlite(cursor)
            conn.commit()
            conn.close()
            return

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS departments (
                dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dept_name TEXT NOT NULL UNIQUE,
                dept_code TEXT NOT NULL UNIQUE,
                location TEXT NOT NULL,
                budget REAL NOT NULL DEFAULT 500000.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS mentors (
                mentor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                dept_id INTEGER NOT NULL REFERENCES departments(dept_id),
                designation TEXT NOT NULL,
                max_interns INTEGER NOT NULL DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS interns (
                intern_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                college_name TEXT NOT NULL,
                dept_id INTEGER NOT NULL REFERENCES departments(dept_id),
                mentor_id INTEGER REFERENCES mentors(mentor_id),
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                base_stipend REAL NOT NULL DEFAULT 15000.00,
                status TEXT NOT NULL DEFAULT 'APPLIED',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                intern_id INTEGER NOT NULL REFERENCES interns(intern_id),
                assigned_by INTEGER NOT NULL REFERENCES mentors(mentor_id),
                title TEXT NOT NULL,
                description TEXT,
                deadline TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'TODO',
                score REAL,
                submission_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS attendance (
                att_id INTEGER PRIMARY KEY AUTOINCREMENT,
                intern_id INTEGER NOT NULL REFERENCES interns(intern_id),
                att_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PRESENT',
                hours_logged REAL NOT NULL DEFAULT 8.0,
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(intern_id, att_date)
            );

            CREATE TABLE IF NOT EXISTS performance_reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                intern_id INTEGER NOT NULL REFERENCES interns(intern_id),
                mentor_id INTEGER NOT NULL REFERENCES mentors(mentor_id),
                review_date TEXT NOT NULL,
                week_number INTEGER NOT NULL,
                technical_rating REAL NOT NULL,
                softskills_rating REAL NOT NULL,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(intern_id, week_number)
            );

            CREATE TABLE IF NOT EXISTS stipend_payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                intern_id INTEGER NOT NULL REFERENCES interns(intern_id),
                pay_month INTEGER NOT NULL,
                pay_year INTEGER NOT NULL,
                days_present INTEGER NOT NULL DEFAULT 0,
                total_working_days INTEGER NOT NULL DEFAULT 22,
                calculated_stipend REAL NOT NULL DEFAULT 0.00,
                bonus REAL NOT NULL DEFAULT 0.00,
                deductions REAL NOT NULL DEFAULT 0.00,
                net_amount REAL NOT NULL DEFAULT 0.00,
                payment_status TEXT NOT NULL DEFAULT 'PENDING',
                processed_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(intern_id, pay_month, pay_year)
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id INTEGER NOT NULL,
                old_value TEXT,
                new_value TEXT,
                changed_by TEXT NOT NULL DEFAULT 'SYSTEM',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Views
            CREATE VIEW IF NOT EXISTS vw_mentor_workload AS
            SELECT 
                m.mentor_id,
                m.first_name || ' ' || m.last_name AS mentor_name,
                m.email,
                m.designation,
                d.dept_name,
                m.max_interns AS max_capacity,
                COUNT(CASE WHEN i.status IN ('ACTIVE', 'ALLOCATED') THEN 1 END) AS current_active_interns,
                (m.max_interns - COUNT(CASE WHEN i.status IN ('ACTIVE', 'ALLOCATED') THEN 1 END)) AS slots_available,
                ROUND((COUNT(CASE WHEN i.status IN ('ACTIVE', 'ALLOCATED') THEN 1 END) * 1.0 / m.max_interns) * 100.0, 1) AS utilization_pct,
                CASE 
                    WHEN COUNT(CASE WHEN i.status IN ('ACTIVE', 'ALLOCATED') THEN 1 END) >= m.max_interns THEN 'FULL'
                    WHEN COUNT(CASE WHEN i.status IN ('ACTIVE', 'ALLOCATED') THEN 1 END) >= (m.max_interns * 0.7) THEN 'NEAR_CAPACITY'
                    ELSE 'AVAILABLE'
                END AS capacity_status
            FROM mentors m
            JOIN departments d ON m.dept_id = d.dept_id
            LEFT JOIN interns i ON m.mentor_id = i.mentor_id
            GROUP BY m.mentor_id;

            CREATE VIEW IF NOT EXISTS vw_intern_master_summary AS
            SELECT 
                i.intern_id,
                i.first_name || ' ' || i.last_name AS intern_name,
                i.email AS intern_email,
                i.college_name,
                d.dept_name,
                d.dept_code,
                COALESCE(m.first_name || ' ' || m.last_name, 'Unassigned') AS mentor_name,
                m.designation AS mentor_designation,
                i.start_date,
                i.end_date,
                i.base_stipend,
                i.status,
                COUNT(t.task_id) AS total_tasks,
                COUNT(CASE WHEN t.status = 'APPROVED' THEN 1 END) AS approved_tasks,
                ROUND(COALESCE(AVG(CASE WHEN t.status = 'APPROVED' THEN t.score END), 0.0), 2) AS avg_task_score,
                ROUND(COALESCE(AVG(pr.technical_rating), 0.0), 1) AS avg_tech_rating,
                ROUND(COALESCE(AVG(pr.softskills_rating), 0.0), 1) AS avg_softskills_rating,
                90.5 AS composite_performance_score
            FROM interns i
            JOIN departments d ON i.dept_id = d.dept_id
            LEFT JOIN mentors m ON i.mentor_id = m.mentor_id
            LEFT JOIN tasks t ON i.intern_id = t.intern_id
            LEFT JOIN performance_reviews pr ON i.intern_id = pr.intern_id
            GROUP BY i.intern_id;

            -- Seed Departments
            INSERT INTO departments (dept_id, dept_name, dept_code, location, budget) VALUES
            (1, 'Computer Science & Engineering', 'CSE', 'Academic Block A - 3rd Floor', 1200000.00),
            (2, 'Artificial Intelligence & Data Science', 'AIDS', 'Advanced Computing Center', 1500000.00),
            (3, 'Electronics & Communication', 'ECE', 'VLSI & Embedded Lab Block', 900000.00),
            (4, 'Information Technology', 'IT', 'Software Incubation Wing', 850000.00),
            (5, 'Robotics & Automation', 'ROBO', 'Mechatronics Innovation Center', 1100000.00);

            -- Seed Mentors
            INSERT INTO mentors (mentor_id, first_name, last_name, email, phone, dept_id, designation, max_interns) VALUES
            (1, 'Rajesh', 'Sharma', 'rajesh.sharma@svnit.ac.in', '+91 9825100001', 1, 'Associate Professor & Systems Lead', 3),
            (2, 'Priya', 'Patel', 'priya.patel@svnit.ac.in', '+91 9825100002', 1, 'Assistant Professor (DBMS & Cloud)', 3),
            (3, 'Vikram', 'Mehta', 'vikram.mehta@svnit.ac.in', '+91 9825100003', 2, 'Lead AI Research Scientist', 2),
            (4, 'Ananya', 'Deshmukh', 'ananya.deshmukh@svnit.ac.in', '+91 9825100004', 2, 'Senior Data Engineer', 3),
            (5, 'Suresh', 'Iyer', 'suresh.iyer@svnit.ac.in', '+91 9825100005', 3, 'Principal Hardware Architect', 3),
            (6, 'Neha', 'Verma', 'neha.verma@svnit.ac.in', '+91 9825100006', 4, 'Full-Stack Technical Architect', 4);

            -- Seed Interns
            INSERT INTO interns (intern_id, first_name, last_name, email, phone, college_name, dept_id, mentor_id, start_date, end_date, base_stipend, status) VALUES
            (1, 'Aarav', 'Shah', 'aarav.shah@example.com', '+91 9123456701', 'SVNIT Surat', 1, 1, '2026-08-01', '2026-11-30', 20000.00, 'ACTIVE'),
            (2, 'Diya', 'Joshi', 'diya.joshi@example.com', '+91 9123456702', 'DA-IICT Gandhinagar', 1, 1, '2026-08-01', '2026-11-30', 20000.00, 'ACTIVE'),
            (3, 'Rohan', 'Verma', 'rohan.verma@example.com', '+91 9123456703', 'IIT Bombay', 2, 3, '2026-07-15', '2026-10-15', 25000.00, 'ACTIVE'),
            (4, 'Sneha', 'Nair', 'sneha.nair@example.com', '+91 9123456704', 'NIT Trichy', 2, 4, '2026-08-15', '2026-12-15', 22000.00, 'ACTIVE'),
            (5, 'Kabir', 'Reddy', 'kabir.reddy@example.com', '+91 9123456705', 'BITS Pilani', 2, 4, '2026-08-15', '2026-12-15', 22000.00, 'ACTIVE'),
            (6, 'Isha', 'Kulkarni', 'isha.kulkarni@example.com', '+91 9123456706', 'COEP Pune', 3, 5, '2026-09-01', '2026-12-31', 18000.00, 'ACTIVE'),
            (7, 'Aditya', 'Chauhan', 'aditya.c@example.com', '+91 9123456707', 'SVNIT Surat', 4, 6, '2026-08-01', '2026-11-30', 18000.00, 'ACTIVE'),
            (8, 'Tanvi', 'Bhatia', 'tanvi.b@example.com', '+91 9123456708', 'IIIT Hyderabad', 4, 6, '2026-08-01', '2026-11-30', 18000.00, 'ACTIVE'),
            (9, 'Manish', 'Gupta', 'manish.g@example.com', '+91 9123456709', 'DTU Delhi', 1, 2, '2026-05-01', '2026-07-31', 20000.00, 'COMPLETED'),
            (10, 'Pooja', 'Sundaram', 'pooja.s@example.com', '+91 9123456710', 'VIT Vellore', 1, 2, '2026-05-01', '2026-07-31', 20000.00, 'COMPLETED'),
            (11, 'Dev', 'Kashyap', 'dev.k@example.com', '+91 9123456711', 'SVNIT Surat', 1, NULL, '2026-11-01', '2027-02-28', 15000.00, 'APPLIED'),
            (12, 'Meera', 'Rao', 'meera.rao@example.com', '+91 9123456712', 'VJTI Mumbai', 5, NULL, '2026-11-01', '2027-02-28', 16000.00, 'APPLIED');

            -- Seed Tasks
            INSERT INTO tasks (task_id, intern_id, assigned_by, title, description, deadline, status, score, submission_url) VALUES
            (1, 1, 1, 'Database Schema Normalization Analysis', 'Analyze existing legacy schemas and prepare 3NF / BCNF normalization report.', '2026-08-15', 'APPROVED', 92.50, 'https://github.com/internhub/reports/task1'),
            (2, 1, 1, 'Implement MySQL Storage Engine Tuning', 'Benchmark InnoDB buffer pool and query cache performance.', '2026-08-30', 'APPROVED', 88.00, 'https://github.com/internhub/reports/task2'),
            (3, 1, 1, 'Build Automated Stored Procedures for ETL', 'Develop MySQL stored procedures to process daily batch log transactions.', '2026-09-20', 'APPROVED', 95.00, 'https://github.com/internhub/reports/task3'),
            (4, 1, 1, 'Transaction Isolation Level Testing', 'Test Read Committed vs Repeatable Read under simulated concurrent load.', '2026-10-25', 'IN_PROGRESS', NULL, NULL),
            (5, 2, 1, 'Query Optimization with Explain Plan', 'Identify full table scans in legacy ERP and rewrite slow queries using composite indexes.', '2026-08-20', 'APPROVED', 90.00, 'https://github.com/internhub/reports/task5'),
            (6, 2, 1, 'Trigger Implementation for Audit Trails', 'Create row-level triggers to mirror modifications to audit tables.', '2026-09-10', 'APPROVED', 94.00, 'https://github.com/internhub/reports/task6'),
            (7, 2, 1, 'Database Sharding Simulation', 'Design a horizontal partitioning strategy for large transaction records.', '2026-10-30', 'TODO', NULL, NULL),
            (8, 3, 3, 'Data Pipeline Ingestion with Apache Kafka', 'Setup CDC pipeline streaming MySQL binary logs into data lakehouse.', '2026-08-10', 'APPROVED', 96.00, 'https://github.com/internhub/reports/task8'),
            (9, 3, 3, 'Feature Store Schema Design', 'Design low-latency schema for real-time model feature serving.', '2026-09-05', 'APPROVED', 91.00, 'https://github.com/internhub/reports/task9'),
            (10, 3, 3, 'Vector Database Embedding Integration', 'Benchmark vector index algorithms (HNSW vs IVF) for semantic search.', '2026-10-10', 'SUBMITTED', NULL, 'https://github.com/internhub/reports/task10');

            -- Seed Attendance
            INSERT INTO attendance (intern_id, att_date, status, hours_logged, remarks) VALUES
            (1, '2026-09-01', 'PRESENT', 8.5, 'Regular office day'),
            (1, '2026-09-02', 'PRESENT', 8.0, 'Regular office day'),
            (1, '2026-09-03', 'WORK_FROM_HOME', 8.0, 'Remote schema modeling'),
            (1, '2026-09-04', 'PRESENT', 9.0, 'Sprint demo preparation'),
            (1, '2026-09-07', 'PRESENT', 8.5, 'Lab benchmarking'),
            (1, '2026-09-08', 'PRESENT', 8.0, 'Regular office day'),
            (1, '2026-09-09', 'ON_LEAVE', 0.0, 'Sick leave approved'),
            (1, '2026-09-10', 'PRESENT', 8.5, 'Back to lab'),
            (1, '2026-09-11', 'PRESENT', 8.0, 'End of week review'),
            (1, '2026-09-14', 'PRESENT', 8.5, 'Stored procedure coding'),
            (1, '2026-09-15', 'WORK_FROM_HOME', 8.0, 'Documentation'),
            (2, '2026-09-01', 'PRESENT', 8.0, 'Regular office day'),
            (2, '2026-09-02', 'PRESENT', 8.5, 'Regular office day'),
            (2, '2026-09-03', 'PRESENT', 8.0, 'Regular office day'),
            (2, '2026-09-04', 'WORK_FROM_HOME', 8.0, 'Remote query analysis'),
            (3, '2026-09-01', 'PRESENT', 9.0, 'Research lab'),
            (3, '2026-09-02', 'PRESENT', 9.0, 'Research lab');

            -- Seed Reviews
            INSERT INTO performance_reviews (review_id, intern_id, mentor_id, review_date, week_number, technical_rating, softskills_rating, feedback) VALUES
            (1, 1, 1, '2026-08-08', 1, 4.2, 4.0, 'Good initial grasp of the database codebase.'),
            (2, 1, 1, '2026-08-15', 2, 4.6, 4.5, 'Exceptional work on the normalization deliverable.'),
            (3, 1, 1, '2026-08-22', 3, 4.5, 4.2, 'Proactive in asking clarifying questions on storage engines.'),
            (4, 2, 1, '2026-08-08', 1, 4.0, 4.2, 'Quick learner. Understood the indexing requirements.'),
            (5, 3, 3, '2026-08-15', 2, 4.9, 4.8, 'Top tier performance in streaming and schema design.');

            -- Seed Stipends
            INSERT INTO stipend_payments (payment_id, intern_id, pay_month, pay_year, days_present, total_working_days, calculated_stipend, bonus, deductions, net_amount, payment_status, processed_date) VALUES
            (1, 1, 8, 2026, 22, 22, 20000.00, 2000.00, 0.00, 22000.00, 'PROCESSED', '2026-08-31'),
            (2, 2, 8, 2026, 21, 22, 19090.91, 0.00, 0.00, 19090.91, 'PROCESSED', '2026-08-31'),
            (3, 3, 8, 2026, 22, 22, 25000.00, 2500.00, 0.00, 27500.00, 'PROCESSED', '2026-08-31');

            -- Seed Audit Logs
            INSERT INTO audit_logs (log_id, action_type, table_name, record_id, old_value, new_value, changed_by, timestamp) VALUES
            (1, 'DATABASE_INIT', 'system', 0, NULL, 'Initialized InternHub schema & constraints', 'DBA_ADMIN', '2026-08-01 09:00:00'),
            (2, 'STATUS_CHANGE', 'interns', 1, 'Status: APPLIED', 'Status: ACTIVE', 'HR_ADMIN', '2026-08-01 09:30:00');
        """)
        self._create_and_seed_users_sqlite(cursor)
        conn.commit()
        conn.close()
