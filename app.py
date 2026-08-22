# app.py
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
    )
@app.route("/")
def home():
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
        db.commit()
        db.close()
        return redirect(url_for("home"))
    return render_template("add_patient.html")

@app.route("/add-med", methods=["GET", "POST"])
def add_med():
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

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM patients ORDER BY name")
    patients = cursor.fetchall()
    db.close()
    return render_template("add_med.html", patients=patients)

@app.route('/debug')
def debug():
    return "App is running!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    