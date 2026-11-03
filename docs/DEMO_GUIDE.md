# Capacity Connect — Demonstration Guide
## Smart India Hackathon 2026 Presentation Walkthrough

This guide details the end-to-end evaluation scenario for SIH judges, demonstrating the seamless interaction between **Administrator**, **Trainer**, and **Employee/Learner** personas.

---

## 1. Quick Launch Instructions

Ensure your environment is running:

```powershell
# In project root:
.\venv\Scripts\Activate.ps1

# Verify migrations and demo seed data:
python manage.py migrate
python manage.py seed_demo

# Start the development server:
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000/`.

---

## 2. Seed Demo Credentials

| Role | Username | Password | Key Capabilities |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `Admin@12345` | Platform-wide KPIs, User approvals, Audit PDF reports, Django Admin |
| **Trainer** | `trainer_ai` | `Trainer@12345` | Authored courses, Module management, MCQ examinations, Trainee progress monitoring |
| **Trainer (Climate)** | `trainer_climate` | `Trainer@12345` | Monsoon & Climate Modeling specialist |
| **Trainer (GIS)** | `trainer_gis` | `Trainer@12345` | Satellite oceanography & remote sensing specialist |
| **Employee / Learner** | `emp_arun` | `Employee@12345` | Certified scientist with issued certificate |
| **Employee / Learner** | `emp_vikram` | `Employee@12345` | Learner in progress (66.7% completed on Applied Met course) |
| **Employee / Learner** | `emp_priya` | `Employee@12345` | Certified coastal hazard specialist |

---

## 3. Recommended 3-Act Judge Demonstration

### Act 1: Administrator Oversight & Compliance
1. Sign in as `admin` (`admin` / `Admin@12345`).
2. Explore the **Executive Administration Dashboard**:
   - Live KPI counters (total personnel, active courses, completions, certificates).
   - 4 Interactive Chart.js charts: Course completion ratio, popular courses by enrolled staff, department-wise distribution, and competency domains.
3. Click **"Download Audit PDF"** in the top bar:
   - Notice the instant generation of an official ReportLab PDF audit report with executive KPIs and department breakdown.
4. Navigate to **User Directory & Approvals** (`/accounts/manage/users/`):
   - Filter by role (`TRAINER` / `EMPLOYEE`) or status (`PENDING`).
   - Demonstrate quick approval and account activation/deactivation.

### Act 2: Trainer Course & Assessment Delivery
1. Sign in as `trainer_ai` (`trainer_ai` / `Trainer@12345`).
2. Open the **Trainer Workspace**:
   - Review active learners and the real-time Trainee Progress monitoring table.
3. Navigate to **Course Management** (`/courses/trainer/my-courses/`):
   - Click **"Modules"** on *"Applied Meteorological Data Analysis with Python"*.
   - View sequential learning modules and attached resources (PDFs, scientific code snippets, external archives).
4. Click **"Exam"**:
   - View configured MCQ questions, mark values, and verified answer keys.
5. Visit **Trainer Discovery Engine** (`/competencies/discovery/`):
   - Select competencies (e.g. *Artificial Intelligence*, *Machine Learning*, *Python Programming*).
   - Observe how `trainer_ai` ranks at the top with a transparent breakdown of proficiency points and experience factors.

### Act 3: Employee Learning Journey, Exam & Certificate
1. Sign in as `emp_vikram` (`emp_vikram` / `Employee@12345`).
2. On the **Learner Dashboard**, see *"Applied Meteorological Data Analysis with Python"* at **66.7% progress**.
3. Click **"Resume Learning"**:
   - Navigate to Module 3 (*"Radar and Precipitation Nowcasting"*).
   - Click **"Mark as Completed"** — notice the progress bar automatically advance to **100%**!
4. Click **"Take Course Exam"**:
   - Notice the live countdown timer ticking in the top bar.
   - Answer the multiple-choice questions and submit.
   - Instantly receive server-evaluated score, percentage, and pass status.
5. Claim and View the **Accredited Certificate of Completion**:
   - Observe the recipient name, course title, unique certificate ID (`CC-2026-XXXX-XXXX`), and authorized signatories.
   - Click **"Download PDF"** to open the vector ReportLab PDF document.
6. Public Credential Verification:
   - Sign out or open an incognito window.
   - Visit `/certificates/verify/`.
   - Paste the certificate ID and click **"Verify"** to confirm tamper-proof authenticity.
