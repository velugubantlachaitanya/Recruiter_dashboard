# ============================================================
# JD Parser — Heuristic-based mock (bypasses Claude API)
# ============================================================

import json

def parse_jd(jd_text: str) -> dict:
    """
    Mock implementation: Extracts structured information from a raw Job Description
    using simple heuristics to avoid API costs.
    """
    text = jd_text.lower()
    
    # Determine Role
    role = "Software Engineer"
    if "machine learning" in text or "ml engineer" in text or "ai " in text:
        role = "Senior ML Engineer"
    elif "data" in text:
        role = "Data Scientist"
    elif "frontend" in text or "react" in text:
        role = "Frontend Developer"

    # Determine required skills
    possible_skills = ["python", "pytorch", "tensorflow", "react", "node.js", "aws", "gcp", "docker", "kubernetes", "sql", "java", "c++", "llm", "langchain", "fastapi"]
    required_skills = [s for s in possible_skills if s in text]
    
    if not required_skills:
        required_skills = ["Python", "Machine Learning"] # fallback

    return {
        "role_title": role,
        "required_skills": [s.title() for s in required_skills[:5]],
        "preferred_skills": [s.title() for s in required_skills[5:]] if len(required_skills) > 5 else ["AWS", "Docker"],
        "min_experience_years": 5 if "senior" in text else 2,
        "employment_type": "Full-time",
        "location": "Remote" if "remote" in text else "Hyderabad, India",
        "remote_allowed": "remote" in text or "hybrid" in text,
        "education_required": "B.Tech/B.E. in CS or related",
        "tier1_preferred": "iit" in text or "nit" in text or "bits" in text,
        "domain_keywords": ["AI", "SaaS"] if "ai" in text else ["Software"]
    }
