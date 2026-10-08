# Assisted-Living Facility Operational Communication System

> **ACADEMIC PROOF OF CONCEPT (Semester 5 C28)**  
> **PROJECT TITLE:** From Operational Pain to Working Product: Assisted-Living Facility Supporting Residents' Independence Levels  
> **IMPORTANT SCOPE NOTICE:** This system is **NOT** a medical diagnosis system, clinical decision support system, or medical prediction engine. It supports **operational communication only** between assisted-living staff and authorized family members.

---

## 1. Project Overview

Assisted-living families currently face a communication dilemma: they either receive *too little information* or are overwhelmed by *raw care logs* containing internal staff handover notes and confusing medical jargon.

This working proof-of-concept solves this problem by providing concise, relevant operational updates while strictly enforcing:
- **Resident Consent:** Granular, category-level information-sharing permissions.
- **Family Roles:** Tiered access across Primary, Secondary, Emergency, and View-Only contacts.
- **Strict Non-Medical Boundary:** Intercepts clinical terms, diagnoses, and medication advice.
- **Human-in-the-Loop Review:** Mandatory review queue for high-urgency events and exceptions.
- **Data Segregation:** Internal staff notes are never disclosed to family members.

---

## 2. Directory Structure

```
assisted-living-communication/
├── app.py                      # Flask web application & REST routes
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview & documentation
├── .gitignore                  # Git exclusions
│
├── database/
│   ├── database.db             # SQLite relational database
│   └── schema.sql              # Database schema definition (9 tables)
│
├── data/                       # Synthetic CSV datasets
│   ├── residents.csv           # Resident profiles & independence levels
│   ├── care_events.csv         # 100 synthetic care observations & logs
│   ├── family_members.csv      # Family directory & role assignments
│   ├── consent.csv             # Resident consent matrix
│   ├── questions.csv           # Family inquiries & staff responses
│   └── exceptions.csv          # Operational exceptions
│
├── scripts/
│   ├── generate_data.py        # Generates synthetic CSV data
│   └── initialize_database.py  # Builds database & seeds demo users
│
├── services/                   # Modular business logic
│   ├── consent_checker.py      # Validates category-level resident consent
│   ├── role_checker.py         # Enforces family role access policies
│   ├── summary_generator.py    # Rule-based concise operational summarizer
│   ├── safety_checker.py       # Medical boundary classifier & review triggers
│   └── communication_service.py# End-to-end pipeline orchestrator
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base layout with persistent non-medical banner
│   ├── login.html              # Authentication & 1-click demo logins
│   ├── dashboard.html          # Operational metrics & demo scenario launcher
│   ├── residents.html          # Residents directory & independence tiers
│   ├── resident_detail.html    # Profile, care timeline, & consent status
│   ├── care_events.html        # Event log & new event recording modal
│   ├── family_members.html     # Role matrix & capabilities
│   ├── consent.html            # Granular consent matrix & status toggle
│   ├── communication.html      # Dual-pane internal vs. family inspection view
│   ├── review_queue.html       # Staff review queue (Approve, Edit, Reject, Escalate)
│   ├── questions.html          # Family Q&A with live medical boundary warnings
│   └── experiment.html         # Empirical evaluation dashboard & charts
│
├── static/
│   ├── css/
│   │   └── style.css           # Clean, accessible academic styling
│   ├── js/
│   │   └── app.js              # Real-time medical warning & modal management
│   └── images/
│       └── metrics_comparison.png # Matplotlib empirical benchmark chart
│
├── experiments/
│   ├── run_experiment.py       # Benchmark evaluation script (100 events)
│   ├── experiment.ipynb        # Jupyter analysis notebook
│   └── results/
│       ├── experiment_results.json # Computed empirical metrics
│       └── metrics_comparison.png  # Comparison visualization chart
│
├── tests/                      # Automated test suite (28 tests)
│   ├── test_consent.py         # Unit tests for consent rules
│   ├── test_roles.py           # Unit tests for role permissions
│   ├── test_summary.py         # Unit tests for summary generation
│   ├── test_failure_cases.py   # Unit tests for 5 critical edge cases
│   └── test_routes.py          # Integration tests for Flask endpoints
│
└── docs/                       # Academic documentation suite
    ├── api_and_schema_reference.md # Complete database schema & 23 API route contracts
    ├── summarization_logic.md  # Deterministic rule-based summarization engine
    ├── experiment_results.md   # Dataset statistics, measured results & error analysis
    ├── review2_improvements.md # Review 1 feedback traceability matrix
    ├── workflow.md             # End-to-end operational workflow
    ├── architecture.md         # Component diagrams & data model
    ├── failure_mode_analysis.md# Deep dive on 5 failure & edge cases
    ├── human_review_points.md  # Supervisory review triggers & actions
    ├── user_validation.md      # Persona models & walkthrough guide
    └── experiment_methodology.md# Empirical benchmark metrics & trade-offs
```

---

## 3. Quick Start & Setup Instructions

### Prerequisites
- Python 3.9+ (Installed on Windows, macOS, or Linux)
- Pip

### Installation
1. Open a terminal in the project directory:
   ```bash
   cd C:\Users\arunk\.gemini\antigravity\scratch\assisted-living-communication
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Re-generate synthetic data and initialize the database:
   ```bash
   python scripts/generate_data.py
   python scripts/initialize_database.py
   ```

4. Run the web application:
   ```bash
   python app.py
   ```

5. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 4. Demo User Credentials & Personas

The application includes pre-configured demo credentials. You can sign in using standard credentials or use the **One-Click Demo Sign-In** links on the login screen:

| Username | Role | Display Name | Associated Resident | Password |
|---|---|---|---|---|
| **Dharshini** | `admin` | Facility Administrator | All Facility | `admin123` |
| **Madhu** | `staff` | Care Staff | All Facility | `staff123` |
| **Kavi** | `family` | Primary Contact | Devi Raman (RES001) | `kavi123` |
| **Charu** | `family` | Secondary Contact | Devi Raman (RES001) | `charu123` |
| **Hema** | `family` | Emergency Contact | Ramesh Sharma (RES002) | `hema123` |
| **Abi** | `family` | View-Only Contact (Revoked) | Kamala Sundaram (RES003) | `abi123` |
| **Mala** | `family` | Primary Contact | Mohan Patel (RES004) | `mala123` |

---

## 5. Main Workflow & Key Features

### 1. Pre-Disclosure Authorization & Dual-Pane Inspection (`/communication`)
- Select any care event and family recipient.
- The pipeline executes:
  1. Role Permission Check
  2. Resident Consent Check
  3. Non-Medical Boundary Check
  4. Human Review Gate
- Displays side-by-side **Internal Staff Record** (with confidential handover notes) vs. **Family Communication Summary** (clean, concise, non-medical).

### 2. Human Review & Escalation Queue (`/review_queue`)
- Triggered automatically for:
  - High-urgency events (`urgency == 'High'`)
  - Operational exceptions (`exception_flag == 1`)
  - Clinical terms detected in observation
  - Missing event information
- Staff reviewers can **Approve**, **Edit**, **Reject**, or **Escalate** with audit logging.

### 3. Family Q&A Portal (`/questions`)
- Real-time client-side warning banner detects clinical terms as the family member types.
- If a family member submits a medical inquiry (e.g., asking for medication dosage), the system intercepts it, classifies it as `Flagged Medical`, and immediately routes it to facility staff.

### 4. Empirical Evaluation Benchmark (`/experiment`)
- Compares 100 synthetic events between **Baseline (Raw Logs)** and **Prototype (Guarded Pipeline)** across 108 candidate evaluations.
- Actual Measured Results (`experiments/results/experiment_results.json`):
  1. Family Understanding Score: 70.0% -> 90.9% (+20.9%)
  2. Unnecessary Disclosure Rate: 100.0% -> 0.0% (-100.0%)
  3. Unauthorised Disclosure Rate: 20.4% -> 0.0% (-20.4%)
  4. Information Omission Rate: 0.0% -> 3.7% (+3.7%)
  5. Medical-Boundary Violation Rate: 0.9% -> 0.0% (-0.9%)
  6. Human Review Trigger Rate: 0.0% -> 12.0% (+12.0%)
- Includes generated matplotlib charts and standalone Jupyter notebook (`experiments/experiment.ipynb`).

---

## 6. API Endpoint Reference

> [!NOTE]
> This section provides a concise technical overview of all application endpoints implemented in `app.py`. For exhaustive input/output schemas, JSON payload specifications, database operations, and validation rules, see the full specification in [`docs/api_and_schema_reference.md`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/docs/api_and_schema_reference.md).

All endpoints follow strict authentication and role-based access control policies. Session access is guarded via `@login_required`, and non-medical boundaries are enforced at the service layer.

| HTTP Method | Route / Path | Authentication / Role Requirement | Purpose |
|---|---|---|---|
| `GET` | `/login` | Public (Unauthenticated) | Renders the login portal with pre-configured one-click academic credentials. |
| `POST` | `/login` | Public (Unauthenticated) | Authenticates username and password against salted hashes; starts session. |
| `GET` | `/logout` | Public (Unauthenticated) | Clears active session and redirects to login portal. |
| `GET` | `/switch_user/<username>` | Public (Unauthenticated) | Rapid persona switcher for academic evaluation across roles without manual re-login. |
| `GET` | `/` | Public (Unauthenticated) | Root redirector routing authenticated users to `/dashboard` and unauthenticated users to `/login`. |
| `GET` | `/dashboard` | `@login_required` (`admin`, `staff`, `family`) | Displays operational metrics, active resident counts, recent communications, and demo scenario links. |
| `GET` | `/residents` | `@login_required` (`admin`, `staff`, `family`) | Displays facility resident directory, independence levels, and authorized family contacts. |
| `GET` | `/residents/<resident_id>` | `@login_required` (`admin`, `staff`, `family`) | Displays detailed profile for a resident, including care history and family consent status. |
| `GET` | `/care_events` | `@login_required` (`admin`, `staff`, `family`) | Displays filterable log of recorded operational care events with resident and urgency filters. |
| `POST` | `/care_events/add` | `@login_required` (`admin`, `staff`) | Records new care event (observation, assistance level, urgency, exception flag, and confidential staff note). |
| `GET` | `/family_members` | `@login_required` (`admin`, `staff`, `family`) | Displays registered family contacts, relationship to residents, and designated access roles. |
| `GET` | `/consent` | `@login_required` (`admin`, `staff`, `family`) | Displays granular resident information-sharing consent matrix across update categories. |
| `POST` | `/consent/toggle/<consent_id>` | `@login_required` (`admin`, `staff`) | Toggles consent record status between `Active` and `Revoked`. |
| `GET` | `/communication` | `@login_required` (`admin`, `staff`, `family`) | Dual-pane inspector contrasting internal staff records (with notes) against synthesized family summaries. |
| `POST` | `/api/generate_update` | Public REST Endpoint | Programmatically processes care event for family contact, returns JSON, and logs to database. |
| `GET` | `/review_queue` | `@login_required` (`admin`, `staff`) | Displays communications awaiting supervisory review and immutable review audit log history. |
| `POST` | `/review/submit` | `@login_required` (`admin`, `staff`) | Records human review decision (`Approve`, `Edit`, `Reject`, `Escalate`) with justification into `review_logs`. |
| `GET` | `/questions` | `@login_required` (`admin`, `staff`, `family`) | Displays family questions ledger, answers, and real-time medical boundary status flags. |
| `POST` | `/questions/submit` | `@login_required` (`admin`, `staff`, `family`) | Evaluates role and consent, intercepts medical questions (referring to nursing), or queues operational question. |
| `POST` | `/questions/answer` | `@login_required` (`admin`, `staff`) | Records staff operational response to pending family question. |
| `GET` | `/experiment` | `@login_required` (`admin`, `staff`, `family`) | Displays empirical evaluation benchmark dashboard comparing Baseline vs. Prototype metrics and charts. |
| `POST` | `/experiment/run` | `@login_required` (`admin`, `staff`) | Re-executes benchmark evaluation script across 100 care events and regenerates metrics. |
| `GET` | `/experiment/download_notebook` | `@login_required` (`admin`, `staff`, `family`) | Downloads standalone Jupyter analysis notebook (`experiments/experiment.ipynb`). |
| `GET` | `/run_scenario/<scenario>` | `@login_required` (`admin`, `staff`, `family`) | One-click launcher loading benchmark scenarios (Journeys 1–2, Cases 1–4) into the pipeline inspector. |

---

## 7. Database Schema Overview

> [!NOTE]
> This section provides a concise architectural overview of the 9 relational tables in SQLite (`database/database.db`). For exhaustive column definitions, nullability, defaults, check constraints, and ER diagrams, see [`docs/api_and_schema_reference.md`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/docs/api_and_schema_reference.md) and [`database/schema.sql`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/database/schema.sql).

The relational schema strictly enforces foreign key integrity (`PRAGMA foreign_keys = ON;`) to protect operational provenance and resident privacy.

### Relational Tables Summary

1. **`users`**
   - **Purpose:** Manages application authentication credentials, signed session state, and persona authorization levels.
   - **Primary Key:** `user_id` (e.g., `'USR001'`)
   - **Important Key & Relationship Fields:**
     - `username` (UNIQUE, login identifier)
     - `password_hash` (Werkzeug salted SHA-256 hash)
     - `role` (`CHECK` constraint: `'admin'`, `'staff'`, `'family'`)
     - `linked_family_id` (FOREIGN KEY referencing `family_members(family_id)`)

2. **`residents`**
   - **Purpose:** Stores synthetic resident demographic data, baseline care independence tiers, and communication preferences.
   - **Primary Key:** `resident_id` (e.g., `'RES001'`)
   - **Important Key & Relationship Fields:**
     - `resident_name` (synthetic resident name)
     - `independence_level` (`CHECK` constraint: `'Independent'`, `'Needs Minimal Assistance'`, `'Needs Moderate Assistance'`, `'Needs High Assistance'`)
     - `preferred_communication_style` (e.g., `'Brief & Timely'`, `'Daily Summary'`)
     - `active_status` (`1` = Active, `0` = Inactive)

3. **`family_members`**
   - **Purpose:** Catalogs registered family liaisons, familial relationships, and assigned communication access roles.
   - **Primary Key:** `family_id` (e.g., `'FAM001'`)
   - **Important Key & Relationship Fields:**
     - `resident_id` (FOREIGN KEY referencing `residents(resident_id)`)
     - `role` (`CHECK` constraint: `'Primary Family Contact'`, `'Secondary Family Contact'`, `'Emergency Contact'`, `'View-Only Contact'`)
     - `relationship` (e.g., `'Daughter'`, `'Son'`, `'Niece'`)
     - `active_status` (`1` = Active, `0` = Inactive)

4. **`consent`**
   - **Purpose:** Enforces granular, resident-directed information-sharing permissions per family member across specific operational categories.
   - **Primary Key:** `consent_id` (e.g., `'CON001'`)
   - **Important Key & Relationship Fields:**
     - `resident_id` (FOREIGN KEY referencing `residents(resident_id)`)
     - `family_id` (FOREIGN KEY referencing `family_members(family_id)`)
     - `consent_status` (`CHECK` constraint: `'Active'`, `'Revoked'`, `'Pending'`)
     - Category Permission Flags: `care_activity_updates` (0/1), `routine_updates` (0/1), `exception_updates` (0/1), `communication_questions` (0/1)
     - `effective_date` (ISO date string)

5. **`care_events`**
   - **Purpose:** Standardized log of daily operational care events, observed assistance levels, urgency ratings, and confidential shift handover notes.
   - **Primary Key:** `event_id` (e.g., `'EVT001'`)
   - **Important Key & Relationship Fields:**
     - `resident_id` (FOREIGN KEY referencing `residents(resident_id)`)
     - `event_type` (category: `'Morning Routine'`, `'Meal'`, `'Activity'`, `'Mobility'`, `'Personal Care'`, `'Social Activity'`, `'Scheduled Appointment'`, `'Other Operational Event'`)
     - `assistance_level` (`'Independent'`, `'Minimal'`, `'Moderate'`, `'High'`)
     - `urgency` (`'Low'`, `'Normal'`, `'High'`)
     - `exception_flag` (`1` = exception/deviation, `0` = normal routine)
     - `staff_note` (Confidential caregiver handover note, strictly excluded from family disclosures)
     - `created_by` (Staff username)

6. **`exceptions`**
   - **Purpose:** Records operational care deviations (missed appointments, declined meals, mobility refusals) and tracking status.
   - **Primary Key:** `exception_id` (e.g., `'EXC001'`)
   - **Important Key & Relationship Fields:**
     - `event_id` (FOREIGN KEY referencing `care_events(event_id)`)
     - `resident_id` (FOREIGN KEY referencing `residents(resident_id)`)
     - `severity` (`CHECK` constraint: `'Low'`, `'Moderate'`, `'High'`)
     - `review_required` (`1` = review required, `0` = routine)
     - `resolution_status` (`CHECK` constraint: `'Open'`, `'Under Review'`, `'Resolved'`)

7. **`questions`**
   - **Purpose:** Manages family operational inquiries, staff answers, and automated medical boundary interceptions.
   - **Primary Key:** `question_id` (e.g., `'QUE001'`)
   - **Important Key & Relationship Fields:**
     - `family_id` (FOREIGN KEY referencing `family_members(family_id)`)
     - `resident_id` (FOREIGN KEY referencing `residents(resident_id)`)
     - `status` (`CHECK` constraint: `'Pending'`, `'Answered'`, `'Flagged Medical'`, `'Escalated'`)
     - `category` (`'Activity'`, `'Meal'`, `'Routine'`, `'Schedule'`, `'General'`, `'Medical Inquiry'`)
     - `staff_response` (Answer text or automated clinical referral notice)
     - `answered_by` (Staff responder handle or `'Safety Checker (Automated)'`)

8. **`communications`**
   - **Purpose:** Central ledger recording generated family summaries, disclosure decisions, supervisory review statuses, and blocking rationales.
   - **Primary Key:** `comm_id` (e.g., `'COM-A1B2C3D4'`)
   - **Important Key & Relationship Fields:**
     - `event_id` (FOREIGN KEY referencing `care_events(event_id)`)
     - `resident_id` (FOREIGN KEY referencing `residents(resident_id)`)
     - `family_id` (FOREIGN KEY referencing `family_members(family_id)`)
     - `original_observation` (Verbatim factual observation evaluated)
     - `generated_summary` (Synthesized family summary; `NULL` if blocked)
     - `disclosure_status` (`CHECK` constraint: `'Approved'`, `'Blocked'`, `'Pending Review'`, `'Rejected'`)
     - `review_status` (`CHECK` constraint: `'Auto-Approved'`, `'Pending Review'`, `'Reviewed'`, `'Rejected'`, `'Escalated'`)
     - `block_reason` (Human-readable rationale if blocked or rejected)

9. **`review_logs`**
   - **Purpose:** Immutable audit trail recording supervisory actions, timestamps, reviewer identities, and justification notes for regulatory compliance.
   - **Primary Key:** `log_id` (e.g., `'LOG001'`)
   - **Important Key & Relationship Fields:**
     - `comm_id` (FOREIGN KEY referencing `communications(comm_id)`)
     - `question_id` (FOREIGN KEY referencing `questions(question_id)`)
     - `reviewer_name` (Staff or admin reviewer persona)
     - `action_taken` (`CHECK` constraint: `'Approve'`, `'Reject'`, `'Edit'`, `'Escalate'`)
     - `action_timestamp` (Timestamp string)
     - `notes` (Supervisory rationale or edit justification)

### Entity Cardinality & Architecture Summary
- **Residents to Family Members (1:N):** A resident links to multiple family members with differentiated access tiers.
- **Resident & Family Member to Consent (1:1 per pair):** Every resident-family pairing maintains an independent consent configuration.
- **Resident to Care Events (1:N):** Operational events are logged against residents.
- **Care Event to Exception (1:N optional):** Deviations from normal care routines link to the exceptions table.
- **Care Event & Family Member to Communication (N:1, N:1):** Each generated family summary connects a specific event and family contact.
- **Communication to Review Logs (1:N):** Gated communications record every supervisory action (e.g., Edit followed by Approve).
- **User to Family Member (1:1 optional):** Family user accounts link to a corresponding `family_id` to enforce least-privilege scoping.

---

## 8. Running Automated Tests

Run the full test suite with Python's standard `unittest`:
```bash
python -m unittest discover tests -v
```

All 35 tests will execute, verifying:
- Active and revoked consent handling
- Role-based access policies and server-side RBAC enforcement
- Multi-persona isolation across Admin, Staff, and Family roles
- Rule-based concise operational summarization
- All 5 critical failure and edge cases
- Flask web routes, session authentication, and direct URL tampering prevention

---

## 9. Known Limitations & Future Work

### Limitations
1. **Rule-Based Phrasing:** The deterministic summarizer uses pattern templates; highly idiosyncratic staff shorthand may be passed to the review queue rather than auto-summarized.
2. **Local Single-Instance Database:** SQLite is ideal for a local prototype but would transition to PostgreSQL in a multi-facility enterprise environment.

### Recommended Next Steps
1. Implement multi-language localization for family summaries (e.g., Tamil, Hindi, Spanish).
2. Add SMS and email webhook notifications for approved communications.
3. Integrate electronic signature captures for resident consent changes.

---

## 10. Review 2 Improvements

Addressing direct feedback from Semester 5 C28 Review 1 (Qbee evaluation), the project now includes comprehensive formal specifications, rule documentation, and empirical validation:

- **Concrete Database Schema Documentation:** Full relational schema reference for all 9 database tables (`database/schema.sql`), documenting column types, primary/foreign keys, nullability, defaults, constraints, and ER cardinality ([`docs/api_and_schema_reference.md`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/docs/api_and_schema_reference.md)).
- **Formal API & Route Contracts:** Complete specifications for all 23 Flask endpoints in `app.py` detailing HTTP methods, authentication levels, allowed roles, payload validation, database operations, responses, and error handling ([`docs/api_and_schema_reference.md`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/docs/api_and_schema_reference.md)).
- **Documented Deterministic Summarization Rules:** In-depth technical specification of the rule-based, non-LLM text transformation engine in `services/summary_generator.py`, documenting attribute extraction, assistance level mapping, category templates, concrete 18-rule lookup table, clinical regex filtering (`services/safety_checker.py`), and 6 human review triggers ([`docs/summarization_logic.md`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/docs/summarization_logic.md)).
- **Synthetic Dataset Statistics:** Complete breakdown of the evaluation dataset: 5 residents, 5 family members, 5 consent records, 100 care events, 2 exceptions, 3 questions, and 108 candidate evaluation pairs ([`docs/experiment_results.md`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/docs/experiment_results.md)).
- **Baseline vs. Prototype Experiment Results:** Empirical comparison using actual measured figures from `experiments/results/experiment_results.json`: Family Understanding Score: 70.0% -> 90.9%, Unnecessary Disclosure Rate: 100.0% -> 0.0%, Unauthorised Disclosure Rate: 20.4% -> 0.0%, Information Omission Rate: 0.0% -> 3.7%, Medical-Boundary Violation Rate: 0.9% -> 0.0%, and Human Review Trigger Rate: 0.0% -> 12.0% ([`docs/experiment_results.md`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/docs/experiment_results.md)).
- **Error Analysis & Research Limitations:** Comprehensive review of omission trade-offs, clinical regex interception, and unmeasured operational parameters ([`docs/experiment_results.md`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/docs/experiment_results.md)).
- **Review 2 Traceability Documentation:** Matrix mapping Review 1 Qbee requirements directly to codebase implementation, evidentiary files, and verification statuses ([`docs/review2_improvements.md`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/docs/review2_improvements.md)).

