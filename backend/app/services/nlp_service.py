import re
from typing import List, Tuple, Dict, Optional

# Comprehensive skills taxonomy
SKILLS_DB = {
    "programming_languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "ruby",
        "php", "swift", "kotlin", "scala", "r", "matlab", "perl", "haskell", "elixir",
        "dart", "lua", "julia", "fortran", "cobol", "assembly", "bash", "powershell"
    ],
    "web_frontend": [
        "react", "vue", "angular", "svelte", "nextjs", "nuxtjs", "gatsby", "html", "css",
        "sass", "scss", "tailwind", "bootstrap", "material-ui", "shadcn", "redux", "mobx",
        "graphql", "webpack", "vite", "jest", "cypress", "storybook", "figma"
    ],
    "web_backend": [
        "node.js", "express", "fastapi", "django", "flask", "spring", "rails", "laravel",
        "asp.net", "nestjs", "gin", "fiber", "actix", "rocket", "phoenix", "strapi",
        "rest api", "grpc", "websocket", "microservices", "oauth", "jwt"
    ],
    "databases": [
        "postgresql", "mysql", "sqlite", "mongodb", "redis", "elasticsearch", "cassandra",
        "dynamodb", "firestore", "neo4j", "influxdb", "clickhouse", "snowflake", "bigquery",
        "oracle", "sql server", "mariadb", "cockroachdb", "supabase", "planetscale"
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible", "jenkins",
        "github actions", "gitlab ci", "circleci", "helm", "prometheus", "grafana",
        "datadog", "splunk", "elk stack", "nginx", "apache", "linux", "git", "ci/cd"
    ],
    "data_ml": [
        "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
        "keras", "scikit-learn", "pandas", "numpy", "spark", "hadoop", "airflow", "dbt",
        "tableau", "power bi", "looker", "data engineering", "etl", "mlops", "llm",
        "langchain", "hugging face", "opencv", "matplotlib", "seaborn", "plotly"
    ],
    "mobile": [
        "ios", "android", "react native", "flutter", "xamarin", "ionic", "swiftui",
        "jetpack compose", "objective-c", "cordova"
    ],
    "security": [
        "cybersecurity", "penetration testing", "sso", "saml", "encryption", "firewall",
        "iam", "zero trust", "devsecops", "owasp", "soc 2", "gdpr", "hipaa"
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "problem solving", "agile", "scrum",
        "kanban", "project management", "mentoring", "stakeholder management", "jira",
        "confluence", "product management", "ux", "ui design"
    ],
    "architecture": [
        "system design", "distributed systems", "event-driven", "cqrs", "domain-driven design",
        "api design", "serverless", "monolith", "service mesh", "caching", "message queue",
        "kafka", "rabbitmq", "celery", "redis queue"
    ]
}

ALL_SKILLS = []
for category, skills in SKILLS_DB.items():
    ALL_SKILLS.extend(skills)

ALL_SKILLS = sorted(set(ALL_SKILLS), key=len, reverse=True)


def normalize_text(text: str) -> str:
    return text.lower().strip()


def extract_skills(text: str) -> List[str]:
    """Extract skills from text using keyword matching."""
    text_lower = normalize_text(text)
    found_skills = set()

    for skill in ALL_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)

    # Normalize common variations
    normalizations = {
        "node.js": "node.js",
        "nodejs": "node.js",
        "react.js": "react",
        "reactjs": "react",
        "vue.js": "vue",
        "vuejs": "vue",
        "next.js": "nextjs",
        "angular.js": "angular",
        "angularjs": "angular",
    }
    normalized = set()
    for skill in found_skills:
        normalized.add(normalizations.get(skill, skill))

    return sorted(list(normalized))


def extract_experience_years(text: str) -> Optional[float]:
    """Extract years of experience from text."""
    text_lower = text.lower()
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s+of\s+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s+of\s+experience',
        r'(\d+)\+?\s*yrs?\s+exp',
    ]
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return float(match.group(1))

    # Try to detect from date ranges
    year_ranges = re.findall(r'(20\d{2}|19\d{2})\s*[-–]\s*(20\d{2}|present|current)', text_lower)
    if year_ranges:
        total = 0
        for start, end in year_ranges:
            s = int(start)
            e = 2024 if end in ('present', 'current') else int(end)
            total += max(0, e - s)
        if total > 0:
            return float(min(total, 40))
    return None


def extract_education(text: str) -> List[Dict]:
    """Extract education information."""
    education = []
    degrees = {
        "phd": "PhD", "ph.d": "PhD", "doctorate": "PhD",
        "master": "Master's", "m.s": "Master's", "m.sc": "Master's", "mba": "MBA",
        "bachelor": "Bachelor's", "b.s": "Bachelor's", "b.sc": "Bachelor's", "b.e": "Bachelor's",
        "associate": "Associate's",
        "diploma": "Diploma", "certificate": "Certificate"
    }
    text_lower = text.lower()
    for key, label in degrees.items():
        if key in text_lower:
            education.append({"degree": label})
            break
    return education


def extract_contact_info(text: str) -> Dict:
    """Extract name, email, phone from resume text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

    email_match = re.search(email_pattern, text)
    phone_match = re.search(phone_pattern, text)

    # Try to extract name from first non-empty lines
    name = "Unknown Candidate"
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if lines:
        first_line = lines[0]
        # Name is usually 2-4 words, no special chars
        if re.match(r'^[A-Za-z\s]{2,40}$', first_line) and len(first_line.split()) <= 4:
            name = first_line.title()
        elif len(lines) > 1:
            second = lines[1]
            if re.match(r'^[A-Za-z\s]{2,40}$', second) and len(second.split()) <= 4:
                name = second.title()

    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
    }


def calculate_match_score(
    candidate_skills: List[str],
    required_skills: List[str],
    preferred_skills: List[str],
    candidate_exp: Optional[float],
    required_exp: Optional[int]
) -> Tuple[float, List[str], List[str]]:
    """Calculate match score between candidate and job description."""
    if not required_skills and not preferred_skills:
        return 0.0, [], []

    candidate_set = set(s.lower() for s in candidate_skills)
    required_set = set(s.lower() for s in required_skills)
    preferred_set = set(s.lower() for s in preferred_skills)

    # Required skills matching (70% weight)
    if required_set:
        req_matched = candidate_set.intersection(required_set)
        req_score = len(req_matched) / len(required_set)
    else:
        req_matched = set()
        req_score = 1.0

    # Preferred skills matching (20% weight)
    if preferred_set:
        pref_matched = candidate_set.intersection(preferred_set)
        pref_score = len(pref_matched) / len(preferred_set)
    else:
        pref_matched = set()
        pref_score = 0.0

    # Experience matching (10% weight)
    exp_score = 0.0
    if required_exp and candidate_exp:
        if candidate_exp >= required_exp:
            exp_score = 1.0
        else:
            exp_score = candidate_exp / required_exp

    total_score = (req_score * 0.70) + (pref_score * 0.20) + (exp_score * 0.10)
    total_score = round(total_score * 100, 1)

    matched = sorted(list(req_matched.union(pref_matched)))
    missing = sorted(list(required_set - candidate_set))

    return total_score, matched, missing


def generate_recommendations(
    candidate_skills: List[str],
    missing_skills: List[str],
    match_score: float,
    candidate_name: str
) -> List[str]:
    """Generate AI-style recommendations for a candidate."""
    recs = []

    if match_score >= 85:
        recs.append(f"Strong match — {candidate_name} meets most requirements and is highly recommended for an interview.")
    elif match_score >= 65:
        recs.append(f"Good candidate — {candidate_name} meets core requirements with minor skill gaps.")
    elif match_score >= 40:
        recs.append(f"Moderate match — {candidate_name} has foundational skills but significant gaps exist.")
    else:
        recs.append(f"Below threshold — {candidate_name} lacks many required skills for this role.")

    if missing_skills:
        top_missing = missing_skills[:3]
        recs.append(f"Key missing skills: {', '.join(top_missing)}. Consider if these are trainable on the job.")

    if len(candidate_skills) > 15:
        recs.append("Broad technical skillset — candidate appears versatile and adaptable.")

    if match_score >= 70 and missing_skills:
        recs.append("Recommend a technical screening to validate self-reported skills and assess learnability.")

    return recs


def parse_jd_skills(jd_text: str) -> Tuple[List[str], List[str], Optional[int]]:
    """Extract required and preferred skills from job description."""
    all_skills = extract_skills(jd_text)
    exp = extract_experience_years(jd_text)

    text_lower = jd_text.lower()

    # Heuristic: skills near "required", "must have" → required; near "preferred", "nice to have" → preferred
    required_section = ""
    preferred_section = ""

    req_patterns = [r'required.*?(?=preferred|nice to have|bonus|$)', r'must have.*?(?=preferred|nice to have|$)']
    pref_patterns = [r'preferred.*?(?=required|$)', r'nice to have.*?(?=required|$)', r'bonus.*?(?=required|$)']

    for p in req_patterns:
        m = re.search(p, text_lower, re.DOTALL)
        if m:
            required_section += m.group(0)

    for p in pref_patterns:
        m = re.search(p, text_lower, re.DOTALL)
        if m:
            preferred_section += m.group(0)

    required_skills = extract_skills(required_section) if required_section else all_skills[:len(all_skills)//2 + 1]
    preferred_skills = extract_skills(preferred_section) if preferred_section else []

    # If no split found, treat all as required
    if not required_section and not preferred_section:
        required_skills = all_skills
        preferred_skills = []

    return required_skills, preferred_skills, int(exp) if exp else None
