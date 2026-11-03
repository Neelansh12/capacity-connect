# SIH Requirements Traceability Matrix (RTM)
## Smart India Hackathon 2026 | Problem Statement ID: SIH26075
### Digital Capacity Building & Learning Management Portal

| Req ID | Requirement Description | Implementation Component / File | Verification & Test Coverage |
| :--- | :--- | :--- | :--- |
| **REQ-01** | Employee Training & Professional Development | `apps/courses/views.py` (`course_learn_view`, `module_complete_view`) | `test_genuine_progress_calculation` in `apps.courses.tests` |
| **REQ-02** | Competency Assessment & Skill Development | `apps/competencies/models.py`, `apps/competencies/views.py` | `test_explainable_recommendation_ranking` in `apps.competencies.tests` |
| **REQ-03** | Centralized Learning Resource Management | `apps/communications/models.py` (`TrainerResource`), `templates/communications/resource_library.html` | Verified manual upload & download, `seed_demo` dataset |
| **REQ-04** | Trainer Discovery & Expertise Mapping | `apps/competencies/engine.py` (`recommend_trainers_for_competencies`), `templates/competencies/trainer_discovery.html` | `test_explainable_recommendation_ranking` |
| **REQ-05** | Course Creation & Delivery | `apps/courses/views.py` (`trainer_course_create_view`, `trainer_module_manage_view`) | Tested course CRUD and module sequencing |
| **REQ-06** | Learning Progress & Performance Monitoring | `apps/courses/models.py` (`calculate_progress`), `apps/analytics/views.py` (`trainer_dashboard_view`) | `test_genuine_progress_calculation` |
| **REQ-07** | Knowledge Sharing Across Departments | `apps/communications/models.py` (`Announcement`, `TrainerResource`, `CourseFeedback`) | `seed_demo` multi-institute dataset across IMD, INCOIS, IITM, NCMRWF, NIOT |
| **REQ-08** | Certificate Generation & Institutional Reporting | `apps/certificates/services.py`, `apps/analytics/reports.py` (ReportLab) | `test_certificate_eligibility_enforcement`, `test_certificate_issuance_and_pdf_generation` |
| **REQ-09** | Role-Based Access Control & User Approval | `apps/accounts/models.py`, `apps/accounts/decorators.py` | `test_unapproved_user_redirect`, `test_role_based_access_restriction` |
| **REQ-10** | MCQ Assessment Engine | `apps/assessments/models.py`, `apps/assessments/views.py` | `test_assessment_server_side_evaluation_and_pass`, `test_assessment_attempt_limit_enforcement` |
| **REQ-11** | Public Certificate Verification | `apps/certificates/views.py` (`certificate_verify_view`), `templates/certificates/verify.html` | `test_public_certificate_verification` |
| **REQ-12** | Database-Backed Chart.js Analytics | `apps/analytics/views.py` (`admin_dashboard_view`), Chart.js renderers | Verified no hardcoded chart statistics |
