import os
import time
import psycopg2
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection(retries=10, delay=3):
    last_err = None
    for _ in range(retries):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.autocommit = True
            return conn
        except Exception as e:
            last_err = e
            time.sleep(delay)
    raise last_err

def init_db():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
    conn.close()

@app.route("/", methods=["GET"])
def index_get():
    return render_template("index.html")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
