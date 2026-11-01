# SVNIT Surat — CS203 Database Management Systems
## Viva Defense & Practical Examination Guide: **InternHub**
### Team: `sandpaper`

This guide prepares your team for the lab viva, practical exam questions, and project presentation before your professors.

---

### Core Relational Concepts & Normalization

#### Q1. What is the difference between 3NF and BCNF?
**Answer:**
- **3NF:** For every non-trivial functional dependency $X \rightarrow Y$, either $X$ is a superkey OR $Y$ is a prime attribute (part of some candidate key).
- **BCNF:** For every non-trivial functional dependency $X \rightarrow Y$, $X$ MUST be a superkey. There is no exception for $Y$ being a prime attribute.
- **In InternHub:** All our tables satisfy BCNF because all determinant attributes on the left-hand side are candidate keys.

#### Q2. Why is denormalization avoided in this transactional database?
**Answer:** Denormalization introduces update anomalies, insertion anomalies, and deletion anomalies. For instance, if department information were stored directly inside the `interns` table, renaming a department would require updating thousands of rows, risking inconsistency.

#### Q3. What candidate keys exist in your `attendance` table?
**Answer:** There are two candidate keys:
1. `att_id` (Surrogate primary key).
2. The composite natural key `(intern_id, att_date)`. This composite key guarantees that an intern cannot be logged more than once on the same date.

---

### Stored Programs & Procedural SQL

#### Q4. What is a Cursor and when is it required?
**Answer:** A cursor is a database object pointing to a result set that allows row-by-row navigation and processing. While standard SQL operates on set-level operations, our stored procedure `sp_generate_monthly_stipend` uses a cursor because for each intern, we must execute procedural logic: calculate attendance percentages for a specific month, call a stored function for their weighted score, evaluate bonus eligibility, and record the payment record.

#### Q5. How does MySQL handle cursor completion?
**Answer:** In MySQL, cursor exhaustion is handled by declaring a handler:
```sql
DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
```
When `FETCH` reaches the end of the active set, MySQL sets `done = TRUE`, allowing the loop to gracefully terminate via `LEAVE read_loop;`.

#### Q6. What is the difference between a Stored Procedure and a Stored Function?
**Answer:**
- **Function:** Must return a single scalar value using the `RETURN` keyword. Can be invoked directly within `SELECT` statements (e.g. `SELECT fn_calculate_overall_score(intern_id)`). It cannot commit or roll back transactions.
- **Procedure:** Invoked using `CALL sp_name(...)`. It can return multiple values via `OUT` parameters or return multiple result sets. It can manage transactions.

#### Q7. Explain your trigger `trg_prevent_mentor_overload`.
**Answer:** It is a `BEFORE INSERT` and `BEFORE UPDATE` row-level trigger on the `interns` table. Before a new intern is associated with a mentor or when an intern's status changes to `ACTIVE`, the trigger counts the mentor's currently active interns. If this count meets or exceeds the mentor's `max_interns` threshold, it raises an exception using `SIGNAL SQLSTATE '45000'`, cancelling the transaction and rolling back any changes.

#### Q8. Why did you use `SIGNAL SQLSTATE '45000'`?
**Answer:** `SQLSTATE '45000'` is the standard ANSI SQL-92 code reserved for user-defined unhandled exceptions. In MySQL, executing `SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '...'` halts execution and sends a clear, human-readable error message back to the client application.

---

### Constraints & ACID Properties

#### Q9. How does `ON DELETE RESTRICT` differ from `ON DELETE SET NULL` and `CASCADE` in your schema?
**Answer:**
- `RESTRICT` on `departments`: If someone tries to delete a department that still has mentors or interns, MySQL throws an error and prevents the deletion to protect institutional hierarchy.
- `SET NULL` on `mentor_id`: If a mentor resigns, the intern record is preserved with `mentor_id` set to `NULL` until a new supervisor is assigned.
- `CASCADE` on `tasks` and `attendance`: If an intern test record is deleted, their subsidiary tasks and logs are automatically removed to avoid orphaned rows.

#### Q10. How do you guarantee the Atomicity and Consistency of intern onboarding?
**Answer:** Through `sp_onboard_intern`. The procedure encapsulates the insertion into `interns` and the recording of the audit event into `audit_logs` inside a single execution block. If the mentor capacity trigger throws an exception, the entire operation is halted, ensuring no partial or invalid intern record is ever committed.

---

### Indexing & Performance Tuning

#### Q11. Which storage engine did you select and why?
**Answer:** We selected **InnoDB**, the default transactional storage engine in MySQL. InnoDB supports ACID transactions, row-level locking (concurrency), and foreign key referential integrity constraints, unlike MyISAM which only supports table-level locking and lacks foreign key enforcement.

#### Q12. Why did you create a composite index on `tasks(deadline, status)`?
**Answer:** Mentors and interns frequently query pending tasks ordered by urgency (`WHERE status = 'TODO' ORDER BY deadline ASC`). A composite index on `(deadline, status)` allows the MySQL query optimizer to perform an index range scan directly without performing a separate sort in temporary memory (avoiding `Using filesort`).

---

### Security, Access Control & Compliance

#### Q13. How does your database prevent students from tampering with their daily working hours?
**Answer:** 
1. **At the Database Engine Level:** A row-level `BEFORE UPDATE` trigger `trg_prevent_attendance_tampering` intercepts any update statement affecting `hours_logged` or `att_date`. If executed without an authorized supervisor override tag, MySQL immediately aborts the transaction using `SIGNAL SQLSTATE '45000'`.
2. **At the Procedural Level:** Authorized corrections can only be performed by Faculty Mentors or HR Admins through `sp_adjust_attendance_hours`, which tags the record and writes an immutable audit record to `audit_logs`.
3. **At the Application Level:** Student attendance inputs are locked to the current date (`CURDATE()`), and once submitted, the form is replaced by an immutable locked status card.

#### Q14. How is user authentication implemented in the relational database model?
**Answer:** User credentials are stored in a normalized `users` table (`user_id`, `email`, `password_hash`, `role`, `reference_id`, `full_name`). Passwords are never stored in plaintext; instead, they are hashed using SHA-256 (`SHA2` in MySQL / `hashlib.sha256` in Python). When a user signs in, the system queries:
```sql
SELECT user_id, role, reference_id, full_name 
FROM users 
WHERE email = :email AND password_hash = :hash AND is_active = 1;
```
This maps the authenticated session directly to their role-specific foreign key (`mentor_id` or `intern_id`), enforcing row-level data isolation throughout the application.

---

### Presentation Demonstration Checklist

1. Show **MySQL Workbench**:
   - Run `SELECT * FROM departments;`
   - Run `SELECT * FROM vw_mentor_workload;`
2. Show **Web Interface (`streamlit run app.py`)**:
   - Navigate to **Executive Dashboard** to showcase the KPI metrics and department distribution chart.
   - Go to **Admin Portal**: Fill out the onboarding form and demonstrate successful execution.
   - Run the **Cursor Stipend Calculation** button to show monthly disbursement.
   - Switch to **Mentor Portal**: Grade an intern's deliverable and enter a weekly review.
   - Switch to **Intern Portal**: Demonstrate logging attendance.
3. Open **SQL Workbench Console** in the app and run a custom `JOIN` query to show live interactivity.
