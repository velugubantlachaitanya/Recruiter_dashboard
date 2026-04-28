# ============================================================
# Scorer — Combined score, star rating, explainability
# Now integrates resume quality + AI interview priority scoring
# Pure open-source / rule-based, no external API required
# ============================================================

from services.resume_analyzer import compute_resume_quality_score, compute_final_score, analyze_resume

STAR_THRESHOLDS = [
    (65, 5, "🟢 Highly Recommended"),
    (52, 4, "🔵 Strong Candidate"),
    (38, 3, "🟡 Good Potential"),
    (24, 2, "🟠 Needs Review"),
    (0,  1, "🔴 Low Priority"),
]


def get_star_rating(combined_score: float) -> tuple[int, str]:
    for threshold, stars, label in STAR_THRESHOLDS:
        if combined_score >= threshold:
            return stars, label
    return 1, "🔴 Low Priority"


def compute_combined_score(match_score: float, interest_score: float) -> float:
    """Legacy helper kept for backward compatibility (used in quick match preview)."""
    return round(match_score * 0.6 + interest_score * 0.4, 1)


def generate_explainability(
    candidate: dict,
    jd: dict,
    match_score: float,
    interest_score: float,
    breakdown: dict,
    signals: list,
) -> str:
    name        = candidate.get("name", "Candidate")
    role        = jd.get("role_title", "this role")
    skills_score= breakdown.get("skills", 0)
    exp_score   = breakdown.get("experience", 0)
    loc_score   = breakdown.get("location", 0)
    edu         = candidate.get("education", {})
    raw_tier    = edu.get("tier", 3)
    tier        = int(raw_tier.replace("tier","")) if isinstance(raw_tier, str) and raw_tier.startswith("tier") else int(raw_tier)
    inst        = edu.get("institution", "")
    exp_years   = candidate.get("experience_years", 0)

    dims   = {"skills alignment": skills_score, "experience depth": exp_score, "location fit": loc_score}
    top_dim= max(dims, key=dims.get)
    top_val= dims[top_dim]
    tier_label = {1: "Tier-1 institution", 2: "Tier-2 institution", 3: "university"}.get(tier, "university")
    signal_part = f" with {len(signals)} engagement signal(s) including '{signals[0]}'" if signals else ""

    verdict = (
        "excellent match" if match_score >= 80 else
        "strong match"   if match_score >= 60 else
        "moderate match" if match_score >= 40 else
        "partial match"
    )
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
    Build ranked shortlist using the new scoring pipeline:
      - resume_quality_score (YOE + real projects + skills + education)
      - AI interview priority (passed → 45% weight)
      - match_score and interest_score as supporting signals
    """
    entries = []

    for c in candidates:
        cid = c["id"]
        mr  = match_results.get(cid,    {"match_score": 0, "breakdown": {}})
        er  = engagement_results.get(cid, {
            "interest_score": 0, "signals_triggered": [], "conversation": None, "interview": None
        })

        match_score    = mr.get("match_score", 0)
        interest_score = er.get("interest_score", 0)
        interview_data = er.get("interview")

        # Resume quality score
        resume_quality, rq_breakdown = compute_resume_quality_score(c, jd)

        # Final combined score (interview-priority aware)
        final_score, scoring_method = compute_final_score(
            match_score, resume_quality, interest_score, interview_data
        )

        stars, recommendation = get_star_rating(final_score)

        # Full resume analysis
        analysis = analyze_resume(c, jd)

        explainability = generate_explainability(
            c, jd, match_score, interest_score,
            mr.get("breakdown", {}), er.get("signals_triggered", [])
        )

        entries.append({
            "candidate_id":           cid,
            "name":                   c["name"],
            "email":                  c["email"],
            "location":               c["location"],
            "resume_url":             c.get("resume_url", ""),
            "portfolio_url":          c.get("portfolio_url", ""),
            "skills":                 c["skills"],
            "experience_years":       c["experience_years"],
            "education":              c["education"],
            "match_score":            match_score,
            "interest_score":         interest_score,
            "resume_quality_score":   resume_quality,
            "resume_quality_breakdown": rq_breakdown,
            "combined_score":         final_score,
            "scoring_method":         scoring_method,
            "star_rating":            stars,
            "recommendation":         recommendation,
            "match_breakdown":        mr.get("breakdown", {}),
            "interest_signals":       er.get("signals_triggered", []),
            "explainability":         explainability,
            "resume_analysis":        analysis,
            "capable_for_role":       analysis["capable_for_role"],
            "conversation":           er.get("conversation"),
            "interview":              interview_data,
        })

    entries.sort(key=lambda x: (
        x["interview"] is not None and x["interview"].get("passed", False),
        x["combined_score"]
    ), reverse=True)

    for i, e in enumerate(entries):
        e["rank"] = i + 1

    return entries
