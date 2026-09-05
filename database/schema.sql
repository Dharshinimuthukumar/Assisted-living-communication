-- Assisted-Living Facility Operational Communication System
-- Database Schema (SQLite)

PRAGMA foreign_keys = ON;

-- 1. Users Table (Authentication and Access Control)
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'staff', 'family')),
    display_name TEXT NOT NULL,
    linked_family_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (linked_family_id) REFERENCES family_members(family_id)
);

-- 2. Residents Table
CREATE TABLE IF NOT EXISTS residents (
    resident_id TEXT PRIMARY KEY,
    resident_name TEXT NOT NULL,
    age_group TEXT NOT NULL,
    independence_level TEXT NOT NULL CHECK (independence_level IN (
        'Independent',
        'Needs Minimal Assistance',
        'Needs Moderate Assistance',
        'Needs High Assistance'
    )),
    preferred_communication_style TEXT NOT NULL,
    active_status INTEGER NOT NULL DEFAULT 1
);

-- 3. Family Members Table
CREATE TABLE IF NOT EXISTS family_members (
    family_id TEXT PRIMARY KEY,
    family_name TEXT NOT NULL,
    relationship TEXT NOT NULL,
    resident_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN (
        'Primary Family Contact',
        'Secondary Family Contact',
        'Emergency Contact',
        'View-Only Contact'
    )),
    active_status INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (resident_id) REFERENCES residents(resident_id)
);

-- 4. Consent Table
CREATE TABLE IF NOT EXISTS consent (
    consent_id TEXT PRIMARY KEY,
    resident_id TEXT NOT NULL,
    family_id TEXT NOT NULL,
    care_activity_updates INTEGER NOT NULL DEFAULT 0,
    routine_updates INTEGER NOT NULL DEFAULT 0,
    exception_updates INTEGER NOT NULL DEFAULT 0,
    communication_questions INTEGER NOT NULL DEFAULT 0,
    consent_status TEXT NOT NULL CHECK (consent_status IN ('Active', 'Revoked', 'Pending')),
    effective_date TEXT NOT NULL,
    FOREIGN KEY (resident_id) REFERENCES residents(resident_id),
    FOREIGN KEY (family_id) REFERENCES family_members(family_id)
);

-- 5. Care Events Table
CREATE TABLE IF NOT EXISTS care_events (
    event_id TEXT PRIMARY KEY,
    resident_id TEXT NOT NULL,
    event_datetime TEXT NOT NULL,
    event_type TEXT NOT NULL,
    observation TEXT,
    assistance_level TEXT,
    urgency TEXT NOT NULL DEFAULT 'Normal',
    exception_flag INTEGER NOT NULL DEFAULT 0,
    staff_note TEXT, -- Internal operational notes ONLY; not directly disclosed
    created_by TEXT NOT NULL,
    FOREIGN KEY (resident_id) REFERENCES residents(resident_id)
);

-- 6. Exceptions Table
CREATE TABLE IF NOT EXISTS exceptions (
    exception_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    resident_id TEXT NOT NULL,
    exception_type TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('Low', 'Moderate', 'High')),
    review_required INTEGER NOT NULL DEFAULT 1,
    resolution_status TEXT NOT NULL CHECK (resolution_status IN ('Open', 'Under Review', 'Resolved')),
    FOREIGN KEY (event_id) REFERENCES care_events(event_id),
    FOREIGN KEY (resident_id) REFERENCES residents(resident_id)
);

-- 7. Questions Table
CREATE TABLE IF NOT EXISTS questions (
    question_id TEXT PRIMARY KEY,
    family_id TEXT NOT NULL,
    resident_id TEXT NOT NULL,
    question_text TEXT NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Pending', 'Answered', 'Flagged Medical', 'Escalated')),
    created_at TEXT NOT NULL,
    staff_response TEXT,
    answered_by TEXT,
    answered_at TEXT,
    FOREIGN KEY (family_id) REFERENCES family_members(family_id),
    FOREIGN KEY (resident_id) REFERENCES residents(resident_id)
);

-- 8. Communications Table
CREATE TABLE IF NOT EXISTS communications (
    comm_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    resident_id TEXT NOT NULL,
    family_id TEXT NOT NULL,
    original_observation TEXT NOT NULL,
    generated_summary TEXT,
    disclosure_status TEXT NOT NULL CHECK (disclosure_status IN ('Approved', 'Blocked', 'Pending Review', 'Rejected')),
    review_status TEXT NOT NULL CHECK (review_status IN ('Auto-Approved', 'Pending Review', 'Reviewed', 'Rejected', 'Escalated')),
    block_reason TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (event_id) REFERENCES care_events(event_id),
    FOREIGN KEY (resident_id) REFERENCES residents(resident_id),
    FOREIGN KEY (family_id) REFERENCES family_members(family_id)
);

-- 9. Review Logs Table
CREATE TABLE IF NOT EXISTS review_logs (
    log_id TEXT PRIMARY KEY,
    comm_id TEXT,
    question_id TEXT,
    reviewer_name TEXT NOT NULL,
    action_taken TEXT NOT NULL CHECK (action_taken IN ('Approve', 'Reject', 'Edit', 'Escalate')),
    action_timestamp TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (comm_id) REFERENCES communications(comm_id),
    FOREIGN KEY (question_id) REFERENCES questions(question_id)
);
