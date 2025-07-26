import os
import base64
import requests
import os
import subprocess
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


def compress_pdf(input_path, output_path, target_size_mb=0.95):

    try:
        gs_command = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/prepress",  
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            input_path
        ]

        subprocess.run(gs_command, check=True)

    except Exception as e:
        print(f"Ошибка при сжатии: {e}")
        return False

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
        try:
            if not os.path.isfile(attachment_path):
                raise FileNotFoundError(f"Файл не знайдено: {attachment_path}")
            
            original_size = os.path.getsize(attachment_path) / (1024 * 1024)  # Мб
            print(f"Original PDF size: {original_size:.2f} MB")
            compressed_path = attachment_path.replace(".pdf", "_compressed.pdf")

            if original_size > 0.75:
                compress_pdf(attachment_path, compressed_path)

            compressed_size = os.path.getsize(compressed_path) / (1024 * 1024)
            print(f"Compressed PDF size after first pass: {compressed_size:.2f} MB")

            with open(compressed_path, "rb") as f:
                file_bytes = f.read()

            filename = os.path.basename(attachment_path)
            attachment_b64 = base64.b64encode(file_bytes).decode("utf-8")

            email_data["email"]["attachments_binary"] = {
                filename: attachment_b64
            }
        except Exception as e:
            raise


    response = requests.post("https://api.sendpulse.com/smtp/emails", headers=headers, json=email_data)
    resp_json = response.json()
    print("Send response:", resp_json)

    if not resp_json.get("result", False):
        raise Exception(f"Помилка надсилання: {resp_json}")
