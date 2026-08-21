# just seeing if gmail will actually let us send mail
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

msg = EmailMessage()
msg["Subject"] = "test from the med reminder app"
msg["From"] = os.getenv("EMAIL_ADDRESS")
msg["To"] = os.getenv("EMAIL_ADDRESS")  # emailing myself, easiest way to test
msg.set_content("if you're reading this, smtplib works")

try:
    # 465 is the SSL port, gmail wants this one
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("EMAIL_ADDRESS"), os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(msg)
    print("sent it — go check your inbox")
except Exception as e:
    # usually means the app password is wrong or has spaces in it
    print("didn't send:", e)