from celery import Celery
from .email_utils import send_email
from .config import REDIS_BROKER_URL
import os

celery_app = Celery(
    "worker",
    broker=REDIS_BROKER_URL,
    backend=REDIS_BROKER_URL,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Kyiv",
    enable_utc=True,
)

@celery_app.task
def schedule_email_task(email: str, file_path: str):
    try:
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Attachment not found: {file_path}")
        print(f"Attachment found at: {file_path}")

        send_email(
            to_email=email,
            subject="Your Document is Ready",
            content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Your Document is Ready</title>
                </head>
                <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                    <h2>Your Document is Ready</h2>
                    <p>Hello,</p>
                    <p>Your subscription document is attached. Thank you!</p>
                    <p>Contact: <a href="mailto:support@starzen.app">support@starzen.app</a></p>
                    <p style="font-size: 12px; color: #666;">
                        <a href="https://starzen.app/unsubscribe">Unsubscribe</a>
                    </p>
                </body>
                </html>
            """,
            attachment_path=file_path
        )
        print(f"Email sent to {email}")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise