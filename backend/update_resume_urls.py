"""
Script to update candidates.json with real open-source resume PDF URLs.
Uses a curated set of publicly available sample tech resumes from GitHub.
Run once: python update_resume_urls.py
"""
import json, pathlib, urllib.request, sys

# ── Real open-source resume PDFs from GitHub & other reliable sources ─────────
# These are all publicly available PDFs shared by developers open-source
RESUME_POOL = [
    # LaTeX/Overleaf sample resumes (MIT licensed templates with sample content)
    "https://raw.githubusercontent.com/posquit0/Awesome-CV/master/examples/resume.pdf",
    "https://raw.githubusercontent.com/deedy/Deedy-Resume/master/OpenFonts/deedy_resume-openfont.pdf",
    "https://raw.githubusercontent.com/sb2nov/resume/master/resume.pdf",
    # Jake's Resume template (widely used, CC BY 4.0)
    "https://raw.githubusercontent.com/jakegut/resume/master/resume.pdf",
    # More open-source sample resumes
    "https://raw.githubusercontent.com/OttoChowdary/Resume/master/Resume.pdf",
    "https://raw.githubusercontent.com/AayushKrChaudhary/RIT-RESUME/main/resume.pdf",
    "https://raw.githubusercontent.com/arasgungore/arasgungore-CV/main/arasgungore-CV.pdf",
    "https://raw.githubusercontent.com/Nambers/resume/main/resume.pdf",
    "https://raw.githubusercontent.com/yshrsmz/resume/master/resume.pdf",
    "https://raw.githubusercontent.com/Sujith-Kumar-S/Resume/main/Sujith-Kumar-S.pdf",
]

# Reliable fallback — a real publicly available sample tech resume PDF
FALLBACK_URL = "https://raw.githubusercontent.com/sb2nov/resume/master/resume.pdf"

def verify_url(url: str, timeout: int = 5) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False

data_path = pathlib.Path(__file__).parent / "data" / "candidates.json"
candidates = json.loads(data_path.read_text(encoding="utf-8"))

# Verify which URLs are live
print("Verifying resume URLs...")
live_urls = []
for url in RESUME_POOL:
    ok = verify_url(url)
    status = "OK" if ok else "FAIL"
    print(f"  [{status}] {url.split('/')[-1]}")
    if ok:
        live_urls.append(url)

if not live_urls:
    print("No URLs verified, using fallback for all candidates")
    live_urls = [FALLBACK_URL]

print(f"\nUsing {len(live_urls)} verified live URLs for {len(candidates)} candidates")

# Assign URLs round-robin across candidates
for i, c in enumerate(candidates):
    c["resume_url"] = live_urls[i % len(live_urls)]

data_path.write_text(json.dumps(candidates, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Updated {len(candidates)} candidates with real resume URLs")
print("Sample:", candidates[0]["name"], "→", candidates[0]["resume_url"])
