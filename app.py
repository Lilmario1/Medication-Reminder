# app.py
# web interface — shows the table, and lets you add patients + meds without touching mysql

from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
from dotenv import load_dotenv

# pulls the DB creds in from .env
load_dotenv()

app = Flask(__name__)


def get_db():
    """the one db connection we reuse everywhere"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


@app.route("/")
def home():
    """the main table — everybody and what they're on"""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.name, p.email, p.phone,
               m.med_name, m.dosage,
               TIME_FORMAT(m.reminder_time, '%h:%i %p') AS reminder_time
        FROM patients p
        JOIN medications m ON p.id = m.patient_id
    """)

    meds = cursor.fetchall()
    db.close()

    return render_template("index.html", meds=meds)


@app.route("/add-patient", methods=["GET", "POST"])
def add_patient():
    """form to add someone new — GET shows it, POST saves it"""
    if request.method == "POST":
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO patients (name, email, phone)
            VALUES (%s, %s, %s)
                """, (
            request.form["name"].strip(),
            request.form["email"].strip(),
            request.form["phone"].strip()
        ))

        db.commit()   # same deal as reminder.py, no commit means nothing saves
        db.close()

        return redirect(url_for("home"))   # kick em back to the table

    return render_template("add_patient.html")


@app.route("/add-med", methods=["GET", "POST"])
def add_med():
    """form to put someone on a med — dropdown picks the patient"""
    db = get_db()

    if request.method == "POST":
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO medications (patient_id, med_name, dosage, reminder_time, frequency)
            VALUES (%s, %s, %s, %s, %s)
               """, (
            request.form["patient_id"],
            request.form["med_name"].strip(),
            request.form["dosage"].strip(),
            request.form["reminder_time"],
            request.form["frequency"].strip()
        ))

        db.commit()
        db.close()

        return redirect(url_for("home"))

    # GET — need the patient list so the dropdown has something in it
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM patients ORDER BY name")
    patients = cursor.fetchall()
    db.close()

    return render_template("add_med.html", patients=patients)


if __name__ == "__main__":
    app.run(debug=True, port=5001)