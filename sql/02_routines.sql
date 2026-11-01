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
    DECLARE v_avg_tech_rating DECIMAL(3, 1) DEFAULT 0.0;
    DECLARE v_avg_soft_rating DECIMAL(3, 1) DEFAULT 0.0;
    DECLARE v_mentor_score_100 DECIMAL(5, 2) DEFAULT 0.00;
    DECLARE v_composite_score DECIMAL(5, 2) DEFAULT 0.00;
    DECLARE v_task_count INT DEFAULT 0;
    DECLARE v_review_count INT DEFAULT 0;

    -- 1. Calculate average task score from approved tasks (out of 100)
    SELECT COUNT(*), IFNULL(AVG(score), 0.00)
    INTO v_task_count, v_avg_task_score
    FROM tasks
    WHERE intern_id = p_intern_id AND status = 'APPROVED' AND score IS NOT NULL;

    -- 2. Calculate average mentor rating (technical + soft skills on 1-5 scale)
    SELECT COUNT(*), IFNULL(AVG(technical_rating), 0.0), IFNULL(AVG(softskills_rating), 0.0)
    INTO v_review_count, v_avg_tech_rating, v_avg_soft_rating
    FROM performance_reviews
    WHERE intern_id = p_intern_id;

    -- If no tasks and no reviews yet, return 0.00
    IF v_task_count = 0 AND v_review_count = 0 THEN
        RETURN 0.00;
    END IF;

    -- Convert mentor rating (average of tech & soft) from 5-point to 100-point scale
    IF v_review_count > 0 THEN
        SET v_mentor_score_100 = ((v_avg_tech_rating + v_avg_soft_rating) / 2.0) * 20.0;
    END IF;

    -- Weighted formula: 60% task performance + 40% mentor evaluations
    IF v_task_count > 0 AND v_review_count > 0 THEN
        SET v_composite_score = (v_avg_task_score * 0.60) + (v_mentor_score_100 * 0.40);
    ELSEIF v_task_count > 0 THEN
        SET v_composite_score = v_avg_task_score;
    ELSE
        SET v_composite_score = v_mentor_score_100;
    END IF;

    RETURN ROUND(v_composite_score, 2);
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

DROP TRIGGER IF EXISTS trg_audit_intern_status_change;
DELIMITER $$
CREATE TRIGGER trg_audit_intern_status_change
AFTER UPDATE ON interns
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO audit_logs (action_type, table_name, record_id, old_value, new_value, changed_by)
        VALUES (
            'STATUS_CHANGE', 
            'interns', 
            NEW.intern_id, 
            CONCAT('Status: ', OLD.status), 
            CONCAT('Status: ', NEW.status),
            CURRENT_USER()
        );
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

    -- Record in audit log
    INSERT INTO audit_logs (action_type, table_name, record_id, old_value, new_value, changed_by)
    VALUES (
        'INSERT',
        'interns',
        p_new_intern_id,
        NULL,
        CONCAT('Onboarded: ', p_first_name, ' ', p_last_name, ' (Dept: ', p_dept_id, ')'),
        CURRENT_USER()
    );

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

    -- Log completion in audit trail
    INSERT INTO audit_logs (action_type, table_name, record_id, old_value, new_value, changed_by)
    VALUES (
        'INTERNSHIP_COMPLETION',
        'interns',
        p_intern_id,
        CONCAT('Previous Status: ', v_current_status),
        CONCAT('Completed with Final Score: ', p_final_score, '%'),
        CURRENT_USER()
    );

    IF v_pending_tasks = 0 THEN
        SET p_status_message = CONCAT('Success: Internship completed. Final Score: ', p_final_score, '%.');
    END IF;
END$$
DELIMITER ;


-- Procedure 4: Supervisor Attendance Hours Adjustment with Audit Logging
DROP PROCEDURE IF EXISTS sp_adjust_attendance_hours;
DELIMITER $$
CREATE PROCEDURE sp_adjust_attendance_hours(
    IN p_att_id INT,
    IN p_new_hours DECIMAL(4, 2),
    IN p_reason VARCHAR(255),
    IN p_supervisor_name VARCHAR(100),
    OUT p_status_message VARCHAR(255)
)
proc_body: BEGIN
    DECLARE v_old_hours DECIMAL(4, 2);
    DECLARE v_intern_id INT;
    DECLARE v_att_date DATE;

    SELECT hours_logged, intern_id, att_date 
    INTO v_old_hours, v_intern_id, v_att_date
    FROM attendance 
    WHERE att_id = p_att_id;

    IF v_intern_id IS NULL THEN
        SET p_status_message = 'Error: Attendance record not found.';
        LEAVE proc_body;
    END IF;

    IF p_new_hours < 0.00 OR p_new_hours > 24.00 THEN
        SET p_status_message = 'Error: Invalid working hours (must be between 0 and 24).';
        LEAVE proc_body;
    END IF;

    -- Update attendance with authorized override tag in remarks to pass trigger check
    UPDATE attendance
    SET hours_logged = p_new_hours,
        remarks = CONCAT(IFNULL(remarks, ''), ' [SUPERVISOR_OVERRIDE: Adjusted from ', v_old_hours, ' hrs to ', p_new_hours, ' hrs by ', p_supervisor_name, '. Reason: ', p_reason, ']')
    WHERE att_id = p_att_id;

    -- Record adjustment in audit_logs
    INSERT INTO audit_logs (action_type, table_name, record_id, old_value, new_value, changed_by)
    VALUES (
        'ATTENDANCE_ADJUST',
        'attendance',
        p_att_id,
        CONCAT('Intern #', v_intern_id, ' Hours: ', v_old_hours, ' on ', v_att_date),
        CONCAT('Hours: ', p_new_hours, ' (Supervisor: ', p_supervisor_name, ', Reason: ', p_reason, ')'),
        p_supervisor_name
    );

    SET p_status_message = 'Success: Attendance hours adjusted and audit log recorded.';
END$$
DELIMITER ;


-- Procedure 5: Atomic Self-Registration of Student User (Transactional)
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

    -- 3. Log user creation in audit trail
    INSERT INTO audit_logs (action_type, table_name, record_id, old_value, new_value, changed_by)
    VALUES (
        'USER_REGISTRATION',
        'users',
        p_new_user_id,
        NULL,
        CONCAT('Registered Student Intern: ', p_first_name, ' ', p_last_name, ' (Intern ID: #', v_new_intern_id, ')'),
        'SELF_REGISTRATION'
    );

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
    ROUND(IFNULL(AVG(pr.technical_rating), 0.00), 1) AS avg_tech_rating,
    ROUND(IFNULL(AVG(pr.softskills_rating), 0.00), 1) AS avg_softskills_rating,
    fn_calculate_overall_score(i.intern_id) AS composite_performance_score
FROM interns i
JOIN departments d ON i.dept_id = d.dept_id
LEFT JOIN mentors m ON i.mentor_id = m.mentor_id
LEFT JOIN tasks t ON i.intern_id = t.intern_id
LEFT JOIN performance_reviews pr ON i.intern_id = pr.intern_id
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
