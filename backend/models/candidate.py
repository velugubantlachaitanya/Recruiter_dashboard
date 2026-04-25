from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Education(BaseModel):
    degree: str
    institution: str
    tier: int  # 1=IIT/NIT/BITS/IIIT, 2=VIT/Manipal/SRM, 3=Others


class Project(BaseModel):
    name: str
    description: str
    is_real_world: bool = False
    impact: Optional[str] = None


class EngagementSignals(BaseModel):
    applied_to_job: bool = False
    responded_to_outreach: bool = False
    submitted_video_demo: bool = False
    completed_assessment: bool = False
    passed_assessment: bool = False
    interview_scheduled: bool = False
    has_open_source: bool = False


class Candidate(BaseModel):
    id: str
    name: str
    email: str
    location: str
    skills: List[str]
    experience_years: int
    employment_type: str = "Full-time"
    education: Education
    projects: List[Project] = []
    open_source_contributions: List[str] = []
    portfolio_url: Optional[str] = None
    video_intro_url: Optional[str] = None
    resume_url: Optional[str] = None
    engagement_signals: EngagementSignals = Field(default_factory=EngagementSignals)


class ParsedJD(BaseModel):
    role_title: str
    required_skills: List[str]
    preferred_skills: List[str] = []
    min_experience_years: int = 3
    employment_type: str = "Full-time"
    location: str
    remote_allowed: bool = False
    education_required: str = "B.Tech or equivalent"
    tier1_preferred: bool = False
    domain_keywords: List[str] = []


class MatchBreakdown(BaseModel):
    skills: float
    experience: float
    location: float
    education: float
    employment_type: float


class MatchResult(BaseModel):
    candidate_id: str
    match_score: float
    breakdown: MatchBreakdown


class OutreachConversation(BaseModel):
    outreach_email: str
    candidate_reply: str
    is_interested: bool
    interest_signals: List[str]


class InterviewResult(BaseModel):
    interview_score: float
    passed: bool
    questions: List[str]
    evaluation: str


class EngagementResult(BaseModel):
    candidate_id: str
    interest_score: float
    signals_triggered: List[str]
    conversation: Optional[OutreachConversation] = None
    interview: Optional[InterviewResult] = None


class ShortlistEntry(BaseModel):
    rank: int
    candidate_id: str
    name: str
    email: str
    location: str
    skills: List[str]
    experience_years: int
    education: Education
    match_score: float
    interest_score: float
    combined_score: float
    star_rating: int
    recommendation: str
    match_breakdown: MatchBreakdown
    interest_signals: List[str]
    explainability: str
    conversation: Optional[OutreachConversation] = None


class JDParseRequest(BaseModel):
    jd_text: str


class MatchRequest(BaseModel):
    jd: ParsedJD


class EngageRequest(BaseModel):
    candidate_id: str
    jd: ParsedJD


class FullPipelineRequest(BaseModel):
    jd_text: str
    engage_top_n: int = 10
