"""
Generates 100 diverse candidates across 13 domains with Indian names.
Run: python generate_candidates.py
Output: data/candidates.json
"""
import json, random
from pathlib import Path

random.seed(42)

# ── Domain definitions ────────────────────────────────────────────────────────

DOMAINS = {
    "ML/AI Engineer": {
        "skills_pool": ["Python","PyTorch","TensorFlow","scikit-learn","HuggingFace","LangChain",
                        "MLflow","FastAPI","AWS SageMaker","Kubernetes","NLP","Computer Vision",
                        "RAG","RLHF","LLM Fine-tuning","Pandas","NumPy","Docker","Spark","Airflow"],
        "preferred": ["Kubernetes","Docker","AWS","GCP","Azure","Kafka","Ray"],
        "projects_pool": [
            "Built a RAG-based document QA system using LangChain and FAISS",
            "Fine-tuned LLaMA-2 on domain-specific legal corpus with RLHF",
            "Deployed real-time fraud detection model on AWS SageMaker (99.1% AUC)",
            "Developed multilingual NER pipeline using HuggingFace Transformers",
            "Built recommendation engine serving 2M+ users on GCP Vertex AI",
            "Created open-source MLflow plugin for experiment tracking",
            "Designed vision transformer for medical image segmentation",
            "Built LLM-powered code review bot integrated with GitHub Actions",
            "Developed time-series anomaly detection for IoT sensor data",
            "Trained multi-modal model combining text and image for e-commerce search",
        ],
        "count": 12,
    },
    "Frontend Developer": {
        "skills_pool": ["React","TypeScript","Vue.js","Next.js","TailwindCSS","GraphQL","Redux",
                        "Webpack","Vite","Jest","Cypress","HTML5","CSS3","Figma","Storybook",
                        "Angular","Svelte","Three.js","WebSockets","PWA"],
        "preferred": ["Next.js","Svelte","Three.js","WebAssembly","Micro-frontends"],
        "projects_pool": [
            "Built a real-time collaborative whiteboard app using React and WebSockets",
            "Developed a design system with 80+ Storybook components used across 5 products",
            "Created a PWA for offline-first task management with 50k+ users",
            "Migrated legacy jQuery app to React, reducing bundle size by 60%",
            "Built interactive 3D product configurator using Three.js",
            "Developed micro-frontend architecture for enterprise dashboard",
            "Created accessible UI library following WCAG 2.1 AA standards",
            "Built real-time analytics dashboard with D3.js and WebSockets",
        ],
        "count": 10,
    },
    "Backend Developer": {
        "skills_pool": ["Python","FastAPI","Django","Go","Java","Spring Boot","Node.js","PostgreSQL",
                        "Redis","Docker","Kafka","gRPC","REST APIs","MongoDB","Elasticsearch",
                        "RabbitMQ","AWS Lambda","Terraform","Nginx","MySQL"],
        "preferred": ["Go","gRPC","Kafka","Terraform","Kubernetes","AWS"],
        "projects_pool": [
            "Designed microservices architecture handling 500k req/day using FastAPI and Kafka",
            "Built high-throughput payment processing service in Go (10k TPS)",
            "Created distributed task queue using RabbitMQ and Celery",
            "Developed REST API gateway with JWT auth, rate limiting and caching (Redis)",
            "Built event-driven order management system with Spring Boot and Kafka",
            "Implemented CQRS pattern for e-commerce platform with 1M+ SKUs",
            "Designed database sharding strategy reducing query latency by 70%",
            "Built webhook delivery system with retry logic and dead-letter queues",
        ],
        "count": 10,
    },
    "Full Stack Developer": {
        "skills_pool": ["React","Node.js","TypeScript","PostgreSQL","Docker","GraphQL","Next.js",
                        "MongoDB","Redis","AWS","Python","FastAPI","TailwindCSS","Prisma","tRPC",
                        "Supabase","Firebase","Vercel","Nginx","CI/CD"],
        "preferred": ["tRPC","Supabase","Turborepo","Bun","Edge Functions"],
        "projects_pool": [
            "Built SaaS analytics platform (Next.js + FastAPI) with 10k+ users",
            "Developed full-stack e-commerce app with real-time inventory updates",
            "Created open-source project management tool (React + Node.js, 3k GitHub stars)",
            "Built multi-tenant CRM platform with role-based access control",
            "Developed real-time chat application using Socket.io and React",
            "Created headless CMS with Next.js frontend and Strapi backend",
            "Built fintech dashboard with live stock prices and portfolio tracking",
            "Developed food delivery app with real-time order tracking",
        ],
        "count": 10,
    },
    "Data Scientist": {
        "skills_pool": ["Python","R","SQL","Pandas","NumPy","scikit-learn","XGBoost","LightGBM",
                        "Tableau","Power BI","Spark","A/B Testing","Statistics","Bayesian Methods",
                        "Feature Engineering","AutoML","SHAP","Plotly","SciPy","Statsmodels"],
        "preferred": ["Databricks","Snowflake","dbt","MLflow","Metabase"],
        "projects_pool": [
            "Built customer churn prediction model (AUC 0.94) saving $2M/yr",
            "Designed A/B testing framework reducing experiment runtime by 40%",
            "Created demand forecasting model for 10k+ SKUs using LightGBM",
            "Developed NPS driver analysis using NLP and topic modelling",
            "Built credit risk scoring model for NBFC with 95% accuracy",
            "Created cohort analysis tool for product team using Tableau",
            "Designed propensity model for targeted marketing campaigns",
            "Built time-series sales forecasting with Prophet and ensemble methods",
        ],
        "count": 8,
    },
    "DevOps/Cloud Engineer": {
        "skills_pool": ["AWS","GCP","Azure","Kubernetes","Terraform","Docker","CI/CD","Jenkins",
                        "GitHub Actions","Ansible","Prometheus","Grafana","Helm","Istio","ArgoCD",
                        "ELK Stack","Linux","Bash","Python","Vault"],
        "preferred": ["ArgoCD","Istio","Crossplane","OpenTelemetry","Pulumi"],
        "projects_pool": [
            "Designed multi-region Kubernetes cluster handling 1M+ daily deployments",
            "Built GitOps pipeline with ArgoCD reducing deploy time from 2hr to 10min",
            "Implemented zero-downtime blue-green deployment strategy on AWS EKS",
            "Created infrastructure-as-code for 200+ microservices using Terraform",
            "Built cost optimization tool saving $300k/yr on cloud spend",
            "Designed observability stack with Prometheus, Grafana and Jaeger",
            "Migrated monolith to Kubernetes cutting infra costs by 45%",
            "Built self-healing infrastructure with auto-scaling and chaos engineering",
        ],
        "count": 8,
    },
    "Mobile Developer": {
        "skills_pool": ["Flutter","Dart","React Native","Swift","Kotlin","Android","iOS","Firebase",
                        "GraphQL","REST APIs","SQLite","BLoC","Provider","Riverpod","Jetpack Compose",
                        "SwiftUI","Fastlane","App Store Connect","Push Notifications","In-App Purchases"],
        "preferred": ["Jetpack Compose","SwiftUI","Fastlane","Detox","Maestro"],
        "projects_pool": [
            "Built Flutter e-commerce app with 500k+ downloads on Play Store",
            "Developed cross-platform fintech app (React Native) with biometric auth",
            "Created iOS health tracking app using HealthKit and CoreML",
            "Built real-time ride-sharing app with live location using Google Maps SDK",
            "Developed Flutter-based EdTech app with offline video playback",
            "Created Android app with AR product try-on using ARCore",
            "Built multi-language Flutter app supporting 15 Indian languages",
            "Developed iOS social networking app with Stories feature (SwiftUI)",
        ],
        "count": 8,
    },
    "Data Engineer": {
        "skills_pool": ["Python","SQL","Apache Spark","Kafka","Airflow","dbt","Snowflake","BigQuery",
                        "Databricks","AWS Glue","Delta Lake","Flink","Hadoop","Hive","Presto",
                        "Redshift","Elasticsearch","Terraform","Docker","Kubernetes"],
        "preferred": ["Iceberg","Trino","Dagster","DuckDB","MotherDuck"],
        "projects_pool": [
            "Built real-time data pipeline processing 5TB/day using Kafka and Spark",
            "Designed medallion architecture on Databricks for unified data lakehouse",
            "Created dbt transformation layer reducing data freshness from 6hr to 15min",
            "Built CDC pipeline from 50+ source systems using Debezium and Kafka",
            "Developed data quality framework with Great Expectations",
            "Migrated on-prem Hadoop cluster to Snowflake cutting costs by 55%",
            "Built ML feature store serving 200+ features for 10 ML models",
            "Designed streaming analytics platform for real-time ad bidding",
        ],
        "count": 8,
    },
    "Cybersecurity Engineer": {
        "skills_pool": ["Penetration Testing","Python","SIEM","Splunk","Wireshark","Metasploit",
                        "Burp Suite","OWASP","Zero Trust","IAM","SOC","Incident Response",
                        "Threat Modelling","CTF","Linux","Network Security","SAST/DAST",
                        "Cryptography","Firewall","PKI"],
        "preferred": ["Wazuh","Snort","Zeek","MITRE ATT&CK","SOAR"],
        "projects_pool": [
            "Conducted red team assessment discovering 23 critical vulnerabilities",
            "Built SIEM dashboard detecting insider threats in real-time",
            "Developed automated vulnerability scanner for cloud infrastructure",
            "Led incident response for ransomware attack, recovered systems in 4hr",
            "Implemented zero-trust architecture for 5000-employee org",
            "Created threat intelligence platform aggregating 50+ OSINT feeds",
        ],
        "count": 6,
    },
    "Blockchain Developer": {
        "skills_pool": ["Solidity","Ethereum","Web3.js","Ethers.js","Hardhat","Truffle","IPFS",
                        "React","TypeScript","Smart Contracts","DeFi","NFT","Chainlink","Layer 2",
                        "Rust","Solana","Polygon","OpenZeppelin","The Graph","MetaMask"],
        "preferred": ["ZK-proofs","StarkNet","Foundry","Anchor","Cairo"],
        "projects_pool": [
            "Built DeFi lending protocol with $10M+ TVL on Ethereum mainnet",
            "Developed NFT marketplace with royalty enforcement using ERC-2981",
            "Created cross-chain bridge for EVM-compatible networks",
            "Built DAO governance smart contracts with quadratic voting",
            "Developed on-chain identity verification using zero-knowledge proofs",
        ],
        "count": 5,
    },
    "QA Engineer": {
        "skills_pool": ["Selenium","Cypress","Playwright","Jest","PyTest","Postman","JMeter",
                        "TestNG","Appium","BDD/Gherkin","API Testing","Load Testing","Python",
                        "Java","CI/CD","Docker","JIRA","SQL","Performance Testing","Accessibility Testing"],
        "preferred": ["Playwright","k6","Contract Testing","Chaos Testing","Allure"],
        "projects_pool": [
            "Built end-to-end test suite (1200+ tests) with Playwright reducing regression time by 80%",
            "Designed API contract testing framework using Pact",
            "Created performance testing suite identifying bottleneck causing 30% latency",
            "Built visual regression testing pipeline integrated with CI/CD",
            "Developed mobile test automation framework with Appium for 3 platforms",
        ],
        "count": 5,
    },
    "UI/UX Designer": {
        "skills_pool": ["Figma","Adobe XD","Sketch","Prototyping","User Research","Usability Testing",
                        "Design Systems","Wireframing","Accessibility","HTML/CSS","Framer","Miro",
                        "Information Architecture","Motion Design","Lottie","A/B Testing","Hotjar",
                        "Design Tokens","Component Libraries","Design Ops"],
        "preferred": ["Framer","Spline","ProtoPie","UX Writing","Service Design"],
        "projects_pool": [
            "Redesigned checkout flow increasing conversions by 34% (A/B tested)",
            "Built design system with 120+ components used by 8 product teams",
            "Conducted 40-user research study reshaping product roadmap",
            "Created accessibility-first design language (WCAG 2.1 AA compliant)",
            "Designed onboarding flow reducing drop-off by 52% using prototyping",
        ],
        "count": 5,
    },
    "Product Manager": {
        "skills_pool": ["Product Strategy","Roadmapping","SQL","Figma","JIRA","Data Analysis",
                        "OKRs","User Stories","Stakeholder Management","A/B Testing","GTM Strategy",
                        "Agile","Scrum","Market Research","Competitive Analysis","Python","Tableau",
                        "Customer Interviews","Prioritization Frameworks","Growth Hacking"],
        "preferred": ["Amplitude","Mixpanel","Notion","Productboard","Pendo"],
        "projects_pool": [
            "Led 0→1 product launch reaching 100k users in 6 months",
            "Drove 45% increase in DAU through feature discovery improvements",
            "Managed cross-functional team of 15 to ship payments product in 3 months",
            "Defined pricing strategy increasing ARPU by 28%",
            "Built self-serve onboarding reducing time-to-value from 7 days to 1 day",
        ],
        "count": 5,
    },
}

# ── Indian names per domain ───────────────────────────────────────────────────

NAMES = {
    "ML/AI Engineer": [
        "Arjun Sharma","Priya Nair","Kiran Reddy","Ananya Krishnan","Rahul Gupta",
        "Sneha Iyer","Vikram Malhotra","Divya Menon","Siddharth Joshi","Neha Agarwal",
        "Aditya Rao","Kavitha Subramanian",
    ],
    "Frontend Developer": [
        "Rohan Verma","Pooja Pillai","Akash Kumar","Swati Desai","Nikhil Bhat",
        "Deepika Nambiar","Harish Patel","Revathi Chandrasekaran","Ankit Mehta","Simran Kaur",
    ],
    "Backend Developer": [
        "Rajesh Yadav","Meghna Srinivasan","Gaurav Tiwari","Latha Murthy","Abhishek Pandey",
        "Varsha Hegde","Suraj Bhatt","Manisha Jain","Prasad Kulkarni","Rithika Natarajan",
    ],
    "Full Stack Developer": [
        "Vivek Singh","Padmaja Venkataraman","Tarun Saxena","Nithya Krishnamurthy","Saurabh Chaudhary",
        "Anusha Gopalan","Ritesh Mishra","Keerthi Raghavan","Manas Tripathi","Aparna Balakrishnan",
    ],
    "Data Scientist": [
        "Rohit Mahajan","Sindhu Parthasarathy","Ajay Nair","Deepa Subramaniam",
        "Shubham Gupta","Preethi Rajan","Sanjay Kulkarni","Lakshmi Narayanan",
    ],
    "DevOps/Cloud Engineer": [
        "Arun Pillai","Madhavi Rao","Naveen Reddy","Shweta Acharya",
        "Ravi Shankar","Indira Mohan","Suresh Babu","Poornima Venkatesh",
    ],
    "Mobile Developer": [
        "Kartik Sharma","Bhavana Krishnan","Suraj Patel","Anjali Nair",
        "Dev Verma","Sowmya Rajan","Nitin Joshi","Ramya Subramanian",
    ],
    "Data Engineer": [
        "Praveen Kumar","Archana Pillai","Mohit Sharma","Swetha Iyer",
        "Varun Bhat","Girija Menon","Navneet Singh","Shalini Rao",
    ],
    "Cybersecurity Engineer": [
        "Rajan Mehta","Kavya Nair","Sudheer Reddy","Priya Venkatesh","Aakash Singh","Deepak Pandey",
    ],
    "Blockchain Developer": [
        "Roshan Kumar","Nithila Krishnan","Sai Kiran","Aditi Sharma","Arnav Bose",
    ],
    "QA Engineer": [
        "Sruthi Pillai","Manoj Yadav","Pradeep Nair","Anitha Subramanian","Harsha Varma",
    ],
    "UI/UX Designer": [
        "Vishal Kapoor","Ranjitha Menon","Akhil Reddy","Neethu Thomas","Sumit Chauhan",
    ],
    "Product Manager": [
        "Ashwin Nair","Shilpa Rao","Vikrant Sharma","Roshni Pillai","Arun Balaji",
    ],
}

LOCATIONS = ["Hyderabad","Bengaluru","Chennai","Pune","Mumbai","Delhi NCR","Kolkata","Ahmedabad","Jaipur","Remote"]
EDUCATION_TIERS = [
    {"degree":"B.Tech","field":"Computer Science","institution":"IIT Hyderabad","tier":"tier1"},
    {"degree":"B.Tech","field":"Computer Science","institution":"NIT Warangal","tier":"tier2"},
    {"degree":"M.Tech","field":"AI & ML","institution":"IIT Bombay","tier":"tier1"},
    {"degree":"B.E.","field":"Information Technology","institution":"BITS Pilani","tier":"tier1"},
    {"degree":"B.Tech","field":"Computer Science","institution":"IIIT Hyderabad","tier":"tier1"},
    {"degree":"M.S.","field":"Computer Science","institution":"IISc Bengaluru","tier":"tier1"},
    {"degree":"B.Tech","field":"Electronics","institution":"VIT Vellore","tier":"tier2"},
    {"degree":"B.E.","field":"Computer Science","institution":"Anna University","tier":"tier2"},
    {"degree":"MCA","field":"Computer Applications","institution":"Osmania University","tier":"tier3"},
    {"degree":"B.Tech","field":"Information Technology","institution":"Manipal University","tier":"tier2"},
]

def make_email(name):
    parts = name.lower().split()
    return f"{parts[0]}.{parts[-1]}@{''.join(random.choices(['gmail','outlook','yahoo','proton'], weights=[5,3,1,1]))}.com"

def make_github(name):
    slug = name.lower().replace(" ", "-")
    return f"https://github.com/{slug}"

def make_linkedin(name):
    slug = name.lower().replace(" ", "-")
    return f"https://linkedin.com/in/{slug}"

COMPANIES = [
    "Flipkart","Swiggy","Zomato","CRED","Razorpay","Groww","Meesho","Ola","Paytm",
    "PhonePe","Juspay","Browserstack","Freshworks","Zoho","Unacademy","Google","Microsoft",
    "Amazon","Atlassian","Thoughtworks","Nutanix","Salesforce","Adobe","Walmart Labs","Uber"
]

OSS_OPTIONS = [
    "Maintainer of popular open-source library (2k+ GitHub stars)",
    "Core contributor to Apache open-source project (50+ PRs merged)",
    "Active contributor to HuggingFace Transformers library",
    "Published open-source CLI tool with 1k+ weekly downloads on PyPI",
    "Top 3% Stack Overflow contributor (5k+ reputation)",
    "Created widely-used GitHub Action with 500+ stars",
    "Contributed to LangChain, FastAPI, and scikit-learn repositories",
    "Organizer of local tech meetup with 200+ members",
]

def pick_skills(pool, n_required=6, n_preferred=3):
    required = random.sample(pool[:12], min(n_required, len(pool[:12])))
    preferred = random.sample(pool[12:] if len(pool) > 12 else pool, min(n_preferred, max(0, len(pool)-12)))
    return list(set(required + preferred))

# ── Tier profile definitions ──────────────────────────────────────────────────
# Each candidate gets a tier that controls YOE, education, n_projects, OSS
# Distribution: 20 five-star, 25 four-star, 30 three-star, 15 two-star, 10 one-star

TIER_PROFILES = [
    # (label, yoe_range, edu_weights, n_projects, oss_prob, n_skills)
    ("⭐⭐⭐⭐⭐",  (8, 14), [0.85, 0.15, 0.00], 4, 0.90, (9, 12)),  # 5-star
    ("⭐⭐⭐⭐",   (5,  9), [0.55, 0.40, 0.05], 3, 0.65, (7, 10)),  # 4-star
    ("⭐⭐⭐",    (3,  6), [0.30, 0.55, 0.15], 2, 0.40, (6,  9)),  # 3-star
    ("⭐⭐",     (1,  4), [0.10, 0.50, 0.40], 1, 0.20, (5,  7)),  # 2-star
    ("⭐",      (0,  2), [0.05, 0.35, 0.60], 0, 0.05, (3,  5)),  # 1-star
]
TIER_COUNTS = [20, 25, 30, 15, 10]

# Flatten: assign a tier to each candidate index (0-99)
tier_assignments = []
for t_idx, count in enumerate(TIER_COUNTS):
    tier_assignments.extend([t_idx] * count)
random.shuffle(tier_assignments)

TIER_EDUS = [
    # tier1-heavy options
    [e for e in EDUCATION_TIERS if e["tier"] == "tier1"],
    EDUCATION_TIERS,
    [e for e in EDUCATION_TIERS if e["tier"] in ("tier2", "tier3")],
]

# ── Generate candidates ───────────────────────────────────────────────────────

candidates = []
candidate_num = 1
global_idx = 0

for domain, cfg in DOMAINS.items():
    names = NAMES[domain]
    for i, name in enumerate(names[:cfg["count"]]):
        cid = f"C{candidate_num:03d}"
        t_idx   = tier_assignments[global_idx % len(tier_assignments)]
        t_label, yoe_range, edu_weights, n_proj_target, oss_prob, skill_range = TIER_PROFILES[t_idx]

        yoe     = random.randint(*yoe_range)
        n_skills = random.randint(*skill_range)
        skills  = pick_skills(cfg["skills_pool"], n_required=min(n_skills, 10), n_preferred=max(0, min(3, n_skills - 5)))

        # Projects — higher tiers get more impactful project descriptions
        pool_size = len(cfg["projects_pool"])
        n_proj    = min(n_proj_target, pool_size)
        chosen_projects = random.sample(cfg["projects_pool"], n_proj) if n_proj > 0 else []

        # Education weighted by tier
        edu_pool_idx = random.choices([0, 1, 2], weights=edu_weights)[0]
        edu_pool     = TIER_EDUS[edu_pool_idx]
        education    = random.choice(edu_pool if edu_pool else EDUCATION_TIERS)

        # OSS contributions
        open_source = []
        if random.random() < oss_prob:
            n_oss = 2 if t_idx == 0 else 1
            open_source = random.sample(OSS_OPTIONS, min(n_oss, len(OSS_OPTIONS)))

        location = random.choice(LOCATIONS)

        candidate = {
            "id": cid,
            "name": name,
            "email": make_email(name),
            "phone": f"+91-{random.randint(7000000000,9999999999)}",
            "location": location,
            "domain": domain,
            "tier_label": t_label,
            "experience_years": yoe,
            "skills": skills,
            "education": {
                "degree": education["degree"],
                "field": education["field"],
                "institution": education["institution"],
                "tier": education["tier"],
            },
            "current_role": f"{domain} at {random.choice(COMPANIES)}",
            "real_world_projects": [
                {"title": p.split(" using")[0].split(" with")[0][:55], "description": p}
                for p in chosen_projects
            ],
            "open_source_contributions": open_source,
            "resume_url": "",
            "portfolio_url": make_github(name),
            "linkedin_url": make_linkedin(name),
            "engagement_signals": {
                "responded_to_outreach": t_idx <= 1 or random.random() > 0.4,
                "visited_career_page":   t_idx <= 2 or random.random() > 0.5,
                "applied_directly":      t_idx == 0 or random.random() > 0.6,
                "has_open_source":       len(open_source) > 0,
                "referral":              t_idx <= 1 and random.random() > 0.5,
            },
            "interview_score": None,
            "interview_passed": None,
        }
        candidates.append(candidate)
        candidate_num += 1
        global_idx += 1

out = Path(__file__).parent / "data" / "candidates.json"
out.parent.mkdir(exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump(candidates, f, indent=2, ensure_ascii=False)

print(f"Generated {len(candidates)} candidates -> {out}")
tier_counts = {}
for c in candidates:
    tier_counts[c["tier_label"]] = tier_counts.get(c["tier_label"], 0) + 1
for t in ["5-star","4-star","3-star","2-star","1-star"]:
    star_label = {"5-star":"⭐⭐⭐⭐⭐","4-star":"⭐⭐⭐⭐","3-star":"⭐⭐⭐","2-star":"⭐⭐","1-star":"⭐"}[t]
    cnt = tier_counts.get(star_label, 0)
    print(f"  {t} ({star_label}): {cnt} candidates")
