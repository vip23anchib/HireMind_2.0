
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

    SKILLS = [
        "Python",
        "Django",
        "Flask",
        "FastAPI",
        "SQL",
        "MySQL",
        "PostgreSQL",
        "JavaScript",
        "ReactJS",
        "AngularJS",
        "Git",
        "Docker",
        "AWS",
        "Java",
        "C++",
        "Spring",
        "MongoDB"
    ]

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

    pattern = r'([A-Za-z+#]+)\s*-\s*(\d+)\s+years'

    matches = re.findall(pattern, text)

    for skill, years in matches:

        experience_data[skill] = years

    return experience_data
    print(experience_data)