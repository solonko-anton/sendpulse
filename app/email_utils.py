import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email: str, subject: str, content: str, attachment_path: str = None):
    SMTP_SERVER = "smtp-pulse.com"
    SMTP_PORT = 465

    from_email = os.getenv("SENDPULSE_SENDER_EMAIL")
    login_email = os.getenv("LOGIN_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([from_email, login_email, smtp_password]):
        raise ValueError("Missing SMTP credentials")

    print(f"Sending email from {from_email} as {login_email}...")

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    msg.attach(MIMEText(content, "html"))

    if attachment_path:
        attachment_path = os.path.abspath(attachment_path)
        print(f"Checking attachment: {attachment_path}")
        if not os.path.exists(attachment_path):
            raise FileNotFoundError(f"Attachment not found: {attachment_path}")
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            msg.attach(part)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(login_email, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
            print("Email sent!")
    except Exception as e:
        print(f"Error during SMTP send: {e}")
        raise