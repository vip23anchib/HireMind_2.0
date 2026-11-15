# HIREMIND ATS — SYSTEM ARCHITECTURE & CODEBASE AUDIT

**Author:** Staff Software Engineer & Solutions Architect  
**Project:** HireMind ATS 2.0 Modernization  
**Repository:** `https://github.com/vip23anchib/HireMind_2.0`  
**Date:** November 2026  
**Document Version:** 1.0.0  
**Status:** Milestone 1 Complete — Codebase Audit & Target Architecture Specification  

---

## 1. Executive Summary & Codebase Audit

HireMind is an Applicant Tracking System (ATS) built with Django that empowers recruiters to manage vacancies, accept public job applications, parse resumes, match candidates against job requirements using skill/experience extraction algorithms, track candidate status transitions, and visualize hiring metrics.

Rather than being a greenfield project or a superficial prototype, HireMind contains real domain logic:
1. **Resume Intelligence**: Text extraction from PDF documents using `pypdf`, skill extraction via normalized synonym dictionaries, and regex-based experience extraction.
2. **ATS Match Scoring**: Deterministic matching of candidate skills and required job skills yielding percentage match scores.
3. **Recruiter Search Engine**: Multi-skill candidate query resolution supporting both boolean `AND` (set intersection) and `OR` (union) semantics with experience thresholds.
4. **Recruitment Lifecycle & Audit Trail**: Multi-stage application status workflow (`Applied`, `Under Review`, `Shortlisted`, `Interview Scheduled`, `Rejected`, `Hired`) with historical action logging.
5. **Analytics**: Skill demand aggregation and experience distribution plotted using Plotly.

### Current Stack Summary
- **Backend**: Python 3.12.10, Django 6.0.6, `dj-database-url` 2.1.0, `whitenoise` 6.12.0, `gunicorn` 23.0.0.
- **Data Persistence**: SQLite (local dev), PostgreSQL configured in settings via `dj_database_url`.
- **Parsing & Math**: `pypdf` 6.13.2, `pdfreader` 0.1.15, `numpy` 2.4.6.
- **Frontend / UI**: Django Templates (DTL), Vanilla JavaScript (inline DOM scripts), Custom CSS files (`globalCSSfiles/`).
- **Data Visualization**: `plotly` 6.8.0 (offline HTML div injection).
- **Authentication**: Built-in Django session authentication with custom `login_view` and `logout_view`.

---

## 2. Current Architecture & Module Breakdown

The existing project is structured as a Django project (`my_project`) orchestrating four internal applications:

```
HireMindPro/
├── my_project/               # Core Django configuration (settings, urls, wsgi, asgi)
├── applicants/               # Candidates, resumes, skills, applications, activity logs
│   ├── management/commands/  # Management commands (generate_candidates, benchmark_search)
│   ├── migrations/           # Database migrations (0001 - 0005)
│   ├── static/               # App-level static CSS
│   ├── templates/            # HTML templates for forms, tables, search, dashboard
│   ├── views/                # Split view package: form_views.py, main_views.py, form_helper.py
│   ├── models.py             # UserData, Document, Skill, UserSkill, Application, ActivityLog
│   ├── urls.py               # Candidate, application, search, and dashboard routes
│   └── utils.py              # Activity logging helper
├── jobs/                     # Job postings, careers portal, application entry
│   ├── migrations/           # Database migrations (0001)
│   ├── static/               # App-level static CSS
│   ├── templates/            # HTML templates for careers, job details, job management
│   ├── models.py             # Job model
│   ├── urls.py               # Careers and job management routes
│   └── views.py              # Public job views and recruiter CRUD views
├── members/                  # Recruiter team management and master page layouts
│   ├── migrations/           # Database migrations (0001 - 0002)
│   ├── static/               # Static images (logo) and styles
│   ├── templates/            # master.html, public_master.html, landing_page.html, all_members.html
│   ├── models.py             # Member model (OneToOne with auth.User)
│   ├── forms.py              # MemberForm (User + Member creation)
│   ├── urls.py               # Member listing and onboarding routes
│   └── views.py              # Member management views
├── relationships/            # Sandbox/experimentation app (Authors, Books, Students, Courses)
├── globalCSSfiles/           # Monolithic static stylesheet collection (25 CSS files)
├── media/uploads/            # Sample uploaded resumes (.pdf)
├── requirements.txt          # Python dependencies
├── Procfile & build.sh       # Render deployment scripts
└── backup.json / sqlite_backup.json # Fixture datasets (100k benchmarks & 334 live records)
```

### Module Responsibilities

| Module | Core Responsibility | Key Models | Key Views |
| :--- | :--- | :--- | :--- |
| **`applicants`** | Candidate profiles, resume ingestion, skill extraction, application lifecycle, activity tracking | `UserData`, `Document`, `Skill`, `UserSkill`, `Application`, `ActivityLog` | `form`, `applications_list`, `update_application_status`, `search_candidates`, `candidate_profile`, `ats_dashboard`, `home_page`, `logs` |
| **`jobs`** | Vacancy publishing, public job descriptions, candidate application entry, job status toggling | `Job` | `careers`, `job_detail`, `apply_job`, `manage_jobs`, `create_job`, `edit_job`, `toggle_job_status` |
| **`members`** | Internal recruitment team members, role assignments, system user onboarding | `Member` | `landing_page`, `members`, `details`, `add_member` |
| **`relationships`** | Experimental sandbox created for relational database query testing | `Author`, `Book`, `Course`, `Student`, etc. | `search_candidates_index` |

---

## 3. Existing Data Model & Entity Relationships

```mermaid
erDiagram
    auth_User ||--o| Member : "profile for"
    auth_User ||--o{ UserData : "submitted by"
    auth_User ||--o{ Document : "uploaded by"
    auth_User ||--o{ ActivityLog : "performed by"

    Job ||--o{ Application : "receives"
    Job }|--|{ Skill : "requires (required_skills)"

    UserData ||--o{ Application : "submits"
    UserData ||--o{ Document : "owns"
    UserData ||--o{ UserSkill : "has"
    UserData ||--o{ ActivityLog : "subject of"

    Skill ||--o{ UserSkill : "assigned in"

    Member {
        int id PK
        int user_id FK
        string firstname
        string lastname
        string middlename
        string phone
        date joined_date
        string role "Admin, HR Manager, Recruiter"
    }

    Job {
        int id PK
        string title
        string slug UK
        string department
        string location
        string job_type "Full Time, Internship, Contract"
        text description
        text requirements
        text responsibilities
        int experience_required
        bool is_active
        datetime created_at
    }

    UserData {
        int id PK
        int user_id FK
        string name "db_index=True"
        string email
        string gender
        string phone_number
        string country
        text cover_letter
        string linkedin_url
        string portfolio_url
    }

    Skill {
        int id PK
        string name UK
    }

    UserSkill {
        int id PK
        int user_data_id FK
        int skill_id FK
        int years_of_experience
    }

    Document {
        int id PK
        int user_id FK
        int user_data_id FK
        text pdf_text
        text additional_info
        text experience_info
        string file "uploads/"
        datetime uploaded_at
    }

    Application {
        int id PK
        int candidate_id FK
        int job_id FK
        string status "Applied, Under Review, Shortlisted, Interview Scheduled, Rejected, Hired"
        float ats_score
        datetime applied_at
    }

    ActivityLog {
        int id PK
        int candidate_id FK
        int performed_by_id FK
        string action
        datetime created_at
    }
```

### Relational Dynamics:
- **`UserData` ↔ `Skill`**: Many-to-many relationship mediated through explicit through-model `UserSkill`, capturing `years_of_experience` per skill.
- **`Job` ↔ `Skill`**: Direct Django ManyToManyField (`Job.required_skills`).
- **`Application`**: Junction between `UserData` (candidate) and `Job`, with an ATS percentage score and recruiting workflow status.
- **`Document`**: Linked 1-to-many to `UserData`, storing the uploaded resume binary path and extracted text columns.

---

## 4. Existing Workflows & Request Lifecycles

### 4.1 Candidate Public Application Workflow
```mermaid
sequenceDiagram
    autonumber
    actor Candidate as Public Candidate
    participant Browser
    participant Django as Django Server
    participant Helper as form_helper.py
    participant DB as Database (SQLite/Postgres)
    participant Storage as Media Storage

    Candidate->>Browser: Navigate to /careers/
    Browser->>Django: GET /careers/
    Django->>DB: Query Job.objects.filter(is_active=True)
    Django-->>Browser: Render careers.html
    Candidate->>Browser: Select Job -> Click "Apply Now"
    Browser->>Django: GET /careers/<slug>/apply/
    Django-->>Browser: Render apply_job.html
    Candidate->>Browser: Fill Details + Select PDF Resume -> Submit
    Browser->>Django: POST /registration/ (multipart/form-data)
    Note over Django,Helper: Synchronous In-Request Processing
    Django->>Storage: Save uploaded PDF file to media/uploads/
    Django->>Helper: extract_pdf_text(file)
    Helper-->>Django: Return raw text
    Django->>Helper: extract_skill_experience(raw_text)
    Django->>Helper: extract_skills_from_database(raw_text)
    Django->>DB: Create UserData record
    Django->>DB: Create Document record (pdf_text, metadata)
    loop For each detected skill
        Django->>DB: Get or create Skill
        Django->>DB: Create/Update UserSkill (years_of_experience)
    end
    Note over Django: Calculate ATS Score: (matched_skills / job_skills) * 100
    Django->>DB: Create Application(candidate, job, ats_score)
    Django->>DB: Create ActivityLog(candidate, "Applied with ATS score ...")
    Django-->>Browser: 302 Redirect to /success/
    Browser-->>Candidate: Display Success Screen
```

### 4.2 Recruiter Pipeline Management Workflow
```mermaid
sequenceDiagram
    autonumber
    actor Recruiter
    participant Browser
    participant Django as Django Server
    participant DB as Database

    Recruiter->>Browser: Submit Login credentials
    Browser->>Django: POST /login/
    Django->>DB: authenticate(username, password)
    Django-->>Browser: Set session cookie & redirect to /home-page/
    Recruiter->>Browser: Navigate to Applications (/applications/)
    Browser->>Django: GET /applications/?job=1&status=Applied&sort=high_ats
    Django->>DB: Application.objects.select_related('candidate', 'job').filter(...).order_by('-ats_score')
    Django-->>Browser: Render applications_list.html
    Recruiter->>Browser: Change Candidate status to "Shortlisted"
    Browser->>Django: POST /applications/<id>/status/
    Django->>DB: Update Application status = 'Shortlisted'
    Django->>DB: Create ActivityLog(candidate, performed_by=request.user, "Candidate shortlisted")
    Django-->>Browser: 302 Redirect to /applications/
```

---

## 5. Technical Deep-Dives into Business Logic

### 5.1 Resume Intelligence Engine (`form_helper.py` & `form_views.py`)
1. **PDF Text Extraction**: Uses `pypdf.PdfReader` to iterate through pages and concatenate string buffers:
   ```python
   reader = PdfReader(pdf_file)
   text = "".join(page.extract_text() or "" for page in reader.pages)
   ```
2. **Resume Classification Heuristic**: `is_resume(text)` scores presence of 8 anchor keywords (`skills`, `experience`, `education`, `projects`, `certifications`, `linkedin`, `resume`, `internship`). A document requires $\ge 3$ hits to pass.
3. **Skill Normalization Dictionary**: `SKILL_SYNONYMS` maps over 40 variations (e.g., `'reactjs'`, `'react.js'`, `'react native'` $\to$ `'React.js'`, `'dj'`, `'django rest framework'` $\to$ `'Django REST Framework'`).
4. **Skill Detection**: `extract_skills_from_database(text)` uses word boundary regex:
   ```python
   pattern = r'\b' + re.escape(synonym.lower()) + r'\b'
   ```
5. **Skill-Specific Experience Regex**:
   `r'([A-Za-z0-9.+# ]+?)\s*-\s*(\d+)\s+years'` and `r'([A-Za-z0-9.+# ]+?)\s*\(\s*(\d+)\s+years?\s*\)'`.
6. **General Information Extraction**:
   - Email regex: `r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'`
   - Phone regex: `r'\+?\d[\d\s-]{8,15}'`
   - Total experience: `r'(\d+)\s*(?:years?|yrs?)'`

### 5.2 Recruiter Candidate Search Engine (`main_views.py`)
Recruiters search across candidates using a composite parameter set: `skill`, `experience`, and `search_type` (`"and"` vs `"or"`):
- **OR Branch**: Chains `Q(skill__name__iexact=skill_name)` with the bitwise OR operator (`|=`), finding candidates matching *any* requested skill.
- **AND Branch**: Performs set intersection on candidate IDs:
  ```python
  for skill_name in skills_list:
      skill_candidates = set(UserSkill.objects.filter(skill__name__iexact=skill_name).values_list('user_data_id', flat=True))
      candidate_ids = skill_candidates if candidate_ids is None else candidate_ids & skill_candidates
  ```
- **Scoring & Missing Skills**: Computes matched skill ratio against requested skills and identifies missing skill deltas:
  $$\text{Score} = \text{round}\left(\frac{\text{len}(\text{matched\_skills})}{\text{len}(\text{requested\_skills})} \times 100\right)$$
  $$\text{Missing Skills} = \text{set}(\text{requested\_skills}) - \text{set}(\text{candidate\_skills})$$

### 5.3 ATS Match Scoring Engine (`form_views.py`)
When an application is linked to a vacancy:
$$\text{ATS Score} = \begin{cases} \text{round}\left(\frac{|\text{CandidateSkills} \cap \text{JobSkills}|}{|\text{JobSkills}|} \times 100, 2\right) & \text{if } |\text{JobSkills}| > 0 \\ 0 & \text{otherwise} \end{cases}$$

### 5.4 Analytics Engine (`main_views.py`)
- Evaluates aggregate candidate metrics (`total_candidates`, `total_skills`, `total_user_skills`).
- Aggregates top skills across candidate resumes:
  ```python
  UserSkill.objects.values('skill__name').annotate(total=Count('skill')).order_by('-total')
  ```
- Aggregates average experience by technology:
  ```python
  UserSkill.objects.values('skill__name').annotate(avg_years=Avg('years_of_experience')).order_by('-avg_years')
  ```
- Renders Plotly offline bar graphs into standalone HTML strings (`plot(fig, output_type='div')`) embedded in the Django template.

---

## 6. Comprehensive Technical Debt & Bug Audit

During our static analysis and live test runs, the following bugs, technical debt, and security vulnerabilities were identified in the existing codebase:

### Verified Code Bugs

| ID | Location | Issue Description | Consequence |
| :--- | :--- | :--- | :--- |
| **BUG-01** | `jobs/views.py:121-154` | `create_job` creates a Job without assigning it to a variable, but line 152 tries to access `job.title` in `ActivityLog`. | `UnboundLocalError: local variable 'job' referenced before assignment` on submitting the Create Job form. |
| **BUG-02** | `applicants/views/main_views.py:445` | `search_candidates` references `requested_count` on line 445 without defining it in scope (it was supposed to be `len(skills_list)`). | `UnboundLocalError: local variable 'requested_count' referenced before assignment` whenever a recruiter searches candidates by skill. |
| **BUG-03** | `applicants/utils.py:6-8` | `create_log` calls `ActivityLog.objects.create(user=user, action=action)`. However, Migration 0004 renamed `user` to `performed_by`. | `TypeError: ActivityLog() got an unexpected keyword argument 'user'` whenever `create_log()` is invoked. |
| **BUG-04** | `applicants/views/form_helper.py:221` | `extract_skills` iterates `for skill in SKILLS:`, but `SKILLS` is not defined (the list is named `SKILL_DATABASE`). | `NameError: name 'SKILLS' is not defined` if `extract_skills` is called. |
| **BUG-05** | `applicants/views/main_views.py:222, 262` | `form_submit` and `ajax_data` try to populate `message` and `skills` directly on `UserData`, but those columns do not exist on `UserData`. | `FieldError / OperationalError` if legacy AJAX form endpoints are called. |

### Architectural Bottlenecks & Anti-Patterns

1. **Synchronous In-Request PDF Processing**:
   - `applicants/views/form_views.py:form` executes PDF parsing, multiple regex searches, dictionary lookups, skill creation, and ATS scoring synchronously inside the HTTP POST request.
   - *Impact*: Under multi-page resume uploads or concurrent candidate traffic, worker threads block for several seconds, leading to HTTP 504 Gateway Timeouts.
2. **N+1 Database Query in Candidate Listing**:
   - `applicants/views/main_views.py:161-172`:
     ```python
     for user in users:
         latest_application = user.applications.order_by('-applied_at').first()
     ```
   - *Impact*: Executes an extra SQL query for every candidate rendered in `form_data.html`.
3. **Hardcoded Database Credentials**:
   - `my_project/settings.py:88`: Hardcoded default fallback `postgresql://postgres:231105@localhost:5432/hiremind_db`. If Postgres is not running locally on that exact password, Django crashes immediately without an override.
4. **Hardcoded Django `SECRET_KEY`**:
   - `SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-itob=9)_bekhucdubl!savlxs#q5iua+43ej)q_sh@yo+g32^*')` is exposed in source code.
5. **Overlapping and Confusing URL Paths**:
   - `path('', landing_page)`, `path('dashboard/', include('members.urls'))`, `path('landing-dashboard/', include('members.urls'))`, `path('', include('applicants.urls'))`. Both `''` and `dashboard/` mount overlapping paths.
6. **Sandbox App Left in Production**:
   - `relationships` app contains tutorial models (`Author`, `Book`, `Course`, `Student`) completely unrelated to recruitment.
7. **Unprotected File Storage**:
   - Resume files stored in `media/uploads/` are exposed as static files without authorization checks. Any user can enumerate and download candidate resumes by URL.
8. **Lack of Upload Validation**:
   - No validation on MIME type (magic bytes), file dimensions, or payload size limits; only checks `.name.endswith('.pdf')`.
9. **Monolithic CSS & Inline Scripts**:
   - Over 25 separate CSS files in `globalCSSfiles/` without bundling, minification, or modern CSS architecture.

---

## 7. Target Production Architecture

The modernized HireMind 2.0 architecture decouples presentation from business logic and background processing:

```
+-----------------------------------------------------------------------------------+
|                                  CLIENT LAYER                                     |
|  React 18 + TypeScript + Vite SPA (Public Portal + Protected Recruiter Dashboard) |
+----------------------------------------+------------------------------------------+
                                         | JSON / REST (Axios / TanStack Query)
                                         v
+-----------------------------------------------------------------------------------+
|                                   NGINX REVERSE PROXY                             |
|  - TLS Termination    - Static Asset Caching    - Security Headers    - Rate Limit|
+-------------------+-----------------------------------+---------------------------+
                    | /api/v1/ and /media/ (protected)  | /
                    v                                   v
+---------------------------------------+   +---------------------------------------+
|          GUNICORN (WSGI)              |   |          VITE BUILD ASSETS            |
|       Django REST Framework           |   |       HTML / JS / CSS Bundles         |
+-------------------+-------------------+   +---------------------------------------+
                    |
      +-------------+-------------+-----------------------+
      |                           |                       |
      v                           v                       v
+---------------+       +-------------------+   +-------------------+
|  POSTGRESQL   |       |   REDIS (BROKER   |   |   MEDIA STORAGE   |
|   DATABASE    |       |   & CACHE STORE)  |   |   (Protected Local|
| (ACID / Index)|       |                   |   |    or S3 Bucket)  |
+---------------+       +---------+---------+   +-------------------+
                                  |
                                  v
                        +-------------------+
                        |   CELERY WORKER   |
                        | - PDF Parsing     |
                        | - Skill Extract   |
                        | - Experience Calc |
                        | - ATS Matching    |
                        +-------------------+
```

### 7.1 Backend Target Structure (Modular Monolith)

```
backend/
├── manage.py
├── config/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── celery.py
├── apps/
│   ├── accounts/          # User authentication, roles (Admin/HR Manager/Recruiter), token/session
│   ├── jobs/              # Job posting models, selectors, services, DRF ViewSets
│   ├── candidates/        # Candidate models (UserData), skill links, selectors, services
│   ├── applications/      # Application lifecycle, status history, pipeline management
│   ├── resumes/           # Resume uploads, validation, document storage, async tasks
│   ├── search/            # ATS query engine, multi-skill AND/OR filters, index optimization
│   ├── analytics/         # SQL aggregation services, caching, recruitment metrics API
│   ├── activity_logs/     # Audit trail logging service and API
│   └── common/            # Base models, custom pagination, exception handlers, permissions
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

### 7.2 Service Layer Pattern
Business logic will be moved entirely out of views into service functions:
- `apps.resumes.services.resume_parser.py`: PDF text extraction and regex parsing.
- `apps.candidates.services.matching.py`: Deterministic ATS scoring service.
- `apps.applications.services.pipeline.py`: Stage transition and audit logging.
- `apps.analytics.services.metrics.py`: Aggregate SQL statistics computation.

### 7.3 Frontend Target Structure (React + TypeScript + Vite)

```
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── api/                 # Centralized Axios client & domain endpoints
    │   ├── client.ts
    │   ├── auth.ts
    │   ├── jobs.ts
    │   ├── candidates.ts
    │   ├── applications.ts
    │   ├── resumes.ts
    │   ├── search.ts
    │   └── analytics.ts
    ├── components/          # Reusable enterprise UI component library
    │   ├── ui/              # Button, Input, Modal, Table, Badge, Dropdown, Tabs, Toast
    │   ├── layout/          # DashboardLayout, PublicLayout, Sidebar, Navbar
    │   └── feedback/        # Skeleton, EmptyState, ErrorBoundary, ConfirmDialog
    ├── context/             # AuthContext, NotificationContext
    ├── hooks/               # useAuth, useDebounce, usePagination, useToast
    ├── pages/
    │   ├── public/          # CareersPage, JobDetailPage, ApplicationSuccessPage
    │   └── recruiter/       # Dashboard, JobsList, JobCreateEdit, CandidateList,
    │                        # CandidateProfile, PipelineBoard, CandidateSearch,
    │                        # AnalyticsDashboard, AuditLogs, TeamMembers
    ├── routes/              # React Router v6 with ProtectedRoute guards
    ├── types/               # TypeScript interfaces matching backend DRF serializers
    └── utils/               # Date formatting, score color helpers, token storage
```

---

## 8. Target REST API Architecture (`/api/v1/`)

All endpoints will be versioned under `/api/v1/`, enforcing consistent JSON envelopes, HTTP status codes, and error formatting.

### 8.1 API Endpoints Specification

| Domain | Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/v1/auth/login/` | Recruiter login (session/token) | No |
| | `POST` | `/api/v1/auth/logout/` | Terminate session | Yes |
| | `GET` | `/api/v1/auth/me/` | Current user profile & role | Yes |
| **Jobs** | `GET` | `/api/v1/jobs/` | List active vacancies (public & recruiter) | Public/Yes |
| | `POST` | `/api/v1/jobs/` | Create a job posting | Yes (Recruiter/Admin) |
| | `GET` | `/api/v1/jobs/{id}/` | Retrieve job details (or by slug) | Public/Yes |
| | `PUT/PATCH` | `/api/v1/jobs/{id}/` | Update job details | Yes (Recruiter/Admin) |
| | `POST` | `/api/v1/jobs/{id}/toggle-status/` | Toggle active/inactive status | Yes (Recruiter/Admin) |
| | `GET` | `/api/v1/jobs/{id}/applications/` | List applications for this job | Yes |
| **Candidates** | `GET` | `/api/v1/candidates/` | Paginated candidate list with filters | Yes |
| | `POST` | `/api/v1/candidates/` | Register candidate (public application) | No |
| | `GET` | `/api/v1/candidates/{id}/` | Candidate full profile with skills | Yes |
| | `PUT/PATCH` | `/api/v1/candidates/{id}/` | Update candidate details | Yes |
| | `DELETE` | `/api/v1/candidates/{id}/` | Remove candidate | Yes (Admin) |
| | `GET` | `/api/v1/candidates/{id}/resume/` | Download candidate resume | Yes |
| **Applications** | `GET` | `/api/v1/applications/` | List applications with filter/sort | Yes |
| | `POST` | `/api/v1/applications/` | Submit job application | Public |
| | `GET` | `/api/v1/applications/{id}/` | Application details | Yes |
| | `PATCH` | `/api/v1/applications/{id}/status/` | Transition pipeline status | Yes |
| | `GET` | `/api/v1/applications/{id}/history/` | Status audit log history | Yes |
| **Resumes** | `POST` | `/api/v1/resumes/upload/` | Upload resume file & queue task | Public/Yes |
| | `GET` | `/api/v1/resumes/{id}/status/` | Poll resume processing status | Public/Yes |
| **Search** | `GET` | `/api/v1/search/candidates/` | Multi-skill AND/OR ATS search | Yes |
| | `GET` | `/api/v1/search/matches/` | Candidate-to-Job match analysis | Yes |
| **Analytics** | `GET` | `/api/v1/analytics/dashboard/` | Core recruitment KPI summary | Yes |
| | `GET` | `/api/v1/analytics/skills/` | Skill demand distribution | Yes |
| | `GET` | `/api/v1/analytics/experience/` | Experience averages by skill | Yes |
| | `GET` | `/api/v1/analytics/funnel/` | Application conversion funnel | Yes |
| **Activity** | `GET` | `/api/v1/activity-logs/` | Paginated recruitment audit logs | Yes |
| **Members** | `GET` | `/api/v1/members/` | List recruitment team members | Yes |
| | `POST` | `/api/v1/members/` | Onboard new recruiter/admin | Yes (Admin) |

### 8.2 Standardized JSON Response Formats

#### Success Envelope (Paginated):
```json
{
  "count": 142,
  "next": "http://localhost:8000/api/v1/candidates/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Vipanchi Barman",
      "email": "vipanchi@example.com",
      "skills": [
        {"name": "Python", "years_of_experience": 3},
        {"name": "Django", "years_of_experience": 3}
      ],
      "current_status": "Shortlisted",
      "latest_ats_score": 66.67
    }
  ]
}
```

#### Error Envelope:
```json
{
  "status_code": 400,
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid submission payload.",
  "details": {
    "email": ["Enter a valid email address."],
    "myfile": ["The uploaded file must be a valid PDF document."]
  }
}
```

---

## 9. Asynchronous Resume Processing Architecture (Celery + Redis)

To solve the synchronous latency bottleneck, resume uploads will be decoupled from parsing via Celery:

```
Candidate / Recruiter
         │
         │ Uploads resume (POST /api/v1/resumes/upload/)
         ▼
   Django DRF View
         │
         ├── 1. Validates file header / magic bytes & size
         ├── 2. Persists Document record (status = "QUEUED")
         ├── 3. Enqueues task `process_resume_task.delay(document_id)`
         │
         ▼ Returns HTTP 202 Accepted { "task_id": "...", "status": "QUEUED" }
(Candidate immediately sees confirmation; no blocked request)
         │
         ▼
    Redis Queue
         │
         ▼
   Celery Worker
         │
         ├── 1. Updates Document status to "PROCESSING"
         ├── 2. Extracts PDF text (`pypdf`)
         ├── 3. Executes skill identification & experience mapping
         ├── 4. Updates UserData & UserSkill relations in DB transaction
         ├── 5. Recalculates ATS score for linked Application(s)
         ├── 6. Writes ActivityLog entry
         └── 7. Updates Document status to "COMPLETED"
               (or "FAILED" with error details if corrupt)
```

### Resume Processing State Machine:
$$\text{UPLOADED} \longrightarrow \text{QUEUED} \longrightarrow \text{PROCESSING} \genfrac{}{}{0pt}{}{\nearrow}{\searrow} \begin{array}{l} \text{COMPLETED} \\ \text{FAILED (Retries $\le 3$ with exponential backoff)} \end{array}$$

---

## 10. Database Modernization & PostgreSQL Strategy

### 10.1 Schema Enhancements
1. **Primary & Foreign Keys**: Retain BigAutoField / AutoField PKs, enforce explicit `on_delete=models.CASCADE` or `models.SET_NULL`.
2. **Indexing Strategy**:
   - `UserData.name`: B-Tree index for prefix and substring lookups.
   - `Skill.name`: Unique B-Tree index.
   - `UserSkill`: Composite unique index on `('user_data', 'skill')`, single index on `years_of_experience`.
   - `Application`: Index on `status`, composite index on `('candidate', 'job')`, index on `applied_at` and `ats_score`.
   - `Job`: Index on `slug` (unique), `is_active`, `created_at`.
   - `ActivityLog`: Index on `created_at`.
3. **Data Integrity & Transactions**:
   - Wrap candidate registration + document link + initial application creation in `transaction.atomic()`.
   - Add status history tracking model `ApplicationStatusHistory` to record every transition with timestamp and user attribution.

### 10.2 SQLite to PostgreSQL Migration Strategy
1. The repository includes `sqlite_backup.json` (334 verified records representing full business operations).
2. Development and Docker environments will point `DATABASE_URL` to PostgreSQL.
3. Django migrations will run against PostgreSQL, followed by loading `sqlite_backup.json` to ensure zero data loss.
4. If migrating from an existing live SQLite file:
   - Run `python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > data_export.json`
   - Point to PostgreSQL, execute `python manage.py migrate`
   - Load data via `python manage.py loaddata data_export.json`

---

## 11. Security & File Storage Hardening

1. **Secure Document Serving**:
   - Do not serve `/media/uploads/` publicly via static web server.
   - Resumes will be accessed via authenticated endpoint `/api/v1/candidates/{id}/resume/` using Django `FileResponse` with `Content-Disposition: inline` and permission check.
2. **File Upload Security**:
   - Enforce 5MB file size limit.
   - Validate PDF magic bytes (`%PDF-`) using `python-magic` or header inspection rather than trusting user-submitted filenames.
3. **Authentication & Token Management**:
   - Django session authentication with CSRF protection for same-origin SPA, or DRF Knox/Token authentication.
   - Enforce HTTP-only, SameSite=Lax, and Secure session cookies in production.
4. **Environment Isolation**:
   - Strict separation of development settings (`DEBUG=True`, console logging) from production settings (`DEBUG=False`, `ALLOWED_HOSTS`, strict `CORS_ALLOWED_ORIGINS`, SSL redirection).

---

## 12. Phased Migration Roadmap

```
+-----------------------------------------------------------------------------------+
| MILESTONE 1: Complete Codebase Audit & ARCHITECTURE.md Specification (COMPLETED)   |
+----------------------------------------+------------------------------------------+
                                         |
+----------------------------------------v------------------------------------------+
| MILESTONE 2: Backend Architecture Refactoring & Django App Domain Boundaries      |
|              (accounts, jobs, candidates, applications, resumes, search, etc.)    |
+----------------------------------------+------------------------------------------+
                                         |
+----------------------------------------v------------------------------------------+
| MILESTONE 3: Database Architecture Modernization & PostgreSQL Migration           |
|              (Constraints, indexes, transactions, fixture migration)              |
+----------------------------------------+------------------------------------------+
                                         |
+----------------------------------------v------------------------------------------+
| MILESTONE 4: DRF Foundation & OpenAPI Documentation (drf-spectacular)             |
+----------------------------------------+------------------------------------------+
                                         |
+----------------------------------------v------------------------------------------+
| MILESTONES 5-9: Core REST API Implementation                                      |
|                 - MS 5: Auth, Permissions & User Profile APIs                     |
|                 - MS 6: Jobs CRUD & Statistics APIs                               |
|                 - MS 7: Candidates & Profile APIs                                 |
|                 - MS 8: Applications, Status Transition & History APIs            |
|                 - MS 9: Protected Resume Upload & Secure File APIs                |
+----------------------------------------+------------------------------------------+
                                         |
+----------------------------------------v------------------------------------------+
| MILESTONES 10-11: Celery + Redis Asynchronous Processing Integration              |
|                   - Background resume parsing & state machine tracking            |
+----------------------------------------+------------------------------------------+
                                         |
+----------------------------------------v------------------------------------------+
| MILESTONES 12-14: Search, Scoring & Analytics Services                            |
|                   - MS 12: ATS Candidate Search Engine API (AND/OR, experience)  |
|                   - MS 13: Deterministic ATS Match Scoring Service                |
|                   - MS 14: SQL Aggregation Analytics APIs (Funnel, Skills, Exp)   |
+----------------------------------------+------------------------------------------+
                                         |
+----------------------------------------v------------------------------------------+
| MILESTONES 15-25: React 18 + TypeScript + Vite Frontend Implementation            |
|                   - MS 15: React SPA Shell, Design Tokens, Tailwind, Layouts     |
|                   - MS 16: Authentication UI & Auth Guarded Routes                |
|                   - MS 17: Enterprise Recruiter Dashboard                         |
|                   - MS 18: Jobs Management & Creation UI                          |
|                   - MS 19: Candidates Table & Profile UI                          |
|                   - MS 20: Application Pipeline Kanban/Table UI                   |
|                   - MS 21: Asynchronous Resume Upload & Status Tracker UI         |
|                   - MS 22: Candidate Search UI (Skill chips, AND/OR selector)     |
|                   - MS 23: ATS Match Scoring & Gap Analysis UI                    |
|                   - MS 24: Analytics Dashboard UI (Recharts / Chart.js)           |
|                   - MS 25: Public Careers Portal & Candidate Application UI       |
+----------------------------------------+------------------------------------------+
                                         |
+----------------------------------------v------------------------------------------+
| MILESTONES 26-30: Polish, Quality Assurance & Production Infrastructure           |
|                   - MS 26: Enterprise UI/UX Polish (Skeletons, Toasts, Responsive)|
|                   - MS 27: Comprehensive Backend & Frontend Automated Tests       |
|                   - MS 28: Production Docker & Docker Compose Setup               |
|                   - MS 29: Production Configuration, Security & Health Checks     |
|                   - MS 30: Final End-to-End Validation & Documentation Wrap-up    |
+-----------------------------------------------------------------------------------+
```

---

## 13. Milestone 1 Verification Sign-Off

- **Codebase Audited**: All models, views, templates, management commands, and settings inspected.
- **Functionality Verified**: Existing Django application executed against test dataset; public careers page, job detail, candidate registration, login, dashboard, application pipeline, ATS dashboard, and member directory tested with HTTP 200 responses.
- **Bugs Identified & Logged**: 5 critical runtime bugs and 9 architectural bottlenecks cataloged for phased remediation.
- **Data Integrity Preserved**: Verified 334 live records in `sqlite_backup.json` covering users, jobs, candidates, applications, skills, and activity logs.
- **Documentation Complete**: `ARCHITECTURE.md` committed and pushed as the foundational blueprint.
