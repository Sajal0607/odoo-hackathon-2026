-- Dayflow HRMS database schema

CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id     TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    role            TEXT NOT NULL CHECK (role IN ('Employee', 'Admin')),
    phone           TEXT DEFAULT '',
    address         TEXT DEFAULT '',
    job_title       TEXT DEFAULT '',
    department      TEXT DEFAULT '',
    profile_picture TEXT DEFAULT '',
    join_date       TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS attendance (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date       TEXT NOT NULL,
    check_in   TEXT DEFAULT NULL,
    check_out  TEXT DEFAULT NULL,
    status     TEXT NOT NULL DEFAULT 'Present'
        CHECK (status IN ('Present', 'Absent', 'Half-day', 'Leave')),
    UNIQUE (user_id, date)
);

CREATE TABLE IF NOT EXISTS leave_requests (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    leave_type    TEXT NOT NULL CHECK (leave_type IN ('Paid', 'Sick', 'Unpaid')),
    start_date    TEXT NOT NULL,
    end_date      TEXT NOT NULL,
    remarks       TEXT DEFAULT '',
    status        TEXT NOT NULL DEFAULT 'Pending'
        CHECK (status IN ('Pending', 'Approved', 'Rejected')),
    admin_comment TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS payroll (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    basic_salary  REAL NOT NULL DEFAULT 0,
    allowances    REAL NOT NULL DEFAULT 0,
    deductions    REAL NOT NULL DEFAULT 0,
    net_salary    REAL NOT NULL DEFAULT 0
);