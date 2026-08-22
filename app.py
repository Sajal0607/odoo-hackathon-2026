""" DAY FLOW - HUMAN RESOURCE MANAGEMENT SYSTEM 
----------------------------------------------------
Run with:
    python app.py 
in the terminal to start the application.

the first run will automatcally create the database file database.db 
using schema.sql file.
and seed one demo Admin account.
"""
import os
import sqlite3
from datetime import date, datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, g 
)
from werkzeug.security import generate_password_hash, check_password_hash
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

app= Flask(__name__)
app.secret_key = "dayflow-hackathon-secret-key-change-me"
def get_db():
    """ this function opens a new databse if there is none yet formed"""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row 
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(exception = None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
        
def init_db() : 
    """ Create tables (if they don't exist) and seed the database with a demo Admin account"""
    first_time = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
        
    if first_time:
        conn.execute(
            """INSERT INTO users 
                (employee_id, name, email, password_hash, role, job_title, department, join_date) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "ADMIN001",
                "Demo Admin", 
                "admin@dayflow.com",
                generate_password_hash("admin123"),
                "Admin",
                "HR Manager",
                "Human Resources",
                date.today().isoformat(),
            ),
        )
        conn.commit()
        print("="* 60)
        print("Seeded demo Admin account:")
        print("     Email: admin@dayflow.com")
        print("Password: admin123")
        print("="* 60)
    conn.close()
#--------------------------------------------
# Auth helpers / decorators
#--------------------------------------------

def login_required(view):
    @wraps(view)
    def wrapped(*args,**kwargs):
        if "user_id" not in session:
            flash("Please sign in to continue.", "error")
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped

def admin_required(view):
    @wraps(view)
    def wrapped(*args,**kwargs):
        if session.get("role") != "Admin":
            flash("You do not have permission to access this page.", "error")
            return redirect(url_for("dashboard"))
        return view(*args,**kwargs)
    return wrapped
def current_user():
    """ Returns the current logged-in user"""
    if "user_id" not in session:
        return None
    return get_db().execute(
        "SELECT * FROM users WHERE id =?", (session["user_id"],)
    ) .fetchone()

#--------------------------------------------
# ADMIN ROUTES
#--------------------------------------------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        employee_id = request.form["employee_id"].strip()
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        role = request.form["role"] # "Employee" or "Admin"
        
        errors = []
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
            if role not in ("Employee", "Admin"):
                errors.append("Invalid role selected.")
            if not employee_id or not name or not email:
                errors.append("All fields are required.")
                
            db = get_db()
            existing = db.execute(
                "SELECT * FROM users WHERE email = ? OR employee_id =?",
                (email, employee_id),
            ) . fetchone()
            if existing:
                errors.append("An account with this email or employee ID already exists.")
                
                if errors:
                    for e in errors:
                        flash(e, "error")
                    return render_template("signup.html", form= request.form)
                
                db.execute(
                    """INSERT INTO users (employee_id, name, email, password_hash, role, join_date) VALUES (?, ?, ?, ?, ?, ?)""",
                    (employee_id, name, email, generate_password_hash(password),role, date.today().isoformat()),
                )
                db.commit()
                flash("Acount created! Please sign in.", "success")
                return redirect(url_for("login"))
            return render_template("signup.html", form ={})

@app.route("/login", methods=["GET", "POST"]) 
def login() : 
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        
        user = get_db().execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")
        
        session.clear()
        session["user_id"] = user["id"]
        session["role"] = user["role"]
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login")) 


#--------------------------------------------
# DASHBOARD
#--------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    db = get_db()
    
    if user["role"] == "Admin":
        employees = db.execute(
            "SELECT * FROM users WHERE role = 'Employee' ORDER BY name"
        ) .fetchall()
        pending_leaves = db.execute(
            "SELECT COUNT(*) c FROM leave_requests WHERE status = 'Pending'"
        ).fetchone() ["c"]
        today_present = db.execute(
            "SELECT COUNT(*) c FROM attendance WHERE date = ? AND status = 'Present'", (date.today().isoformat(),),).fetchone()["c"]
        return render_template("admin_dashboard.html", user = user, employees = employees, pending_leaves = pending_leaves, today_present = today_present,
        )
        
    #--------------------------------------------
    # EMPLOYEE DASHBOARD
    #--------------------------------------------
    today = date.today().isoformat()
    today_att = db.execute(
        "SELECT * FROM attendance WHERE user_id = ? AND date = ?",
        (user["id"], today),
    ).fetchone()
    recent_leaves = db.execute(
        "SELECT * FROM leave_requests WHERE user_id = ? ORDER BY id DESC LIMIT 3",
        (user["id"],),
    ).fetchall()
    return render_template(
        "employee_dashboard.html",
        user=user, today_att=today_att, recent_leaves=recent_leaves,
    )
    
#--------------------------------------------
# PROFILE
#--------------------------------------------
@app.route("/profile", methods = ["GET", "POST"])
@login_required
def profile():
    user = current_user()
    db = get_db()
    
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        
        if user["role"] == "Admin" and request.form.get("editing_employee_id"):
            #Admin is editing an employee's profile
            emp_id = request.form.get["editing_employee_id"]
            db.execute(
                """UPDATE users SET name= ?,phone = ?, address = ?, job_title = ?, department = ? WHERE id=?""",
                (
                    request.form["name"], phone, address,
                    request.form["job_title"], request.form["department"], emp_id,
                ),
            )
            db.commit()
            flash("Employee profile updated.", "success")
            return redirect(url_for("view_emplpoyee", emp_id = emp_id))
        
        # Regular self-edit: limited field only
        db.execute(
            "UPDATE users SET phone = ?, address = ? WHERE id = ?",
            (phone, address, user["id"]),
        )
        db.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user, target = user, editable = True)

@app.route("/employee<int:emp_id>")
@login_required
@admin_required
def view_employee(emp_id):
    target = get_db().execute("SELECT * FROM users WHERE id=?",
    (emp_id,)).fetchone()
    if target is None:
        flash ("Employee not found.", "error")
        return redirect(url_for("dashboard"))
    return render_template("profile.html", user=current_user(), target=target, editable=True)

#--------------------------------------------
# ATTENDANCE
#--------------------------------------------
@app.route("/attendance")
@login_required
def attendance():
    user = current_user()
    db = get_db()

    if user["role"] == "Admin":
        rows = db.execute(
            """SELECT a.*, u.name, u.employee_id FROM attendance a 
            JOIN users u ON u.id = a.user_id
            ORDER BY a.date DESC LIMIT 200"""
        ) .fetchall()
        return render_template("attendance_admin.html", user = user, rows = rows)
    row = db.execute(
        "SELECT * FROM attendance WHERE user_id=? ORDER BY date DESC LIMIT 60",
        (user["id"],),
    ).fetchall()