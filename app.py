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
from wekzeug.security import generate_password_hash, check_password_hash
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
        conn.execute("""INSERT INTO users (employee_id, anme, email, password_hash, role, job_title, department, join_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        