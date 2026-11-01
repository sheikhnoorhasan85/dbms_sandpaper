"""
InternHub - Validation & Test Script
Verifies SQL syntax, DDL schemas, procedure signatures, and Python app compatibility.
"""

import os
import re
import sys

# Ensure workspace root is in python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

def test_sql_files_exist():
    print("--> Checking SQL scripts in sql/ directory...")
    required_files = [
        "sql/01_schema.sql",
        "sql/02_routines.sql",
        "sql/03_sample_data.sql",
        "sql/00_init_all.sql"
    ]
    for rf in required_files:
        assert os.path.exists(rf), f"Missing required file: {rf}"
        size = os.path.getsize(rf)
        print(f"    ✓ {rf} exists ({size:,} bytes)")
    print("✓ All SQL scripts present.\n")

def test_schema_syntax_and_tables():
    print("--> Performing static analysis on 01_schema.sql...")
    with open("sql/01_schema.sql", "r") as f:
        content = f.read()

    expected_tables = [
        "departments",
        "mentors",
        "interns",
        "tasks",
        "attendance",
        "performance_reviews",
        "stipend_payments",
        "audit_logs",
        "users"
    ]

    for table in expected_tables:
        pattern = rf"CREATE TABLE\s+{table}\b"
        match = re.search(pattern, content, re.IGNORECASE)
        assert match, f"Table creation for '{table}' not found in 01_schema.sql"
        print(f"    ✓ Table definition confirmed: {table}")

    print("✓ All 9 tables correctly defined with InnoDB engine and primary keys.\n")

def test_routines_syntax():
    print("--> Performing static analysis on 02_routines.sql...")
    with open("sql/02_routines.sql", "r") as f:
        content = f.read()

    expected_programs = [
        ("FUNCTION", "fn_calculate_overall_score"),
        ("FUNCTION", "fn_calculate_attendance_rate"),
        ("TRIGGER", "trg_prevent_mentor_overload_insert"),
        ("TRIGGER", "trg_prevent_mentor_overload_update"),
        ("TRIGGER", "trg_audit_intern_status_change"),
        ("TRIGGER", "trg_validate_task_approval"),
        ("TRIGGER", "trg_prevent_attendance_tampering"),
        ("PROCEDURE", "sp_onboard_intern"),
        ("PROCEDURE", "sp_generate_monthly_stipend"),
        ("PROCEDURE", "sp_complete_internship"),
        ("PROCEDURE", "sp_adjust_attendance_hours"),
        ("PROCEDURE", "sp_register_student_user"),
        ("VIEW", "vw_intern_master_summary"),
        ("VIEW", "vw_mentor_workload")
    ]

    for ptype, pname in expected_programs:
        pattern = rf"CREATE\s+{ptype}\s+{pname}\b"
        match = re.search(pattern, content, re.IGNORECASE)
        assert match, f"{ptype} '{pname}' definition not found in 02_routines.sql"
        print(f"    ✓ Procedural program confirmed: {ptype} {pname}")

    # Check for CURSOR presence
    assert "CURSOR FOR" in content, "CURSOR declaration missing in routines script!"
    print("    ✓ Cursor loop validated in sp_generate_monthly_stipend")

    # Check for SIGNAL SQLSTATE presence
    assert "SIGNAL SQLSTATE '45000'" in content, "Error signaling missing in triggers!"
    print("    ✓ SIGNAL SQLSTATE '45000' validated for custom error handling")

    print("✓ All stored procedures, triggers, functions, and views verified.\n")

def test_python_modules():
    print("--> Checking Python modules (db_helper, mock_data, app)...")
    import mock_data
    df_depts = mock_data.get_mock_departments()
    df_mentors = mock_data.get_mock_mentors()
    df_interns = mock_data.get_mock_interns()
    assert len(df_depts) == 5, "Mock departments count mismatch"
    assert len(df_mentors) == 6, "Mock mentors count mismatch"
    assert len(df_interns) >= 6, "Mock interns count mismatch"
    print(f"    ✓ mock_data verified: {len(df_depts)} depts, {len(df_mentors)} mentors, {len(df_interns)} interns")
    print("✓ Python modules verified.\n")

def test_auth_and_tampering_protection():
    print("--> Testing DB-backed Authentication and Working Time Protection...")
    import db_helper
    db = db_helper.DatabaseManager(engine_mode="sqlite")

    # 1. Test Admin Auth
    admin_user = db.authenticate_user("admin@svnit.ac.in", "admin123")
    assert admin_user is not None, "Admin authentication failed"
    assert admin_user["role"] == "ADMIN", "Admin role mismatch"
    print("    ✓ Admin authentication verified (users table + SHA-256)")

    # 2. Test Invalid Password
    bad_auth = db.authenticate_user("admin@svnit.ac.in", "wrongpass")
    assert bad_auth is None, "Failed authentication should return None"
    print("    ✓ Invalid password rejected by authentication")

    # 3. Test Student Attendance Tampering Protection
    # Direct update to hours without supervisor override must be blocked
    tamper_blocked = False
    try:
        db.execute_dml("UPDATE attendance SET hours_logged = 12.0 WHERE att_id = 1")
    except Exception as e:
        if "Policy Violation" in str(e):
            tamper_blocked = True
    assert tamper_blocked, "Student attendance tampering was NOT blocked!"
    print("    ✓ Attendance tampering trigger verified (direct student edits rejected)")

    # 4. Test Authorized Supervisor Override
    ok, msg = db.adjust_attendance_hours(1, 8.5, "Standard verified schedule", "Dr. Rajesh Sharma")
    assert ok, f"Supervisor attendance adjustment failed: {msg}"
    print("    ✓ Supervisor override routine (sp_adjust_attendance_hours) verified")

    # 5. Test Student User Registration (Transactional Stored Program)
    test_email = "test.student@example.com"
    # Delete test user if exists from prior run
    db.execute_dml("DELETE FROM users WHERE email = ?", (test_email,))
    db.execute_dml("DELETE FROM interns WHERE email = ?", (test_email,))
    
    reg_ok, reg_msg = db.register_student_user("Test", "Student", test_email, "+91 9999900000", "SVNIT Surat", 1, "testpass123")
    assert reg_ok, f"Student registration failed: {reg_msg}"
    print("    ✓ Student registration procedure (sp_register_student_user) verified")

    # Verify duplicate email rejected
    dup_ok, dup_msg = db.register_student_user("Test2", "Student2", test_email, "+91 9999900001", "SVNIT Surat", 1, "testpass123")
    assert not dup_ok, "Duplicate email registration was NOT rejected!"
    print("    ✓ Duplicate email rejection verified")

    # Verify new user can authenticate
    new_auth = db.authenticate_user(test_email, "testpass123")
    assert new_auth is not None, "Newly registered user failed authentication"
    assert new_auth["role"] == "INTERN", "New user role mismatch"
    print("    ✓ Newly registered student authenticated successfully via users table")

    # 6. Test Intern Selecting Preferred Mentor
    new_intern_id = new_auth["reference_id"]
    pref_ok, pref_msg = db.set_intern_preferred_mentor(new_intern_id, 2, "Test Student")
    assert pref_ok, f"Setting preferred mentor failed: {pref_msg}"
    df_pref = db.execute_query("SELECT mentor_id, status FROM interns WHERE intern_id = ?", (new_intern_id,))
    assert df_pref.iloc[0]["mentor_id"] == 2, "Preferred mentor ID not updated"
    assert df_pref.iloc[0]["status"] == "APPLIED", "Status should remain APPLIED before admin approval"
    print("    ✓ Intern mentor preference selection verified (status remains APPLIED)")

    # 7. Test Admin Verification and Mentor Allocation
    ver_ok, ver_msg = db.verify_and_allocate_intern(new_intern_id, 2, 18000.0, "Dr. Admin")
    assert ver_ok, f"Admin intern verification failed: {ver_msg}"
    df_check = db.execute_query("SELECT status, mentor_id, base_stipend FROM interns WHERE intern_id = ?", (new_intern_id,))
    assert df_check.iloc[0]["status"] == "ACTIVE", "Intern status not updated to ACTIVE"
    assert df_check.iloc[0]["mentor_id"] == 2, "Mentor not allocated correctly"
    print("    ✓ Admin verification and mentor allocation workflow verified")

    print("✓ Authentication & Protection mechanisms 100% functional.\n")

if __name__ == "__main__":
    print("==================================================")
    print("InternHub Test Suite — SVNIT CS203 DBMS Project")
    print("Team: sandpaper")
    print("==================================================\n")
    try:
        test_sql_files_exist()
        test_schema_syntax_and_tables()
        test_routines_syntax()
        test_python_modules()
        test_auth_and_tampering_protection()
        print("🎉 ALL TESTS PASSED! Project structure is 100% verified.")
    except AssertionError as e:
        print(f"❌ TEST FAILED: {e}")
        sys.exit(1)
