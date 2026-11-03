# Django Syllabus Implementation Mapping
## Academic & Technical Traceability Across Six Units

This document maps all six core units of the advanced Django curriculum to the concrete architectural implementation in **Capacity Connect**.

---

### UNIT I — INTRODUCTION TO DJANGO
- **Python & Virtual Environment Setup:** Configured with Python 3.13 virtual environment (`venv/`), dependencies isolated via `requirements.txt`.
- **Project Initialization & Architecture:** `manage.py`, `config/settings.py`, `config/urls.py`, `config/wsgi.py`, `config/asgi.py`.
- **Modular App Architecture:** Decoupled apps registered in `INSTALLED_APPS`: `apps.core`, `apps.accounts`, `apps.courses`, `apps.assessments`, `apps.competencies`, `apps.certificates`, `apps.analytics`, `apps.communications`.
- **CLI Utilities:** Custom management command `python manage.py seed_demo` implemented in `apps/core/management/commands/seed_demo.py`.

---

### UNIT II — VIEWS AND URLS
- **Function-Based Views with Granular Decorators:** `apps/accounts/views.py` (`login_view`, `register_view`), `apps/courses/views.py` (`course_learn_view`, `module_complete_view`), `apps/assessments/views.py` (`assessment_take_view`).
- **URL Configuration & Namespacing:** App-level routing with `app_name = ...` in `apps/accounts/urls.py`, `apps/courses/urls.py`, `apps/competencies/urls.py`, `apps/assessments/urls.py`, `apps/certificates/urls.py`, `apps/analytics/urls.py`, `apps/communications/urls.py`, included hierarchically in `config/urls.py`.
- **Request & Response Objects:** HTTP GET, POST handling, JSON serialization for Chart.js, binary PDF stream responses via `HttpResponse(content_type='application/pdf')` in `apps/certificates/views.py` and `apps/analytics/views.py`.
- **Dynamic Parameters & Slugs:** `<slug:slug>` parameters in `courses/urls.py`, `<int:user_id>` in `accounts/urls.py`, `<str:cert_id>` in `certificates/urls.py`.
- **Error Handlers:** `handler400`, `handler403`, `handler404`, `handler500` routed to custom branded error views in `apps/core/views.py`.

---

### UNIT III — TEMPLATES, DEBUGGING AND TESTING
- **Django Template Language (DTL):** Master template inheritance with `templates/base.html`, reusable template partials (`components/navbar.html`, `components/sidebar.html`, `components/messages.html`, `components/footer.html`).
- **Context Processors:** Global request context injection via `apps.core.context_processors.portal_context` providing real-time notification counters and circulars.
- **Static & Media Asset Handling:** Pipeline using `STATICFILES_DIRS`, `MEDIA_ROOT`, compiled Tailwind CSS (`static/dist/css/output.css`), and compiled TypeScript modules (`static/dist/js/app.js`).
- **Automated Testing Suite:** 12 automated unit and integration tests passing across:
  - `apps/accounts/tests.py` (role tests, unapproved redirect, admin approval)
  - `apps/courses/tests.py` (duplicate enrollment prevention, genuine progress calculation)
  - `apps/assessments/tests.py` (backend score calculation, attempt limits)
  - `apps/competencies/tests.py` (recommendation engine algorithm)
  - `apps/certificates/tests.py` (eligibility rules, ReportLab PDF generation, public verification)

---

### UNIT IV — FORMS & MODELFORMS
- **ModelForms with Server-Side Validation:** `apps/accounts/forms.py` (`UserRegistrationForm`, `EmployeeProfileForm`, `TrainerProfileForm`), `apps/courses/forms.py` (`CourseForm`, `CourseModuleForm`), `apps/assessments/forms.py` (`AssessmentForm`, `QuestionForm`), `apps/competencies/forms.py` (`TrainerCompetencyForm`).
- **CSRF Token Protection:** Enforced across all forms via `{% csrf_token %}` with Django's `CsrfViewMiddleware`.
- **Input Sanitization & Custom Clean Methods:** Password matching and unauthorized self-registration privilege escalation prevention in `clean_role()` and `clean()` in `apps/accounts/forms.py`.
- **Post/Redirect/Get (PRG) Pattern:** Applied consistently across registration, enrollments, module completions, assessment attempts, and profile modifications.

---

### UNIT V — MODELS, MIGRATIONS AND ADMIN
- **Relational Architecture:** PostgreSQL primary database with standard relational constraints:
  - `OneToOneField` (`User` <-> `EmployeeProfile`, `Enrollment` <-> `Certificate`, `Course` <-> `Assessment`)
  - `ForeignKey` (`CourseModule` -> `Course`, `LearningResource` -> `CourseModule`, `User` -> `Department`)
  - `ManyToManyField` equivalents via intermediary models (`TrainerCompetency`, `EmployeeCompetency`, `CourseCompetency`)
  - `UniqueConstraint` on `('employee', 'course')`, `('enrollment', 'module')`, `('assessment', 'employee', 'attempt_number')`.
- **Django Migrations:** Discrete, versioned migrations across all 8 apps.
- **Django Admin Customization:** Comprehensive admin integration in `apps/*/admin.py` with `list_display`, `list_filter`, `search_fields`, `prepopulated_fields`, and `inlines` (`ModuleInline`, `ResourceInline`, `OptionInline`).

---

### UNIT VI — COOKIES, SESSIONS AND AUTHENTICATION
- **Custom User Model:** Subclassed `AbstractUser` before initial migration (`accounts.User`) with custom `Role` and `ApprovalStatus` enums.
- **Authentication & Security:** Native password hashing with PBKDF2/SHA256, session authentication, cookie expiry, login and logout workflows.
- **Role-Based Authorization Decorators:** Custom decorators in `apps/accounts/decorators.py` enforcing authentication, administrative approval, and granular role permissions (`@admin_required`, `@trainer_required`, `@employee_required`).

