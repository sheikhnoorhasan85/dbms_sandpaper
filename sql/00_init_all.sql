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
-- 6. Table: stipend_payments
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
-- 7. Table: users
-- Secure user authentication table with roles and foreign key references
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(64) NOT NULL,
    role ENUM('ADMIN', 'MENTOR', 'INTERN') NOT NULL,
    reference_id INT NULL, -- references mentor_id if MENTOR, intern_id if INTERN
    full_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_user_role CHECK (role IN ('ADMIN', 'MENTOR', 'INTERN'))
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
CREATE INDEX idx_stipend_intern ON stipend_payments(intern_id);
CREATE INDEX idx_users_email_role ON users(email, role);

-- Operational indexes for search, filtering, and report aggregation
CREATE INDEX idx_interns_status ON interns(status);
CREATE INDEX idx_tasks_deadline_status ON tasks(deadline, status);
CREATE INDEX idx_attendance_date ON attendance(att_date);
CREATE INDEX idx_stipend_period ON stipend_payments(pay_year, pay_month, payment_status);


-- ============================================================================
-- PART 2: PROCEDURAL LOGIC (FUNCTIONS, TRIGGERS, PROCEDURES, VIEWS)
-- ============================================================================

-- ============================================================================
-- Project: InternHub - Comprehensive Internship Management System
-- Team: sandpaper
-- Course: CS203 - Database Management Systems (B.Tech CSE Sem-III, SVNIT Surat)
-- File: 02_routines.sql
-- Description: MySQL Stored Programs (Triggers, Stored Procedures with Cursors, 
--              Stored Functions, and Analytic Views)
-- ============================================================================

USE internhub_db;

-- ============================================================================
-- 1. STORED FUNCTIONS
-- ============================================================================

DROP FUNCTION IF EXISTS fn_calculate_overall_score;
DELIMITER $$
CREATE FUNCTION fn_calculate_overall_score(p_intern_id INT)
RETURNS DECIMAL(5, 2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_avg_task_score DECIMAL(5, 2) DEFAULT 0.00;
    DECLARE v_task_count INT DEFAULT 0;

    -- Calculate average task score from approved tasks (out of 100)
    SELECT COUNT(*), IFNULL(AVG(score), 0.00)
    INTO v_task_count, v_avg_task_score
    FROM tasks
    WHERE intern_id = p_intern_id AND status = 'APPROVED' AND score IS NOT NULL;

    IF v_task_count = 0 THEN
        RETURN 0.00;
    END IF;

    RETURN ROUND(v_avg_task_score, 2);
END$$
DELIMITER ;

DROP FUNCTION IF EXISTS fn_calculate_attendance_rate;
DELIMITER $$
CREATE FUNCTION fn_calculate_attendance_rate(p_intern_id INT, p_month INT, p_year INT)
RETURNS DECIMAL(5, 2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_days_present INT DEFAULT 0;
    DECLARE v_total_logged INT DEFAULT 0;
    DECLARE v_rate DECIMAL(5, 2) DEFAULT 0.00;

    SELECT 
        COUNT(CASE WHEN status IN ('PRESENT', 'WORK_FROM_HOME') THEN 1 END),
        COUNT(*)
    INTO v_days_present, v_total_logged
    FROM attendance
    WHERE intern_id = p_intern_id
      AND MONTH(att_date) = p_month
      AND YEAR(att_date) = p_year;

    IF v_total_logged = 0 THEN
        RETURN 0.00;
    END IF;

    SET v_rate = (v_days_present / v_total_logged) * 100.00;
    RETURN ROUND(v_rate, 2);
END$$
DELIMITER ;


-- ============================================================================
-- 2. DATABASE TRIGGERS
-- ============================================================================

DROP TRIGGER IF EXISTS trg_prevent_mentor_overload_insert;
DELIMITER $$
CREATE TRIGGER trg_prevent_mentor_overload_insert
BEFORE INSERT ON interns
FOR EACH ROW
BEGIN
    DECLARE v_active_count INT DEFAULT 0;
    DECLARE v_max_allowed INT DEFAULT 3;

    -- Check only if mentor is assigned and intern is active or allocated
    IF NEW.mentor_id IS NOT NULL AND NEW.status IN ('ACTIVE', 'ALLOCATED') THEN
        -- Get mentor's max allowed capacity
        SELECT max_interns INTO v_max_allowed
        FROM mentors
        WHERE mentor_id = NEW.mentor_id;

        -- Count currently active/allocated interns for this mentor
        SELECT COUNT(*) INTO v_active_count
        FROM interns
        WHERE mentor_id = NEW.mentor_id
          AND status IN ('ACTIVE', 'ALLOCATED');

        IF v_active_count >= v_max_allowed THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Capacity Exceeded: Selected mentor has reached their maximum active intern quota!';
        END IF;
    END IF;
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_prevent_mentor_overload_update;
DELIMITER $$
CREATE TRIGGER trg_prevent_mentor_overload_update
BEFORE UPDATE ON interns
FOR EACH ROW
BEGIN
    DECLARE v_active_count INT DEFAULT 0;
    DECLARE v_max_allowed INT DEFAULT 3;

    -- Trigger check if mentor changed or status changed to ACTIVE/ALLOCATED
    IF NEW.mentor_id IS NOT NULL AND NEW.status IN ('ACTIVE', 'ALLOCATED') 
       AND (OLD.mentor_id IS NULL OR OLD.mentor_id != NEW.mentor_id OR OLD.status NOT IN ('ACTIVE', 'ALLOCATED')) THEN
        
        SELECT max_interns INTO v_max_allowed
        FROM mentors
        WHERE mentor_id = NEW.mentor_id;

        SELECT COUNT(*) INTO v_active_count
        FROM interns
        WHERE mentor_id = NEW.mentor_id
          AND intern_id != NEW.intern_id
          AND status IN ('ACTIVE', 'ALLOCATED');

        IF v_active_count >= v_max_allowed THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Capacity Exceeded: Selected mentor has reached their maximum active intern quota!';
        END IF;
    END IF;
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_validate_task_approval;
DELIMITER $$
CREATE TRIGGER trg_validate_task_approval
BEFORE UPDATE ON tasks
FOR EACH ROW
BEGIN
    IF NEW.status = 'APPROVED' AND (NEW.score IS NULL OR NEW.score < 0.00 OR NEW.score > 100.00) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Validation Error: An approved task must be assigned a score between 0 and 100.';
    END IF;
END$$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_prevent_attendance_tampering;
DELIMITER $$
CREATE TRIGGER trg_prevent_attendance_tampering
BEFORE UPDATE ON attendance
FOR EACH ROW
BEGIN
    -- Block modifications to logged working hours or attendance dates unless authorized
    IF (OLD.hours_logged != NEW.hours_logged OR OLD.att_date != NEW.att_date) THEN
        IF NEW.remarks IS NULL OR NEW.remarks NOT LIKE '%[SUPERVISOR_OVERRIDE]%' THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Policy Violation: Logged working hours cannot be modified by students. Contact HR or your Mentor for adjustments.';
        END IF;
    END IF;
END$$
DELIMITER ;


-- ============================================================================
-- 3. STORED PROCEDURES
-- ============================================================================

-- Procedure 1: Atomic Onboarding of Interns
DROP PROCEDURE IF EXISTS sp_onboard_intern;
DELIMITER $$
CREATE PROCEDURE sp_onboard_intern(
    IN p_first_name VARCHAR(50),
    IN p_last_name VARCHAR(50),
    IN p_email VARCHAR(100),
    IN p_phone VARCHAR(20),
    IN p_college VARCHAR(150),
    IN p_dept_id INT,
    IN p_mentor_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE,
    IN p_base_stipend DECIMAL(10, 2),
    OUT p_new_intern_id INT,
    OUT p_status_message VARCHAR(255)
)
proc_body: BEGIN
    DECLARE v_dept_exists INT DEFAULT 0;
    DECLARE v_mentor_exists INT DEFAULT 0;

    -- Validate date order
    IF p_end_date < p_start_date THEN
        SET p_status_message = 'Error: End date must be on or after start date.';
        SET p_new_intern_id = NULL;
        LEAVE proc_body;
    END IF;

    -- Validate department existence
    SELECT COUNT(*) INTO v_dept_exists FROM departments WHERE dept_id = p_dept_id;
    IF v_dept_exists = 0 THEN
        SET p_status_message = 'Error: Department does not exist.';
        SET p_new_intern_id = NULL;
        LEAVE proc_body;
    END IF;

    -- Validate mentor existence if assigned
    IF p_mentor_id IS NOT NULL THEN
        SELECT COUNT(*) INTO v_mentor_exists FROM mentors WHERE mentor_id = p_mentor_id;
        IF v_mentor_exists = 0 THEN
            SET p_status_message = 'Error: Mentor does not exist.';
            SET p_new_intern_id = NULL;
            LEAVE proc_body;
        END IF;
    END IF;

    -- Insert new intern record
    INSERT INTO interns (
        first_name, last_name, email, phone, college_name, 
        dept_id, mentor_id, start_date, end_date, base_stipend, status
    ) VALUES (
        p_first_name, p_last_name, p_email, p_phone, p_college, 
        p_dept_id, p_mentor_id, p_start_date, p_end_date, p_base_stipend, 
        IF(p_mentor_id IS NOT NULL, 'ACTIVE', 'APPLIED')
    );

    SET p_new_intern_id = LAST_INSERT_ID();

    SET p_status_message = 'Success: Intern onboarded successfully.';
END$$
DELIMITER ;


-- Procedure 2: Monthly Stipend Calculation using a CURSOR (Phase D Requirement)
DROP PROCEDURE IF EXISTS sp_generate_monthly_stipend;
DELIMITER $$
CREATE PROCEDURE sp_generate_monthly_stipend(
    IN p_pay_month INT,
    IN p_pay_year INT,
    IN p_standard_working_days INT,
    OUT p_records_processed INT,
    OUT p_total_disbursed DECIMAL(12, 2)
)
BEGIN
    -- Declare local variables for cursor processing
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_intern_id INT;
    DECLARE v_base_stipend DECIMAL(10, 2);
    DECLARE v_days_present INT;
    DECLARE v_calculated_stipend DECIMAL(10, 2);
    DECLARE v_bonus DECIMAL(10, 2);
    DECLARE v_net_amount DECIMAL(10, 2);
    DECLARE v_avg_score DECIMAL(5, 2);

    -- Cursor iterating through all active interns
    DECLARE cur_active_interns CURSOR FOR
        SELECT intern_id, base_stipend
        FROM interns
        WHERE status IN ('ACTIVE', 'COMPLETED');

    -- Declare continue handler for cursor exhaustion
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    SET p_records_processed = 0;
    SET p_total_disbursed = 0.00;

    OPEN cur_active_interns;

    read_loop: LOOP
        FETCH cur_active_interns INTO v_intern_id, v_base_stipend;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Count verified present days for the requested month & year
        SELECT COUNT(*) INTO v_days_present
        FROM attendance
        WHERE intern_id = v_intern_id
          AND MONTH(att_date) = p_pay_month
          AND YEAR(att_date) = p_pay_year
          AND status IN ('PRESENT', 'WORK_FROM_HOME');

        -- Calculate pro-rated base stipend: (days_present / standard_working_days) * base_stipend
        IF p_standard_working_days > 0 THEN
            SET v_calculated_stipend = ROUND((v_days_present / p_standard_working_days) * v_base_stipend, 2);
        ELSE
            SET v_calculated_stipend = 0.00;
        END IF;

        -- Optional performance bonus: if overall performance score > 85, add 10% bonus
        SET v_avg_score = fn_calculate_overall_score(v_intern_id);
        IF v_avg_score >= 85.00 THEN
            SET v_bonus = ROUND(v_calculated_stipend * 0.10, 2);
        ELSE
            SET v_bonus = 0.00;
        END IF;

        SET v_net_amount = v_calculated_stipend + v_bonus;

        -- Upsert record into stipend_payments table
        INSERT INTO stipend_payments (
            intern_id, pay_month, pay_year, days_present, total_working_days,
            calculated_stipend, bonus, deductions, net_amount, payment_status, processed_date
        ) VALUES (
            v_intern_id, p_pay_month, p_pay_year, v_days_present, p_standard_working_days,
            v_calculated_stipend, v_bonus, 0.00, v_net_amount, 'PROCESSED', CURDATE()
        )
        ON DUPLICATE KEY UPDATE
            days_present = VALUES(days_present),
            total_working_days = VALUES(total_working_days),
            calculated_stipend = VALUES(calculated_stipend),
            bonus = VALUES(bonus),
            net_amount = VALUES(net_amount),
            payment_status = 'PROCESSED',
            processed_date = CURDATE();

        SET p_records_processed = p_records_processed + 1;
        SET p_total_disbursed = p_total_disbursed + v_net_amount;

    END LOOP;

    CLOSE cur_active_interns;
END$$
DELIMITER ;


-- Procedure 3: Complete Internship & Generate Exit Summary
DROP PROCEDURE IF EXISTS sp_complete_internship;
DELIMITER $$
CREATE PROCEDURE sp_complete_internship(
    IN p_intern_id INT,
    OUT p_final_score DECIMAL(5, 2),
    OUT p_status_message VARCHAR(255)
)
proc_body: BEGIN
    DECLARE v_pending_tasks INT DEFAULT 0;
    DECLARE v_current_status VARCHAR(20);

    -- Check intern status
    SELECT status INTO v_current_status
    FROM interns
    WHERE intern_id = p_intern_id;

    IF v_current_status IS NULL THEN
        SET p_status_message = 'Error: Intern record not found.';
        SET p_final_score = 0.00;
        LEAVE proc_body;
    END IF;

    -- Count pending tasks (not approved or rejected)
    SELECT COUNT(*) INTO v_pending_tasks
    FROM tasks
    WHERE intern_id = p_intern_id AND status IN ('TODO', 'IN_PROGRESS', 'SUBMITTED');

    IF v_pending_tasks > 0 THEN
        SET p_status_message = CONCAT('Warning: Intern still has ', v_pending_tasks, ' unreviewed/pending task(s).');
    END IF;

    -- Calculate final overall score
    SET p_final_score = fn_calculate_overall_score(p_intern_id);

    -- Update intern status to COMPLETED
    UPDATE interns
    SET status = 'COMPLETED'
    WHERE intern_id = p_intern_id;

    IF v_pending_tasks = 0 THEN
        SET p_status_message = CONCAT('Success: Internship completed. Final Score: ', p_final_score, '%.');
    END IF;
END$$
DELIMITER ;


-- Procedure 4: Atomic Self-Registration of Student User (Transactional)
DROP PROCEDURE IF EXISTS sp_register_student_user;
DELIMITER $$
CREATE PROCEDURE sp_register_student_user(
    IN p_first_name VARCHAR(50),
    IN p_last_name VARCHAR(50),
    IN p_email VARCHAR(100),
    IN p_phone VARCHAR(20),
    IN p_college VARCHAR(150),
    IN p_dept_id INT,
    IN p_password_hash VARCHAR(64),
    OUT p_new_user_id INT,
    OUT p_status_message VARCHAR(255)
)
proc_body: BEGIN
    DECLARE v_email_exists INT DEFAULT 0;
    DECLARE v_new_intern_id INT;

    -- Check for duplicate email in users table
    SELECT COUNT(*) INTO v_email_exists 
    FROM users 
    WHERE LOWER(email) = LOWER(p_email);

    IF v_email_exists > 0 THEN
        SET p_status_message = 'Error: An account with this email address already exists.';
        SET p_new_user_id = NULL;
        LEAVE proc_body;
    END IF;

    -- Execute Atomic Multi-Table Transaction
    START TRANSACTION;

    -- 1. Insert intern application record
    INSERT INTO interns (
        first_name, last_name, email, phone, college_name,
        dept_id, mentor_id, start_date, end_date, base_stipend, status
    ) VALUES (
        p_first_name, p_last_name, p_email, p_phone, p_college,
        p_dept_id, NULL, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 90 DAY), 15000.00, 'APPLIED'
    );
    SET v_new_intern_id = LAST_INSERT_ID();

    -- 2. Insert authentication credentials into users table
    INSERT INTO users (
        email, password_hash, role, reference_id, full_name, is_active
    ) VALUES (
        p_email, p_password_hash, 'INTERN', v_new_intern_id, CONCAT(p_first_name, ' ', p_last_name), TRUE
    );
    SET p_new_user_id = LAST_INSERT_ID();

    COMMIT;
    SET p_status_message = 'Success: Account created successfully! You can now sign in.';
END$$
DELIMITER ;


-- ============================================================================
-- 4. ANALYTIC VIEWS
-- ============================================================================

-- View 1: Consolidated Intern Performance and Master Information
DROP VIEW IF EXISTS vw_intern_master_summary;
CREATE VIEW vw_intern_master_summary AS
SELECT 
    i.intern_id,
    CONCAT(i.first_name, ' ', i.last_name) AS intern_name,
    i.email AS intern_email,
    i.college_name,
    d.dept_name,
    d.dept_code,
    IFNULL(CONCAT(m.first_name, ' ', m.last_name), 'Unassigned') AS mentor_name,
    m.designation AS mentor_designation,
    i.start_date,
    i.end_date,
    i.base_stipend,
    i.status,
    COUNT(t.task_id) AS total_tasks,
    COUNT(CASE WHEN t.status = 'APPROVED' THEN 1 END) AS approved_tasks,
    ROUND(IFNULL(AVG(CASE WHEN t.status = 'APPROVED' THEN t.score END), 0.00), 2) AS avg_task_score,
    fn_calculate_overall_score(i.intern_id) AS composite_performance_score
FROM interns i
JOIN departments d ON i.dept_id = d.dept_id
LEFT JOIN mentors m ON i.mentor_id = m.mentor_id
LEFT JOIN tasks t ON i.intern_id = t.intern_id
GROUP BY 
    i.intern_id, i.first_name, i.last_name, i.email, i.college_name,
    d.dept_name, d.dept_code, m.first_name, m.last_name, m.designation,
    i.start_date, i.end_date, i.base_stipend, i.status;

-- View 2: Mentor Workload & Capacity Utilization
DROP VIEW IF EXISTS vw_mentor_workload;
CREATE VIEW vw_mentor_workload AS
SELECT 
    m.mentor_id,
    CONCAT(m.first_name, ' ', m.last_name) AS mentor_name,
    m.email,
    m.designation,
    d.dept_name,
    m.max_interns AS max_capacity,
    COUNT(CASE WHEN i.status IN ('ACTIVE', 'ALLOCATED') THEN 1 END) AS current_active_interns,
    (m.max_interns - COUNT(CASE WHEN i.status IN ('ACTIVE', 'ALLOCATED') THEN 1 END)) AS slots_available,
    ROUND((COUNT(CASE WHEN i.status IN ('ACTIVE', 'ALLOCATED') THEN 1 END) / m.max_interns) * 100.0, 1) AS utilization_pct,
    CASE 
        WHEN COUNT(CASE WHEN i.status IN ('ACTIVE', 'ALLOCATED') THEN 1 END) >= m.max_interns THEN 'FULL'
        WHEN COUNT(CASE WHEN i.status IN ('ACTIVE', 'ALLOCATED') THEN 1 END) >= (m.max_interns * 0.7) THEN 'NEAR_CAPACITY'
        ELSE 'AVAILABLE'
    END AS capacity_status
FROM mentors m
JOIN departments d ON m.dept_id = d.dept_id
LEFT JOIN interns i ON m.mentor_id = i.mentor_id
GROUP BY m.mentor_id, m.first_name, m.last_name, m.email, m.designation, d.dept_name, m.max_interns;


-- ============================================================================
-- PART 3: REALISTIC SAMPLE DATA
-- ============================================================================

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
-- 6. Seed Stipend Payments (Historical records)
-- ----------------------------------------------------------------------------
INSERT INTO stipend_payments (payment_id, intern_id, pay_month, pay_year, days_present, total_working_days, calculated_stipend, bonus, deductions, net_amount, payment_status, processed_date) VALUES
(1, 1, 8, 2026, 22, 22, 20000.00, 2000.00, 0.00, 22000.00, 'PROCESSED', '2026-08-31'),
(2, 2, 8, 2026, 21, 22, 19090.91, 0.00, 0.00, 19090.91, 'PROCESSED', '2026-08-31'),
(3, 3, 8, 2026, 22, 22, 25000.00, 2500.00, 0.00, 27500.00, 'PROCESSED', '2026-08-31'),
(4, 9, 7, 2026, 22, 22, 20000.00, 2000.00, 0.00, 22000.00, 'PROCESSED', '2026-07-31'),
(5, 10, 7, 2026, 22, 22, 20000.00, 1500.00, 0.00, 21500.00, 'PROCESSED', '2026-07-31');

-- ----------------------------------------------------------------------------
-- 7. Seed Users (Database Authentication)
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
(8, 'rohan.verma@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'INTERN', 3, 'Rohan Verma', TRUE);
