-- ============================================================================
-- Project: InternHub - Comprehensive Internship Management System
-- Team: sandpaper
-- Course: CS203 - Database Management Systems (B.Tech CSE Sem-III, SVNIT Surat)
-- File: 03_sample_data.sql
-- Description: Realistic seed data for testing queries, procedures, views, and web UI
-- ============================================================================

USE internhub_db;

-- ----------------------------------------------------------------------------
-- 1. Seed Departments
-- ----------------------------------------------------------------------------
INSERT INTO departments (dept_id, dept_name, dept_code, location, budget) VALUES
(1, 'Computer Science & Engineering', 'CSE', 'Academic Block A - 3rd Floor', 1200000.00),
(2, 'Artificial Intelligence & Data Science', 'AIDS', 'Advanced Computing Center', 1500000.00),
(3, 'Electronics & Communication', 'ECE', 'VLSI & Embedded Lab Block', 900000.00),
(4, 'Information Technology', 'IT', 'Software Incubation Wing', 850000.00),
(5, 'Robotics & Automation', 'ROBO', 'Mechatronics Innovation Center', 1100000.00);

-- ----------------------------------------------------------------------------
-- 2. Seed Mentors (Capacity between 2 and 4 interns)
-- ----------------------------------------------------------------------------
INSERT INTO mentors (mentor_id, first_name, last_name, email, phone, dept_id, designation, max_interns) VALUES
(1, 'Rajesh', 'Sharma', 'rajesh.sharma@svnit.ac.in', '+91 9825100001', 1, 'Associate Professor & Systems Lead', 3),
(2, 'Priya', 'Patel', 'priya.patel@svnit.ac.in', '+91 9825100002', 1, 'Assistant Professor (DBMS & Cloud)', 3),
(3, 'Vikram', 'Mehta', 'vikram.mehta@svnit.ac.in', '+91 9825100003', 2, 'Lead AI Research Scientist', 2),
(4, 'Ananya', 'Deshmukh', 'ananya.deshmukh@svnit.ac.in', '+91 9825100004', 2, 'Senior Data Engineer', 3),
(5, 'Suresh', 'Iyer', 'suresh.iyer@svnit.ac.in', '+91 9825100005', 3, 'Principal Hardware Architect', 3),
(6, 'Neha', 'Verma', 'neha.verma@svnit.ac.in', '+91 9825100006', 4, 'Full-Stack Technical Architect', 4);

-- ----------------------------------------------------------------------------
-- 3. Seed Interns (Various stages: ACTIVE, ALLOCATED, COMPLETED, APPLIED)
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- 4. Seed Tasks
-- ----------------------------------------------------------------------------
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
(10, 3, 3, 'Vector Database Embedding Integration', 'Benchmark vector index algorithms (HNSW vs IVF) for semantic search.', '2026-10-10', 'SUBMITTED', NULL, 'https://github.com/internhub/reports/task10'),

(11, 4, 4, 'Exploratory Data Analysis on User Demographics', 'Clean raw user clickstream and generate statistical summary reports.', '2026-09-01', 'APPROVED', 85.00, 'https://github.com/internhub/reports/task11'),
(12, 4, 4, 'Automated Data Quality Validation Scripts', 'Write validation rules to catch nulls, boundary anomalies, and duplicate keys.', '2026-09-25', 'APPROVED', 89.00, 'https://github.com/internhub/reports/task12'),
(13, 4, 4, 'Interactive Executive Reporting Dashboard', 'Build a responsive reporting dashboard displaying monthly retention KPIs.', '2026-10-20', 'IN_PROGRESS', NULL, NULL),

(14, 5, 4, 'Data Warehouse Star Schema Modeling', 'Design dimensional facts and dimension tables for sales analytics.', '2026-09-10', 'APPROVED', 87.50, 'https://github.com/internhub/reports/task14'),
(15, 5, 4, 'ETL Incremental Load Pipeline', 'Implement watermarking pattern for high-throughput incremental data loads.', '2026-10-05', 'APPROVED', 93.00, 'https://github.com/internhub/reports/task15'),

(16, 6, 5, 'Embedded IoT Sensor Data Protocol', 'Design compact binary message schema for microcontroller telemetry.', '2026-09-20', 'APPROVED', 88.00, 'https://github.com/internhub/reports/task16'),
(17, 6, 5, 'Firmware Over-The-Air Update Engine', 'Implement cryptographic verification for signed firmware blobs.', '2026-10-28', 'TODO', NULL, NULL),

(18, 7, 6, 'REST API Backend Architecture', 'Create modular microservices handling user identity and authentication.', '2026-08-25', 'APPROVED', 91.00, 'https://github.com/internhub/reports/task18'),
(19, 7, 6, 'Role-Based Access Control (RBAC) Engine', 'Implement JWT token verification and permission middleware.', '2026-09-18', 'APPROVED', 94.00, 'https://github.com/internhub/reports/task19'),
(20, 8, 6, 'Frontend Component Library & State Store', 'Develop accessible component system with Redux/Zustand integration.', '2026-09-15', 'APPROVED', 89.50, 'https://github.com/internhub/reports/task20'),

(21, 9, 2, 'Summer Project: Distributed Transaction Coordinator', 'Completed 2PC distributed consensus implementation.', '2026-06-15', 'APPROVED', 98.00, 'https://github.com/internhub/reports/task21'),
(22, 9, 2, 'Summer Project: Technical Documentation & Report', 'Final project submission and viva defense.', '2026-07-25', 'APPROVED', 95.00, 'https://github.com/internhub/reports/task22'),
(23, 10, 2, 'Summer Project: High-Availability Replication Setup', 'Configured active-passive MySQL replication cluster with automated failover.', '2026-06-20', 'APPROVED', 92.00, 'https://github.com/internhub/reports/task23'),
(24, 10, 2, 'Summer Project: Benchmark Stress Testing', 'Conducted sysbench TPS stress testing up to 10k connections.', '2026-07-28', 'APPROVED', 94.00, 'https://github.com/internhub/reports/task24');

-- ----------------------------------------------------------------------------
-- 5. Seed Attendance Logs (Sample month: September 2026)
-- ----------------------------------------------------------------------------
INSERT INTO attendance (intern_id, att_date, status, hours_logged, remarks) VALUES
-- Intern 1 (Aarav Shah)
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
(1, '2026-09-16', 'PRESENT', 8.5, 'Regular office day'),
(1, '2026-09-17', 'PRESENT', 8.0, 'Regular office day'),
(1, '2026-09-18', 'PRESENT', 8.5, 'Mentor progress meeting'),
(1, '2026-09-21', 'PRESENT', 8.0, 'Regular office day'),
(1, '2026-09-22', 'PRESENT', 8.5, 'Regular office day'),
(1, '2026-09-23', 'PRESENT', 8.0, 'Regular office day'),
(1, '2026-09-24', 'PRESENT', 9.0, 'Bug fixes and test suite'),
(1, '2026-09-25', 'PRESENT', 8.0, 'Regular office day'),
(1, '2026-09-28', 'PRESENT', 8.5, 'Final September review'),
(1, '2026-09-29', 'PRESENT', 8.0, 'Regular office day'),
(1, '2026-09-30', 'PRESENT', 8.5, 'Monthly summary presentation'),

-- Intern 2 (Diya Joshi)
(2, '2026-09-01', 'PRESENT', 8.0, 'Regular office day'),
(2, '2026-09-02', 'PRESENT', 8.5, 'Regular office day'),
(2, '2026-09-03', 'PRESENT', 8.0, 'Regular office day'),
(2, '2026-09-04', 'WORK_FROM_HOME', 8.0, 'Remote query analysis'),
(2, '2026-09-07', 'PRESENT', 8.0, 'Regular office day'),
(2, '2026-09-08', 'PRESENT', 8.5, 'Regular office day'),
(2, '2026-09-09', 'PRESENT', 8.0, 'Regular office day'),
(2, '2026-09-10', 'PRESENT', 8.0, 'Regular office day'),
(2, '2026-09-11', 'ABSENT', 0.0, 'Unnotified absence'),
(2, '2026-09-14', 'PRESENT', 8.5, 'Regular office day'),
(2, '2026-09-15', 'PRESENT', 8.0, 'Regular office day'),
(2, '2026-09-16', 'PRESENT', 8.0, 'Regular office day'),
(2, '2026-09-17', 'PRESENT', 8.5, 'Regular office day'),
(2, '2026-09-18', 'PRESENT', 8.0, 'Regular office day'),
(2, '2026-09-21', 'PRESENT', 8.0, 'Regular office day'),
(2, '2026-09-22', 'WORK_FROM_HOME', 8.0, 'Remote trigger testing'),
(2, '2026-09-23', 'PRESENT', 8.5, 'Regular office day'),
(2, '2026-09-24', 'PRESENT', 8.0, 'Regular office day'),
(2, '2026-09-25', 'PRESENT', 8.0, 'Regular office day'),
(2, '2026-09-28', 'PRESENT', 8.5, 'Regular office day'),
(2, '2026-09-29', 'PRESENT', 8.0, 'Regular office day'),
(2, '2026-09-30', 'PRESENT', 8.0, 'Regular office day'),

-- Intern 3 (Rohan Verma)
(3, '2026-09-01', 'PRESENT', 9.0, 'Research lab'),
(3, '2026-09-02', 'PRESENT', 9.0, 'Research lab'),
(3, '2026-09-03', 'PRESENT', 8.5, 'Research lab'),
(3, '2026-09-04', 'WORK_FROM_HOME', 8.0, 'Kafka pipeline testing'),
(3, '2026-09-07', 'PRESENT', 9.0, 'Research lab'),
(3, '2026-09-08', 'PRESENT', 8.5, 'Research lab'),
(3, '2026-09-09', 'PRESENT', 8.0, 'Research lab'),
(3, '2026-09-10', 'PRESENT', 9.0, 'Research lab'),
(3, '2026-09-11', 'PRESENT', 8.5, 'Research lab'),
(3, '2026-09-14', 'PRESENT', 9.0, 'Research lab'),
(3, '2026-09-15', 'PRESENT', 8.5, 'Research lab'),
(3, '2026-09-16', 'PRESENT', 9.0, 'Research lab'),
(3, '2026-09-17', 'PRESENT', 8.5, 'Research lab'),
(3, '2026-09-18', 'PRESENT', 9.0, 'Research lab'),
(3, '2026-09-21', 'PRESENT', 8.5, 'Research lab'),
(3, '2026-09-22', 'PRESENT', 9.0, 'Research lab'),
(3, '2026-09-23', 'PRESENT', 8.5, 'Research lab'),
(3, '2026-09-24', 'PRESENT', 9.0, 'Research lab'),
(3, '2026-09-25', 'PRESENT', 8.5, 'Research lab'),
(3, '2026-09-28', 'PRESENT', 9.0, 'Research lab'),
(3, '2026-09-29', 'PRESENT', 8.5, 'Research lab'),
(3, '2026-09-30', 'PRESENT', 9.0, 'Research lab');

-- ----------------------------------------------------------------------------
-- 6. Seed Performance Reviews
-- ----------------------------------------------------------------------------
INSERT INTO performance_reviews (review_id, intern_id, mentor_id, review_date, week_number, technical_rating, softskills_rating, feedback) VALUES
(1, 1, 1, '2026-08-08', 1, 4.2, 4.0, 'Good initial grasp of the database codebase. Clear communication in team standups.'),
(2, 1, 1, '2026-08-15', 2, 4.6, 4.5, 'Exceptional work on the normalization deliverable. Followed proper third normal form.'),
(3, 1, 1, '2026-08-22', 3, 4.5, 4.2, 'Proactive in asking clarifying questions on storage engines.'),
(4, 1, 1, '2026-08-29', 4, 4.8, 4.7, 'Outstanding stored procedure coding skills and error handling.'),

(5, 2, 1, '2026-08-08', 1, 4.0, 4.2, 'Quick learner. Understood the indexing requirements effectively.'),
(6, 2, 1, '2026-08-15', 2, 4.4, 4.3, 'Strong SQL query optimization demonstrated using EXPLAIN.'),
(7, 2, 1, '2026-08-22', 3, 4.6, 4.5, 'Delivered clean trigger scripts with appropriate error signaling.'),

(8, 3, 3, '2026-08-15', 2, 4.9, 4.8, 'Top tier performance in streaming and schema design.'),
(9, 3, 3, '2026-08-29', 4, 4.8, 4.7, 'Consistently delivers ahead of schedule with production-grade quality.'),

(10, 4, 4, '2026-08-22', 3, 4.2, 4.4, 'Very diligent and communicative data scientist intern.'),
(11, 4, 4, '2026-09-05', 5, 4.5, 4.6, 'Data cleaning scripts were well structured and documented.'),

(12, 9, 2, '2026-07-28', 12, 5.0, 5.0, 'Outstanding summer performance. Fully completed all milestones with distinction.');

-- ----------------------------------------------------------------------------
-- 7. Seed Stipend Payments (Historical records)
-- ----------------------------------------------------------------------------
INSERT INTO stipend_payments (payment_id, intern_id, pay_month, pay_year, days_present, total_working_days, calculated_stipend, bonus, deductions, net_amount, payment_status, processed_date) VALUES
(1, 1, 8, 2026, 22, 22, 20000.00, 2000.00, 0.00, 22000.00, 'PROCESSED', '2026-08-31'),
(2, 2, 8, 2026, 21, 22, 19090.91, 0.00, 0.00, 19090.91, 'PROCESSED', '2026-08-31'),
(3, 3, 8, 2026, 22, 22, 25000.00, 2500.00, 0.00, 27500.00, 'PROCESSED', '2026-08-31'),
(4, 9, 7, 2026, 22, 22, 20000.00, 2000.00, 0.00, 22000.00, 'PROCESSED', '2026-07-31'),
(5, 10, 7, 2026, 22, 22, 20000.00, 1500.00, 0.00, 21500.00, 'PROCESSED', '2026-07-31');

-- ----------------------------------------------------------------------------
-- 8. Seed Audit Logs
-- ----------------------------------------------------------------------------
INSERT INTO audit_logs (log_id, action_type, table_name, record_id, old_value, new_value, changed_by, timestamp) VALUES
(1, 'DATABASE_INIT', 'system', 0, NULL, 'Initialized InternHub database schema and constraints', 'DBA_ADMIN', '2026-08-01 09:00:00'),
(2, 'STATUS_CHANGE', 'interns', 1, 'Status: APPLIED', 'Status: ACTIVE', 'HR_ADMIN', '2026-08-01 09:30:00'),
(3, 'STATUS_CHANGE', 'interns', 2, 'Status: APPLIED', 'Status: ACTIVE', 'HR_ADMIN', '2026-08-01 09:35:00'),
(4, 'STATUS_CHANGE', 'interns', 9, 'Status: ACTIVE', 'Status: COMPLETED', 'SYSTEM', '2026-07-31 17:00:00'),
(5, 'STATUS_CHANGE', 'interns', 10, 'Status: ACTIVE', 'Status: COMPLETED', 'SYSTEM', '2026-07-31 17:05:00');

-- ----------------------------------------------------------------------------
-- 9. Seed Users (Database Authentication)
-- Passwords:
-- 'admin123'    -> 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
-- 'password123' -> ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f
-- ----------------------------------------------------------------------------
INSERT INTO users (user_id, email, password_hash, role, reference_id, full_name, is_active) VALUES
-- Admin Account
(1, 'admin@svnit.ac.in', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'ADMIN', NULL, 'HR Directorate (Admin)', TRUE),

-- Mentor Accounts (reference_id links to mentor_id)
(2, 'rajesh.sharma@svnit.ac.in', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'MENTOR', 1, 'Dr. Rajesh Sharma', TRUE),
(3, 'priya.patel@svnit.ac.in', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'MENTOR', 2, 'Dr. Priya Patel', TRUE),
(4, 'vikram.mehta@svnit.ac.in', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'MENTOR', 3, 'Dr. Vikram Mehta', TRUE),
(5, 'ananya.deshmukh@svnit.ac.in', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'MENTOR', 4, 'Ananya Deshmukh', TRUE),

-- Intern Accounts (reference_id links to intern_id)
(6, 'aarav.shah@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'INTERN', 1, 'Aarav Shah', TRUE),
(7, 'diya.joshi@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'INTERN', 2, 'Diya Joshi', TRUE),
(8, 'rohan.verma@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'INTERN', 3, 'Rohan Verma', TRUE),

-- Evaluator / Professor Account
(9, 'evaluator@svnit.ac.in', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'EVALUATOR', NULL, 'Lab Evaluator (SVNIT)', TRUE);
