from dotenv import load_dotenv
import os

load_dotenv()

REDIS_BROKER_URL = os.getenv("REDIS_BROKER_URL", "redis://redis:6379/0")
SENDPULSE_API_ID = os.getenv("SENDPULSE_API_ID", "your_api_id")
SENDPULSE_API_SECRET = os.getenv("SENDPULSE_API_SECRET", "your_api_secret")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
ADDRESSBOOK_ID_1 = os.getenv("ADDRESSBOOK_ID_1", "12345") 
ADDRESSBOOK_ID_2 = os.getenv("ADDRESSBOOK_ID_2", "67890")