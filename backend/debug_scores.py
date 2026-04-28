import json, sys
sys.path.insert(0, '.')
from agents.jd_parser import parse_jd
from agents.candidate_matcher import match_all_candidates
from services.resume_analyzer import compute_resume_quality_score, compute_final_score

with open('data/candidates.json', encoding='utf-8') as f:
    candidates = json.load(f)

jd = parse_jd('Senior ML Engineer Python PyTorch TensorFlow HuggingFace LangChain AWS MLflow 5+ years Hyderabad')
results = match_all_candidates(jd, candidates)
print('Top 10 match scores:')
for r in results[:10]:
    c = next(x for x in candidates if x['id'] == r['candidate_id'])
    rq, _ = compute_resume_quality_score(c, jd)
    final, _ = compute_final_score(r['match_score'], rq, 65, None)
    n_proj = len(c.get('real_world_projects', []))
    oss = len(c.get('open_source_contributions', []))
    print(f"  {c['name']} ({c['domain']}) | match={r['match_score']:.1f} | rq={rq:.1f} | final={final:.1f} | yoe={c['experience_years']} | proj={n_proj} | oss={oss}")
