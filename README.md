# InternHub: Comprehensive Internship & Mentor Management System

[![DBMS](https://img.shields.io/badge/Course-CS203%20DBMS%20SVNIT-blue)](https://www.svnit.ac.in)
[![Team](https://img.shields.io/badge/Team-sandpaper-brightgreen)](#)
[![Database](https://img.shields.io/badge/Database-MySQL%20Workbench-orange)](#)
[![Web%20Interface](https://img.shields.io/badge/Interface-Python%20Streamlit-red)](#)

A production-grade, relational Database Management System and full-stack web application developed for **B.Tech. II (CSE) Semester-III CS203 Database Management Systems** at **Sardar Vallabhbhai National Institute of Technology (SVNIT), Surat**.

---

## 👥 Team & Project Metadata
- **Project Title:** InternHub
- **Team Name:** `sandpaper`
- **Institute:** Sardar Vallabhbhai National Institute of Technology (SVNIT), Surat
- **Department:** Computer Science & Engineering
- **Academic Year:** 2026-27

---

## 📁 Repository Structure
```
.
├── sql/
│   ├── 00_init_all.sql         # Unified master script (Execute in MySQL Workbench)
│   ├── 01_schema.sql           # Table DDL, Constraints (PK, FK, CHECK, UNIQUE), Indexes
│   ├── 02_routines.sql         # Triggers, Stored Procedures with Cursors, Functions, Views
│   └── 03_sample_data.sql      # Realistic seed data for immediate demonstration
├── docs/
│   ├── PROJECT_REPORT.md       # Complete formal report covering Phases A through F
│   └── VIVA_QUESTIONS.md       # 25+ Viva defense & practical exam preparation Q&As
├── scripts/
│   └── test_db_logic.py        # Automated test suite verifying schemas and routines
├── app.py                      # Main Streamlit web application interface
├── db_helper.py                # Database connector & stored procedure coordinator
├── mock_data.py                # Responsive demo-mode fallback datasets
├── requirements.txt            # Python dependencies
├── .env.example                # MySQL connection configuration template
└── README.md                   # This documentation guide
```

---

## 🚀 Quickstart Guide

### Step 1: Database Setup in MySQL Workbench
1. Launch **MySQL Workbench** and connect to your local MySQL server.
2. In the top menu, go to **File $\rightarrow$ Open SQL Script...** and select:
   ```
   sql/00_init_all.sql
   ```
   *(Alternatively, run `01_schema.sql`, `02_routines.sql`, and `03_sample_data.sql` in sequence)*.
3. Click the ⚡ **Execute (Lightning Bolt)** icon.
4. Refresh your schemas list; you will see `internhub_db` fully created with tables, triggers, procedures, functions, views, and sample records!

---

### Step 2: Install Python Dependencies
Open your terminal in this project folder and run:
```bash
pip install -r requirements.txt
```

---

### Step 3: Run the Web Dashboard
Start the interactive web interface:
```bash
streamlit run app.py
```
Your default browser will automatically open to `http://localhost:8501`.

#### 🔐 Default Test Accounts (Database Authenticated via `users` table):
| Role | Email | Password | Account Purpose |
| :--- | :--- | :--- | :--- |
| **👑 HR / Admin** | `admin@svnit.ac.in` | `admin123` | Institutional management, onboarding SP, batch cursor stipend |
| **👨‍🏫 Faculty Mentor** | `rajesh.sharma@svnit.ac.in` | `password123` | Supervises interns, assigns tasks, supervisor attendance adjustments |
| **🎓 Student Intern** | `aarav.shah@example.com` | `password123` | Logs today's attendance, submits work links, views stipend slips |
| **🔍 Lab Evaluator** | `evaluator@svnit.ac.in` | `admin123` | Full inspection across all tables, ERD, and SQL query console |

*Tip: The sign-in page includes one-click credential quick-fill chips for swift evaluation during viva!*

---

### Step 4: Run Automated Verification Tests
Run the project test suite to verify table schemas, constraints, cursors, triggers, and tamper protections:
```bash
python3 scripts/test_db_logic.py
```

---

## 🌟 Key Database Features (Mapped to SVNIT Rubric)

### 1. Conceptual & Logical Normalization (Phases B & C)
- Fully normalized up to **BCNF** (Boyce-Codd Normal Form) to eliminate update, insertion, and deletion anomalies.
- Formal functional dependency proofs and relational decompositions documented in [PROJECT_REPORT.md](docs/PROJECT_REPORT.md).

### 2. Procedural Logic & Cursors (Phase D)
- **Cursors in Stored Procedures:** `sp_generate_monthly_stipend` employs a cursor to iterate through all active interns, aggregating verified days from `attendance`, computing pro-rated stipends, querying `fn_calculate_overall_score`, and awarding performance bonuses.
- **Triggers with Error Signals:**
  - `trg_prevent_mentor_overload`: Enforces that mentors never exceed their `max_interns` capacity using `SIGNAL SQLSTATE '45000'`.
  - `trg_prevent_attendance_tampering`: **Blocks students from altering their daily working hours or dates once recorded.**
  - `trg_audit_intern_status_change`: Automates change logs into `audit_logs`.
  - `trg_validate_task_approval`: Enforces score assignment upon task approval.
- **Stored Procedures:**
  - `sp_onboard_intern`: Atomically verifies constraints and creates active intern records.
  - `sp_generate_monthly_stipend`: Batch cursor payroll engine.
  - `sp_adjust_attendance_hours`: Authorized supervisor override routine logging adjustments into `audit_logs`.
- **Stored Functions:**
  - `fn_calculate_overall_score`: Standardizes weighted composite scoring ($60\%$ tasks + $40\%$ mentor ratings).
  - `fn_calculate_attendance_rate`: Dynamic monthly attendance percentage computation.
- **Analytic Views:**
  - `vw_intern_master_summary`: Consolidated 360-degree intern dashboard view.
  - `vw_mentor_workload`: Real-time mentor quota and utilization tracking.

### 3. Application Interface (Phase E)
- **Executive Dashboard:** High-level KPI cards and department workload analytics.
- **Admin / HR Portal:** Atomically onboard interns via `sp_onboard_intern` and trigger batch payroll runs.
- **Mentor Portal:** Manage interns, assign deliverables, score submissions, and submit weekly reviews.
- **Intern Portal:** Self-service attendance logging, task progress tracking, and stipend slip viewer.
- **SQL Workbench Console:** Execute custom SELECT queries, test join queries, and export outputs to CSV.

---

## 🎓 Viva & Practical Exam Preparation
Consult [docs/VIVA_QUESTIONS.md](docs/VIVA_QUESTIONS.md) for 25 in-depth technical questions and answers covering:
- BCNF vs 3NF comparison on this exact schema.
- Why cursors are appropriate for payroll aggregation.
- How MySQL triggers protect domain constraints from concurrent race conditions.
- Indexing strategies on foreign keys and operational query filters.
