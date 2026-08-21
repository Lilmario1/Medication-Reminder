# reminder.py
# figures out what meds are due right now, hits people up by email + text, writes down what it did

import os
import smtplib
import mysql.connector
from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv
from twilio.rest import Client

# grabs the db + email + twilio creds from .env so nothing's hardcoded
load_dotenv()


def get_db():
    """the one db connection we reuse everywhere"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def check_whats_due():
    """anything scheduled for this exact minute?"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    now = datetime.now().strftime("%H:%M")
    print(f"Checking for meds due at {now}...\n")

    cursor.execute("""
        SELECT p.name, p.email, p.phone,
               m.id, m.med_name, m.dosage, m.reminder_time
        FROM patients p
        JOIN medications m ON p.id = m.patient_id
        WHERE TIME_FORMAT(m.reminder_time, '%H:%i') = %s
    """, (now,))

    due = cursor.fetchall()
    db.close()
    return due


def already_sent_today(med_id, method):
    """did we already hit this one today on this channel? email and sms track separately"""
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM reminders
        WHERE medication_id = %s
          AND method = %s
          AND DATE(sent_at) = CURDATE()
          AND status = 'sent'
    """, (med_id, method))

    count = cursor.fetchone()[0]
    db.close()
    return count > 0


def log_reminder(med_id, method, status):
    """write it down so the next run knows what happened"""
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO reminders (medication_id, sent_at, method, status)
        VALUES (%s, NOW(), %s, %s)
    """, (med_id, method, status))

    db.commit()   # no commit = the insert just vanishes, learned that the hard way
    db.close()


def send_email(med):
    """actually sends the email"""
    first_name = med["name"].split()[0]   # first name only, full name reads like junk mail

    msg = EmailMessage()
    msg["Subject"] = f"Reminder: {med['med_name']}"
    msg["From"] = os.getenv("EMAIL_ADDRESS")
    msg["To"] = med["email"]
    msg.set_content(
        f"Hi {first_name},\n\n"
        f"This is a reminder to take your {med['med_name']} ({med['dosage']}).\n\n"
        f"If you've already taken it, no action needed.\n\n"
        f"Medication Reminder"
    )

    # 465 is the ssl port, gmail wants this one
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("EMAIL_ADDRESS"), os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(msg)


def send_sms(med):
    """texts the patient — trial account so we're stuck with twilio's template for now"""
    client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))

    client.messages.create(
        body="sms_appointment_reminders",   # swap for real text once the account's upgraded
        from_=os.getenv("TWILIO_NUMBER"),
        to=med["phone"]
    )


def try_send(med, method, send_func):
    """one wrapper for both channels so we're not copy-pasting the same try/except twice"""
    if already_sent_today(med["id"], method):
        print(f"  {method}: skipping, already went out today")
        return

    try:
        send_func(med)
        log_reminder(med["id"], method, "sent")
        print(f"  {method}: sent")
    except Exception as e:
        # logging failures too so we can see what broke later
        log_reminder(med["id"], method, "failed")
        print(f"  {method}: failed — {e}")


def send_reminder(med):
    """hit them on both channels"""
    print(f"REMINDER for {med['name']}")
    print(f"  Time to take {med['med_name']} ({med['dosage']})")

    try_send(med, "email", send_email)
    try_send(med, "sms", send_sms)
    print()


# run it
if __name__ == "__main__":
    due_now = check_whats_due()

    if not due_now:
        print("Nothing due right now.")
    else:
        for med in due_now:
            send_reminder(med)