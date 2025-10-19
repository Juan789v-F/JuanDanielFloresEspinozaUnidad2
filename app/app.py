import os
import time
import psycopg2
from flask import Flask, render_template, request, redirect, abort
from dotenv import load_dotenv

# Cargar .env explícitamente
load_dotenv()

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL no está definida. Revisa que .env esté montado y contenga:\n"
        "DATABASE_URL=postgresql://usuario:clave_segura@db:5432/mensajesdb"
    )

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

# 🔧 Ejecutar la inicialización una vez al importar la app (compatible con Flask 3)
try:
    init_db()
except Exception as e:
    # Si no puede inicializar (p. ej. DB aún no lista), fallará con 500 en tiempo de request,
    # pero aquí dejamos rastro claro en logs del contenedor.
    app.logger.exception("Error inicializando la base de datos al inicio: %s", e)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        mensaje = request.form.get("mensaje", "").strip()
        if nombre and mensaje:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO mensajes (nombre, mensaje) VALUES (%s, %s);",
                    (nombre, mensaje)
                )
            conn.close()
        return redirect("/")

    # GET: listar mensajes
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, nombre, mensaje, created_at FROM mensajes ORDER BY created_at DESC;")
        mensajes = cur.fetchall()
    conn.close()
    return render_template("index.html", mensajes=mensajes)
