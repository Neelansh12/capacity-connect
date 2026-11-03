# Capacity Connect — Application Architecture
## SIH 2026 | Problem Statement ID: SIH26075

Capacity Connect is developed as an enterprise **monolithic web application utilizing Django Server-Side Rendering (SSR)**, compiled Tailwind CSS, TypeScript modules, and PostgreSQL.

---

## 1. Monolithic SSR Architectural Pattern

The platform strictly avoids fragile detached frontends or distributed microservice overheads, providing zero-latency transactional consistency across course progress, assessment submissions, and certificate issuance:

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT BROWSER                                    |
|   (HTML5, Compiled Tailwind CSS, TypeScript Bundles, Chart.js, Lucide Icons)       |
+------------------------------------------+----------------------------------------+
                                           | HTTP Requests / CSRF Protected
                                           v
+-----------------------------------------------------------------------------------+
|                              DJANGO MONOLITHIC SERVER                             |
|                                                                                   |
|  +--------------------+  +--------------------+  +-----------------------------+  |
|  | config.urls / WSGI |  | Middleware Stack   |  | Authentication / Sessions   |  |
|  | & Routing Router   |  | (CSRF, Auth, Sec)  |  | (Role-Based Permissions)    |  |
|  +---------+----------+  +---------+----------+  +--------------+--------------+  |
|            |                       |                            |                 |
|            v                       v                            v                 |
|  +-----------------------------------------------------------------------------+  |
|  |                             DJANGO APPLICATIONS                             |  |
|  |  [apps.core]          - Landing page, portal branding, global context       |  |
|  |  [apps.accounts]      - User approval workflow, AbstractUser, profiles     |  |
|  |  [apps.courses]       - Course CRUD, modules, resources, progress tracking |  |
|  |  [apps.assessments]   - Timed MCQ engine, backend evaluation, score logic   |  |
|  |  [apps.competencies]  - Competency framework, rule-based recommendation    |  |
|  |  [apps.certificates]  - Automatic eligibility, ReportLab PDF, verification |  |
|  |  [apps.analytics]     - Role-based dashboards, Chart.js, PDF audits        |  |
|  |  [apps.communications]- Announcements, notifications, feedback, library    |  |
|  +-------------------------------------+---------------------------------------+  |
|                                        |                                          |
|                                        v                                          |
|  +-----------------------------------------------------------------------------+  |
|  |                     DJANGO ORM / RELATIONAL DATABASE                        |  |
|  |              PostgreSQL (Primary) / SQLite (Fallback)                       |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Layer Responsibilities

### Core (`apps.core`)
- Hosts the public landing page, organizational identity, and dynamic context processors (`portal_context`) surfacing unread notifications and circular alerts.
- Provides unified HTTP 400, 403, 404, and 500 error handlers.

### Accounts (`apps.accounts`)
- Implements custom `User(AbstractUser)` with strictly enforced role choices (`ADMIN`, `TRAINER`, `EMPLOYEE`) and approval statuses (`PENDING`, `APPROVED`, `REJECTED`).
- Server-side role protection prevents privilege escalation.
- Custom decorators: `@approval_required`, `@admin_required`, `@trainer_required`, `@employee_required`.

### Courses & Learning (`apps.courses`)
- Models courses, sequential modules, and learning resources (video lectures, scientific PDFs, PPT slide decks, and external references).
- Employs genuine transactional progress tracking via `Enrollment` and `ModuleProgress` records.

### Competency & Trainer Discovery (`apps.competencies`)
- Houses an institutional competency library with domains (Scientific, Technical, Managerial, Operational).
- Transparent, explainable rule-based recommendation engine (`apps.competencies.engine`) computing normalized match scores based on proficiency points, practical years of experience, and platform courses delivered.

### Assessments (`apps.assessments`)
- Timed MCQ examination engine.
- Enforces time limits, maximum attempt caps, and backend-only mark evaluation.

### Certificates (`apps.certificates`)
- Automatically assesses completion eligibility (100% module progress + passing exam score).
- Generates high-resolution landscape PDF certificates with ReportLab.
- Provides a public verification endpoint (`/certificates/verify/?id=...`).

### Analytics & Reports (`apps.analytics`)
- Aggregates database counts and renders real Chart.js analytics across roles.
- Employs ReportLab to compile institutional capacity audit PDF reports on demand.

