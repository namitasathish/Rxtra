import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

def send_email(info):
    user = os.getenv("EMAIL_USER")
    pwd = os.getenv("EMAIL_PASSWORD")
    recipient_email = info.get("email")

    if not user or not pwd:
        print("Email credentials not found in .env file.")
        return

    if not recipient_email:
        print("No recipient email provided.")
        return

    subject = f"Reminder: Take {info['dosage_mg']}mg {info['medicine']}"
    body = (
        f"Hello,\n\n"
        f"This is your scheduled reminder to take:\n"
        f"- Medicine: {info['medicine']}\n"
        f"- Dosage: {info['dosage_mg']}mg\n"
        f"- Frequency: {info['frequency_per_day']} times/day\n"
        f"- Duration: {info['duration_days']} days\n\n"
        f"Take care!"
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(user, pwd)
            s.sendmail(user, recipient_email, msg.as_string())
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
