# seeing if twilio will actually send from python
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))

try:
    msg = client.messages.create(
     body="sms_appointment_reminders",   # trial accounts only take template names, not real text
        from_=os.getenv("TWILIO_NUMBER"),   # trailing underscore because 'from' is a python keyword
        to="+15615739624"                    # your verified number
    )
    print("sent it — check your phone")
except Exception as e:
    # usually a bad token or an unverified 'to' number on trial accounts
    print("didn't send:", e)