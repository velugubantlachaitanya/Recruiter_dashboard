# ============================================================
# JD Parser — Claude API extracts structured JD fields
# ============================================================

import json
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def parse_jd(jd_text: str) -> dict:
    """
    Extract structured information from a raw Job Description using Claude.
    Returns a dict matching the ParsedJD schema.
    """
    client = get_client()

    prompt = f"""You are an expert JD parser for a recruiting platform. Extract structured information from the following Job Description.

Return ONLY a valid JSON object with EXACTLY these fields (no markdown fences, no explanation):
{{
  "role_title": "exact job title",
  "required_skills": ["skill1", "skill2", ...],
  "preferred_skills": ["nice_to_have1", ...],
  "min_experience_years": 4,
  "employment_type": "Full-time",
  "location": "City, Country",
  "remote_allowed": true,
  "education_required": "B.Tech/B.E. in CS or related",
  "tier1_preferred": false,
  "domain_keywords": ["keyword1", "keyword2", ...]
}}

Rules:
- required_skills: must-have technical skills only (max 10)
- preferred_skills: nice-to-have skills (max 8)
- employment_type: "Full-time", "Part-time", or "Contract"
- remote_allowed: true if mentions remote/hybrid
- tier1_preferred: true if mentions IIT/NIT/BITS/premium institutes
- domain_keywords: industry/domain terms (AI, FinTech, SaaS, etc.)

Job Description:
{jd_text}"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    
    # Strip markdown fences if present (json, JSON, etc.)
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:])  # Skip first line with ```
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
    
    # Find the first { and last } to extract JSON
    start_idx = raw.find('{')
    end_idx = raw.rfind('}')
    
    if start_idx != -1 and end_idx != -1:
        raw = raw[start_idx:end_idx+1]
    
    return json.loads(raw.strip())
