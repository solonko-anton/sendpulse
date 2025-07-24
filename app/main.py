from fastapi import FastAPI, HTTPException
from fastapi import File, UploadFile, Form
from pydantic import BaseModel, EmailStr
from .email_utils import send_email
from .tasks import schedule_email_task
from .config import SENDPULSE_API_ID, SENDPULSE_API_SECRET, ADDRESSBOOK_ID_1, ADDRESSBOOK_ID_2
from pysendpulse.pysendpulse import PySendPulse
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import asyncio
import os

app = FastAPI()

executor = ThreadPoolExecutor()

SENDPULSE_SENDER_EMAIL = os.getenv("SENDPULSE_SENDER_EMAIL")
LOGIN_EMAIL = os.getenv("LOGIN_EMAIL") 
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

SPApiProxy = PySendPulse(SENDPULSE_API_ID, SENDPULSE_API_SECRET)

class EmailRequest(BaseModel):
    email: EmailStr
    plan: str = "1" 

def add_to_addressbook(email: str, plan: str):
    addressbook_id = ADDRESSBOOK_ID_1 if plan == "1" else ADDRESSBOOK_ID_2
    variables = {"email": email, "plan": plan}
    response = SPApiProxy.add_emails_to_addressbook(addressbook_id, [variables])
    if not response.get("result", False):
        raise Exception(f"Failed to add {email} to addressbook {addressbook_id}: {response}")
    
@app.post("/subscribe/")
async def subscribe(
    email: EmailStr = Form(...),
    plan: str = Form("1"),
    file: UploadFile = File(...)
):
    try:
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{email}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        add_to_addressbook(email, plan)

        selected_template = 35175

        variables = {
            "email": email,
            "plan": plan,
        }

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            executor,
            partial(
                send_email,
                to_email=email,
                subject="Your Birth Chart is in Progress! Here’s What’s Next" if plan == "1" else "Your Soulmate Reading is in Progress! Here’s What’s Next",
                template_id=selected_template if plan == "1" else 35180,
                variables=variables,
            )
        )

        schedule_email_task.apply_async(args=[email, file_path, plan], countdown=24*3600)

        return {
            "message": f"Email на {email} надіслано.",
            "template_id": selected_template
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка: {str(e)}")
