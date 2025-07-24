import os
import base64
import requests
import mimetypes
from dotenv import load_dotenv

load_dotenv()

SENDPULSE_API_ID = os.getenv("SENDPULSE_API_ID")
SENDPULSE_API_SECRET = os.getenv("SENDPULSE_API_SECRET")
SENDPULSE_SENDER_EMAIL = os.getenv("SENDPULSE_SENDER_EMAIL")


def get_access_token():
    response = requests.post(
        "https://api.sendpulse.com/oauth/access_token",
        data={
            "grant_type": "client_credentials",
            "client_id": SENDPULSE_API_ID,
            "client_secret": SENDPULSE_API_SECRET
        }
    ).json()

    token = response.get("access_token")
    if not token:
        raise Exception(f"Не вдалося отримати токен: {response}")
    return token


def get_templates():
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get("https://api.sendpulse.com/templates", headers=headers)
    response.raise_for_status()
    templates = response.json()
    return [{"id": tpl["real_id"], "name": tpl["name"]} for tpl in templates]


def send_email(to_email: str, subject: str, template_id: int, variables: dict = None, attachment_path: str = None):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if not SENDPULSE_SENDER_EMAIL:
        raise ValueError("SENDPULSE_SENDER_EMAIL не вказано")

    email_data = {
        "email": {
            "subject": subject,
            "from": {
                "name": "Starzen Team",
                "email": SENDPULSE_SENDER_EMAIL
            },
            "to": [{"email": to_email}],
            "template": {
                "id": template_id,
                "variables": variables or {}
            }
        }
    }

    if attachment_path:
        print(f"Starting attachment processing: {attachment_path}")
        try:
            if not os.path.isfile(attachment_path):
                raise FileNotFoundError(f"Файл не знайдено: {attachment_path}")
            print(f"File exists: {attachment_path}")
            with open(attachment_path, "rb") as f:
                file_bytes = f.read()
            print(f"File bytes read, length: {len(file_bytes)}")
            if len(file_bytes) == 0:
                raise ValueError(f"Файл порожній: {attachment_path}")

            filename = os.path.basename(attachment_path)
            attachment_b64 = base64.b64encode(file_bytes).decode("utf-8")
            file_size = len(file_bytes) / (1024 * 1024)
            print(f"Attachment filename: {filename}, size: {file_size:.2f} MB")
            email_data["email"]["attachments_binary"] = {
                filename: attachment_b64
            }
            print(f"Attachment added to email_data: {email_data}")
        except Exception as e:
            print(f"Error processing attachment: {str(e)}")
            raise 


    response = requests.post("https://api.sendpulse.com/smtp/emails", headers=headers, json=email_data)
    resp_json = response.json()
    print("Send response:", resp_json)

    if not resp_json.get("result", False):
        raise Exception(f"Помилка надсилання: {resp_json}")
