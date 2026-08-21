# quick sanity check that we can actually reach the database
import os
import mysql.connector
from dotenv import load_dotenv

# grabs everything from .env so no passwords live in the code
load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    print("we're in — connection works")
    conn.close()
except mysql.connector.Error as e:
    # if this fires, check the .env values first, usually the culprit
    print("nope, connection failed:", e)
    