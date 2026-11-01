-- ============================================================================
-- Project: InternHub - Comprehensive Internship Management System
-- Team: sandpaper
-- Course: CS203 - Database Management Systems (B.Tech CSE Sem-III, SVNIT Surat)
-- File: 01_schema.sql
-- Description: DDL script creating the database, tables, constraints, and indexes
-- ============================================================================

DROP DATABASE IF EXISTS internhub_db;
CREATE DATABASE internhub_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE internhub_db;

-- ----------------------------------------------------------------------------
-- 1. Table: departments
-- Entity storing academic or organizational departments hosting internships
-- ----------------------------------------------------------------------------
CREATE TABLE departments (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL UNIQUE,
    dept_code VARCHAR(10) NOT NULL UNIQUE,
    location VARCHAR(100) NOT NULL,
    budget DECIMAL(12, 2) NOT NULL DEFAULT 500000.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_dept_budget CHECK (budget >= 0.00)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 2. Table: mentors
-- Entity storing supervisors/professors/industry guides supervising interns
-- ----------------------------------------------------------------------------
CREATE TABLE mentors (
    mentor_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    dept_id INT NOT NULL,
    designation VARCHAR(100) NOT NULL,
    max_interns INT NOT NULL DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mentors_dept FOREIGN KEY (dept_id) 
        REFERENCES departments(dept_id) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT chk_mentor_capacity CHECK (max_interns > 0 AND max_interns <= 10)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 3. Table: interns
-- Core entity storing intern biodata, academic affiliation, and status
-- ----------------------------------------------------------------------------
CREATE TABLE interns (
    intern_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    college_name VARCHAR(150) NOT NULL,
    dept_id INT NOT NULL,
    mentor_id INT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    base_stipend DECIMAL(10, 2) NOT NULL DEFAULT 15000.00,
    status ENUM('APPLIED', 'ALLOCATED', 'ACTIVE', 'COMPLETED', 'TERMINATED') 
        NOT NULL DEFAULT 'APPLIED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_interns_dept FOREIGN KEY (dept_id) 
        REFERENCES departments(dept_id) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT fk_interns_mentor FOREIGN KEY (mentor_id) 
        REFERENCES mentors(mentor_id) 
        ON UPDATE CASCADE 
        ON DELETE SET NULL,
    CONSTRAINT chk_intern_dates CHECK (end_date >= start_date),
    CONSTRAINT chk_intern_stipend CHECK (base_stipend >= 0.00)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 4. Table: tasks
-- Entity storing work assignments, deadlines, progress status, and scores
-- ----------------------------------------------------------------------------
CREATE TABLE tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    intern_id INT NOT NULL,
    assigned_by INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    deadline DATE NOT NULL,
    status ENUM('TODO', 'IN_PROGRESS', 'SUBMITTED', 'APPROVED', 'REJECTED') 
        NOT NULL DEFAULT 'TODO',
    score DECIMAL(5, 2) NULL,
    submission_url VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tasks_intern FOREIGN KEY (intern_id) 
        REFERENCES interns(intern_id) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    CONSTRAINT fk_tasks_mentor FOREIGN KEY (assigned_by) 
        REFERENCES mentors(mentor_id) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT chk_task_score CHECK (score IS NULL OR (score >= 0.00 AND score <= 100.00))
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 5. Table: attendance
-- Daily attendance logs with uniqueness constraint per intern per calendar date
-- ----------------------------------------------------------------------------
CREATE TABLE attendance (
    att_id INT AUTO_INCREMENT PRIMARY KEY,
    intern_id INT NOT NULL,
    att_date DATE NOT NULL,
    status ENUM('PRESENT', 'ABSENT', 'WORK_FROM_HOME', 'ON_LEAVE') 
        NOT NULL DEFAULT 'PRESENT',
    hours_logged DECIMAL(4, 2) NOT NULL DEFAULT 8.00,
    remarks VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attendance_intern FOREIGN KEY (intern_id) 
        REFERENCES interns(intern_id) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    CONSTRAINT uk_intern_att_date UNIQUE (intern_id, att_date),
    CONSTRAINT chk_attendance_hours CHECK (hours_logged >= 0.00 AND hours_logged <= 24.00)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 6. Table: performance_reviews
-- Weekly evaluations conducted by mentors grading technical and soft skills
-- ----------------------------------------------------------------------------
CREATE TABLE performance_reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    intern_id INT NOT NULL,
    mentor_id INT NOT NULL,
    review_date DATE NOT NULL,
    week_number INT NOT NULL,
    technical_rating DECIMAL(3, 1) NOT NULL,
    softskills_rating DECIMAL(3, 1) NOT NULL,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reviews_intern FOREIGN KEY (intern_id) 
        REFERENCES interns(intern_id) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    CONSTRAINT fk_reviews_mentor FOREIGN KEY (mentor_id) 
        REFERENCES mentors(mentor_id) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT uk_intern_weekly_review UNIQUE (intern_id, week_number),
    CONSTRAINT chk_review_week CHECK (week_number >= 1 AND week_number <= 52),
    CONSTRAINT chk_tech_rating CHECK (technical_rating >= 1.0 AND technical_rating <= 5.0),
    CONSTRAINT chk_soft_rating CHECK (softskills_rating >= 1.0 AND softskills_rating <= 5.0)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 7. Table: stipend_payments
-- Monthly stipend billing records computed from attendance and base compensation
-- ----------------------------------------------------------------------------
CREATE TABLE stipend_payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    intern_id INT NOT NULL,
    pay_month INT NOT NULL,
    pay_year INT NOT NULL,
    days_present INT NOT NULL DEFAULT 0,
    total_working_days INT NOT NULL DEFAULT 22,
    calculated_stipend DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    bonus DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    deductions DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    net_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    payment_status ENUM('PENDING', 'PROCESSED', 'REJECTED') 
        NOT NULL DEFAULT 'PENDING',
    processed_date DATE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_stipend_intern FOREIGN KEY (intern_id) 
        REFERENCES interns(intern_id) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    CONSTRAINT uk_intern_stipend_period UNIQUE (intern_id, pay_month, pay_year),
    CONSTRAINT chk_stipend_month CHECK (pay_month BETWEEN 1 AND 12),
    CONSTRAINT chk_stipend_year CHECK (pay_year >= 2020),
    CONSTRAINT chk_stipend_days CHECK (days_present >= 0 AND total_working_days > 0),
    CONSTRAINT chk_net_amount CHECK (net_amount >= 0.00)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 8. Table: audit_logs
-- System audit trail logging state transitions, triggers, and automated updates
-- ----------------------------------------------------------------------------
CREATE TABLE audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    action_type VARCHAR(20) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INT NOT NULL,
    old_value TEXT NULL,
    new_value TEXT NULL,
    changed_by VARCHAR(100) NOT NULL DEFAULT 'SYSTEM',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 9. Table: users
-- Secure user authentication table with roles and foreign key references
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(64) NOT NULL,
    role ENUM('ADMIN', 'MENTOR', 'INTERN', 'EVALUATOR') NOT NULL,
    reference_id INT NULL, -- references mentor_id if MENTOR, intern_id if INTERN
    full_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_user_role CHECK (role IN ('ADMIN', 'MENTOR', 'INTERN', 'EVALUATOR'))
) ENGINE=InnoDB;

-- ============================================================================
-- Indexing Strategy (Phase D Requirement)
-- Indexes created for foreign keys, join efficiency, and frequent filter fields
-- ============================================================================

-- Foreign key indexes for accelerated join performance
CREATE INDEX idx_mentors_dept ON mentors(dept_id);
CREATE INDEX idx_interns_dept ON interns(dept_id);
CREATE INDEX idx_interns_mentor ON interns(mentor_id);
CREATE INDEX idx_tasks_intern ON tasks(intern_id);
CREATE INDEX idx_tasks_mentor ON tasks(assigned_by);
CREATE INDEX idx_attendance_intern ON attendance(intern_id);
CREATE INDEX idx_reviews_intern ON performance_reviews(intern_id);
CREATE INDEX idx_reviews_mentor ON performance_reviews(mentor_id);
CREATE INDEX idx_stipend_intern ON stipend_payments(intern_id);
CREATE INDEX idx_users_email_role ON users(email, role);

-- Operational indexes for search, filtering, and report aggregation
CREATE INDEX idx_interns_status ON interns(status);
CREATE INDEX idx_tasks_deadline_status ON tasks(deadline, status);
CREATE INDEX idx_attendance_date ON attendance(att_date);
CREATE INDEX idx_stipend_period ON stipend_payments(pay_year, pay_month, payment_status);
CREATE INDEX idx_audit_table_record ON audit_logs(table_name, record_id);
