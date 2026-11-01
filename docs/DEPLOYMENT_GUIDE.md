# InternHub: Deployment & Role-Based Access Guide
## Course: CS203 Database Management Systems — SVNIT Surat
### Team: `sandpaper`

This guide explains how the **Role-Based Views** work and provides two simple methods to deploy the website so anyone (teammates, professors, evaluators) can access it online.

---

## 1. Role-Based Views & User Types

The application includes an **Authentication & Role Selection Gate**:

| Role Type | Target Audience | Tailored Dashboard Views & Capabilities |
| :--- | :--- | :--- |
| **👑 Admin / HR Officer** | Department Leads & Incubation Cell | • **Executive Dashboard:** Institutional metrics, department distribution charts, mentor workload.<br>• **Onboard Intern:** Execute `sp_onboard_intern` stored procedure.<br>• **Monthly Stipend Run:** Batch cursor payroll computation.<br>• **Faculty Quotas:** Real-time mentor quota tracking (`vw_mentor_workload`). |
| **👨‍🏫 Faculty Mentor** | Project Supervisors & Professors | • **My Supervised Interns:** Filtered strictly to students under this mentor's guidance.<br>• **Assign Deliverable:** Create new milestone tasks.<br>• **Evaluate Submissions:** Grade work; enforces score validation trigger (0–100).<br>• **Weekly Performance Review:** Submit technical and soft skill ratings (1–5 scale). |
| **🎓 Student Intern** | Enrolled Students | • **My Profile:** View assigned mentor, department, contract stipend, and performance score.<br>• **Daily Attendance:** Log attendance; enforces unique date constraint.<br>• **My Tasks:** View assigned milestones and submit deliverable URLs.<br>• **My Stipend Slips:** View itemized monthly payments with attendance & bonuses. |
| **🔍 Academic Evaluator** | Lab Professors & Viva Evaluators | • **Full Inspection Mode:** Access all portals, test database triggers, inspect ER diagrams, and execute queries in the SQL Console. |

---

## 2. Option A: Instant Live Public Link (Zero-Setup in 30 Seconds)

If you want someone to test or view your website **right now** while it runs on your Mac M4 Air:

1. In one terminal window, ensure your app is running:
   ```bash
   cd "/Users/noor/Downloads/dbms sandpaper "
   source venv/bin/activate
   streamlit run app.py
   ```
2. Open a **new terminal tab** (`Cmd + T`) and run this single command:
   ```bash
   ssh -p 443 -R0:localhost:8501 a.pinggy.io
   ```
   *(Or using `localhost.run`: `ssh -R 80:localhost:8501 localhost.run`)*
3. You will immediately get an **`https://...` public URL**.
4. Share that link with anyone — they can open it on their phone, laptop, or tablet and interact with your project live!

---

## 3. Option B: Permanent Free Cloud Deployment (Streamlit Community Cloud)

To get a permanent public link (e.g., `https://internhub-sandpaper.streamlit.app`) that stays online 24/7 even when your Mac is sleeping:

### Step 1: Initialize Git and Commit
In your terminal:
```bash
cd "/Users/noor/Downloads/dbms sandpaper "
git init
git add .
git commit -m "feat: InternHub with role-based authentication and dual-engine database"
```

### Step 2: Push to GitHub
1. Go to [github.com](https://github.com) and create a new repository named `internhub` (public or private).
2. Link and push your code:
   ```bash
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/internhub.git
   git push -u origin main
   ```

### Step 3: Deploy on Streamlit Community Cloud (100% Free)
1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **"New app"**.
3. Select your repository: `YOUR_GITHUB_USERNAME/internhub`.
4. Main file path: `app.py`.
5. Click **"Deploy!"**.
6. Within 60 seconds, your website is live with a permanent public URL that anyone in the world can access!

---

## 4. How the Database Works When Deployed Online

Your application features an **Autonomous Dual-Engine Database Architecture**:
1. **When running on your Mac M4 Air**: Connects to your local **MySQL Workbench** (`127.0.0.1:3306`).
2. **When deployed on Streamlit Cloud**: If a remote MySQL server is not configured, it automatically activates the **Autonomous Cloud Relational Engine (SQLite)** initialized with all 8 tables, triggers, views, and seed data.
3. **Optional Cloud MySQL (Aiven / TiDB)**: If you want a live cloud MySQL database, you can add your credentials in Streamlit's **Settings $\rightarrow$ Secrets**:
   ```toml
   [mysql]
   host = "your-cloud-mysql-host.com"
   port = 3306
   user = "your_user"
   password = "your_password"
   database = "internhub_db"
   ```
