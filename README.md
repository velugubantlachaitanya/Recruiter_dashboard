## 🎯 Project Overview

Build a full-stack AI agent that:
1. **Parses a Job Description (JD)** → extracts structured requirements
2. **Discovers & matches candidates** from a mock/simulated candidate pool
3. **Engages candidates conversationally** (simulated AI outreach)
4. **Scores and ranks candidates** on two axes: Match Score + Interest Score
5. **Outputs a recruiter-ready shortlist** with a star rating (1–5 ⭐)

---

## 🏗️ Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                        │
│  • JD Upload / Paste   • Candidate Cards   • Shortlist Table   │
│  • Star Rating UI      • Chat Simulation   • Score Dashboard   │
└───────────────────────────────┬────────────────────────────────┘
                                │ REST API / WebSocket
┌───────────────────────────────▼────────────────────────────────┐
│                      BACKEND (FastAPI / Node)                  │
│                                                                │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │  JD Parser  │  │  Candidate   │  │  Engagement Agent   │   │
│  │  (Claude    │  │  Matcher     │  │  (Conversational    │   │
│  │   API)      │  │  (ML Scorer) │  │   AI / Email Sim)   │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Ranking & Scoring Engine                   │   │
│  │    Match Score (0–100) + Interest Score (0–100)         │   │
│  │    → Combined Star Rating (1–5 ⭐)                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬────────────────────────────────┘
                                │
┌───────────────────────────────▼────────────────────────────────┐
│                     DATA LAYER                                 │
│   Mock Candidate DB (JSON/SQLite) │ Claude API │ Open-Source   │
│   Interview Tool │ Email Service  │ Redis Cache (optional)     │
└────────────────────────────────────────────────────────────────┘
```

---

## 📁 Recommended Folder Structure

```
talent-scout-agent/
├── README.md
├── instruction.md             ← THIS FILE
├── architecture.png           ← Export from draw.io / Excalidraw
├── sample_inputs/
│   ├── sample_jd.txt
│   └── sample_candidates.json
├── sample_outputs/
│   └── shortlist_output.json
│
├── backend/
│   ├── main.py                ← FastAPI entry point
│   ├── requirements.txt
│   ├── agents/
│   │   ├── jd_parser.py       ← Step 1: JD Analysis
│   │   ├── candidate_matcher.py ← Step 2: ML Matching
│   │   ├── engagement_agent.py  ← Step 3: Conversational AI
│   │   └── scorer.py          ← Step 4: Match + Interest Scoring
│   ├── models/
│   │   └── candidate.py       ← Pydantic data models
│   ├── data/
│   │   └── candidates.json    ← Mock candidate pool (50–100 profiles)
│   └── services/
│       ├── email_service.py   ← Open-source email simulation
│       └── interview_service.py ← Open-source interview integration
│
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── JDUploader.jsx
│   │   │   ├── CandidateCard.jsx
│   │   │   ├── ShortlistTable.jsx
│   │   │   ├── StarRating.jsx
│   │   │   └── ChatSimulator.jsx
│   │   └── pages/
│   │       ├── Dashboard.jsx
│   │       └── RecruiterView.jsx
│
└── docker-compose.yml         ← For local setup (optional)
```

---

## ⚙️ Step-by-Step Implementation Plan

---

### STEP 1 — JD Parser (Claude API)

**File:** `backend/agents/jd_parser.py`

**What it does:** Extract structured data from a raw Job Description.

**Fields to extract:**
| Field | Example |
|---|---|
| `role_title` | "Senior ML Engineer" |
| `required_skills` | ["Python", "PyTorch", "LLMs"] |
| `preferred_skills` | ["Kubernetes", "MLflow"] |
| `min_experience_years` | 4 |
| `employment_type` | "Full-time" / "Contract" |
| `location` | "Hyderabad, India" |
| `remote_allowed` | true / false |
| `education_required` | "B.Tech/B.E. in CS or related" |
| `education_tier_preference` | "Tier 1 preferred" |

**Implementation:**
```python
import anthropic
import json

client = anthropic.Anthropic(api_key="YOUR_API_KEY")

def parse_jd(jd_text: str) -> dict:
    prompt = f"""
    You are a JD parser. Extract structured information from this Job Description.
    Return ONLY a valid JSON object with these fields:
    role_title, required_skills (list), preferred_skills (list),
    min_experience_years (int), employment_type, location,
    remote_allowed (bool), education_required, tier1_preferred (bool),
    domain_keywords (list).

    JD:
    {jd_text}
    """
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.content[0].text)
```

---

### STEP 2 — Candidate Pool (Mock Data)

**File:** `backend/data/candidates.json`

Each candidate profile should include:

```json
{
  "id": "C001",
  "name": "Arjun Sharma",
  "email": "arjun@example.com",
  "location": "Hyderabad, India",
  "skills": ["Python", "PyTorch", "TensorFlow", "LLMs", "FastAPI"],
  "experience_years": 5,
  "employment_type": "Full-time",
  "education": {
    "degree": "B.Tech Computer Science",
    "institution": "IIT Hyderabad",
    "tier": 1
  },
  "projects": [
    {
      "name": "Real-time Fraud Detection System",
      "description": "Built ML pipeline deployed in production at FinTech startup",
      "is_real_world": true,
      "impact": "Reduced fraud by 40%"
    }
  ],
  "open_source_contributions": ["huggingface/transformers", "langchain"],
  "portfolio_url": "https://github.com/arjunsharma",
  "video_intro_url": null,
  "resume_url": "https://example.com/resume/arjun.pdf"
}
```

**Create 50–100 diverse candidates** with varied skills, locations, tiers, and experience levels.

---

### STEP 3 — Candidate Matcher (ML Scoring = Match Score)

**File:** `backend/agents/candidate_matcher.py`

**Match Score (0–100)** calculated from:

| Factor | Weight | Logic |
|---|---|---|
| **Skills Match** | 35% | `matched_skills / required_skills * 100` |
| **Experience** | 20% | Full marks if ≥ min_years; partial if within 1 yr |
| **Location** | 20% | Full if same city/country; 0 if location mismatch + remote not allowed |
| **Education Tier** | 15% | Tier 1 (IIT/NIT/BITS/IIIT) = 100; Tier 2 = 70; Others = 40 |
| **Employment Type** | 10% | Full if matches; 0 if mismatch |

**Implementation using sentence-transformers (open-source ML):**

```python
from sentence_transformers import SentenceTransformer, util
import torch

model = SentenceTransformer('all-MiniLM-L6-v2')  # Free, open-source

def compute_skills_similarity(jd_skills: list, candidate_skills: list) -> float:
    jd_text = ", ".join(jd_skills)
    cand_text = ", ".join(candidate_skills)
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    cand_emb = model.encode(cand_text, convert_to_tensor=True)
    return float(util.cos_sim(jd_emb, cand_emb)[0][0]) * 100

def compute_match_score(jd: dict, candidate: dict) -> dict:
    # Skills (35%)
    skills_score = compute_skills_similarity(
        jd["required_skills"], candidate["skills"]
    ) * 0.35

    # Experience (20%)
    exp_diff = candidate["experience_years"] - jd["min_experience_years"]
    exp_score = 100 if exp_diff >= 0 else max(0, 100 + exp_diff * 20)
    exp_score *= 0.20

    # Location (20%)
    loc_score = 100 if (
        jd["location"].lower() in candidate["location"].lower()
        or jd.get("remote_allowed")
    ) else 0
    loc_score *= 0.20

    # Education Tier (15%)
    tier_map = {1: 100, 2: 70, 3: 40}
    edu_score = tier_map.get(candidate["education"]["tier"], 30) * 0.15

    # Employment Type (10%)
    emp_score = 100 if jd["employment_type"] == candidate["employment_type"] else 0
    emp_score *= 0.10

    total = skills_score + exp_score + loc_score + edu_score + emp_score

    return {
        "match_score": round(total, 1),
        "breakdown": {
            "skills": round(skills_score / 0.35, 1),
            "experience": round(exp_score / 0.20, 1),
            "location": round(loc_score / 0.20, 1),
            "education": round(edu_score / 0.15, 1),
            "employment_type": round(emp_score / 0.10, 1)
        }
    }
```

**Explainability:** Return the `breakdown` dict so the UI can show why each candidate scored as they did.

---

### STEP 4 — Engagement Agent (Interest Score)

**File:** `backend/agents/engagement_agent.py`

**Interest Score (0–100)** is calculated based on candidate engagement signals.

**Scoring Rubric:**

| Signal | Points | ⭐ Contribution |
|---|---|---|
| Applied to the job | +15 pts | Base engagement |
| Responded to outreach email | +10 pts | Shows awareness |
| Resume submitted with video demo | +20 pts | ⭐⭐ (2 stars zone) |
| Completed AI/automated assessment | +20 pts | High commitment |
| Passed all assessment sections | +10 pts | Quality signal |
| Attended/scheduled interview | +15 pts | ⭐⭐⭐–⭐⭐⭐⭐ zone |
| Open-source portfolio / GitHub activity | +10 pts | Bonus |

**Star Rating Formula:**

```
interest_score = sum of applicable signals (0–100)
match_score    = from Step 3 (0–100)
combined_score = (match_score * 0.6) + (interest_score * 0.4)

Star Rating:
  combined >= 85 → ⭐⭐⭐⭐⭐ (Highly Recommended)
  combined >= 70 → ⭐⭐⭐⭐   (Strong Candidate)
  combined >= 55 → ⭐⭐⭐     (Good Potential)
  combined >= 40 → ⭐⭐       (Needs Review)
  combined <  40 → ⭐        (Low Priority)
```

**Simulated Conversational Outreach (Claude API):**

```python
def simulate_outreach_conversation(candidate: dict, jd: dict) -> dict:
    """Simulate AI sending outreach and candidate responding."""
    
    system_prompt = """You are an AI recruiter assistant. Simulate a realistic
    email exchange between a recruiter AI and a candidate. Generate:
    1. The outreach email sent to candidate
    2. A realistic candidate reply (interested OR not interested)
    3. The interest_signals detected from the reply
    Return as JSON."""

    prompt = f"""
    Candidate: {candidate['name']}, {candidate['experience_years']} yrs exp
    Job: {jd['role_title']} at {jd['location']}
    Skills match: {', '.join(set(jd['required_skills']) & set(candidate['skills']))}
    
    Simulate the outreach and reply. Return JSON with:
    outreach_email, candidate_reply, is_interested (bool), interest_signals (list)
    """
    # Call Claude API here
    ...
```

---

### STEP 5 — Open-Source Tools Integration

#### 🤖 AI Interview Tool (Open-Source)
Use **[interviewer.ai open-source alternative]** or build a simple one:

**Option A: Use `elevenlabs` + Claude for voice interview simulation**
```python
# Simulate AI interview questions and evaluate answers
def run_ai_interview(candidate_id: str, jd: dict) -> dict:
    questions = generate_interview_questions(jd)  # Claude API
    # In real app: candidate answers via form/video
    # In simulation: Claude generates realistic answers
    answers = simulate_candidate_answers(questions, candidate)
    score = evaluate_answers(questions, answers)  # Claude API
    return {"interview_score": score, "passed": score > 70}
```

**Option B: Use open-source `Livekit` or `Daily.co` for real video interviews**

#### 📧 Email Service (Open-Source)
Use **`resend`** (free tier) or **`nodemailer`** with Gmail SMTP:

```python
# backend/services/email_service.py
import resend  # pip install resend

resend.api_key = "re_your_key_here"  # Free 3000 emails/month

def send_outreach_email(to: str, subject: str, html: str):
    params = {
        "from": "scout@yourhackathon.dev",
        "to": [to],
        "subject": subject,
        "html": html
    }
    return resend.Emails.send(params)
```

**Alternative (100% local, no signup):** Use `mailhog` (Docker) to catch emails locally.

```yaml
# docker-compose.yml
services:
  mailhog:
    image: mailhog/mailhog
    ports:
      - "8025:8025"   # Web UI
      - "1025:1025"   # SMTP
```

---

### STEP 6 — Final Ranked Output

**File:** `backend/agents/scorer.py`

```python
def generate_shortlist(candidates_with_scores: list) -> list:
    """Sort and rank candidates, return recruiter-ready shortlist."""
    
    for c in candidates_with_scores:
        combined = (c["match_score"] * 0.6) + (c["interest_score"] * 0.4)
        c["combined_score"] = round(combined, 1)
        c["star_rating"] = get_star_rating(combined)
        c["recommendation"] = get_recommendation_label(combined)
    
    # Sort by combined score descending
    return sorted(candidates_with_scores, key=lambda x: x["combined_score"], reverse=True)

def get_star_rating(score: float) -> int:
    if score >= 85: return 5
    if score >= 70: return 4
    if score >= 55: return 3
    if score >= 40: return 2
    return 1

def get_recommendation_label(score: float) -> str:
    labels = {5: "🟢 Highly Recommended", 4: "🔵 Strong Candidate",
              3: "🟡 Good Potential", 2: "🟠 Needs Review", 1: "🔴 Low Priority"}
    return labels[get_star_rating(score)]
```

**Sample Output JSON:**
```json
[
  {
    "rank": 1,
    "candidate_id": "C001",
    "name": "Arjun Sharma",
    "match_score": 88.5,
    "interest_score": 75.0,
    "combined_score": 83.1,
    "star_rating": 4,
    "recommendation": "🔵 Strong Candidate",
    "match_breakdown": {
      "skills": 92, "experience": 100, "location": 100,
      "education": 100, "employment_type": 100
    },
    "interest_signals": ["Applied", "Responded to email", "Submitted video demo"],
    "explainability": "Strong skills match on Python, PyTorch, LLMs. IIT grad, local hire."
  }
]
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **AI/LLM** | Claude API (claude-sonnet-4-6) | JD parsing, outreach, explainability |
| **ML Matching** | sentence-transformers (all-MiniLM-L6-v2) | Free, fast, open-source |
| **Backend** | FastAPI (Python) | Fast, async, easy to deploy |
| **Frontend** | React + TailwindCSS | Clean recruiter UI |
| **Email** | Resend (free) or Mailhog (local) | Open-source outreach simulation |
| **Interview** | Custom AI assessment via Claude | Simulated interview scoring |
| **Database** | JSON files / SQLite | Simple, no setup required |
| **Deployment** | Vercel (frontend) + Railway/Render (backend) | Free tier, fast deploy |

---

## 🚀 Local Setup Instructions (for README)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/talent-scout-agent
cd talent-scout-agent

# 2. Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# 3. Run backend
uvicorn main:app --reload --port 8000

# 4. Frontend setup
cd ../frontend
npm install
npm run dev

# 5. Open browser
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

**requirements.txt:**
```
fastapi
uvicorn
anthropic
sentence-transformers
torch
pydantic
python-dotenv
resend
```

---
