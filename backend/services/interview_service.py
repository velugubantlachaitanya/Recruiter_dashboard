# ============================================================
# Interview Service — AI interview question generation & evaluation
# ============================================================

from agents.engagement_agent import run_ai_interview


def conduct_interview(candidate: dict, jd: dict) -> dict:
    """
    Run a simulated AI interview for a candidate.
    Delegates to the engagement agent's Claude-based interview simulation.
    Returns interview result dict.
    """
    return run_ai_interview(candidate, jd)
