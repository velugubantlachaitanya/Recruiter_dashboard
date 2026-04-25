# ============================================================
# Email Service — SMTP simulation (Mailhog compatible)
# ============================================================

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))


def build_outreach_email_html(candidate_name: str, role_title: str, body: str) -> str:
    """Generate HTML email for outreach."""
    return f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{ font-family: Inter, Arial, sans-serif; background: #0f0f1e; color: #e0e0ff; padding: 24px; }}
    .card {{ background: #1a1a35; border: 1px solid #3a3a6a; border-radius: 12px; padding: 28px; max-width: 560px; margin: 0 auto; }}
    .header {{ color: #7c6ff7; font-size: 1.1rem; font-weight: 700; margin-bottom: 16px; }}
    .body {{ font-size: 0.9rem; line-height: 1.7; color: #c0c0d8; }}
    .cta {{ display: inline-block; margin-top: 18px; padding: 10px 22px; background: linear-gradient(135deg,#7c6ff7,#5a8cf8); color: #fff; border-radius: 8px; text-decoration: none; font-weight: 600; }}
    .footer {{ margin-top: 20px; font-size: 0.75rem; color: #5a5a7a; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">🚀 Exciting Opportunity: {role_title}</div>
    <div class="body">
      <p>Hi {candidate_name},</p>
      {body.replace(chr(10), '<br>')}
    </div>
    <a href="#" class="cta">View Opportunity →</a>
    <div class="footer">TalentScout AI · Powered by Claude API · Catalyst Hackathon 2026</div>
  </div>
</body>
</html>"""


def send_outreach_email(
    to_email: str,
    candidate_name: str,
    role_title: str,
    email_body: str,
    from_email: str = "scout@talentscout.ai",
) -> dict:
    """
    Send outreach email via SMTP (Mailhog or real SMTP).
    Returns status dict.
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Exciting {role_title} Opportunity — Let's Connect"
        msg["From"] = from_email
        msg["To"] = to_email

        html = build_outreach_email_html(candidate_name, role_title, email_body)
        msg.attach(MIMEText(email_body, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=3) as server:
            server.sendmail(from_email, [to_email], msg.as_string())

        return {"status": "sent", "to": to_email, "via": f"{SMTP_HOST}:{SMTP_PORT}"}

    except Exception as e:
        # In demo mode, just simulate success
        return {"status": "simulated", "to": to_email, "note": str(e)}
