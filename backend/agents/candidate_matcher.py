# ============================================================
# Candidate Matcher — ML-based scoring (sklearn TF-IDF)
# ============================================================

import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Singleton vectorizer
_vectorizer = TfidfVectorizer(analyzer="word", ngram_range=(1, 2))


def compute_skills_similarity(jd_skills: list, candidate_skills: list) -> float:
    """Cosine similarity between JD skills and candidate skills using TF-IDF."""
    if not jd_skills or not candidate_skills:
        return 0.0

    jd_text = " ".join(jd_skills).lower()
    cand_text = " ".join(candidate_skills).lower()

    try:
        tfidf = _vectorizer.fit_transform([jd_text, cand_text])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return float(sim) * 100
    except Exception:
        # Fallback: keyword overlap
        jd_set = set(s.lower() for s in jd_skills)
        cand_set = set(s.lower() for s in candidate_skills)
        overlap = jd_set & cand_set
        return (len(overlap) / len(jd_set)) * 100 if jd_set else 0.0


def compute_match_score(jd: dict, candidate: dict) -> dict:
    """
    Compute weighted match score (0-100) across 5 dimensions.
    Returns match_score and breakdown dict.
    """
    # ── Skills (35%) ──────────────────────────────────────────
    raw_skills = compute_skills_similarity(
        jd.get("required_skills", []),
        candidate.get("skills", [])
    )
    skills_component = raw_skills * 0.35

    # ── Experience (20%) ──────────────────────────────────────
    exp_diff = candidate.get("experience_years", 0) - jd.get("min_experience_years", 0)
    if exp_diff >= 0:
        raw_exp = 100.0
    else:
        # Lose 20 pts per year under minimum, floor at 0
        raw_exp = max(0.0, 100.0 + exp_diff * 20.0)
    exp_component = raw_exp * 0.20

    # ── Location (20%) ────────────────────────────────────────
    jd_location = jd.get("location", "").lower()
    cand_location = candidate.get("location", "").lower()
    remote_allowed = jd.get("remote_allowed", False)

    # Check city match, country match, or remote
    jd_parts = [p.strip() for p in jd_location.split(",")]
    cand_parts = [p.strip() for p in cand_location.split(",")]
    location_match = any(jp in cand_location for jp in jd_parts if jp)
    remote_candidate = "remote" in cand_location

    if location_match:
        raw_loc = 100.0
    elif remote_allowed or remote_candidate:
        raw_loc = 80.0
    else:
        # Check country match (last part)
        jd_country = jd_parts[-1] if jd_parts else ""
        cand_country = cand_parts[-1] if cand_parts else ""
        raw_loc = 50.0 if jd_country and jd_country in cand_country else 0.0
    loc_component = raw_loc * 0.20

    # ── Education Tier (15%) ──────────────────────────────────
    tier_map = {1: 100.0, 2: 70.0, 3: 40.0}
    raw_tier = candidate.get("education", {}).get("tier", 3)
    if isinstance(raw_tier, str) and raw_tier.startswith("tier"):
        edu_tier = int(raw_tier.replace("tier", ""))
    else:
        edu_tier = int(raw_tier)
    raw_edu = tier_map.get(edu_tier, 30.0)
    edu_component = raw_edu * 0.15

    # ── Employment Type (10%) ─────────────────────────────────
    jd_emp = jd.get("employment_type", "Full-time").lower()
    cand_emp = candidate.get("employment_type", "Full-time").lower()
    raw_emp = 100.0 if jd_emp == cand_emp else 0.0
    emp_component = raw_emp * 0.10

    total = skills_component + exp_component + loc_component + edu_component + emp_component

    return {
        "match_score": round(total, 1),
        "breakdown": {
            "skills": round(raw_skills, 1),
            "experience": round(raw_exp, 1),
            "location": round(raw_loc, 1),
            "education": round(raw_edu, 1),
            "employment_type": round(raw_emp, 1),
        }
    }


def match_all_candidates(jd: dict, candidates: list) -> list:
    """Score all candidates against the JD and return sorted results."""
    results = []
    for c in candidates:
        score_data = compute_match_score(jd, c)
        results.append({
            "candidate_id": c["id"],
            "match_score": score_data["match_score"],
            "breakdown": score_data["breakdown"],
        })
    return sorted(results, key=lambda x: x["match_score"], reverse=True)
