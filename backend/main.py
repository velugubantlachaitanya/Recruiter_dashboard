# ============================================================
# FastAPI Main — TalentScout AI Backend
# ============================================================

import json
import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from dotenv import load_dotenv

# Load env
load_dotenv()

# Add backend dir to path so agents/ and services/ resolve correctly
sys.path.insert(0, str(Path(__file__).parent))

from agents.jd_parser import parse_jd
from agents.candidate_matcher import match_all_candidates
from agents.engagement_agent import (
    compute_interest_score,
    simulate_outreach_conversation,
    run_ai_interview,
)
from agents.scorer import generate_shortlist, compute_combined_score, get_star_rating, generate_explainability
from services.email_service import send_outreach_email
from services.resume_generator import generate_resume_pdf
from services.resume_analyzer import analyze_resume, compute_resume_quality_score, compute_final_score

# ── Data loading ──────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent / "data" / "candidates.json"
_candidates_cache: Optional[list] = None


def load_candidates() -> list:
    global _candidates_cache
    if _candidates_cache is None:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            _candidates_cache = json.load(f)
    return _candidates_cache


# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="TalentScout AI API",
    description="AI-Powered Talent Scouting & Engagement Agent — Catalyst Hackathon 2026",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (for demo)
_session: dict = {
    "parsed_jd": None,
    "match_results": {},   # candidate_id -> {match_score, breakdown}
    "engagement_results": {},  # candidate_id -> {interest_score, signals, conversation, interview}
    "shortlist": [],
}


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "TalentScout AI", "candidates_loaded": len(load_candidates())}


# ── Resume PDF (generate on-the-fly) ─────────────────────────────────────────
def _get_resume_pdf(candidate_id: str):
    """Shared helper: load candidate + generate PDF bytes."""
    candidates = load_candidates()
    cand_map   = {c["id"]: c for c in candidates}
    candidate  = cand_map.get(candidate_id)
    if not candidate:
        raise HTTPException(404, f"Candidate {candidate_id} not found")
    try:
        pdf_bytes = generate_resume_pdf(candidate)
    except Exception as e:
        raise HTTPException(500, f"Resume generation failed: {e}")
    return candidate, pdf_bytes

@app.get("/api/resume/{candidate_id}/view")
def api_resume_view(candidate_id: str):
    """Return PDF inline — opens in browser tab."""
    candidate, pdf_bytes = _get_resume_pdf(candidate_id)
    name_slug = candidate["name"].replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{name_slug}_Resume.pdf"'},
    )

@app.get("/api/resume/{candidate_id}")
def api_resume(candidate_id: str):
    """Return PDF as attachment — triggers browser download."""
    candidate, pdf_bytes = _get_resume_pdf(candidate_id)
    name_slug = candidate["name"].replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{name_slug}_Resume.pdf"'},
    )


# ── Resume Analysis (AI-like scoring) ────────────────────────────────────────
@app.get("/api/resume-analysis/{candidate_id}")
def api_resume_analysis(candidate_id: str):
    """Return AI resume analysis for a candidate against the current session JD."""
    candidates = load_candidates()
    cand_map   = {c["id"]: c for c in candidates}
    candidate  = cand_map.get(candidate_id)
    if not candidate:
        raise HTTPException(404, f"Candidate {candidate_id} not found")
    jd = _session.get("parsed_jd") or {}
    analysis = analyze_resume(candidate, jd)
    return {"candidate_id": candidate_id, "analysis": analysis}


# ── Step 1: Parse JD ─────────────────────────────────────────────────────────
@app.post("/api/parse-jd")
async def api_parse_jd(body: dict):
    jd_text = body.get("jd_text", "")
    if not jd_text.strip():
        raise HTTPException(400, "jd_text is required")

    try:
        parsed = parse_jd(jd_text)
    except Exception as e:
        raise HTTPException(500, f"Failed to parse JD: {str(e)}")
    
    _session["parsed_jd"] = parsed
    # Reset downstream results
    _session["match_results"] = {}
    _session["engagement_results"] = {}
    _session["shortlist"] = []
    return {"parsed_jd": parsed}


# ── Step 2: Match Candidates ──────────────────────────────────────────────────
@app.post("/api/match-candidates")
async def api_match_candidates(body: dict):
    jd = body.get("jd") or _session.get("parsed_jd")
    if not jd:
        raise HTTPException(400, "parsed_jd not found. Call /api/parse-jd first.")

    candidates = load_candidates()
    results = match_all_candidates(jd, candidates)

    # Store results
    for r in results:
        _session["match_results"][r["candidate_id"]] = {
            "match_score": r["match_score"],
            "breakdown": r["breakdown"],
        }

    # Enrich with candidate info for frontend
    cand_map = {c["id"]: c for c in candidates}
    enriched = []
    for r in results:
        c = cand_map.get(r["candidate_id"], {})
        # Compute pre-seeded interest score
        signals_dict = c.get("engagement_signals", {})
        # has_open_source from data
        signals_dict["has_open_source"] = bool(c.get("open_source_contributions"))
        interest_score, signals_triggered = compute_interest_score(signals_dict)
        combined = compute_combined_score(r["match_score"], interest_score)
        stars, rec = get_star_rating(combined)

        # Resume quality + new combined score
        resume_quality, rq_breakdown = compute_resume_quality_score(c, jd)
        interview_data = None  # not run yet at match stage
        final_score, scoring_method = compute_final_score(
            r["match_score"], resume_quality, interest_score, interview_data
        )
        final_stars, final_rec = get_star_rating(final_score)
        analysis = analyze_resume(c, jd)

        enriched.append({
            **r,
            "match_breakdown":           r.get("breakdown", {}),
            "name":                      c.get("name", ""),
            "email":                     c.get("email", ""),
            "location":                  c.get("location", ""),
            "skills":                    c.get("skills", []),
            "experience_years":          c.get("experience_years", 0),
            "education":                 c.get("education", {}),
            "open_source_contributions": c.get("open_source_contributions", []),
            "resume_url":                c.get("resume_url", ""),
            "portfolio_url":             c.get("portfolio_url", ""),
            "interest_score":            interest_score,
            "interest_signals":          signals_triggered,
            "resume_quality_score":      resume_quality,
            "resume_quality_breakdown":  rq_breakdown,
            "combined_score":            final_score,
            "scoring_method":            scoring_method,
            "star_rating":               final_stars,
            "recommendation":            final_rec,
            "capable_for_role":          analysis["capable_for_role"],
            "resume_analysis":           analysis,
            "explainability":            generate_explainability(
                c, jd, r["match_score"], interest_score,
                r.get("breakdown", {}), signals_triggered
            ),
        })

    return {"candidates": enriched, "total": len(enriched)}


# ── Step 3a: Engage candidate (outreach) ─────────────────────────────────────
@app.post("/api/engage/{candidate_id}")
async def api_engage(candidate_id: str, body: dict):
    jd = body.get("jd") or _session.get("parsed_jd")
    if not jd:
        raise HTTPException(400, "parsed_jd not found")

    candidates = load_candidates()
    cand_map = {c["id"]: c for c in candidates}
    candidate = cand_map.get(candidate_id)
    if not candidate:
        raise HTTPException(404, f"Candidate {candidate_id} not found")

    # Work on a mutable copy
    import copy
    c = copy.deepcopy(candidate)

    # Simulate outreach conversation
    conversation = simulate_outreach_conversation(c, jd)

    # Recompute interest score after outreach
    signals = c.get("engagement_signals", {})
    signals["has_open_source"] = bool(c.get("open_source_contributions"))
    interest_score, signals_triggered = compute_interest_score(signals)

    # Try to send email (will gracefully fail if no mailhog running)
    email_result = send_outreach_email(
        to_email=c["email"],
        candidate_name=c["name"],
        role_title=jd.get("role_title", "Role"),
        email_body=conversation.get("outreach_email", ""),
    )

    result = {
        "candidate_id": candidate_id,
        "interest_score": interest_score,
        "signals_triggered": signals_triggered,
        "conversation": conversation,
        "email_delivery": email_result,
    }

    _session["engagement_results"][candidate_id] = result
    return result


# ── Step 3b: Run AI Interview ────────────────────────────────────────────────
@app.post("/api/interview/{candidate_id}")
async def api_interview(candidate_id: str, body: dict):
    jd = body.get("jd") or _session.get("parsed_jd")
    if not jd:
        raise HTTPException(400, "parsed_jd not found")

    candidates = load_candidates()
    cand_map = {c["id"]: c for c in candidates}
    candidate = cand_map.get(candidate_id)
    if not candidate:
        raise HTTPException(404, f"Candidate {candidate_id} not found")

    import copy
    c = copy.deepcopy(candidate)
    interview = run_ai_interview(c, jd)

    # Update engagement result
    if candidate_id in _session["engagement_results"]:
        _session["engagement_results"][candidate_id]["interview"] = interview
    else:
        signals = c.get("engagement_signals", {})
        signals["has_open_source"] = bool(c.get("open_source_contributions"))
        interest_score, signals_triggered = compute_interest_score(signals)
        _session["engagement_results"][candidate_id] = {
            "candidate_id": candidate_id,
            "interest_score": interest_score,
            "signals_triggered": signals_triggered,
            "conversation": None,
            "interview": interview,
        }

    return interview


# ── Step 4: Generate Shortlist ────────────────────────────────────────────────
@app.post("/api/shortlist")
async def api_shortlist(body: dict):
    jd = body.get("jd") or _session.get("parsed_jd")
    if not jd:
        raise HTTPException(400, "parsed_jd not found. Run the full pipeline first.")

    candidates = load_candidates()
    cand_map = {c["id"]: c for c in candidates}

    # Ensure we have match results
    if not _session["match_results"]:
        results = match_all_candidates(jd, candidates)
        for r in results:
            _session["match_results"][r["candidate_id"]] = {
                "match_score": r["match_score"],
                "breakdown": r["breakdown"],
            }

    # Build engagement results for candidates not yet engaged
    for c in candidates:
        cid = c["id"]
        if cid not in _session["engagement_results"]:
            signals = c.get("engagement_signals", {})
            signals["has_open_source"] = bool(c.get("open_source_contributions"))
            interest_score, signals_triggered = compute_interest_score(signals)
            _session["engagement_results"][cid] = {
                "candidate_id": cid,
                "interest_score": interest_score,
                "signals_triggered": signals_triggered,
                "conversation": None,
                "interview": None,
            }

    shortlist = generate_shortlist(candidates, _session["match_results"], _session["engagement_results"], jd)
    _session["shortlist"] = shortlist

    return {"shortlist": shortlist, "total": len(shortlist)}


# ── Full Pipeline ────────────────────────────────────────────────────────────
@app.post("/api/full-pipeline")
async def api_full_pipeline(body: dict):
    """
    Run the entire pipeline in one shot:
    1. Parse JD
    2. Match all candidates
    3. Engage top N candidates (outreach simulation)
    4. Generate shortlist
    """
    jd_text = body.get("jd_text", "")
    engage_top_n = body.get("engage_top_n", 6)

    if not jd_text.strip():
        raise HTTPException(400, "jd_text is required")

    # Step 1: Parse
    parsed_jd = parse_jd(jd_text)
    _session["parsed_jd"] = parsed_jd
    _session["match_results"] = {}
    _session["engagement_results"] = {}
    _session["shortlist"] = []

    # Step 2: Match
    candidates = load_candidates()
    results = match_all_candidates(parsed_jd, candidates)
    for r in results:
        _session["match_results"][r["candidate_id"]] = {
            "match_score": r["match_score"],
            "breakdown": r["breakdown"],
        }

    # Step 3: Engage top N
    import copy
    cand_map = {c["id"]: c for c in candidates}
    top_n_ids = [r["candidate_id"] for r in results[:engage_top_n]]

    for cid in top_n_ids:
        c = copy.deepcopy(cand_map[cid])
        try:
            conversation = simulate_outreach_conversation(c, parsed_jd)
        except Exception as e:
            conversation = {
                "outreach_email": f"[Error generating outreach: {e}]",
                "candidate_reply": "[Simulation skipped]",
                "is_interested": False,
                "interest_signals": [],
            }
        signals = c.get("engagement_signals", {})
        signals["has_open_source"] = bool(c.get("open_source_contributions"))
        interest_score, signals_triggered = compute_interest_score(signals)
        _session["engagement_results"][cid] = {
            "candidate_id": cid,
            "interest_score": interest_score,
            "signals_triggered": signals_triggered,
            "conversation": conversation,
            "interview": None,
        }

    # Fill in pre-seeded interest for remaining candidates
    for c in candidates:
        cid = c["id"]
        if cid not in _session["engagement_results"]:
            signals = c.get("engagement_signals", {})
            signals["has_open_source"] = bool(c.get("open_source_contributions"))
            interest_score, signals_triggered = compute_interest_score(signals)
            _session["engagement_results"][cid] = {
                "candidate_id": cid,
                "interest_score": interest_score,
                "signals_triggered": signals_triggered,
                "conversation": None,
                "interview": None,
            }

    # Step 4: Shortlist
    shortlist = generate_shortlist(candidates, _session["match_results"], _session["engagement_results"], parsed_jd)
    _session["shortlist"] = shortlist

    return {
        "parsed_jd": parsed_jd,
        "shortlist": shortlist,
        "total_candidates": len(candidates),
        "engaged_candidates": len(top_n_ids),
    }


# ── Get current session state ─────────────────────────────────────────────────
@app.get("/api/session")
def api_session():
    return {
        "has_jd": _session["parsed_jd"] is not None,
        "parsed_jd": _session["parsed_jd"],
        "matched_count": len(_session["match_results"]),
        "engaged_count": len(_session["engagement_results"]),
        "shortlist_count": len(_session["shortlist"]),
    }


# ── Get all candidates ────────────────────────────────────────────────────────
@app.get("/api/candidates")
def api_candidates(limit: int = Query(50, ge=1, le=100)):
    return {"candidates": load_candidates()[:limit], "total": len(load_candidates())}
