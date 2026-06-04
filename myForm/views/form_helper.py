
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required # Import protection decorator
from ..models import UserData, Document
from django.contrib import messages
from django.http import JsonResponse
from pypdf import PdfReader
from django.core.paginator import Paginator
import re 

SKILL_DATABASE = [
        "Python",
        "Django",
        "Flask",
        "FastAPI",
        "SQL",
        "MySQL",
        "PostgreSQL",
        "JavaScript",
        "React.js",
        "AngularJS",
        "Git",
        "Docker",
        "AWS",
        "Java",
        "C++",
        "Spring",
        "MongoDB",
        "Spring Boot",
        "Node.js",
        "Express.js",
        "HTML",
        "CSS",
        "Redis",
        "Git",
        "GitHub",
        "Excel",
        "Power BI"
    ]

#This mapping normalizes inputs to a clean, standardized string (the values),
# which is incredibly helpful for cleaning up resume parsing data or fixing database lookup issues.
SKILL_SYNONYMS = {
    # --- MERN STACK & FRONTEND ---
    "react": "React.js",
    "reactjs": "React.js",
    "react.js": "React.js",
    "ReactJs": "React.js",
    "react native": "React Native",
    "reactnative": "React Native",
    
    "node": "Node.js",
    "Nodejs": "Node.js",
    "NodeJs": "Node.js",
    "node.js": "Node.js",
    
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "ExpressJs": "Express.js",
    
    "javascript": "JavaScript",
    "js": "JavaScript",
    "ecmascript": "JavaScript",
    "es6": "JavaScript",
    
    "typescript": "TypeScript",
    "ts": "TypeScript",

    "html": "HTML5",
    "html5": "HTML5",
    
    "css": "CSS3",
    "css3": "CSS3",
    "tailwindcss": "Tailwind CSS",
    "tailwind": "Tailwind CSS",
    "sass": "Sass",
    "scss": "Sass",

    "nextjs": "Next.js",
    "next.js": "Next.js",
    
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    
    "angular": "Angular",
    "angularjs": "Angular",
    "angular.js": "Angular",

    # --- PYTHON & BACKEND ---
    "python": "Python",
    "py": "Python",
    
    "django": "Django",
    "dj": "Django",
    "django rest framework": "Django REST Framework",
    "drf": "Django REST Framework",
    
    "flask": "Flask",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",

    # --- DATABASES & CACHING ---
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "psql": "PostgreSQL",
    
    "mysql": "MySQL",
    "my sql": "MySQL",
    
    "sqlite": "SQLite",
    "sqlite3": "SQLite",
    
    "redis": "Redis",
    "firebase": "Firebase",
    "firestore": "Firebase",

    # --- CLOUD, DEVOPS & TOOLS ---
    "aws": "AWS",
    "amazon web services": "AWS",
    "ec2": "AWS",
    "s3": "AWS",
    
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "google cloud platform": "Google Cloud Platform",
    
    "azure": "Microsoft Azure",
    "ms azure": "Microsoft Azure",
    
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    
    "git": "Git",
    "github": "Git",
    "gitlab": "Git",
    
    "cicd": "CI/CD",
    "ci/cd": "CI/CD",
    "github actions": "CI/CD",
    "jenkins": "Jenkins",
    
    "nginx": "Nginx",
    "linux": "Linux",
    "ubuntu": "Linux",

    # --- ARCHITECTURE & API ---
    "rest": "REST API",
    "restful": "REST API",
    "rest api": "REST API",
    "graphql": "GraphQL",
    "gql": "GraphQL",
    "soap": "SOAP",
}

#helper function
def extract_pdf_text(pdf_file):

    try:

        reader = PdfReader(pdf_file)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text

        return text

    except Exception:

        return ""

#helper function to check if uploaded pdf is a resume
def is_resume(text):

    text = text.lower()

    score = 0

    keywords = [
        "skills",
        "experience",
        "education",
        "projects",
        "certifications",
        "linkedin",
        "resume",
        "internship"
    ]

    for word in keywords:

        if word in text:
            score += 1

    return score >= 3

#helper function to extract skills from pdf
def extract_skills(text):

    found_skills = []

    text = text.lower()

    for skill in SKILLS:

        if skill.lower() in text:

            found_skills.append(skill)

    return found_skills

def extract_email(text):

    pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'

    emails = re.findall(pattern, text)

    if emails:
        return emails[0]

    return ""


def extract_phone(text):

    pattern = r'\+?\d[\d\s-]{8,15}'

    phones = re.findall(pattern, text)

    if phones:
        return phones[0]

    return ""


def extract_experience(text):

    pattern = r'(\d+)\s*(?:years?|yrs?)'

    match = re.search(pattern, text.lower())

    if match:
        return match.group()

    return ""


#helper function to find skills + yrs of experience 
def extract_skill_experience(text):

    experience_data = {}

    patterns = [
        r'([A-Za-z0-9.+# ]+?)\s*-\s*(\d+)\s+years',
        r'([A-Za-z0-9.+# ]+?)\s*\(\s*(\d+)\s+years?\s*\)'
    ]

    for pattern in patterns:
        for skill, years in re.findall(pattern, text, re.IGNORECASE):
            experience_data[skill.strip()] = int(years)

    return experience_data
    print(experience_data)




def extract_skills_from_database(text):

    found_skills = set()

    text = text.lower()

    for synonym, canonical_skill in SKILL_SYNONYMS.items():

        pattern = r'\b' + re.escape(synonym.lower()) + r'\b'

        if re.search(pattern, text):
            found_skills.add(canonical_skill)

    return sorted(found_skills)


    
def normalize_skill(skill_name):

    skill = skill_name.strip().lower()

    return SKILL_SYNONYMS.get(
        skill,
        skill_name.strip()
    )