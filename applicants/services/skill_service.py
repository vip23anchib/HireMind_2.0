"""
Skill Catalog, Normalization & Candidate Synchronization Service.
Maintains canonical skill synonym mappings, extracts canonical skills from text,
and synchronizes candidate skill records with database transactions.
Fixes BUG-04: resolves previously undefined 'SKILLS' variable.
"""

import re
import logging
from typing import Dict, List, Set, Tuple, Optional
from django.db import transaction
from applicants.models import Skill, UserSkill, UserData

logger = logging.getLogger(__name__)

SKILL_DATABASE = [
    "Python",
    "Django",
    "Django REST Framework",
    "Flask",
    "FastAPI",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "SQLite",
    "MongoDB",
    "Redis",
    "Firebase",
    "JavaScript",
    "TypeScript",
    "React.js",
    "React Native",
    "Vue.js",
    "Angular",
    "Next.js",
    "Node.js",
    "Express.js",
    "HTML5",
    "CSS3",
    "Tailwind CSS",
    "Sass",
    "AWS",
    "Google Cloud Platform",
    "Microsoft Azure",
    "Docker",
    "Kubernetes",
    "CI/CD",
    "Git",
    "Linux",
    "Nginx",
    "REST API",
    "GraphQL",
    "Java",
    "Spring Boot",
    "C++",
    "Excel",
    "Power BI",
]

SKILL_SYNONYMS: Dict[str, str] = {
    # Frontend & MERN
    "react": "React.js",
    "reactjs": "React.js",
    "react.js": "React.js",
    "react native": "React Native",
    "reactnative": "React Native",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
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

    # Python & Backend
    "python": "Python",
    "py": "Python",
    "django": "Django",
    "dj": "Django",
    "django rest framework": "Django REST Framework",
    "drf": "Django REST Framework",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",

    # Databases & Caches
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
    "sql": "SQL",

    # Cloud, DevOps & Tools
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
    "jenkins": "CI/CD",
    "nginx": "Nginx",
    "linux": "Linux",
    "ubuntu": "Linux",

    # Architecture & API
    "rest": "REST API",
    "restful": "REST API",
    "rest api": "REST API",
    "graphql": "GraphQL",
    "gql": "GraphQL",

    # Additional Languages
    "java": "Java",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "c++": "C++",
    "cpp": "C++",
    "excel": "Excel",
    "power bi": "Power BI",
    "powerbi": "Power BI",
}


def normalize_skill_name(raw_skill: str) -> str:
    """
    Normalizes a skill name variant into its canonical representation.
    e.g., 'reactjs' -> 'React.js', 'django rest framework' -> 'Django REST Framework'.
    """
    cleaned = raw_skill.strip().lower()
    return SKILL_SYNONYMS.get(cleaned, raw_skill.strip())


def extract_skills_from_text(text: str) -> List[str]:
    """
    Identifies all canonical skills mentioned in the given text via word-boundary matching.
    
    :param text: Text to scan.
    :return: Sorted list of unique canonical skill names detected.
    """
    if not text:
        return []
    lower_text = text.lower()
    found_skills: Set[str] = set()

    for synonym, canonical_skill in SKILL_SYNONYMS.items():
        pattern = r'\b' + re.escape(synonym.lower()) + r'\b'
        if re.search(pattern, lower_text):
            found_skills.add(canonical_skill)

    for skill in SKILL_DATABASE:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, lower_text):
            found_skills.add(skill)

    return sorted(found_skills)


@transaction.atomic
def sync_candidate_skills(
    candidate: UserData,
    detected_skills: List[str],
    skill_experience_map: Optional[Dict[str, int]] = None
) -> List[UserSkill]:
    """
    Synchronizes candidate skills: normalizes experience data, updates or creates Skill
    catalogue entries, and writes UserSkill junction records.
    
    :param candidate: Candidate UserData instance.
    :param detected_skills: List of detected skill names.
    :param skill_experience_map: Raw skill-to-years mapping (optional).
    :return: List of UserSkill instances created or updated.
    """
    if skill_experience_map is None:
        skill_experience_map = {}

    normalized_experience: Dict[str, int] = {}
    for skill_name, years in skill_experience_map.items():
        canonical = normalize_skill_name(skill_name)
        normalized_experience[canonical] = years

    user_skills: List[UserSkill] = []
    for raw_skill in detected_skills:
        canonical_name = normalize_skill_name(raw_skill)
        years = normalized_experience.get(canonical_name, 0)

        skill, _ = Skill.objects.get_or_create(name=canonical_name)
        user_skill, _ = UserSkill.objects.update_or_create(
            user_data=candidate,
            skill=skill,
            defaults={"years_of_experience": years}
        )
        user_skills.append(user_skill)

    return user_skills
