"""
Generates a PDF resume for every candidate in candidates.json,
saves them to data/resumes/, and updates resume_url in candidates.json
to the static path so they are served directly via FastAPI.

Run: python generate_resume_pdfs.py
"""
import json
import sys
from pathlib import Path

# Make sure services/ is on path
sys.path.insert(0, str(Path(__file__).parent))
from services.resume_generator import generate_resume_pdf

DATA_DIR    = Path(__file__).parent / "data"
RESUMES_DIR = DATA_DIR / "resumes"
CANDIDATES  = DATA_DIR / "candidates.json"

RESUMES_DIR.mkdir(parents=True, exist_ok=True)

with open(CANDIDATES, "r", encoding="utf-8") as f:
    candidates = json.load(f)

ok = 0
failed = []

for c in candidates:
    cid  = c["id"]
    name = c["name"]
    safe = name.replace(" ", "_")
    filename = f"{cid}_{safe}_Resume.pdf"
    out_path = RESUMES_DIR / filename

    try:
        pdf_bytes = generate_resume_pdf(c)
        out_path.write_bytes(pdf_bytes)
        # Set the static URL — FastAPI will serve /resumes/<filename>
        c["resume_url"] = f"/resumes/{filename}"
        ok += 1
        print(f"  [{cid}] {name} -> {filename} ({len(pdf_bytes):,} bytes)")
    except Exception as e:
        failed.append((cid, name, str(e)))
        print(f"  [{cid}] {name} FAILED: {e}")

# Write updated candidates.json
with open(CANDIDATES, "w", encoding="utf-8") as f:
    json.dump(candidates, f, indent=2, ensure_ascii=False)

print(f"\nDone: {ok} PDFs generated, {len(failed)} failed.")
if failed:
    for cid, name, err in failed:
        print(f"  FAILED [{cid}] {name}: {err}")
print(f"Resumes saved to: {RESUMES_DIR}")
print("candidates.json updated with resume_url for each candidate.")
