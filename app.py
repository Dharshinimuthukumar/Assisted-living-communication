"""Assisted-Living Facility Operational Communication System
Main Flask Application
Semester 5 C28 Academic Proof of Concept
"""

import os
import sqlite3
import json
from functools import wraps
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify, send_file
)
from werkzeug.security import check_password_hash

from services.communication_service import process_care_event_for_family
from services.role_checker import can_submit_questions
from services.consent_checker import check_question_consent
from services.safety_checker import classify_question
from experiments.run_experiment import run_experiment

app = Flask(__name__)
app.secret_key = "assisted-living-secret-key-c28-proof-of-concept"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'database.db')
RESULTS_DIR = os.path.join(BASE_DIR, 'experiments', 'results')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access the application.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_global_context():
    user = None
    pending_count = 0
    if 'user_id' in session:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (session['user_id'],))
        row = cursor.fetchone()
        if row:
            user = dict(row)
        cursor.execute("SELECT COUNT(*) FROM communications WHERE review_status = 'Pending Review'")
        pending_count = cursor.fetchone()[0]
        conn.close()
    return {
        'current_user': user,
        'pending_review_count': pending_count
    }

# ----------------------------------------------------
# AUTHENTICATION & DEMO PERSONA SWITCHING
# ----------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['display_name'] = user['display_name']
            flash(f"Signed in as {user['display_name']} ({user['role'].capitalize()}).", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Use demo passwords: admin123, staff123, <name>123", "danger")

    return render_template('login.html', active_page='login')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for('login'))

@app.route('/switch_user/<username>')
def switch_user(username):
    """Quick demo switcher for academic review presentation."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['display_name'] = user['display_name']
        flash(f"Switched persona to {user['display_name']} ({user['role'].capitalize()}).", "info")
    else:
        flash(f"User '{username}' not found.", "danger")
    return redirect(request.referrer or url_for('dashboard'))

# ----------------------------------------------------
# CORE DASHBOARD
# ----------------------------------------------------

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    # Collect dashboard metrics
    cursor.execute("SELECT COUNT(*) FROM residents WHERE active_status = 1")
    total_residents = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM care_events")
    total_care_events = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM communications WHERE review_status = 'Pending Review'")
    pending_reviews = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM communications WHERE disclosure_status = 'Approved'")
    approved_comms = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM communications WHERE disclosure_status = 'Blocked'")
    blocked_comms = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM care_events WHERE urgency = 'High'")
    high_urgency_events = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM consent WHERE consent_status = 'Active'")
    active_consents = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM consent WHERE consent_status = 'Revoked'")
    revoked_consents = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM consent")
    total_consents = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM questions WHERE status = 'Pending'")
    pending_questions = cursor.fetchone()[0]

    # Recent communications
    cursor.execute("""
        SELECT c.*, r.resident_name, f.family_name, f.role
        FROM communications c
        JOIN residents r ON c.resident_id = r.resident_id
        JOIN family_members f ON c.family_id = f.family_id
        ORDER BY c.created_at DESC LIMIT 8
    """)
    recent_comms = [dict(row) for row in cursor.fetchall()]

    conn.close()

    metrics = {
        'total_residents': total_residents,
        'total_care_events': total_care_events,
        'pending_reviews': pending_reviews,
        'approved_comms': approved_comms,
        'blocked_comms': blocked_comms,
        'high_urgency_events': high_urgency_events,
        'active_consents': active_consents,
        'revoked_consents': revoked_consents,
        'total_consents': total_consents,
        'total_questions': total_questions,
        'pending_questions': pending_questions
    }

    return render_template('dashboard.html', metrics=metrics, recent_comms=recent_comms, active_page='dashboard')

# ----------------------------------------------------
# RESIDENTS
# ----------------------------------------------------

@app.route('/residents')
@login_required
def residents_list():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, GROUP_CONCAT(f.family_name || ' (' || f.role || ')', ', ') as family_names
        FROM residents r
        LEFT JOIN family_members f ON r.resident_id = f.resident_id
        GROUP BY r.resident_id
        ORDER BY r.resident_id ASC
    """)
    residents = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template('residents.html', residents=residents, active_page='residents')

@app.route('/residents/<resident_id>')
@login_required
def resident_detail(resident_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM residents WHERE resident_id = ?", (resident_id,))
    res_row = cursor.fetchone()
    if not res_row:
        flash(f"Resident '{resident_id}' not found.", "danger")
        return redirect(url_for('residents_list'))
    resident = dict(res_row)

    # Family members with consent details
    cursor.execute("""
        SELECT f.*, c.consent_status, c.care_activity_updates, c.routine_updates,
               c.exception_updates, c.communication_questions
        FROM family_members f
        LEFT JOIN consent c ON f.resident_id = c.resident_id AND f.family_id = c.family_id
        WHERE f.resident_id = ?
    """, (resident_id,))
    family_contacts = [dict(row) for row in cursor.fetchall()]

    # Care events
    cursor.execute("""
        SELECT * FROM care_events WHERE resident_id = ? ORDER BY event_datetime DESC
    """, (resident_id,))
    care_events = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return render_template(
        'resident_detail.html',
        resident=resident,
        family_contacts=family_contacts,
        care_events=care_events,
        active_page='residents'
    )

# ----------------------------------------------------
# CARE EVENTS
# ----------------------------------------------------

@app.route('/care_events')
@login_required
def care_events_list():
    resident_id = request.args.get('resident_id', '')
    urgency = request.args.get('urgency', '')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT resident_id, resident_name, independence_level FROM residents ORDER BY resident_name ASC")
    residents = [dict(row) for row in cursor.fetchall()]

    query = """
        SELECT e.*, r.resident_name
        FROM care_events e
        JOIN residents r ON e.resident_id = r.resident_id
        WHERE 1=1
    """
    params = []
    if resident_id:
        query += " AND e.resident_id = ?"
        params.append(resident_id)
    if urgency:
        query += " AND e.urgency = ?"
        params.append(urgency)

    query += " ORDER BY e.event_datetime DESC"
    cursor.execute(query, params)
    events = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return render_template(
        'care_events.html',
        events=events,
        residents=residents,
        selected_res=resident_id,
        selected_urgency=urgency,
        active_page='care_events'
    )

@app.route('/care_events/add', methods=['POST'])
@login_required
def add_care_event():
    resident_id = request.form.get('resident_id')
    event_type = request.form.get('event_type')
    assistance_level = request.form.get('assistance_level')
    urgency = request.form.get('urgency', 'Normal')
    observation = request.form.get('observation', '').strip()
    staff_note = request.form.get('staff_note', '').strip()
    exception_flag = 1 if request.form.get('exception_flag') == '1' else 0

    conn = get_db()
    cursor = conn.cursor()

    # Generate new event id
    cursor.execute("SELECT COUNT(*) FROM care_events")
    count = cursor.fetchone()[0] + 1
    new_event_id = f"EVT{count:03d}"
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    created_by = session.get('username', 'Madhu')

    cursor.execute("""
        INSERT INTO care_events (
            event_id, resident_id, event_datetime, event_type,
            observation, assistance_level, urgency, exception_flag,
            staff_note, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        new_event_id, resident_id, now_str, event_type,
        observation, assistance_level, urgency, exception_flag,
        staff_note, created_by
    ))
    conn.commit()
    conn.close()

    flash(f"Care event '{new_event_id}' successfully recorded.", "success")
    return redirect(url_for('care_events_list'))

# ----------------------------------------------------
# FAMILY MEMBERS & CONSENT
# ----------------------------------------------------

@app.route('/family_members')
@login_required
def family_members_list():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.*, r.resident_name
        FROM family_members f
        JOIN residents r ON f.resident_id = r.resident_id
        ORDER BY f.family_id ASC
    """)
    family_members = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template('family_members.html', family_members=family_members, active_page='family_members')

@app.route('/consent')
@login_required
def consent_matrix():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, r.resident_name, f.family_name, f.role
        FROM consent c
        JOIN residents r ON c.resident_id = r.resident_id
        JOIN family_members f ON c.family_id = f.family_id
        ORDER BY c.consent_id ASC
    """)
    consents = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template('consent.html', consents=consents, active_page='consent')

@app.route('/consent/toggle/<consent_id>', methods=['POST'])
@login_required
def toggle_consent_status(consent_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT consent_status FROM consent WHERE consent_id = ?", (consent_id,))
    row = cursor.fetchone()
    if row:
        new_status = 'Revoked' if row['consent_status'] == 'Active' else 'Active'
        cursor.execute("UPDATE consent SET consent_status = ? WHERE consent_id = ?", (new_status, consent_id))
        conn.commit()
        flash(f"Consent '{consent_id}' updated to '{new_status}'.", "info")
    conn.close()
    return redirect(url_for('consent_matrix'))

# ----------------------------------------------------
# COMMUNICATION PIPELINE INSPECTOR
# ----------------------------------------------------

@app.route('/communication')
@login_required
def communication_view():
    event_id = request.args.get('event_id')
    family_id = request.args.get('family_id')

    conn = get_db()
    cursor = conn.cursor()

    # Load care events for selection
    cursor.execute("""
        SELECT e.event_id, e.event_type, e.urgency, r.resident_name
        FROM care_events e
        JOIN residents r ON e.resident_id = r.resident_id
        ORDER BY e.event_datetime DESC LIMIT 40
    """)
    events = [dict(row) for row in cursor.fetchall()]

    # Load family members for selection
    cursor.execute("""
        SELECT f.family_id, f.family_name, f.relationship, f.role, r.resident_name
        FROM family_members f
        JOIN residents r ON f.resident_id = r.resident_id
        ORDER BY f.family_id ASC
    """)
    family_members = [dict(row) for row in cursor.fetchall()]

    # If no event_id specified, pick the first event
    if not event_id and events:
        event_id = events[0]['event_id']

    # If no family_id specified, find the family linked to that event's resident
    if not family_id and event_id:
        cursor.execute("SELECT resident_id FROM care_events WHERE event_id = ?", (event_id,))
        evt_row = cursor.fetchone()
        if evt_row:
            cursor.execute("SELECT family_id FROM family_members WHERE resident_id = ? LIMIT 1", (evt_row['resident_id'],))
            fam_row = cursor.fetchone()
            if fam_row:
                family_id = fam_row['family_id']

    pipeline_result = None
    if event_id and family_id:
        # Run communication pipeline
        pipeline_result = process_care_event_for_family(conn, event_id, family_id, save_to_db=False)

    # Historical communications ledger
    cursor.execute("""
        SELECT c.*, r.resident_name, f.family_name, f.role
        FROM communications c
        JOIN residents r ON c.resident_id = r.resident_id
        JOIN family_members f ON c.family_id = f.family_id
        ORDER BY c.created_at DESC LIMIT 15
    """)
    historical_comms = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template(
        'communication.html',
        events=events,
        family_members=family_members,
        selected_event_id=event_id,
        selected_family_id=family_id,
        pipeline_result=pipeline_result,
        historical_comms=historical_comms,
        active_page='communication'
    )

@app.route('/api/generate_update', methods=['POST'])
def api_generate_update():
    """REST API endpoint for communication pipeline execution."""
    data = request.get_json() or {}
    event_id = data.get('event_id')
    family_id = data.get('family_id')

    if not event_id or not family_id:
        return jsonify({'success': False, 'error': 'event_id and family_id are required.'}), 400

    conn = get_db()
    result = process_care_event_for_family(conn, event_id, family_id, save_to_db=True)
    conn.close()
    return jsonify(result)

# ----------------------------------------------------
# HUMAN REVIEW QUEUE
# ----------------------------------------------------

@app.route('/review_queue')
@login_required
def review_queue():
    conn = get_db()
    cursor = conn.cursor()

    # Pending communications
    cursor.execute("""
        SELECT c.*, e.event_type, e.urgency, e.exception_flag,
               r.resident_name, f.family_name, f.role
        FROM communications c
        JOIN care_events e ON c.event_id = e.event_id
        JOIN residents r ON c.resident_id = r.resident_id
        JOIN family_members f ON c.family_id = f.family_id
        WHERE c.review_status = 'Pending Review'
        ORDER BY c.created_at ASC
    """)
    pending_comms = [dict(row) for row in cursor.fetchall()]

    # Review logs audit trail
    cursor.execute("""
        SELECT * FROM review_logs ORDER BY action_timestamp DESC LIMIT 20
    """)
    review_logs = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return render_template(
        'review_queue.html',
        pending_comms=pending_comms,
        review_logs=review_logs,
        active_page='review_queue'
    )

@app.route('/review/submit', methods=['POST'])
@login_required
def submit_review_action():
    comm_id = request.form.get('comm_id')
    action_taken = request.form.get('action_taken') # 'Approve', 'Edit', 'Reject', 'Escalate'
    edited_summary = request.form.get('edited_summary', '').strip()
    decision_notes = request.form.get('decision_notes', '').strip()
    reviewer_name = session.get('display_name', 'Madhu (Care Staff)')

    conn = get_db()
    cursor = conn.cursor()

    if action_taken == 'Approve':
        cursor.execute("""
            UPDATE communications
            SET disclosure_status = 'Approved', review_status = 'Reviewed'
            WHERE comm_id = ?
        """, (comm_id,))
    elif action_taken == 'Edit':
        cursor.execute("""
            UPDATE communications
            SET generated_summary = ?, disclosure_status = 'Approved', review_status = 'Reviewed'
            WHERE comm_id = ?
        """, (edited_summary, comm_id))
    elif action_taken == 'Reject':
        cursor.execute("""
            UPDATE communications
            SET disclosure_status = 'Rejected', review_status = 'Rejected', block_reason = ?
            WHERE comm_id = ?
        """, (decision_notes, comm_id))
    elif action_taken == 'Escalate':
        cursor.execute("""
            UPDATE communications
            SET review_status = 'Escalate'
            WHERE comm_id = ?
        """, (comm_id,))

    # Log action
    cursor.execute("SELECT COUNT(*) FROM review_logs")
    log_count = cursor.fetchone()[0] + 1
    log_id = f"LOG{log_count:03d}"
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("""
        INSERT INTO review_logs (log_id, comm_id, question_id, reviewer_name, action_taken, action_timestamp, notes)
        VALUES (?, ?, NULL, ?, ?, ?, ?)
    """, (log_id, comm_id, reviewer_name, action_taken, now_str, decision_notes))

    conn.commit()
    conn.close()

    flash(f"Review decision '{action_taken}' recorded for {comm_id}.", "success")
    return redirect(url_for('review_queue'))

# ----------------------------------------------------
# QUESTIONS & FAMILY INQUIRIES
# ----------------------------------------------------

@app.route('/questions')
@login_required
def questions_list():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT resident_id, resident_name FROM residents ORDER BY resident_name ASC")
    residents = [dict(row) for row in cursor.fetchall()]

    cursor.execute("""
        SELECT q.*, r.resident_name, f.family_name, f.role
        FROM questions q
        JOIN residents r ON q.resident_id = r.resident_id
        JOIN family_members f ON q.family_id = f.family_id
        ORDER BY q.created_at DESC
    """)
    questions = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return render_template(
        'questions.html',
        questions=questions,
        residents=residents,
        active_page='questions'
    )

@app.route('/questions/submit', methods=['POST'])
@login_required
def submit_question():
    resident_id = request.form.get('resident_id')
    category = request.form.get('category', 'General')
    question_text = request.form.get('question_text', '').strip()

    conn = get_db()
    cursor = conn.cursor()

    # Determine requesting family member
    cursor.execute("SELECT linked_family_id FROM users WHERE user_id = ?", (session.get('user_id'),))
    u_row = cursor.fetchone()
    fam_id = u_row['linked_family_id'] if u_row and u_row['linked_family_id'] else 'FAM001'

    cursor.execute("SELECT * FROM family_members WHERE family_id = ?", (fam_id,))
    family = dict(cursor.fetchone())

    # Step 1: Check role permission
    if not can_submit_questions(family.get('role')):
        flash(f"Submission Blocked: {family.get('role')} role does not permit submitting direct questions to staff.", "danger")
        conn.close()
        return redirect(url_for('questions_list'))

    # Step 2: Check consent permission
    cursor.execute("SELECT * FROM consent WHERE resident_id = ? AND family_id = ?", (resident_id, fam_id))
    consent_row = cursor.fetchone()
    consent = dict(consent_row) if consent_row else None
    can_ask, consent_reason = check_question_consent(consent)
    if not can_ask:
        flash(f"Submission Blocked: {consent_reason}", "danger")
        conn.close()
        return redirect(url_for('questions_list'))

    # Step 3: Safety Checker (Case 5 - Medical Question Boundary)
    is_op, safety_response = classify_question(question_text)

    cursor.execute("SELECT COUNT(*) FROM questions")
    q_count = cursor.fetchone()[0] + 1
    new_qid = f"QUE{q_count:03d}"
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not is_op:
        # Intercepted Medical Inquiry
        cursor.execute("""
            INSERT INTO questions (
                question_id, family_id, resident_id, question_text, category,
                status, created_at, staff_response, answered_by, answered_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_qid, fam_id, resident_id, question_text, 'Medical Inquiry',
            'Flagged Medical', now_str, safety_response, 'Safety Checker (Automated)', now_str
        ))
        conn.commit()
        conn.close()
        flash("Operational Support Notice: Your inquiry contains clinical terms. It was redirected to nursing staff rather than processed as an operational question.", "warning")
        return redirect(url_for('questions_list'))

    # Standard Operational Question
    cursor.execute("""
        INSERT INTO questions (
            question_id, family_id, resident_id, question_text, category,
            status, created_at, staff_response, answered_by, answered_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL)
    """, (
        new_qid, fam_id, resident_id, question_text, category,
        'Pending', now_str
    ))
    conn.commit()
    conn.close()

    flash("Operational inquiry submitted to facility staff.", "success")
    return redirect(url_for('questions_list'))

@app.route('/questions/answer', methods=['POST'])
@login_required
def answer_question():
    question_id = request.form.get('question_id')
    staff_response = request.form.get('staff_response', '').strip()
    answered_by = session.get('display_name', 'Madhu (Care Staff)')
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE questions
        SET staff_response = ?, status = 'Answered', answered_by = ?, answered_at = ?
        WHERE question_id = ?
    """, (staff_response, answered_by, now_str, question_id))
    conn.commit()
    conn.close()

    flash(f"Response recorded for {question_id}.", "success")
    return redirect(url_for('questions_list'))

# ----------------------------------------------------
# EXPERIMENT & EVALUATION DASHBOARD
# ----------------------------------------------------

@app.route('/experiment')
@login_required
def experiment_dashboard():
    json_path = os.path.join(RESULTS_DIR, 'experiment_results.json')
    chart_path = os.path.join(BASE_DIR, 'static', 'images', 'metrics_comparison.png')

    if not os.path.exists(json_path) or not os.path.exists(chart_path):
        results = run_experiment()
    else:
        with open(json_path, 'r', encoding='utf-8') as f:
            results = json.load(f)

    return render_template(
        'experiment.html',
        results=results,
        chart_exists=os.path.exists(chart_path),
        cache_buster=datetime.now().timestamp(),
        active_page='experiment'
    )

@app.route('/experiment/run', methods=['POST'])
@login_required
def run_experiment_action():
    results = run_experiment()
    flash(f"Empirical benchmark successfully executed across {results['total_evaluations']} synthetic event pairings.", "success")
    return redirect(url_for('experiment_dashboard'))

@app.route('/experiment/download_notebook')
@login_required
def download_notebook():
    nb_path = os.path.join(BASE_DIR, 'experiments', 'experiment.ipynb')
    if os.path.exists(nb_path):
        return send_file(nb_path, as_attachment=True, download_name='experiment.ipynb')
    flash("Notebook file not found.", "danger")
    return redirect(url_for('experiment_dashboard'))

# ----------------------------------------------------
# ACADEMIC DEMO SCENARIO SHORTCUTS
# ----------------------------------------------------

@app.route('/run_scenario/<scenario>')
@login_required
def run_scenario(scenario):
    scenarios = {
        'journey_1': ('EVT001', 'FAM001', 'Journey 1: Normal Activity -> Devi Raman to Kavi (Approved)'),
        'journey_2': ('EVT002', 'FAM001', 'Journey 2: High Urgency Mobility Exception -> Devi to Kavi (Pending Review)'),
        'case_1': ('EVT003', 'FAM004', 'Case 1: No Consent -> Kamala to Abi with Revoked Consent (Blocked)'),
        'case_2': ('EVT004', 'FAM004', 'Case 2: Role Restriction -> Abi (View-Only) accessing Personal Care (Blocked)'),
        'case_3': ('EVT005', 'FAM003', 'Case 3: Medical Language -> Ramesh to Hema with fever/infection (Pending Review)'),
        'case_4': ('EVT006', 'FAM005', 'Case 4: Missing Information -> Mohan to Mala with blank observation (Pending Review)')
    }

    if scenario in scenarios:
        evt_id, fam_id, desc = scenarios[scenario]
        flash(f"Demonstration Executed: {desc}", "info")
        return redirect(url_for('communication_view', event_id=evt_id, family_id=fam_id))

    flash("Scenario not recognized.", "warning")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
