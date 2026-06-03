# HireMind ATS

A modern Applicant Tracking System (ATS) built with Django that helps recruiters manage jobs, track applications, search candidates, analyze resumes, and streamline hiring workflows.

---

## Overview

HireMind is a full-stack recruitment platform designed to simulate real-world hiring operations.

The system allows recruiters to:

- Create and manage job openings
- Accept applications through a public careers portal
- Upload and analyze candidate resumes
- Extract skills and experience automatically
- Search candidates using ATS-style filters
- Calculate candidate-job match scores
- View recruitment analytics and hiring insights

The project was built to demonstrate practical backend development, database design, resume processing, and recruiter workflow automation using Django.

---

## Key Features

### Recruitment Management

- Create new job postings
- Edit existing jobs
- Open or close vacancies
- Track application counts
- Public careers page for applicants

### Candidate Management

- Candidate database
- Candidate profile pages
- Resume storage and management
- Application tracking

### Resume Intelligence

- PDF resume upload
- Automatic text extraction
- Skill extraction from resumes
- Experience extraction by technology
- Resume-to-profile processing

### ATS Search Engine

- Search candidates by skills
- Multi-skill search support
- AND / OR skill filtering
- Experience-based filtering
- ATS match score calculation

### Analytics Dashboard

- Candidate statistics
- Skills distribution
- Experience insights
- Recruitment metrics
- Hiring trends visualization

### Authentication & Security

- User authentication
- Recruiter login system
- Protected HR dashboard
- Session-based access control

---

## Technology Stack

### Backend

- Python
- Django

### Database

- SQLite

### Frontend

- HTML
- CSS
- JavaScript

### Data Visualization

- Plotly

### Resume Processing

- PyPDF2

### Authentication

- Django Authentication System

---

## System Architecture

Applicant Flow:

```text
Candidate
    ↓
Careers Page
    ↓
Application Form
    ↓
Resume Upload
    ↓
Resume Parsing
    ↓
Skill Extraction
    ↓
Database Storage
    ↓
Candidate Profile
```

Recruiter Flow:

```text
HR Login
    ↓
ATS Dashboard
    ↓
Manage Jobs
    ↓
View Applications
    ↓
Search Candidates
    ↓
Analyze ATS Scores
    ↓
Shortlist Candidates
```

---

## Core Modules

### Jobs Module

Responsible for:

- Job creation
- Job editing
- Job management
- Application tracking

### Candidate Module

Responsible for:

- Candidate records
- Candidate profiles
- Resume association
- Skills management

### Resume Processing Module

Responsible for:

- PDF extraction
- Resume parsing
- Skill identification
- Experience extraction

### Analytics Module

Responsible for:

- Dashboard metrics
- Hiring insights
- Candidate statistics
- Visual reports

---

## Screenshots

### Public Careers Portal

_Add screenshot here_

### Application Form

_Add screenshot here_

### ATS Dashboard

_Add screenshot here_

### Candidate Search

_Add screenshot here_

### Candidate Profile

_Add screenshot here_

### Analytics Dashboard

_Add screenshot here_

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/HireMind.git
```

Navigate to the project directory:

```bash
cd HireMind
```

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment:

Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply migrations:

```bash
python manage.py migrate
```

Run the development server:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000
```

---

## Future Enhancements

Planned improvements:

- AI-powered resume screening
- Semantic candidate search
- Resume ranking engine
- Email notifications
- Interview scheduling
- Recruiter collaboration tools
- Job recommendation engine
- REST API integration
- FastAPI microservices
- LLM-powered candidate matching

---

## Learning Outcomes

This project helped strengthen understanding of:

- Django Architecture
- Models & Relationships
- CRUD Operations
- Authentication
- File Upload Handling
- Resume Processing
- Database Design
- Search Algorithms
- ATS Workflows
- Dashboard Development
- Data Visualization
- Full-Stack Development

---

## Author

Vipanchi

Built as a real-world recruitment management platform to explore Applicant Tracking Systems, resume intelligence, candidate search, and hiring workflow automation using Django.
