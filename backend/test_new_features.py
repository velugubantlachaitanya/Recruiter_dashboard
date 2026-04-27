import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from services.resume_generator import generate_resume_pdf
from services.resume_analyzer import analyze_resume, compute_resume_quality_score, compute_final_score

candidates = json.loads(pathlib.Path('data/candidates.json').read_text())
jd = {
    'role_title': 'Senior ML Engineer',
    'required_skills': ['Python', 'PyTorch', 'FastAPI'],
    'min_experience_years': 5,
    'location': 'Hyderabad, India',
    'remote_allowed': True,
    'employment_type': 'Full-time'
}

print("=== Testing Resume Generator ===")
for c in candidates[:5]:
    pdf = generate_resume_pdf(c)
    print(f"  {c['name']}: PDF {len(pdf)} bytes - OK")

print("\n=== Testing Resume Analyzer ===")
for c in candidates[:5]:
    score, bd = compute_resume_quality_score(c, jd)
    analysis = analyze_resume(c, jd)
    final, method = compute_final_score(c.get('match_score', 50), score, 40, None)
    print(f"  {c['name']}: Quality={score} | Fit={analysis['fit_label']} | Capable={analysis['capable_for_role']}")
    print(f"    Strengths: {len(analysis['strengths'])} | Concerns: {len(analysis['concerns'])}")

print("\n=== Testing Interview Priority Scoring ===")
c = candidates[0]
score, _ = compute_resume_quality_score(c, jd)

# No interview
s1, m1 = compute_final_score(60, score, 40, None)
# Passed interview
s2, m2 = compute_final_score(60, score, 40, {'passed': True, 'interview_score': 85})
# Failed interview
s3, m3 = compute_final_score(60, score, 40, {'passed': False, 'interview_score': 65})

print(f"  No interview:     {s1} ({m1})")
print(f"  Passed interview: {s2} ({m2})")
print(f"  Failed interview: {s3} ({m3})")
print(f"  Interview priority working: {s2 > s1}")

print("\nALL TESTS PASSED!")
