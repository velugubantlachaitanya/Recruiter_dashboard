"""Run this script once to generate candidates.json"""
import json, random

TIER1 = ["IIT Bombay","IIT Delhi","IIT Madras","IIT Hyderabad","IIT Bangalore","NIT Warangal","BITS Pilani","IIIT Hyderabad"]
TIER2 = ["VIT Vellore","Manipal University","SRM University","Amrita University","IIIT Bangalore"]
TIER3 = ["Osmania University","Andhra University","JNTU Hyderabad","Anna University","Pune University"]

NAMES = ["Arjun Sharma","Priya Menon","Rahul Gupta","Sneha Reddy","Karthik Rajan","Divya Nair","Aditya Kumar","Pooja Iyer","Vikram Singh","Ananya Krishnan","Rohan Patel","Meera Joshi","Suresh Babu","Lakshmi Devi","Nikhil Jain","Sanjana Rao","Deepak Verma","Kavya Pillai","Abhinav Tiwari","Shreya Agarwal","Manish Choudhary","Ritika Sharma","Prasad Kulkarni","Swathi Bhat","Harish Nambiar","Geetha Sundaram","Ravi Shankar","Uma Mehta","Vinay Desai","Pallavi Gopal","Arun Nair","Shivangi Yadav","Balaji Venkat","Nandita Roy","Kartik Malhotra","Revathi Kumar","Siddharth Ghosh","Lavanya Subramanian","Tarun Mittal","Chitra Bose","Varun Kapoor","Rekha Iyer","Sandeep Rajan","Jyoti Patel","Madan Kumar","Asha Reddy","Naveen Pillai","Sunita Rao","Gaurav Tiwari","Bhavna Sharma"]

ML_SKILLS = ["Python","PyTorch","TensorFlow","LLMs","Transformers","scikit-learn","NLP","Computer Vision","MLflow","Kubernetes","FastAPI","RAG","LangChain","Hugging Face","CUDA"]
BE_SKILLS  = ["Python","FastAPI","Node.js","Django","Go","Java","Spring Boot","PostgreSQL","MongoDB","Redis","Docker","Kubernetes","REST APIs","GraphQL","Kafka"]
FE_SKILLS  = ["React","TypeScript","Vue.js","Angular","Next.js","TailwindCSS","JavaScript","CSS","Redux","Webpack"]
CLOUD_SKILLS=["AWS","GCP","Azure","Terraform","Docker","Kubernetes","CI/CD","Jenkins","Ansible","Linux"]
DATA_SKILLS = ["Python","SQL","Spark","Kafka","Airflow","dbt","Tableau","Power BI","Pandas","NumPy"]

ALL_CITIES = ["Hyderabad, India","Bangalore, India","Mumbai, India","Delhi, India","Pune, India","Chennai, India","Kolkata, India","Remote, India"]

random.seed(42)

candidates = []
for i, name in enumerate(NAMES):
    idx = i + 1
    tier_roll = random.random()
    if tier_roll < 0.25:
        inst = random.choice(TIER1); tier = 1
    elif tier_roll < 0.55:
        inst = random.choice(TIER2); tier = 2
    else:
        inst = random.choice(TIER3); tier = 3

    skill_pool = random.choice([ML_SKILLS, BE_SKILLS, FE_SKILLS, CLOUD_SKILLS, DATA_SKILLS])
    num_skills = random.randint(5, 10)
    skills = random.sample(skill_pool, min(num_skills, len(skill_pool)))

    exp = random.randint(1, 12)
    city = random.choice(ALL_CITIES)
    emp = random.choice(["Full-time","Full-time","Full-time","Contract"])

    # Pre-seed engagement signals
    has_os = random.random() < 0.4
    eng = {
        "applied_to_job": random.random() < 0.7,
        "responded_to_outreach": False,  # set by engagement agent
        "submitted_video_demo": random.random() < 0.3,
        "completed_assessment": random.random() < 0.35,
        "passed_assessment": random.random() < 0.25,
        "interview_scheduled": random.random() < 0.2,
        "has_open_source": has_os,
    }

    os_contrib = random.sample(["huggingface/transformers","langchain","fastapi","scikit-learn","pytorch","tensorflow","react","django","flask","pandas"], random.randint(0,3)) if has_os else []

    c = {
        "id": f"C{idx:03d}",
        "name": name,
        "email": name.lower().replace(" ",".")[:20] + f"{idx}@example.com",
        "location": city,
        "skills": skills,
        "experience_years": exp,
        "employment_type": emp,
        "education": {"degree": "B.Tech Computer Science", "institution": inst, "tier": tier},
        "projects": [{"name": f"Project Alpha {idx}", "description": "Production ML/software system", "is_real_world": True, "impact": f"Improved efficiency by {random.randint(15,60)}%"}],
        "open_source_contributions": os_contrib,
        "portfolio_url": f"https://github.com/{name.lower().replace(' ','')}{idx}",
        "video_intro_url": f"https://loom.com/v/{idx}" if eng["submitted_video_demo"] else None,
        "resume_url": f"https://example.com/resume/{idx}.pdf",
        "engagement_signals": eng,
    }
    candidates.append(c)

out = "c:\\Users\\chait\\OneDrive\\Desktop\\AI-Powered Talent Scouting & Engagement Agent\\backend\\data\\candidates.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(candidates, f, indent=2)
print(f"Generated {len(candidates)} candidates -> {out}")
