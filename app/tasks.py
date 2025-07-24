from celery import Celery
from .email_utils import send_email
from .config import REDIS_BROKER_URL
import os
import base64

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
def schedule_email_task(email: str, file_path: str, plan: str):
    try:
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Attachment not found: {file_path}")
        send_email(
            to_email=email,
            subject="Your Birth Chart is Ready!" if plan == "1" else " Your Soulmate’s Identity is Ready!",
            template_id=35178 if plan == "1" else 35183,
            attachment_path=file_path
        )
    except Exception as e:
        raise

