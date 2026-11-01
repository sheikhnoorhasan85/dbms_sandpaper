# InternHub: Comprehensive Entity-Relationship (ER) Model
## Course: CS203 Database Management Systems — SVNIT Surat
### Team: `sandpaper`

---

## 1. Crow's Foot Relational ER Diagram

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

    DEPARTMENT {
        int dept_id PK "Surrogate Primary Key"
        varchar dept_name UK "Unique Department Name"
        varchar dept_code UK "Unique Short Code (e.g. CSE)"
        varchar location "Physical Location / Floor"
        decimal budget "Allocated Budget pool (>= 0)"
    }

    MENTOR {
        int mentor_id PK "Surrogate Primary Key"
        varchar first_name "First Name"
        varchar last_name "Last Name"
        varchar email UK "Unique Faculty/Work Email"
        varchar phone "Contact Telephone"
        int dept_id FK "References DEPARTMENT(dept_id)"
        varchar designation "Academic or Industry Title"
        int max_interns "Capacity Quota (1 to 10)"
    }

    INTERN {
        int intern_id PK "Surrogate Primary Key"
        varchar first_name "First Name"
        varchar last_name "Last Name"
        varchar email UK "Unique Student Email"
        varchar phone "Contact Telephone"
        varchar college_name "University / Institute Name"
        int dept_id FK "References DEPARTMENT(dept_id)"
        int mentor_id FK "References MENTOR(mentor_id) [Nullable]"
        date start_date "Internship Commencement Date"
        date end_date "Internship Conclusion Date"
        decimal base_stipend "Contract Monthly Compensation"
        enum status "APPLIED | ALLOCATED | ACTIVE | COMPLETED | TERMINATED"
    }

    TASK {
        int task_id PK "Surrogate Primary Key"
        int intern_id FK "References INTERN(intern_id)"
        int assigned_by FK "References MENTOR(mentor_id)"
        varchar title "Task Milestone Title"
        text description "Detailed Requirements"
        date deadline "Submission Cutoff Date"
        enum status "TODO | IN_PROGRESS | SUBMITTED | APPROVED | REJECTED"
        decimal score "Evaluated Score (0.00 to 100.00)"
        varchar submission_url "Deliverable Repo / Document Link"
    }

    ATTENDANCE {
        int att_id PK "Surrogate Primary Key"
        int intern_id FK "References INTERN(intern_id)"
        date att_date "Calendar Attendance Date"
        enum status "PRESENT | ABSENT | WORK_FROM_HOME | ON_LEAVE"
        decimal hours_logged "Daily Working Hours (0.0 to 24.0)"
        varchar remarks "Optional Notes / Reason for Leave"
    }

    PERFORMANCE_REVIEW {
        int review_id PK "Surrogate Primary Key"
        int intern_id FK "References INTERN(intern_id)"
        int mentor_id FK "References MENTOR(mentor_id)"
        date review_date "Evaluation Date"
        int week_number "Academic Week Number (1 to 52)"
        decimal technical_rating "Technical Rating (1.0 to 5.0)"
        decimal softskills_rating "Soft Skills Rating (1.0 to 5.0)"
        text feedback "Qualitative Mentor Remarks"
    }

    STIPEND_PAYMENT {
        int payment_id PK "Surrogate Primary Key"
        int intern_id FK "References INTERN(intern_id)"
        int pay_month "Billing Calendar Month (1 to 12)"
        int pay_year "Billing Calendar Year (>= 2020)"
        int days_present "Verified Working Days Attended"
        int total_working_days "Standard Calendar Working Days"
        decimal calculated_stipend "Pro-rated Base Stipend"
        decimal bonus "Performance Incentive Bonus"
        decimal deductions "Leave / Disciplinary Deductions"
        decimal net_amount "Final Payout (calculated + bonus - deductions)"
        enum payment_status "PENDING | PROCESSED | REJECTED"
        date processed_date "Disbursement Date"
    }

    AUDIT_LOG {
        int log_id PK "Surrogate Primary Key"
        varchar action_type "INSERT | STATUS_CHANGE | COMPLETION"
        varchar table_name "Target Modified Table"
        int record_id "PK ID of Modified Row"
        text old_value "Previous Attribute State"
        text new_value "New Attribute State"
        varchar changed_by "Database User / Admin"
        timestamp timestamp "UTC / System Timestamp"
    }
```

---

## 2. Cardinality & Participation Constraints Table

| Entity 1 | Relationship | Entity 2 | Cardinality | Participation (Entity 1) | Participation (Entity 2) | Structural Rationale |
| :--- | :---: | :--- | :---: | :---: | :---: | :--- |
| **DEPARTMENT** | *employs* | **MENTOR** | $1 : N$ | Partial | Total | A department can have multiple mentors ($N \ge 0$). Every mentor must belong to exactly one department. |
| **DEPARTMENT** | *hosts* | **INTERN** | $1 : N$ | Partial | Total | An academic department hosts multiple interns. Every intern belongs to a host department. |
| **MENTOR** | *supervises* | **INTERN** | $1 : N$ | Partial | Partial | A mentor guides $0$ to `max_interns` (capped by trigger). An intern has at most one primary supervisor (nullable when initially `APPLIED`). |
| **MENTOR** | *assigns* | **TASK** | $1 : N$ | Partial | Total | A mentor assigns several project milestones. Every task is created by a mentor. |
| **INTERN** | *undertakes* | **TASK** | $1 : N$ | Partial | Total | An intern is assigned multiple tasks. Each task belongs strictly to one intern. |
| **INTERN** | *logs* | **ATTENDANCE** | $1 : N$ | Partial | Total | An intern logs attendance each working day. Every record belongs to an intern; unique per date via `UNIQUE(intern_id, att_date)`. |
| **MENTOR** | *conducts* | **PERFORMANCE_REVIEW** | $1 : N$ | Partial | Total | Mentors evaluate assigned students weekly. Every review is authored by a mentor. |
| **INTERN** | *receives* | **PERFORMANCE_REVIEW** | $1 : N$ | Partial | Total | An intern receives weekly evaluations; unique per week via `UNIQUE(intern_id, week_number)`. |
| **INTERN** | *earns* | **STIPEND_PAYMENT** | $1 : N$ | Partial | Total | An intern is issued monthly payroll statements computed via MySQL Cursor; unique per month via `UNIQUE(intern_id, pay_month, pay_year)`. |
| **INTERN** | *audited_in* | **AUDIT_LOG** | $1 : N$ | Partial | Total | Intern state transitions (`APPLIED` $\rightarrow$ `ACTIVE` $\rightarrow$ `COMPLETED`) automatically log audit trails. |

---

## 3. Attribute Taxonomy (Chen's Notation Breakdown)

### A. Key Attributes (Primary & Candidate Keys)
- `dept_id`, `dept_name`, `dept_code` in `DEPARTMENT`
- `mentor_id`, `email` in `MENTOR`
- `intern_id`, `email` in `INTERN`
- `task_id` in `TASK`
- `att_id` and composite `(intern_id, att_date)` in `ATTENDANCE`
- `review_id` and composite `(intern_id, week_number)` in `PERFORMANCE_REVIEW`
- `payment_id` and composite `(intern_id, pay_month, pay_year)` in `STIPEND_PAYMENT`
- `log_id` in `AUDIT_LOG`

### B. Composite Attributes
- Intern & Mentor full names: decomposed into `first_name` and `last_name` to uphold **1NF (Atomic Attributes)**.
- Attendance composite natural key: `(intern_id, att_date)`.
- Evaluation composite natural key: `(intern_id, week_number)`.
- Payroll billing cycle composite key: `(intern_id, pay_month, pay_year)`.

### C. Derived Attributes (Computed via Stored Programs / Functions)
- **`composite_performance_score`**: Calculated on the fly via `fn_calculate_overall_score(intern_id)`:
  $$\text{Composite Score} = (0.60 \times \text{Avg Task Score}) + (0.40 \times \text{Avg Mentor Rating} \times 20)$$
- **`attendance_rate`**: Calculated via `fn_calculate_attendance_rate(intern_id, month, year)`:
  $$\text{Attendance Rate} = \left(\frac{\text{Present Days}}{\text{Total Logged Days}}\right) \times 100$$
- **`slots_available` & `utilization_pct`**: Derived dynamically in view `vw_mentor_workload`:
  $$\text{Slots Available} = \text{max\_interns} - \text{current\_active\_interns}$$

---

## 4. Referential Integrity & Foreign Key Actions

| Foreign Key | Parent Table | Child Table | ON DELETE | ON UPDATE | Justification |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `dept_id` | `departments` | `mentors` | `RESTRICT` | `CASCADE` | Prevents deleting a department if faculty mentors are currently attached. |
| `dept_id` | `departments` | `interns` | `RESTRICT` | `CASCADE` | Protects institutional record integrity. |
| `mentor_id` | `mentors` | `interns` | `SET NULL` | `CASCADE` | If a mentor leaves, interns remain active and are reassigned rather than deleted. |
| `intern_id` | `interns` | `tasks` | `CASCADE` | `CASCADE` | Deleting a test intern cleans up their associated task records. |
| `intern_id` | `interns` | `attendance` | `CASCADE` | `CASCADE` | Prevents orphaned attendance rows. |
| `intern_id` | `interns` | `performance_reviews`| `CASCADE` | `CASCADE` | Prevents orphaned review rows. |
| `intern_id` | `interns` | `stipend_payments` | `CASCADE` | `CASCADE` | Prevents orphaned disbursement rows. |
