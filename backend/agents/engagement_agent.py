# ============================================================
# Engagement Agent — Mock implementation (bypasses Claude API)
# ============================================================

import json
import random

# Interest signal points rubric (max = 100)
SIGNAL_POINTS = {
    "applied_to_job":        15,
    "applied_directly":      15,  # alias used in candidate data
    "responded_to_outreach": 10,
    "visited_career_page":    8,
    "referral":              12,
    "submitted_video_demo":  20,
    "completed_assessment":  20,
    "passed_assessment":     10,
    "interview_scheduled":   15,
    "has_open_source":       10,
}

SIGNAL_LABELS = {
    "applied_to_job":        "Applied to the job",
    "applied_directly":      "Applied directly to the role",
    "responded_to_outreach": "Responded to outreach email",
    "visited_career_page":   "Visited our careers page",
    "referral":              "Referred by a team member",
    "submitted_video_demo":  "Submitted resume with video demo",
    "completed_assessment":  "Completed AI/automated assessment",
    "passed_assessment":     "Passed all assessment sections",
    "interview_scheduled":   "Attended/scheduled interview",
    "has_open_source":       "Open-source portfolio / GitHub activity",
}

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
    Mock implementation: Generates realistic email and reply based on candidate skills.
    """
    matched_skills = list(
        set(s.lower() for s in jd.get("required_skills", []))
        & set(s.lower() for s in candidate.get("skills", []))
    )

    skill_text = ", ".join(candidate.get("skills", [])[:3])
    role = jd.get('role_title', 'Role')

    outreach_email = f"Hi {candidate['name']},\n\nI was really impressed by your background, particularly your experience with {skill_text}. We are currently looking for a {role} at our company and I believe you would be an excellent fit.\n\nWould you be open to a quick 15-minute chat this week to discuss the role?\n\nBest,\nRecruiting Team"

    is_interested = len(matched_skills) >= 2 or random.random() > 0.3

    if is_interested:
        candidate_reply = f"Hi there,\n\nThanks for reaching out! The {role} position sounds very interesting. I've been working a lot with {skill_text} recently and I'd love to learn more about the team and the tech stack.\n\nHere is a link to my GitHub profile. Let me know what times work best for you."
        interest_signals = ["Expressed interest in role", "Asked about tech stack", "Shared GitHub profile"]
        candidate.setdefault("engagement_signals", {})["responded_to_outreach"] = True
    else:
        candidate_reply = f"Hi,\n\nThanks for reaching out. I'm currently happy at my current role and not looking to move right now. Please keep me in mind for future opportunities."
        interest_signals = []

    return {
        "outreach_email": outreach_email,
        "candidate_reply": candidate_reply,
        "is_interested": is_interested,
        "interest_signals": interest_signals
    }


def run_ai_interview(candidate: dict, jd: dict) -> dict:
    """
    Mock implementation: Generates realistic mock interview questions and scores.
    """
    role = jd.get('role_title', 'Engineer')
    
    questions = [
        f"Can you explain a challenging project where you utilized {candidate['skills'][0] if candidate.get('skills') else 'your skills'}?",
        f"How do you handle performance bottlenecks in a {role} environment?",
        "Describe your approach to testing and ensuring code quality."
    ]

    simulated_answers = [
        f"I recently used {candidate['skills'][0] if candidate.get('skills') else 'my core skills'} to optimize a data pipeline, reducing latency by 40%.",
        "I typically start by profiling the application to identify the exact bottleneck, then I implement caching or database indexing.",
        "I follow test-driven development and ensure we have solid unit and integration test coverage in our CI/CD pipeline."
    ]

    # Generate a good score (75-95)
    overall_score = random.randint(75, 95)
    passed = overall_score >= 80

    if passed:
        candidate.setdefault("engagement_signals", {})["completed_assessment"] = True
        candidate["engagement_signals"]["passed_assessment"] = True

    return {
        "interview_score": overall_score,
        "passed": passed,
        "questions": questions,
        "evaluation": f"{candidate['name']} communicated clearly and demonstrated strong technical proficiency, earning a solid score of {overall_score}."
    }
