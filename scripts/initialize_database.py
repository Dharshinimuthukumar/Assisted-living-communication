"""Database Initialization Script
Sets up SQLite database from schema.sql, populates user credentials with secure hashes,
and imports synthetic datasets into database.db.
"""

import os
import csv
import sqlite3
from werkzeug.security import generate_password_hash
import sys

# Ensure parent directory is in path to import services
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.communication_service import process_care_event_for_family

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'database.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')
DATA_DIR = os.path.join(BASE_DIR, 'data')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    print("Database schema successfully executed.")

    # Helper to load CSV into table
    def load_csv(filename, table_name, columns):
        csv_file = os.path.join(DATA_DIR, filename)
        if not os.path.exists(csv_file):
            print(f"Warning: {csv_file} not found.")
            return
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = [tuple(row[col] for col in columns) for row in reader]
        placeholders = ', '.join(['?'] * len(columns))
        col_names = ', '.join(columns)
        cursor.executemany(f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})", rows)
        print(f"Loaded {len(rows)} rows into {table_name} from {filename}.")

    # 1. Load Core Tables from CSV
    load_csv('residents.csv', 'residents', [
        'resident_id', 'resident_name', 'age_group', 'independence_level', 'preferred_communication_style', 'active_status'
    ])
    load_csv('family_members.csv', 'family_members', [
        'family_id', 'family_name', 'relationship', 'resident_id', 'role', 'active_status'
    ])
    load_csv('consent.csv', 'consent', [
        'consent_id', 'resident_id', 'family_id', 'care_activity_updates', 'routine_updates', 'exception_updates', 'communication_questions', 'consent_status', 'effective_date'
    ])
    load_csv('care_events.csv', 'care_events', [
        'event_id', 'resident_id', 'event_datetime', 'event_type', 'observation', 'assistance_level', 'urgency', 'exception_flag', 'staff_note', 'created_by'
    ])
    load_csv('questions.csv', 'questions', [
        'question_id', 'family_id', 'resident_id', 'question_text', 'category', 'status', 'created_at', 'staff_response', 'answered_by', 'answered_at'
    ])
    load_csv('exceptions.csv', 'exceptions', [
        'exception_id', 'event_id', 'resident_id', 'exception_type', 'description', 'severity', 'review_required', 'resolution_status'
    ])

    # 2. Seed Demo Users
    users = [
        ('USR001', 'Dharshini', generate_password_hash('admin123'), 'admin', 'Dharshini (Facility Administrator)', None),
        ('USR002', 'Madhu', generate_password_hash('staff123'), 'staff', 'Madhu (Assisted-Living Care Staff)', None),
        ('USR003', 'Kavi', generate_password_hash('kavi123'), 'family', 'Kavi (Primary Contact for Devi)', 'FAM001'),
        ('USR004', 'Charu', generate_password_hash('charu123'), 'family', 'Charu (Secondary Contact for Devi)', 'FAM002'),
        ('USR005', 'Hema', generate_password_hash('hema123'), 'family', 'Hema (Emergency Contact for Ramesh)', 'FAM003'),
        ('USR006', 'Abi', generate_password_hash('abi123'), 'family', 'Abi (View-Only Contact for Kamala)', 'FAM004'),
        ('USR007', 'Mala', generate_password_hash('mala123'), 'family', 'Mala (Primary Contact for Mohan)', 'FAM005')
    ]
    cursor.executemany("""
        INSERT INTO users (user_id, username, password_hash, role, display_name, linked_family_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, users)
    print(f"Seeded {len(users)} demo user accounts.")

    conn.commit()

    # 3. Process Initial Key Events through Communication Pipeline
    conn.row_factory = sqlite3.Row
    initial_runs = [
        ('EVT001', 'FAM001'), # Journey 1: Normal Low Urgency -> Devi Raman to Kavi
        ('EVT002', 'FAM001'), # Journey 2: High Urgency Exception -> Devi Raman to Kavi (Pending Review)
        ('EVT003', 'FAM004'), # Case 1: Revoked Consent -> Kamala to Abi (Blocked)
        ('EVT004', 'FAM004'), # Case 2: Insufficient Role -> Kamala to Abi (Blocked)
        ('EVT005', 'FAM003'), # Case 3: Medical Language -> Ramesh to Hema (Pending Review)
        ('EVT006', 'FAM005'), # Case 4: Missing Information -> Mohan to Mala (Pending Review)
    ]

    print("Running initial communication pipeline on key journey events...")
    for evt_id, fam_id in initial_runs:
        res = process_care_event_for_family(conn, evt_id, fam_id, save_to_db=True)
        print(f"  Processed {evt_id} for {fam_id} -> Status: {res.get('disclosure_status')}, Review: {res.get('review_status')}")

    # Seed initial review log for an approved review action demonstration
    cursor.execute("""
        INSERT INTO review_logs (log_id, comm_id, question_id, reviewer_name, action_taken, action_timestamp, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        'LOG001', None, 'QUE001', 'Madhu', 'Approve', '2026-09-03 17:15:00',
        'Verified question is operational regarding music session; responded with positive feedback.'
    ))
    conn.commit()
    conn.close()
    print("Database initialization complete.")

if __name__ == '__main__':
    init_db()
