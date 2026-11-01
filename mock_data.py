"""
InternHub - Mock Data Fallback
Provides preview data when MySQL is not connected or running in demo mode.
"""

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    class MockDataFrame(list):
        @property
        def empty(self):
            return len(self) == 0
        @property
        def columns(self):
            return list(self[0].keys()) if self else []
        def __getitem__(self, key):
            if isinstance(key, str):
                return [row.get(key) for row in self]
            return super().__getitem__(key)

def _create_df(data):
    if PANDAS_AVAILABLE:
        return pd.DataFrame(data)
    return MockDataFrame(data)

def get_mock_departments():
    return _create_df([
        {"dept_id": 1, "dept_name": "Computer Science & Engineering", "dept_code": "CSE", "location": "Academic Block A - 3rd Floor", "budget": 1200000.00},
        {"dept_id": 2, "dept_name": "Artificial Intelligence & Data Science", "dept_code": "AIDS", "location": "Advanced Computing Center", "budget": 1500000.00},
        {"dept_id": 3, "dept_name": "Electronics & Communication", "dept_code": "ECE", "location": "VLSI & Embedded Lab Block", "budget": 900000.00},
        {"dept_id": 4, "dept_name": "Information Technology", "dept_code": "IT", "location": "Software Incubation Wing", "budget": 850000.00},
        {"dept_id": 5, "dept_name": "Robotics & Automation", "dept_code": "ROBO", "location": "Mechatronics Innovation Center", "budget": 1100000.00}
    ])

def get_mock_mentors():
    return _create_df([
        {"mentor_id": 1, "first_name": "Rajesh", "last_name": "Sharma", "email": "rajesh.sharma@svnit.ac.in", "phone": "+91 9825100001", "dept_id": 1, "dept_name": "Computer Science & Engineering", "designation": "Associate Professor & Systems Lead", "max_interns": 3, "current_active_interns": 2, "slots_available": 1, "utilization_pct": 66.7, "capacity_status": "AVAILABLE"},
        {"mentor_id": 2, "first_name": "Priya", "last_name": "Patel", "email": "priya.patel@svnit.ac.in", "phone": "+91 9825100002", "dept_id": 1, "dept_name": "Computer Science & Engineering", "designation": "Assistant Professor (DBMS & Cloud)", "max_interns": 3, "current_active_interns": 0, "slots_available": 3, "utilization_pct": 0.0, "capacity_status": "AVAILABLE"},
        {"mentor_id": 3, "first_name": "Vikram", "last_name": "Mehta", "email": "vikram.mehta@svnit.ac.in", "phone": "+91 9825100003", "dept_id": 2, "dept_name": "Artificial Intelligence & Data Science", "designation": "Lead AI Research Scientist", "max_interns": 2, "current_active_interns": 1, "slots_available": 1, "utilization_pct": 50.0, "capacity_status": "AVAILABLE"},
        {"mentor_id": 4, "first_name": "Ananya", "last_name": "Deshmukh", "email": "ananya.deshmukh@svnit.ac.in", "phone": "+91 9825100004", "dept_id": 2, "dept_name": "Artificial Intelligence & Data Science", "designation": "Senior Data Engineer", "max_interns": 3, "current_active_interns": 2, "slots_available": 1, "utilization_pct": 66.7, "capacity_status": "AVAILABLE"},
        {"mentor_id": 5, "first_name": "Suresh", "last_name": "Iyer", "email": "suresh.iyer@svnit.ac.in", "phone": "+91 9825100005", "dept_id": 3, "dept_name": "Electronics & Communication", "designation": "Principal Hardware Architect", "max_interns": 3, "current_active_interns": 1, "slots_available": 2, "utilization_pct": 33.3, "capacity_status": "AVAILABLE"},
        {"mentor_id": 6, "first_name": "Neha", "last_name": "Verma", "email": "neha.verma@svnit.ac.in", "phone": "+91 9825100006", "dept_id": 4, "dept_name": "Information Technology", "designation": "Full-Stack Technical Architect", "max_interns": 4, "current_active_interns": 2, "slots_available": 2, "utilization_pct": 50.0, "capacity_status": "AVAILABLE"}
    ])

def get_mock_interns():
    return _create_df([
        {"intern_id": 1, "intern_name": "Aarav Shah", "intern_email": "aarav.shah@example.com", "college_name": "SVNIT Surat", "dept_name": "Computer Science & Engineering", "dept_code": "CSE", "mentor_name": "Rajesh Sharma", "mentor_designation": "Associate Professor & Systems Lead", "start_date": "2026-08-01", "end_date": "2026-11-30", "base_stipend": 20000.0, "status": "ACTIVE", "total_tasks": 4, "approved_tasks": 3, "avg_task_score": 91.83, "avg_tech_rating": 4.5, "avg_softskills_rating": 4.4, "composite_performance_score": 90.7},
        {"intern_id": 2, "intern_name": "Diya Joshi", "intern_email": "diya.joshi@example.com", "college_name": "DA-IICT Gandhinagar", "dept_name": "Computer Science & Engineering", "dept_code": "CSE", "mentor_name": "Rajesh Sharma", "mentor_designation": "Associate Professor & Systems Lead", "start_date": "2026-08-01", "end_date": "2026-11-30", "base_stipend": 20000.0, "status": "ACTIVE", "total_tasks": 3, "approved_tasks": 2, "avg_task_score": 92.00, "avg_tech_rating": 4.3, "avg_softskills_rating": 4.3, "composite_performance_score": 89.6},
        {"intern_id": 3, "intern_name": "Rohan Verma", "intern_email": "rohan.verma@example.com", "college_name": "IIT Bombay", "dept_name": "Artificial Intelligence & Data Science", "dept_code": "AIDS", "mentor_name": "Vikram Mehta", "mentor_designation": "Lead AI Research Scientist", "start_date": "2026-07-15", "end_date": "2026-10-15", "base_stipend": 25000.0, "status": "ACTIVE", "total_tasks": 3, "approved_tasks": 2, "avg_task_score": 93.50, "avg_tech_rating": 4.9, "avg_softskills_rating": 4.8, "composite_performance_score": 94.9},
        {"intern_id": 4, "intern_name": "Sneha Nair", "intern_email": "sneha.nair@example.com", "college_name": "NIT Trichy", "dept_name": "Artificial Intelligence & Data Science", "dept_code": "AIDS", "mentor_name": "Ananya Deshmukh", "mentor_designation": "Senior Data Engineer", "start_date": "2026-08-15", "end_date": "2026-12-15", "base_stipend": 22000.0, "status": "ACTIVE", "total_tasks": 3, "approved_tasks": 2, "avg_task_score": 87.00, "avg_tech_rating": 4.4, "avg_softskills_rating": 4.5, "composite_performance_score": 87.8},
        {"intern_id": 5, "intern_name": "Kabir Reddy", "intern_email": "kabir.reddy@example.com", "college_name": "BITS Pilani", "dept_name": "Artificial Intelligence & Data Science", "dept_code": "AIDS", "mentor_name": "Ananya Deshmukh", "mentor_designation": "Senior Data Engineer", "start_date": "2026-08-15", "end_date": "2026-12-15", "base_stipend": 22000.0, "status": "ACTIVE", "total_tasks": 2, "approved_tasks": 2, "avg_task_score": 90.25, "avg_tech_rating": 4.2, "avg_softskills_rating": 4.1, "composite_performance_score": 87.4},
        {"intern_id": 9, "intern_name": "Manish Gupta", "intern_email": "manish.g@example.com", "college_name": "DTU Delhi", "dept_name": "Computer Science & Engineering", "dept_code": "CSE", "mentor_name": "Priya Patel", "mentor_designation": "Assistant Professor (DBMS & Cloud)", "start_date": "2026-05-01", "end_date": "2026-07-31", "base_stipend": 20000.0, "status": "COMPLETED", "total_tasks": 2, "approved_tasks": 2, "avg_task_score": 96.50, "avg_tech_rating": 5.0, "avg_softskills_rating": 5.0, "composite_performance_score": 97.9}
    ])

def get_mock_tasks():
    return _create_df([
        {"task_id": 1, "intern_id": 1, "intern_name": "Aarav Shah", "title": "Database Schema Normalization Analysis", "deadline": "2026-08-15", "status": "APPROVED", "score": 92.50, "submission_url": "https://github.com/internhub/task1"},
        {"task_id": 2, "intern_id": 1, "intern_name": "Aarav Shah", "title": "Implement MySQL Storage Engine Tuning", "deadline": "2026-08-30", "status": "APPROVED", "score": 88.00, "submission_url": "https://github.com/internhub/task2"},
        {"task_id": 3, "intern_id": 1, "intern_name": "Aarav Shah", "title": "Build Automated Stored Procedures for ETL", "deadline": "2026-09-20", "status": "APPROVED", "score": 95.00, "submission_url": "https://github.com/internhub/task3"},
        {"task_id": 4, "intern_id": 1, "intern_name": "Aarav Shah", "title": "Transaction Isolation Level Testing", "deadline": "2026-10-25", "status": "IN_PROGRESS", "score": None, "submission_url": None},
        {"task_id": 8, "intern_id": 3, "intern_name": "Rohan Verma", "title": "Data Pipeline Ingestion with Apache Kafka", "deadline": "2026-08-10", "status": "APPROVED", "score": 96.00, "submission_url": "https://github.com/internhub/task8"},
        {"task_id": 10, "intern_id": 3, "intern_name": "Rohan Verma", "title": "Vector Database Embedding Integration", "deadline": "2026-10-10", "status": "SUBMITTED", "score": None, "submission_url": "https://github.com/internhub/task10"}
    ])

def get_mock_stipends():
    return _create_df([
        {"payment_id": 1, "intern_name": "Aarav Shah", "pay_month": 8, "pay_year": 2026, "days_present": 22, "total_working_days": 22, "calculated_stipend": 20000.00, "bonus": 2000.00, "net_amount": 22000.00, "payment_status": "PROCESSED", "processed_date": "2026-08-31"},
        {"payment_id": 2, "intern_name": "Diya Joshi", "pay_month": 8, "pay_year": 2026, "days_present": 21, "total_working_days": 22, "calculated_stipend": 19090.91, "bonus": 0.00, "net_amount": 19090.91, "payment_status": "PROCESSED", "processed_date": "2026-08-31"},
        {"payment_id": 3, "intern_name": "Rohan Verma", "pay_month": 8, "pay_year": 2026, "days_present": 22, "total_working_days": 22, "calculated_stipend": 25000.00, "bonus": 2500.00, "net_amount": 27500.00, "payment_status": "PROCESSED", "processed_date": "2026-08-31"},
        {"payment_id": 4, "intern_name": "Manish Gupta", "pay_month": 7, "pay_year": 2026, "days_present": 22, "total_working_days": 22, "calculated_stipend": 20000.00, "bonus": 2000.00, "net_amount": 22000.00, "payment_status": "PROCESSED", "processed_date": "2026-07-31"}
    ])
