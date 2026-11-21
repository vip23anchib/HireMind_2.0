# HireMind ATS — Enterprise Full-Stack Applicant Tracking System

![HireMind Banner](https://img.shields.io/badge/HireMind-Enterprise%20ATS-4F46E5?style=for-the-badge&logo=shield&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0-092E20?style=flat-square&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-REST%20APIs-red?style=flat-square)
![React](https://img.shields.io/badge/React-19.0-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-6.x-646CFF?style=flat-square&logo=vite&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind%20CSS-4.x-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.7-37814A?style=flat-square&logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7.x-DC382D?style=flat-square&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Production%20Ready-2496ED?style=flat-square&logo=docker&logoColor=white)

---

## 1. Executive Summary & Architecture

**HireMind ATS** is a production-grade, enterprise-quality Applicant Tracking System designed for high-growth hiring teams and engineering organizations. Modernized from a monolithic Django application into a decoupled full-stack architecture, HireMind provides end-to-end recruitment automation, asynchronous resume parsing, deterministic ATS candidate-to-job matching, Boolean skill search, and real-time recruitment analytics.

### Architectural Blueprint

```
                     +---------------------------------------+
                     |    Web Clients (Browsers, Mobile)     |
                     +-------------------+-------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |        Nginx Gateway (Port 80)        |
                     +---------+-------------------+---------+
                               |                   |
            / (SPA Routes)     |                   | /api/ (REST Requests)
                               v                   v
      +----------------------------+   +-------------------------------+
      | React 19 + TypeScript SPA  |   | Gunicorn + Django 6 REST App  |
      | Vite Bundler, Tailwind CSS |   | drf-spectacular OpenAPI 3.0   |
      +----------------------------+   +-------+---------------+-------+
                                               |               |
                                               v               v
                                    +----------------+   +-----------+
                                    | PostgreSQL 16  |   |  Redis 7  |
                                    | Primary DB     |   | Broker    |
                                    +----------------+   +-----+-----+
                                                               |
                                                               v
                                                 +-----------------------+
                                                 | Celery Async Workers  |
                                                 | OCR, Parsing, Scoring |
                                                 +-----------------------+
```

---

## 2. Technology Stack

| Layer | Technology | Key Capabilities |
|---|---|---|
| **Frontend** | React 19, TypeScript, Vite | Single-page application, custom design system, zero mock data |
| **Styling** | Tailwind CSS v4, Lucide Icons | Responsive layouts, accessible dialogs, drag & drop, status badges |
| **Backend** | Python 3.12, Django 6.0, DRF | Clean architecture domain services, serializers, ViewSets, APIViews |
| **API Docs** | drf-spectacular, OpenAPI 3.0 | Auto-generated interactive Swagger UI & Redoc schemas |
| **Database** | PostgreSQL 16 (SQLite in dev) | Indexed queries, atomic transactions, status history audit trails |
| **Async Tasks** | Celery 5.7, Redis 7 | Non-blocking PDF text extraction, skill sync, ATS recalculation |
| **Containerization**| Docker, Docker Compose, Nginx | Multi-stage production build, healthcheck probes, reverse proxy |

---

## 3. Core Capabilities & Modules

### 3.1 Public Careers Portal & Candidate Application
- **Live Requisitions**: Real-time listing of active job openings filtered by department and location.
- **Role Details**: Public job description, requirements, responsibilities, and required skill chips.
- **Application Submission**: Multi-part application form with real-time PDF validation (max 5MB), contact collection, and instant resume ingestion.

### 3.2 Recruiter Command Center
- **KPI Metrics**: Real-time overview of active candidates, open requisitions, pipeline conversion rate, and confirmed hires.
- **Application Pipeline Kanban**: Multi-stage recruitment tracking (`Applied` -> `Under Review` -> `Shortlisted` -> `Interview Scheduled` -> `Technical Assessment` -> `Offer Extended` -> `Hired` / `Rejected`).
- **Recruitment History Timeline**: Complete audit trail recording who transitioned a candidate, when, and with what recruiter feedback.

### 3.3 Asynchronous Resume Intelligence Engine
- **Decoupled Processing**: Ingestion returns immediate `202 Accepted` while Celery background workers process heavy PDF extraction without blocking HTTP requests.
- **Document State Machine**: Explicit status transitions (`Uploaded` &rarr; `Queued` &rarr; `Processing` &rarr; `Completed` / `Failed`).
- **Skill Extraction & Normalization**: Maps candidate resume text against an indexed catalog of 60+ canonical technologies with synonym resolution.
- **Deterministic ATS Scoring**: Evaluates candidate skill match percentage against job requisitions and identifies missing technical competencies.

### 3.4 ATS Candidate Search Engine
- **Multi-Skill Querying**: Filter candidate database by multiple technical skills simultaneously.
- **Boolean Match Logic**: Switch dynamically between `OR` (matches any target skill) and `AND` (must possess all target skills).
- **Experience Sliders**: Filter candidates by minimum total professional experience.
- **Gap Analysis**: Visual breakdown of matched skills (highlighted in emerald) and missing skills.

### 3.5 Recruitment Analytics
- **Conversion Funnel**: Stage-by-stage candidate progression and drop-off analysis.
- **Skill Demand Distribution**: Bar breakdown of the most prevalent technologies across applicant resumes.
- **Experience Benchmarks**: Average years of experience per technical skill.

---

## 4. API Reference & Documentation

Interactive API documentation is served directly from the Django application:

- **Swagger UI**: [`http://localhost:8000/api/docs/`](http://localhost:8000/api/docs/)
- **Redoc**: [`http://localhost:8000/api/redoc/`](http://localhost:8000/api/redoc/)
- **OpenAPI 3.0 Schema**: [`http://localhost:8000/api/schema/`](http://localhost:8000/api/schema/)

### Core Endpoint Summary

| Domain | Method | Endpoint | Description | Auth Required |
|---|---|---|---|---|
| **Health** | `GET` | `/api/v1/health/` | Liveness & readiness probe | No |
| **Auth** | `POST` | `/api/v1/auth/login/` | Recruiter session authentication | No |
| | `POST` | `/api/v1/auth/logout/` | Terminate recruiter session | Yes |
| | `GET` | `/api/v1/auth/me/` | Current user profile details | Yes |
| **Jobs** | `GET` | `/api/v1/jobs/` | List jobs (supports search & filters) | No |
| | `POST` | `/api/v1/jobs/` | Create a job requisition | Yes (Recruiter) |
| | `GET` | `/api/v1/jobs/{id}/` | Detailed job posting | No |
| | `POST` | `/api/v1/jobs/{id}/toggle-status/` | Toggle job active/closed state | Yes (Recruiter) |
| **Candidates** | `GET` | `/api/v1/candidates/` | Paginated candidate roster | Yes (Recruiter) |
| | `GET` | `/api/v1/candidates/{id}/` | Detailed candidate profile | Yes (Recruiter) |
| | `GET` | `/api/v1/candidates/{id}/resume/` | Protected resume PDF download | Yes (Recruiter) |
| **Applications**| `GET` | `/api/v1/applications/` | List applications by stage | Yes (Recruiter) |
| | `POST` | `/api/v1/applications/` | Submit job application with resume | No (Public) |
| | `PATCH`| `/api/v1/applications/{id}/status/` | Transition recruitment stage | Yes (Recruiter) |
| | `GET` | `/api/v1/applications/{id}/history/` | Application stage audit timeline | Yes (Recruiter) |
| **Resumes** | `POST` | `/api/v1/resumes/upload/` | Asynchronous resume upload | No |
| | `GET` | `/api/v1/resumes/{id}/status/` | Poll parsing & indexing status | No |
| **Search** | `GET` | `/api/v1/search/candidates/` | Multi-skill Boolean ATS search | Yes (Recruiter) |
| | `GET` | `/api/v1/search/matches/` | ATS candidate-job gap analysis | Yes (Recruiter) |
| **Analytics** | `GET` | `/api/v1/analytics/dashboard/` | Core recruitment KPI summary | Yes (Recruiter) |
| | `GET` | `/api/v1/analytics/skills/` | Skill demand distribution | Yes (Recruiter) |
| | `GET` | `/api/v1/analytics/experience/` | Experience averages per skill | Yes (Recruiter) |
| | `GET` | `/api/v1/analytics/funnel/` | Recruitment conversion funnel | Yes (Recruiter) |
| **Activity** | `GET` | `/api/v1/activity-logs/` | System audit activity stream | Yes (Recruiter) |

---

## 5. Quickstart & Deployment

### Option A: Running With Docker Compose (Recommended)

Start the entire production ecosystem (PostgreSQL, Redis, Django Backend, Celery Worker, and Nginx Gateway) with one command:

```bash
# 1. Clone repository and navigate to root
git clone https://github.com/vip23anchib/HireMind_2.0.git
cd HireMind_2.0

# 2. Configure environment
cp .env.example .env

# 3. Launch all containers
docker-compose up --build -d

# 4. Access services
# Nginx Gateway & React Frontend: http://localhost
# Django API & Swagger UI:        http://localhost:8000/api/docs/
```

### Option B: Local Full-Stack Development

#### 1. Backend Setup (Django + Celery)
```bash
# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Load initial verified dataset (334 live records)
python manage.py loaddata sqlite_backup.json

# (Optional) Start Redis & Celery worker in a separate terminal:
# celery -A my_project worker --loglevel=info

# Run Django development server
python manage.py runserver 8000
```

#### 2. Frontend Setup (React 19 + TypeScript + Vite)
```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev

# Open browser at http://localhost:5173
```

---

## 6. Automated Testing & Verification

HireMind includes comprehensive automated tests covering domain services, resume parsing, ATS scoring formulas, Celery task idempotency, and all REST API endpoints.

```bash
# Run full test suite
python manage.py test

# Run API endpoint tests only
python manage.py test api

# Run Celery task tests only
python manage.py test applicants.tests.CeleryResumeProcessingTaskTest

# Validate OpenAPI schema generation
python manage.py spectacular --validate
```

**Test Suite Coverage Summary:**
- **36 automated unit & integration tests** passing with 0 failures and 0 errors.
- OpenAPI 3.0 schema generation validates with 0 errors.
- Full TypeScript type check passes with 0 compiler errors.

---

## 7. License & Credits

Developed with precision and enterprise architecture standards. Designed for scalable recruitment teams and technical demonstrations.
