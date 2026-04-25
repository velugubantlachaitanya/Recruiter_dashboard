# ============================================================
# Engagement Agent — Claude simulates outreach + interest scoring
# ============================================================

import json
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

_client = None

# Interest signal points rubric
SIGNAL_POINTS = {
    "applied_to_job": 15,
    "responded_to_outreach": 10,
    "submitted_video_demo": 20,
    "completed_assessment": 20,
    "passed_assessment": 10,
    "interview_scheduled": 15,
    "has_open_source": 10,
}

SIGNAL_LABELS = {
    "applied_to_job": "Applied to the job",
    "responded_to_outreach": "Responded to outreach email",
    "submitted_video_demo": "Submitted resume with video demo",
    "completed_assessment": "Completed AI/automated assessment",
    "passed_assessment": "Passed all assessment sections",
    "interview_scheduled": "Attended/scheduled interview",
    "has_open_source": "Open-source portfolio / GitHub activity",
}


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
    return _client


def compute_interest_score(signals: dict) -> tuple[float, list]:
    """Calculate interest score from engagement signals. Returns (score, labels)."""
    total = 0.0
    triggered = []
    for signal, points in SIGNAL_POINTS.items():
        if signals.get(signal, False):
            total += points
            triggered.append(SIGNAL_LABELS[signal])
    return min(round(total, 1), 100.0), triggered


def simulate_outreach_conversation(candidate: dict, jd: dict) -> dict:
    """
    Use Claude to simulate:
    1. AI outreach email to candidate
    2. Realistic candidate reply
    3. Interest signals detected from reply
    """
    client = get_client()

    matched_skills = list(
        set(s.lower() for s in jd.get("required_skills", []))
        & set(s.lower() for s in candidate.get("skills", []))
    )

    prompt = f"""You are simulating a realistic AI recruiting outreach exchange.

Candidate: {candidate['name']}, {candidate['experience_years']} years experience
Current Role: inferred from skills: {', '.join(candidate['skills'][:4])}
Location: {candidate['location']}
Education: {candidate['education']['degree']} from {candidate['education']['institution']}

Job Opening: {jd['role_title']} at {jd.get('location', 'Hyderabad, India')}
Required Skills: {', '.join(jd.get('required_skills', []))}
Skills Overlap: {', '.join(matched_skills) if matched_skills else 'indirect overlap'}
Compensation: competitive + equity

Generate a realistic recruiting email exchange. Return ONLY valid JSON (no markdown):
{{
  "outreach_email": "the full outreach email text (3-4 paragraphs, professional but warm)",
  "candidate_reply": "realistic candidate response (2-3 paragraphs, {'enthusiastic and asking questions' if len(matched_skills) >= 3 else 'polite but cautious, mentioning they are open to hearing more'})",
  "is_interested": {"true" if len(matched_skills) >= 2 else "false or true randomly"},
  "interest_signals": ["list of specific positive signals from the reply, e.g., 'Asked about tech stack', 'Shared GitHub profile', 'Mentioned availability']
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
        if raw.endswith("```"):
            raw = raw[:-3]

    data = json.loads(raw.strip())

    # If candidate replied positively, mark responded_to_outreach
    if data.get("is_interested", False):
        candidate.setdefault("engagement_signals", {})["responded_to_outreach"] = True

    return data


def run_ai_interview(candidate: dict, jd: dict) -> dict:
    """
    Claude generates interview questions, simulates answers, evaluates.
    Returns interview_score (0-100) and pass/fail.
    """
    client = get_client()

    prompt = f"""You are conducting an AI technical interview simulation.

Job: {jd['role_title']}
Required Skills: {', '.join(jd.get('required_skills', []))}
Candidate: {candidate['name']}, {candidate['experience_years']} yrs exp
Skills: {', '.join(candidate['skills'])}

Generate a brief interview simulation. Return ONLY valid JSON:
{{
  "questions": ["Q1", "Q2", "Q3"],
  "simulated_answers": ["A1 (realistic for this candidate's profile)", "A2", "A3"],
  "scores_per_question": [80, 75, 90],
  "overall_score": 82,
  "evaluation": "2-sentence overall evaluation of the candidate's interview performance",
  "passed": true
}}

Make scores realistic based on the candidate's skill overlap with the JD requirements."""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:])
        if raw.endswith("```"):
            raw = raw[:-3]

    data = json.loads(raw.strip())

    # If passed, update engagement signals
    if data.get("passed", False):
        candidate.setdefault("engagement_signals", {})["completed_assessment"] = True
        candidate["engagement_signals"]["passed_assessment"] = True

    return {
        "interview_score": data.get("overall_score", 70),
        "passed": data.get("passed", False),
        "questions": data.get("questions", []),
        "evaluation": data.get("evaluation", ""),
    }
