# PostgreSQL Database Architecture & Migration Guide

**Project:** HireMind ATS 2.0  
**Milestone:** 3 — Database Architecture Modernization & PostgreSQL Strategy  

---

## 1. Schema Enhancements & Indexing Strategy

In Milestone 3, all models were reviewed, standardized, and indexed for high-performance PostgreSQL operations:

### 1.1 Candidate Domain (`UserData`)
- **Indexes**:
  - `idx_userdata_name`: B-Tree index on `name` for substring and prefix searches.
  - `idx_userdata_email`: B-Tree index on `email` for rapid recruiter lookup and deduplication checks.

### 1.2 Resume Documents (`Document`)
- **Status State Machine**:
  - `status`: Choices `Uploaded`, `Queued`, `Processing`, `Completed`, `Failed` (default `Completed` to ensure zero disruption to existing records).
  - `error_message`: Captures parsing stack traces or corruption warnings.
- **Indexes**:
  - `idx_doc_status`: B-Tree index for worker queue polling.
  - `idx_doc_uploaded`: Reverse temporal index on `-uploaded_at` for recruiter document history.

### 1.3 Skills & Candidate Skills (`Skill` & `UserSkill`)
- **Candidate Skill Mapping**:
  - `idx_userskill_exp`: Index on `years_of_experience` enabling fast range filters (`years_of_experience >= X`).
  - Unique constraint on `('user_data', 'skill')` prevents duplicate skill rows per candidate.

### 1.4 Job Vacancies (`Job`)
- **Indexes**:
  - `idx_job_active_created`: Composite index on `(is_active, -created_at)` for public careers listing.
  - `idx_job_department`: Index for department-level filtering.
  - `slug`: Unique constraint index for routing.

### 1.5 Applications & Status History (`Application` & `ApplicationStatusHistory`)
- **Pipeline Performance**:
  - `idx_app_status`: Fast stage counting (`Applied`, `Under Review`, `Shortlisted`, `Interview Scheduled`, `Hired`, `Rejected`).
  - `idx_app_applied`: Reverse temporal index for latest application queries.
  - `idx_app_ats_score`: Index on `-ats_score` for high-to-low candidate ranking.
  - `idx_app_job_status`: Composite index on `(job, status)` for lightning-fast kanban board queries.
- **Status Audit Trail (`ApplicationStatusHistory`)**:
  - Tracks `application`, `old_status`, `new_status`, `changed_by`, `notes`, and `changed_at`.
  - Composite index `idx_app_hist_app_date` on `(application, -changed_at)` provides instantaneous candidate lifecycle audit views.

### 1.6 Recruiter Activity Trail (`ActivityLog`)
- **Index**:
  - `idx_actlog_created`: Reverse index on `-created_at` for fast audit log pagination.

---

## 2. Environment Configuration

The application uses `dj-database-url` to parse standard connection strings.

### Environment Variables:
```env
# Local Development (defaults to SQLite if DATABASE_URL is unset)
DATABASE_URL=postgresql://hiremind_user:hiremind_password@localhost:5432/hiremind_db

# Production / Cloud Managed Postgres (e.g., Render, RDS, Neon, Railway)
DATABASE_URL=postgresql://user:pass@host.region.provider.com:5432/dbname?sslmode=require
DB_SSL_REQUIRE=true
```

---

## 3. Data Migration Procedure (SQLite to PostgreSQL)

When transitioning existing production data from SQLite to PostgreSQL:

### Step 1: Export Data from SQLite
```bash
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > full_data_export.json
```

### Step 2: Configure PostgreSQL Connection
```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/hiremind_db"
```

### Step 3: Run Migrations on PostgreSQL
```bash
python manage.py migrate
```

### Step 4: Import Data into PostgreSQL
```bash
python manage.py loaddata sqlite_backup.json
# or: python manage.py loaddata full_data_export.json
```

### Step 5: Verify Data Consistency
```bash
python manage.py shell -c "
from applicants.models import UserData, Application, Document, Skill
print('Candidates:', UserData.objects.count())
print('Applications:', Application.objects.count())
print('Documents:', Document.objects.count())
print('Skills:', Skill.objects.count())
"
```
