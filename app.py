import os, sqlite3, uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from config import Config
from utils.qrcode_generator import generate_qr
from utils.pdf_generator import generate_pdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.config.from_object(Config)
app.secret_key = app.config["SECRET_KEY"]

def get_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id TEXT PRIMARY KEY,
            full_name TEXT,
            dob TEXT,
            age INTEGER,
            gender TEXT,
            school TEXT,
            grade TEXT,
            position TEXT,
            height TEXT,
            previous_team TEXT,
            tshirt_size TEXT,

            guardian_name TEXT,
            guardian_relation TEXT,
            guardian_phone1 TEXT,
            guardian_phone2 TEXT,
            guardian_email TEXT,
            guardian_occupation TEXT,

            medical_conditions TEXT,
            injuries TEXT,
            allergies TEXT,
            medication TEXT,
            emergency_contact TEXT,

            skill_level TEXT,
            goals TEXT,

            date TEXT
        )
    """)
    db.commit()
    db.close()

init_db()

@app.route("/health")
def health():
    return "OK"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        reg_id = str(uuid.uuid4())

        db = get_db()
        db.execute("""
            INSERT INTO registrations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            reg_id,
            data["full_name"], data["dob"], data["age"], data["gender"],
            data["school"], data["grade"], data["position"],
            data.get("height"), data.get("previous_team"), data["tshirt_size"],

            data["guardian_name"], data["guardian_relation"],
            data["guardian_phone1"], data.get("guardian_phone2"),
            data.get("guardian_email"), data.get("guardian_occupation"),

            data.get("medical_conditions"), data.get("injuries"),
            data.get("allergies"), data.get("medication"),
            data["emergency_contact"],

            data["skill_level"], data["goals"],
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        ))
        db.commit()
        db.close()

        return redirect(url_for("success", reg_id=reg_id))

    return render_template("register.html")

@app.route("/success/<reg_id>")
def success(reg_id):
    db = get_db()
    reg = db.execute("SELECT * FROM registrations WHERE id=?", (reg_id,)).fetchone()
    db.close()

    qr = generate_qr(reg_id)
    return render_template("success.html", registration=reg, qr_code=qr)

@app.route("/receipt/<reg_id>")
def receipt(reg_id):
    db = get_db()
    reg = db.execute("SELECT * FROM registrations WHERE id=?", (reg_id,)).fetchone()
    db.close()

    qr = generate_qr(reg_id)
    pdf = generate_pdf(dict(reg), qr)
    return send_file(pdf, as_attachment=True, download_name="registration_receipt.pdf")

