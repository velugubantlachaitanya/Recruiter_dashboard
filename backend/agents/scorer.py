# ============================================================
# Scorer — Combined score, star rating, explainability
# Pure open-source / rule-based, no external API required
# ============================================================

STAR_THRESHOLDS = [
    (85, 5, "🟢 Highly Recommended"),
    (70, 4, "🔵 Strong Candidate"),
    (55, 3, "🟡 Good Potential"),
    (40, 2, "🟠 Needs Review"),
    (0,  1, "🔴 Low Priority"),
]


def get_star_rating(combined_score: float) -> tuple[int, str]:
    """Return (star_count, recommendation_label) for a combined score."""
    for threshold, stars, label in STAR_THRESHOLDS:
        if combined_score >= threshold:
            return stars, label
    return 1, "🔴 Low Priority"


def compute_combined_score(match_score: float, interest_score: float) -> float:
    """60% match + 40% interest."""
    return round(match_score * 0.6 + interest_score * 0.4, 1)


def generate_explainability(
    candidate: dict,
    jd: dict,
    match_score: float,
    interest_score: float,
    breakdown: dict,
    signals: list,
) -> str:
    """
    Generate a human-readable explainability sentence using rule-based logic.
    Fully open-source — no external API needed.
    """
    name = candidate.get("name", "Candidate")
    role = jd.get("role_title", "this role")
    skills_score = breakdown.get("skills", 0)
    exp_score = breakdown.get("experience", 0)
    loc_score = breakdown.get("location", 0)
    edu = candidate.get("education", {})
    tier = edu.get("tier", 3)
    inst = edu.get("institution", "")
    exp_years = candidate.get("experience_years", 0)

    # Determine strongest dimension
    dims = {
        "skills alignment": skills_score,
        "experience depth": exp_score,
        "location fit": loc_score,
    }
    top_dim = max(dims, key=dims.get)
    top_val = dims[top_dim]

    # Tier label
    tier_label = {1: "Tier-1 institution", 2: "Tier-2 institution", 3: "university"}.get(tier, "university")

    # Signal summary
    if signals:
        signal_part = f" with {len(signals)} engagement signal(s) including '{signals[0]}'"
    else:
        signal_part = ""

    # Score verdict
    if match_score >= 80:
        verdict = "excellent match"
    elif match_score >= 60:
        verdict = "strong match"
    elif match_score >= 40:
        verdict = "moderate match"
    else:
        verdict = "partial match"

    return (
        f"{name} is a {verdict} for {role} — {top_dim} score {top_val:.0f}/100, "
        f"{exp_years} yrs experience, graduated from {inst} ({tier_label}){signal_part}."
    )


def generate_shortlist(
    candidates: list,
    match_results: dict,
    engagement_results: dict,
    jd: dict,
) -> list:
    """
    Build ranked shortlist combining match and interest scores.
    candidates: list of candidate dicts
    match_results: {candidate_id: {match_score, breakdown}}
    engagement_results: {candidate_id: {interest_score, signals_triggered, conversation, interview}}
    """
    entries = []

    for c in candidates:
        cid = c["id"]
        mr = match_results.get(cid, {"match_score": 0, "breakdown": {}})
        er = engagement_results.get(cid, {"interest_score": 0, "signals_triggered": [], "conversation": None, "interview": None})

        match_score = mr.get("match_score", 0)
        interest_score = er.get("interest_score", 0)
        combined = compute_combined_score(match_score, interest_score)
        stars, recommendation = get_star_rating(combined)

        explainability = generate_explainability(
            c, jd, match_score, interest_score,
            mr.get("breakdown", {}), er.get("signals_triggered", [])
        )

        entries.append({
            "candidate_id": cid,
            "name": c["name"],
            "email": c["email"],
            "location": c["location"],
            "skills": c["skills"],
            "experience_years": c["experience_years"],
            "education": c["education"],
            "match_score": match_score,
            "interest_score": interest_score,
            "combined_score": combined,
            "star_rating": stars,
            "recommendation": recommendation,
            "match_breakdown": mr.get("breakdown", {}),
            "interest_signals": er.get("signals_triggered", []),
            "explainability": explainability,
            "conversation": er.get("conversation"),
            "interview": er.get("interview"),
        })

    # Sort by combined score descending
    entries.sort(key=lambda x: x["combined_score"], reverse=True)

    # Add rank
    for i, e in enumerate(entries):
        e["rank"] = i + 1

    return entries


def _fallback_explainability(c: dict, match: float, interest: float, breakdown: dict) -> str:
    edu = c.get("education", {})
    inst = edu.get("institution", "")
    tier = edu.get("tier", 3)
    skills_score = breakdown.get("skills", 0)
    tier_label = "Tier 1" if tier == 1 else "Tier 2" if tier == 2 else "Tier 3"
    return (
        f"Skills match {skills_score:.0f}/100, {c.get('experience_years', 0)} yrs exp, "
        f"{tier_label} grad from {inst}. Combined: {match:.0f} match + {interest:.0f} interest."
    )
