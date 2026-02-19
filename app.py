from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import sqlite3
import uuid
from datetime import datetime
from io import BytesIO

app = Flask(__name__)
app.secret_key = "super-secret-key"

DATABASE = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS registrations (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            dob TEXT,
            gender TEXT,
            occupation TEXT,
            city TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


@app.route("/health")
def health():
    return "OK", 200


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        reg_id = str(uuid.uuid4())

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO registrations
            (id, name, email, phone, dob, gender, occupation, city, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                reg_id,
                request.form["name"],
                request.form["email"],
                request.form["phone"],
                request.form["dob"],
                request.form["gender"],
                request.form["occupation"],
                request.form["city"],
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
        conn.close()

        flash("Registration successful!")
        return redirect(url_for("receipt", reg_id=reg_id))

    return render_template("register.html")


@app.route("/receipt/<reg_id>")
def receipt(reg_id):
    conn = get_db_connection()
    reg = conn.execute(
        "SELECT * FROM registrations WHERE id = ?", (reg_id,)
    ).fetchone()
    conn.close()

    if not reg:
        return "Registration not found", 404

    return render_template("receipt.html", registration=reg)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid credentials")

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    regs = conn.execute("SELECT * FROM registrations").fetchall()
    conn.close()

    return render_template("admin_dashboard.html", registrations=regs)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))
