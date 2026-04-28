# ============================================================
# Resume Analyzer — Rule-based AI resume intelligence
# Scores candidates on YOE, real-world projects, skills, education
# Fully open-source, no external API required
# ============================================================


def compute_resume_quality_score(candidate: dict, jd: dict) -> tuple[float, dict]:
    """
    Score a candidate's resume 0-100 based on:
      - Years of Experience vs JD requirement  (30 pts)
      - Real-world production projects          (25 pts)
      - Technical skills depth                  (25 pts)
      - Education tier                          (20 pts)
    Returns (score, breakdown_dict)
    """
    exp       = candidate.get("experience_years", 0)
    min_exp   = jd.get("min_experience_years", 3)
    # Support both data shapes: legacy "projects[].is_real_world" and new "real_world_projects[]"
    legacy_proj  = [p for p in candidate.get("projects", []) if p.get("is_real_world")]
    new_proj     = candidate.get("real_world_projects", [])
    real_proj    = legacy_proj if legacy_proj else new_proj
    oss          = candidate.get("open_source_contributions", [])
    skills       = set(s.lower() for s in candidate.get("skills", []))
    req_skills   = set(s.lower() for s in jd.get("required_skills", []))
    raw_tier = candidate.get("education", {}).get("tier", 3)
    # Support both "tier1"/"tier2"/"tier3" strings and integer 1/2/3
    if isinstance(raw_tier, str):
        edu_tier = int(raw_tier.replace("tier", "")) if raw_tier.startswith("tier") else 3
    else:
        edu_tier = int(raw_tier)

    # ── Years of Experience (30 pts) ──────────────────────────
    gap = exp - min_exp
    if gap >= 5:
        yoe_score = 30
    elif gap >= 3:
        yoe_score = 27
    elif gap >= 2:
        yoe_score = 24
    elif gap >= 1:
        yoe_score = 22
    elif gap >= 0:
        yoe_score = 20
    elif gap >= -1:
        yoe_score = 12
    elif gap >= -2:
        yoe_score = 6
    else:
        yoe_score = 0

    # ── Real-World Projects (25 pts) ──────────────────────────
    n_real = len(real_proj)
    # Impact bonus: any project with measurable result in description
    impact_keywords = [
        "million", "m+", "m users", "k users", "k+", "% ", "tps", "tb/", "tvl",
        "stars", "downloads", "saving", "auc", "tvl", "revenue", "reduced", "increased",
        "deployed", "production", "scale", "users", "daily", "weekly",
    ]
    impact_bonus = sum(
        1 for p in real_proj
        if p.get("impact") or any(kw in (p.get("description", "") + p.get("title", "")).lower() for kw in impact_keywords)
    )
    if n_real >= 4:
        proj_score = 25
    elif n_real >= 3:
        proj_score = 23
    elif n_real == 2:
        proj_score = 17
    elif n_real == 1:
        proj_score = 10
    else:
        proj_score = 0
    proj_score = min(25, proj_score + min(impact_bonus, 4))

    # Open-source bump (up to +5 absorbed into proj_score ceiling)
    if oss:
        proj_score = min(25, proj_score + len(oss) * 2)

    # ── Technical Skills Match (25 pts) ───────────────────────
    if req_skills:
        matched = skills & req_skills
        ratio   = len(matched) / len(req_skills)
        skill_score = round(ratio * 25)
    else:
        skill_score = 15  # neutral if JD has no required skills

    # ── Education Tier (20 pts) ───────────────────────────────
    edu_score = {1: 20, 2: 14, 3: 8}.get(edu_tier, 5)

    total = yoe_score + proj_score + skill_score + edu_score

    return round(min(total, 100), 1), {
        "yoe":        yoe_score,
        "projects":   proj_score,
        "skills":     skill_score,
        "education":  edu_score,
    }


def analyze_resume(candidate: dict, jd: dict) -> dict:
    """
    Generate detailed AI resume analysis.
    Returns a rich dict with strengths, concerns, verdict, and fit label.
    """
    resume_quality, rq_breakdown = compute_resume_quality_score(candidate, jd)

    exp       = candidate.get("experience_years", 0)
    min_exp   = jd.get("min_experience_years", 3)
    role      = jd.get("role_title", "this role")
    name      = candidate.get("name", "Candidate")
    skills    = candidate.get("skills", [])
    req_skills= jd.get("required_skills", [])
    edu       = candidate.get("education", {})
    raw_tier  = edu.get("tier", 3)
    tier      = int(raw_tier.replace("tier","")) if isinstance(raw_tier, str) and raw_tier.startswith("tier") else int(raw_tier)
    inst      = edu.get("institution", "")
    degree    = edu.get("degree", "")
    legacy_proj = [p for p in candidate.get("projects", []) if p.get("is_real_world")]
    new_proj    = candidate.get("real_world_projects", [])
    real_proj   = legacy_proj if legacy_proj else new_proj
    oss       = candidate.get("open_source_contributions", [])

    req_set   = set(s.lower() for s in req_skills)
    cand_set  = set(s.lower() for s in skills)
    matched   = req_set & cand_set
    missing   = req_set - cand_set

    strengths = []
    concerns  = []

    # ── Experience analysis ───────────────────────────────────
    gap = exp - min_exp
    if gap >= 5:
        strengths.append(
            f"Exceptional {exp} yrs experience — {gap} years beyond the {min_exp}-yr requirement, "
            f"bringing deep domain expertise to {role}"
        )
    elif gap >= 2:
        strengths.append(
            f"Strong {exp} yrs experience exceeds the {min_exp}-yr requirement by {gap} years"
        )
    elif gap >= 0:
        strengths.append(
            f"Meets the {min_exp}-yr experience requirement with {exp} years in the field"
        )
    elif gap >= -2:
        concerns.append(
            f"Experience gap: {exp} yrs vs {min_exp} yrs required — may need ramp-up time"
        )
    else:
        concerns.append(
            f"Significant experience shortfall: {exp} yrs vs {min_exp} yrs required for {role}"
        )

    # ── Skills analysis ───────────────────────────────────────
    if matched:
        strengths.append(
            f"Strong skill alignment — proficient in {', '.join(s.title() for s in sorted(matched))}"
        )
    if missing:
        concerns.append(
            f"Skill gaps vs JD requirements: {', '.join(s.title() for s in sorted(missing))}"
        )
    if len(skills) > 8:
        strengths.append(f"Broad tech stack with {len(skills)} skills — versatile profile")

    # ── Real-world projects ───────────────────────────────────
    if real_proj:
        proj_titles = [p.get("title") or p.get("description", "")[:60] for p in real_proj[:2]]
        strengths.append(
            f"{len(real_proj)} real-world production project(s) — e.g. {'; '.join(proj_titles)}"
        )
    else:
        concerns.append(
            "No verified real-world production projects on resume — academic/personal projects only"
        )

    # ── Open source ───────────────────────────────────────────
    if oss:
        strengths.append(
            f"Active open-source contributor: {', '.join(oss[:4])}"
            + (" and more" if len(oss) > 4 else "")
        )

    # ── Education ─────────────────────────────────────────────
    tier_labels = {1: "Tier-1 (IIT/IIM/BITS level) — elite credential", 2: "Tier-2 institution — solid academic foundation", 3: "Tier-3 institution"}
    if tier == 1:
        strengths.append(f"Elite academic pedigree: {degree} from {inst} ({tier_labels[1]})")
    elif tier == 2:
        strengths.append(f"Good academic background: {degree} from {inst} ({tier_labels[2]})")
    else:
        concerns.append(
            f"Tier-3 institution ({inst}) — practical experience and projects are more important here"
        )

    # ── Fit verdict ───────────────────────────────────────────
    if resume_quality >= 78:
        fit_label  = "Excellent Fit"
        fit_color  = "emerald"
        verdict    = (
            f"{name}'s resume is an excellent match for {role}. "
            f"With {exp} years of hands-on experience, strong skill alignment, and verified production impact, "
            f"this candidate is a top-tier pick. Resume quality score: {resume_quality}/100."
        )
        why_preferred = (
            f"{name} stands out because the resume demonstrates not just theoretical knowledge but real-world "
            f"delivery — {len(real_proj)} production project(s) with measurable impact. "
            f"The skill set directly covers {len(matched)} of the {len(req_set)} required skills, "
            f"and {exp} years of experience {'exceeds' if exp > min_exp else 'meets'} the bar."
        )
    elif resume_quality >= 60:
        fit_label  = "Good Fit"
        fit_color  = "blue"
        verdict    = (
            f"{name} presents a competitive resume for {role}. "
            f"Solid {exp}-year background with good skill coverage. "
            f"A few gaps exist but overall a strong candidate. Resume quality score: {resume_quality}/100."
        )
        why_preferred = (
            f"{name}'s profile shows strong practical capability. "
            f"The resume covers {len(matched)} of {len(req_set)} required skills "
            f"and includes {len(real_proj)} real-world project(s), making it a reliable choice for {role}."
        )
    elif resume_quality >= 40:
        fit_label  = "Moderate Fit"
        fit_color  = "yellow"
        verdict    = (
            f"{name} has a moderate fit for {role}. "
            f"Some relevant skills and experience, but notable gaps in key areas. "
            f"Resume quality score: {resume_quality}/100."
        )
        why_preferred = (
            f"{name} shows foundational competence relevant to {role}, "
            f"but the resume reveals gaps in {len(missing)} required skill(s) "
            f"and limited production project evidence."
        )
    else:
        fit_label  = "Weak Fit"
        fit_color  = "red"
        verdict    = (
            f"{name} is below the threshold for {role}. "
            f"Significant experience or skill gaps make this a risky hire without upskilling. "
            f"Resume quality score: {resume_quality}/100."
        )
        why_preferred = (
            f"{name}'s resume does not closely align with {role} requirements. "
            f"Consider for a more junior position or revisit after skill development."
        )

    # ── Capability for the role ───────────────────────────────
    capable = resume_quality >= 55 or (exp >= min_exp and len(matched) >= max(1, len(req_set) // 2))

    return {
        "resume_quality_score":  resume_quality,
        "resume_quality_breakdown": rq_breakdown,
        "fit_label":             fit_label,
        "fit_color":             fit_color,
        "verdict":               verdict,
        "why_preferred":         why_preferred,
        "strengths":             strengths,
        "concerns":              concerns,
        "capable_for_role":      capable,
        "skills_matched":        sorted(matched),
        "skills_missing":        sorted(missing),
    }


def compute_final_score(
    match_score: float,
    resume_quality: float,
    interest_score: float,
    interview_data: dict | None,
) -> tuple[float, str]:
    """
    Compute final combined score with AI interview priority.

    Priority rules:
      1. Candidate passed AI interview  → interview score carries 45% weight (top priority)
      2. Candidate took but failed interview → resume/match still used, slight interview bonus
      3. No interview → score purely on resume quality + match + interest
    Returns (final_score, scoring_method_label)
    """
    if interview_data and interview_data.get("passed"):
        iv_score = interview_data.get("interview_score", 80)
        score = (
            match_score   * 0.30 +
            resume_quality * 0.25 +
            iv_score       * 0.45
        )
        method = "AI Interview + Resume + Match"
    elif interview_data and not interview_data.get("passed"):
        iv_score = interview_data.get("interview_score", 60)
        score = (
            match_score    * 0.40 +
            resume_quality * 0.35 +
            iv_score       * 0.15 +
            interest_score * 0.10
        )
        method = "Resume + Match (Interview attempted)"
    else:
        score = (
            match_score    * 0.45 +
            resume_quality * 0.35 +
            interest_score * 0.20
        )
        method = "Resume + Match + Engagement"

    return round(min(score, 100), 1), method
