# CAPACITY CONNECT
## Digital Capacity Building & Learning Management Portal
### Smart India Hackathon 2026 | Problem Statement ID: SIH26075
**Theme:** Smart Education & Administration  
**Organization:** Ministry of Earth Sciences (MoES) / Central Organizations  
**Tagline:** *Learn. Develop. Connect. Grow.*

---

## 1. Project Overview

**Capacity Connect** is a centralized organizational capacity-building and learning management portal engineered specifically for the Ministry of Earth Sciences (MoES) and central organizations. It facilitates end-to-end talent development, transparent trainer discovery, continuous competency tracking, timed assessments, and verifiable institutional certification.

Unlike generic LMS tools, Capacity Connect is structured around organizational governance:
- **Administrative Governance:** Personnel registration approval, role assignment, institutional oversight, and downloadable PDF audit reports.
- **Trainer Discovery & Expertise Mapping:** Transparent, explainable rule-based matching engine mapping instructor competencies, proficiency levels, and scientific experience.
- **Hands-on Course Curriculum:** Multi-format learning resources (PDFs, scientific code notebooks, presentations, and external video lectures) with genuine progress tracking.
- **MCQ Assessment Engine:** Timed examinations with server-side evaluation, attempt caps, and deadline enforcement.
- **Verifiable Institutional Certification:** Automated eligibility verification and ReportLab vector PDF certificate generation with unique IDs and a public verification portal.

---

## 2. Technology Stack

- **Backend:** Python 3.13, Django 5.x (Monolithic Server-Side Rendering architecture)
- **Database:** PostgreSQL (Primary), SQLite (Supported local development fallback via environment configuration)
- **Frontend:** Django Templates, Tailwind CSS (CLI compiled), TypeScript (compiled to ES2022 modules), Chart.js, Lucide Icons
- **Document & PDF Generation:** ReportLab 5.x (Certificates & Administrative Audit Reports)
- **Development & Build Tools:** Git, npm, Tailwind CLI, TypeScript compiler (`tsc`)

---

## 3. Project Directory Structure

```text
Capacity-Connect/
│
├── manage.py                     # Django management utility
├── requirements.txt              # Python dependencies
├── package.json                  # Frontend Tailwind & TypeScript scripts
├── tsconfig.json                 # TypeScript compiler configuration
├── tailwind.config.js            # Design system color palette & typography
├── .env.example                  # Environment template
├── .gitignore                    # Version control exclusions
│
├── config/                       # Core Django project configuration
│   ├── settings.py               # Modular settings with env database switch
│   ├── urls.py                   # Master URL routing & custom error handlers
│   ├── wsgi.py                   # WSGI entrypoint
│   └── asgi.py                   # ASGI entrypoint
│
├── apps/                         # Modular Django applications
│   ├── core/                     # Landing page, context processors, seed_demo command
│   ├── accounts/                 # Custom User model, approval workflow, profiles, RBAC
│   ├── courses/                  # Course catalog, modules, resources, genuine progress
│   ├── assessments/              # Timed MCQ engine, question bank, server-side scoring
│   ├── competencies/             # Competency library, explainable recommendation engine
│   ├── certificates/             # Automatic eligibility, ReportLab PDF, public verification
│   ├── analytics/                # Role-based dashboards, Chart.js, executive PDF reports
│   └── communications/           # Announcements, in-app notifications, knowledge library
│
├── templates/                    # Server-rendered DTL templates
│   ├── base.html                 # Main layout shell with navbar & responsive sidebar
│   ├── components/               # Navbar, sidebar, toasts, footer partials
│   ├── public/                   # Landing page & About page
│   ├── registration/             # Login, register, pending approval, profile
│   ├── admin_dashboard/          # Admin KPIs, charts, user directory
│   ├── trainer/                  # Trainer workspace, course creation, exam builder
│   ├── employee/                 # Learner dashboard & skill matrix
│   ├── courses/                  # Catalog, course detail, learning portal, feedback
│   ├── assessments/              # Instructions, active exam screen, result breakdown
│   ├── certificates/             # HTML certificate preview, public verification
│   ├── communications/           # Circulars, notifications, centralized knowledge base
│   └── errors/                   # Custom 400, 403, 404, 500 error pages
│
├── static/
│   ├── src/                      # Source CSS and TypeScript
│   └── dist/                     # Compiled production CSS and JS assets
│
├── media/                        # User uploads, course thumbnails, certificates
└── docs/                         # Technical documentation & presentation guides
```

---

## 4. Installation & Local Setup

### Prerequisites
- Python 3.10+ (Verified on Python 3.13)
- Node.js 18+ and npm
- PostgreSQL 14+ (or use the built-in SQLite development fallback)
- Git

### Step-by-Step Instructions

1. **Clone the Repository & Navigate to Directory:**
   ```powershell
   git clone <repository-url>
   cd Capacity-Connect
   ```

2. **Set Up Python Virtual Environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Python Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Install Frontend Dependencies & Compile Assets:**
   ```powershell
   npm install
   npm run build
   ```
   *(Compiles Tailwind CSS to `static/dist/css/output.css` and TypeScript to `static/dist/js/app.js`)*

5. **Configure Environment Variables:**
   Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
   *(To use PostgreSQL, set `DB_ENGINE=django.db.backends.postgresql` and supply your database credentials; by default it operates with the SQLite fallback)*

6. **Apply Database Migrations:**
   ```powershell
   python manage.py migrate
   ```

7. **Seed the Comprehensive Demo Dataset:**
   ```powershell
   python manage.py seed_demo
   ```

8. **Start the Development Server:**
   ```powershell
   python manage.py runserver
   ```
   Open your browser at `http://127.0.0.1:8000/`.

---

## 5. Seed Demo Credentials

| Role | Username | Password | Organization / Notes |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `Admin@12345` | Ministry of Earth Sciences Executive / IMD |
| **Trainer (AI / HPC)** | `trainer_ai` | `Trainer@12345` | NCMRWF (Deep Learning & NWP) |
| **Trainer (Climate)** | `trainer_climate` | `Trainer@12345` | IITM (Coupled Climate Models) |
| **Trainer (GIS)** | `trainer_gis` | `Trainer@12345` | INCOIS (Satellite Oceanography) |
| **Employee (Completed)**| `emp_arun` | `Employee@12345` | IMD (Has verified certificate) |
| **Employee (In Progress)**| `emp_vikram` | `Employee@12345` | NCMRWF (66.7% progress on Applied Met) |
| **Employee (Certified)**| `emp_priya` | `Employee@12345` | INCOIS (Coastal Hazard Mapping certified) |

---

## 6. Running the Automated Test Suite

To run all 12 automated unit and integration tests across accounts, courses, assessments, competencies, and certificates:

```powershell
python manage.py test apps.accounts.tests apps.courses.tests apps.assessments.tests apps.competencies.tests apps.certificates.tests
```

All 12 tests execute and pass without errors.

---

## 7. Documentation Index

- [`docs/ARCHITECTURE.md`](file:///c:/Users/neela/OneDrive/Desktop/Capacity-Connect/docs/ARCHITECTURE.md): Architectural design, layer responsibilities, and request flow.
- [`docs/ERD.md`](file:///c:/Users/neela/OneDrive/Desktop/Capacity-Connect/docs/ERD.md): Database schema and Mermaid Entity-Relationship diagram.
- [`docs/IMPLEMENTATION_PLAN.md`](file:///c:/Users/neela/OneDrive/Desktop/Capacity-Connect/docs/IMPLEMENTATION_PLAN.md): Milestone progress and deliverable tracking.
- [`docs/SIH_REQUIREMENTS_TRACEABILITY.md`](file:///c:/Users/neela/OneDrive/Desktop/Capacity-Connect/docs/SIH_REQUIREMENTS_TRACEABILITY.md): Matrix mapping all SIH26075 requirements to code and tests.
- [`docs/DJANGO_SYLLABUS_MAPPING.md`](file:///c:/Users/neela/OneDrive/Desktop/Capacity-Connect/docs/DJANGO_SYLLABUS_MAPPING.md): Academic mapping across all six units of the Django syllabus.
- [`docs/DEMO_GUIDE.md`](file:///c:/Users/neela/OneDrive/Desktop/Capacity-Connect/docs/DEMO_GUIDE.md): 3-Act Judge Demonstration script.

---

## 8. License & Acknowledgments

Developed for the **Smart India Hackathon 2026 (SIH26075)** in alignment with the institutional capacity building mandate of the **Ministry of Earth Sciences (MoES)**, Government of India.

