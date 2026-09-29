# Technical API and Database Schema Reference

**Project Title:** From Operational Pain to Working Product: Assisted-Living Facility Supporting Residents' Independence Levels  
**Academic Context:** Semester 5 C28 Review 2 Technical Specification  
**System Classification:** Non-Medical Operational Communication Gateway (Synthetic Data Only)

---

## A. System Data Flow Architecture

The end-to-end communication pipeline follows a strict, sequential gatekeeper model. Information cannot be synthesized or exposed without passing prior authorization and safety checks.

```
       [Raw Care Event Logged]
                 │
                 ▼
       ┌───────────────────┐
       │   Role Checker    │ ──(Insufficient Role)──> [Disclosure Blocked: Logged & Protected]
       └───────────────────┘
                 │ (Role Authorized)
                 ▼
       ┌───────────────────┐
       │  Consent Checker  │ ──(Revoked/Disabled)───> [Disclosure Blocked: Standard Notice]
       └───────────────────┘
                 │ (Consent Granted)
                 ▼
       ┌───────────────────┐
       │ Summary Generator │ (Deterministic Rule-Based Transformation)
       └───────────────────┘
                 │
                 ▼
       ┌───────────────────┐
       │  Safety Checker   │ ──(Clinical Jargon / Missing Facts / High Urgency)
       └───────────────────┘                       │
                 │ (Safe Operational Event)        ▼
                 │                      ┌──────────────────────┐
                 │                      │  Human Review Queue  │
                 │                      └──────────────────────┘
                 │                                 │ (Approve / Edit / Reject / Escalate)
                 ▼                                 ▼
       [Approved Communication] ────────> [Family Portal Delivery]
```

### Pipeline Flow Sequence:
1. **Event Ingestion:** Care staff record an event (`event_type`, `observation`, `assistance_level`, `urgency`, optional `staff_note`).
2. **Role Verification (`role_checker.py`):** The system verifies that the target family member's registered role has permissions to access this category of update.
3. **Consent Verification (`consent_checker.py`):** The system inspects the resident's active consent record for the specific update category (`routine_updates`, `care_activity_updates`, `exception_updates`).
4. **Summary Generation (`summary_generator.py`):** If authorized, the deterministic rule-based engine synthesizes a concise family update and strictly omits internal staff handover notes.
5. **Safety & Boundary Scan (`safety_checker.py`):** The engine scans text against medical regex dictionaries for diagnoses, vitals, drugs, and verifies field completeness.
6. **Human Review Gate (`review_queue.html`):** If high urgency, operational exceptions, missing fields, or clinical terminology are detected, the update is held in `Pending Review`.
7. **Delivery:** Authorized, verified summaries are recorded in `communications` table and made visible on the family portal.

---

## B. Database Schema Reference

The database engine is **SQLite 3** (`database/database.db`), initialized via `database/schema.sql`. Foreign keys are strictly enforced via `PRAGMA foreign_keys = ON;`.

### 1. `users` Table
- **Purpose:** Manages user authentication, session security, and role-based interface authorization.
- **Columns:**
  | Column Name | Data Type | Key | Nullable | Default Value | Constraints / Notes |
  |---|---|---|---|---|---|
  | `user_id` | TEXT | PRIMARY KEY | NO | None | Unique string ID (e.g., `'USR001'`) |
  | `username` | TEXT | UNIQUE | NO | None | Unique login handle (e.g., `'Dharshini'`, `'Madhu'`) |
  | `password_hash` | TEXT | - | NO | None | Werkzeug salted SHA-256 password hash |
  | `role` | TEXT | - | NO | None | `CHECK (role IN ('admin', 'staff', 'family'))` |
  | `display_name` | TEXT | - | NO | None | Human-readable persona title |
  | `linked_family_id` | TEXT | FOREIGN KEY | YES | NULL | References `family_members(family_id)` |
  | `created_at` | DATETIME | - | YES | `CURRENT_TIMESTAMP` | Account creation timestamp |

### 2. `residents` Table
- **Purpose:** Stores synthetic resident demographic details, care independence tiers, and preferred communication styles.
- **Columns:**
  | Column Name | Data Type | Key | Nullable | Default Value | Constraints / Notes |
  |---|---|---|---|---|---|
  | `resident_id` | TEXT | PRIMARY KEY | NO | None | Unique identifier (e.g., `'RES001'`) |
  | `resident_name` | TEXT | - | NO | None | Fictional synthetic name |
  | `age_group` | TEXT | - | NO | None | Age bracket (e.g., `'75-84'`, `'85+'`) |
  | `independence_level` | TEXT | - | NO | None | `CHECK (independence_level IN ('Independent', 'Needs Minimal Assistance', 'Needs Moderate Assistance', 'Needs High Assistance'))` |
  | `preferred_communication_style` | TEXT | - | NO | None | Resident's preference (e.g., `'Brief & Timely'`, `'Daily Summary'`) |
  | `active_status` | INTEGER | - | NO | `1` | `1` = Active, `0` = Inactive |

### 3. `family_members` Table
- **Purpose:** Stores registered family contacts, relationship to resident, and access roles.
- **Columns:**
  | Column Name | Data Type | Key | Nullable | Default Value | Constraints / Notes |
  |---|---|---|---|---|---|
  | `family_id` | TEXT | PRIMARY KEY | NO | None | Unique contact ID (e.g., `'FAM001'`) |
  | `family_name` | TEXT | - | NO | None | Family contact name (e.g., `'Kavi'`, `'Charu'`) |
  | `relationship` | TEXT | - | NO | None | Familial relation (e.g., `'Daughter'`, `'Son'`, `'Niece'`) |
  | `resident_id` | TEXT | FOREIGN KEY | NO | None | References `residents(resident_id)` |
  | `role` | TEXT | - | NO | None | `CHECK (role IN ('Primary Family Contact', 'Secondary Family Contact', 'Emergency Contact', 'View-Only Contact'))` |
  | `active_status` | INTEGER | - | NO | `1` | `1` = Active, `0` = Inactive |

### 4. `consent` Table
- **Purpose:** Enforces granular, resident-directed information-sharing permissions across categories.
- **Columns:**
  | Column Name | Data Type | Key | Nullable | Default Value | Constraints / Notes |
  |---|---|---|---|---|---|
  | `consent_id` | TEXT | PRIMARY KEY | NO | None | Unique consent ID (e.g., `'CON001'`) |
  | `resident_id` | TEXT | FOREIGN KEY | NO | None | References `residents(resident_id)` |
  | `family_id` | TEXT | FOREIGN KEY | NO | None | References `family_members(family_id)` |
  | `care_activity_updates` | INTEGER | - | NO | `0` | Boolean flag (`1` = permitted, `0` = blocked) |
  | `routine_updates` | INTEGER | - | NO | `0` | Boolean flag (`1` = permitted, `0` = blocked) |
  | `exception_updates` | INTEGER | - | NO | `0` | Boolean flag (`1` = permitted, `0` = blocked) |
  | `communication_questions` | INTEGER | - | NO | `0` | Boolean flag (`1` = Q&A allowed, `0` = blocked) |
  | `consent_status` | TEXT | - | NO | None | `CHECK (consent_status IN ('Active', 'Revoked', 'Pending'))` |
  | `effective_date` | TEXT | - | NO | None | ISO date string (`YYYY-MM-DD`) |

### 5. `care_events` Table
- **Purpose:** Logs standardized daily care events, observed assistance levels, operational urgency, and confidential staff notes.
- **Columns:**
  | Column Name | Data Type | Key | Nullable | Default Value | Constraints / Notes |
  |---|---|---|---|---|---|
  | `event_id` | TEXT | PRIMARY KEY | NO | None | Unique event ID (e.g., `'EVT001'`) |
  | `resident_id` | TEXT | FOREIGN KEY | NO | None | References `residents(resident_id)` |
  | `event_datetime` | TEXT | - | NO | None | Date-time string (`YYYY-MM-DD HH:MM:SS`) |
  | `event_type` | TEXT | - | NO | None | Category (e.g., `'Morning Routine'`, `'Meal'`, `'Activity'`, `'Mobility'`, `'Personal Care'`, `'Social Activity'`, `'Scheduled Appointment'`, `'Other Operational Event'`) |
  | `observation` | TEXT | - | YES | NULL | Observable factual care record |
  | `assistance_level` | TEXT | - | YES | NULL | Level (e.g., `'Independent'`, `'Minimal'`, `'Moderate'`, `'High'`) |
  | `urgency` | TEXT | - | NO | `'Normal'` | Urgency tag (`'Low'`, `'Normal'`, `'High'`) |
  | `exception_flag` | INTEGER | - | NO | `0` | `1` = Operational exception, `0` = Standard |
  | `staff_note` | TEXT | - | YES | NULL | **Confidential internal note** (strictly not disclosed) |
  | `created_by` | TEXT | - | NO | None | Staff username who recorded event |

### 6. `exceptions` Table
- **Purpose:** Tracks operational deviations (e.g., missed activities, declined meals) and review status.
- **Columns:**
  | Column Name | Data Type | Key | Nullable | Default Value | Constraints / Notes |
  |---|---|---|---|---|---|
  | `exception_id` | TEXT | PRIMARY KEY | NO | None | Unique exception ID (e.g., `'EXC001'`) |
  | `event_id` | TEXT | FOREIGN KEY | NO | None | References `care_events(event_id)` |
  | `resident_id` | TEXT | FOREIGN KEY | NO | None | References `residents(resident_id)` |
  | `exception_type` | TEXT | - | NO | None | Descriptive label (e.g., `'Missed Scheduled Session'`) |
  | `description` | TEXT | - | NO | None | Objective explanation of deviation |
  | `severity` | TEXT | - | NO | None | `CHECK (severity IN ('Low', 'Moderate', 'High'))` |
  | `review_required` | INTEGER | - | NO | `1` | `1` = Review required, `0` = Routine |
  | `resolution_status` | TEXT | - | NO | None | `CHECK (resolution_status IN ('Open', 'Under Review', 'Resolved'))` |

### 7. `questions` Table
- **Purpose:** Logs family operational inquiries, staff answers, and automated medical boundary interceptions.
- **Columns:**
  | Column Name | Data Type | Key | Nullable | Default Value | Constraints / Notes |
  |---|---|---|---|---|---|
  | `question_id` | TEXT | PRIMARY KEY | NO | None | Unique question ID (e.g., `'QUE001'`) |
  | `family_id` | TEXT | FOREIGN KEY | NO | None | References `family_members(family_id)` |
  | `resident_id` | TEXT | FOREIGN KEY | NO | None | References `residents(resident_id)` |
  | `question_text` | TEXT | - | NO | None | Text submitted by family member |
  | `category` | TEXT | - | NO | None | Topic (e.g., `'Activity'`, `'Meal'`, `'Routine'`, `'Schedule'`, `'General'`, `'Medical Inquiry'`) |
  | `status` | TEXT | - | NO | None | `CHECK (status IN ('Pending', 'Answered', 'Flagged Medical', 'Escalated'))` |
  | `created_at` | TEXT | - | NO | None | Submission timestamp (`YYYY-MM-DD HH:MM:SS`) |
  | `staff_response` | TEXT | - | YES | NULL | Operational response text |
  | `answered_by` | TEXT | - | YES | NULL | Staff persona who responded |
  | `answered_at` | TEXT | - | YES | NULL | Response timestamp |

### 8. `communications` Table
- **Purpose:** Stores the output ledger of generated family summaries, disclosure statuses, and block reasons.
- **Columns:**
  | Column Name | Data Type | Key | Nullable | Default Value | Constraints / Notes |
  |---|---|---|---|---|---|
  | `comm_id` | TEXT | PRIMARY KEY | NO | None | Unique communication ID (e.g., `'COM-A1B2C3D4'`) |
  | `event_id` | TEXT | FOREIGN KEY | NO | None | References `care_events(event_id)` |
  | `resident_id` | TEXT | FOREIGN KEY | NO | None | References `residents(resident_id)` |
  | `family_id` | TEXT | FOREIGN KEY | NO | None | References `family_members(family_id)` |
  | `original_observation` | TEXT | - | NO | None | Verbatim care observation evaluated |
  | `generated_summary` | TEXT | - | YES | NULL | Concise rule-generated summary (NULL if blocked) |
  | `disclosure_status` | TEXT | - | NO | None | `CHECK (disclosure_status IN ('Approved', 'Blocked', 'Pending Review', 'Rejected'))` |
  | `review_status` | TEXT | - | NO | None | `CHECK (review_status IN ('Auto-Approved', 'Pending Review', 'Reviewed', 'Rejected', 'Escalated'))` |
  | `block_reason` | TEXT | - | YES | NULL | Explanation if disclosure blocked or rejected |
  | `created_at` | TEXT | - | NO | None | Generation timestamp |

### 9. `review_logs` Table
- **Purpose:** Provides an immutable audit trail of supervisor actions in the review queue.
- **Columns:**
  | Column Name | Data Type | Key | Nullable | Default Value | Constraints / Notes |
  |---|---|---|---|---|---|
  | `log_id` | TEXT | PRIMARY KEY | NO | None | Unique log ID (e.g., `'LOG001'`) |
  | `comm_id` | TEXT | FOREIGN KEY | YES | NULL | References `communications(comm_id)` |
  | `question_id` | TEXT | FOREIGN KEY | YES | NULL | References `questions(question_id)` |
  | `reviewer_name` | TEXT | - | NO | None | Staff/admin reviewer persona |
  | `action_taken` | TEXT | - | NO | None | `CHECK (action_taken IN ('Approve', 'Reject', 'Edit', 'Escalate'))` |
  | `action_timestamp` | TEXT | - | NO | None | Timestamp of action |
  | `notes` | TEXT | - | YES | NULL | Justification / reasoning notes |

---

## C. Entity Relationships and Cardinality

```
┌──────────────┐          1:N          ┌──────────────────┐          1:1          ┌──────────┐
│  residents   │ ───────────────────── │  family_members  │ ───────────────────── │  users   │
└──────────────┘                       └──────────────────┘                       └──────────┘
       │ 1                                      │ 1
       │                                        │
       │ 1:N                                    │ 1:N
       ▼                                        ▼
┌──────────────┐          N:1          ┌──────────────────┐
│ care_events  │                       │     consent      │
└──────────────┘                       └──────────────────┘
       │ 1                                      │
       │                                        │
       │ 1:N                                    │ 1:N
       ▼                                        ▼
┌──────────────┐          N:1          ┌──────────────────┐
│  exceptions  │                       │    questions     │
└──────────────┘                       └──────────────────┘
       │                                        │
       │                                        │
       ▼                                        ▼
┌─────────────────────────────────────────────────────────┐
│                     communications                      │
└─────────────────────────────────────────────────────────┘
                            │ 1
                            │ 1:N
                            ▼
┌─────────────────────────────────────────────────────────┐
│                       review_logs                       │
└─────────────────────────────────────────────────────────┘
```

### Relationship Rules:
1. **Resident to Family Members (1:N):** A resident can have multiple family contacts with distinct roles (e.g., Devi Raman has Kavi as Primary and Charu as Secondary).
2. **Resident and Family Member to Consent (1:1 per pair):** Each unique (resident, family member) pair has exactly one consent configuration specifying category-level permissions.
3. **Resident to Care Events (1:N):** All care events are linked to a valid resident.
4. **Care Event to Exception (1:N optional):** Operational events marked as exceptions link to the exceptions table for severity classification.
5. **Care Event and Family Member to Communication (N:1, N:1):** Every generated communication bridges an event and a requesting contact.
6. **Communication to Review Logs (1:N):** Gated communications can undergo multiple review audit actions (e.g., Edit followed by Approve).
7. **User to Family Member (1:1 optional):** User accounts for family personas link to a corresponding `family_id` to enforce role scoping.

---

## D. API & Flask Route Contracts

All 23 routes in `app.py` are documented below with input validation, authorization rules, database operations, and response contracts.

---

### 1. Authentication Routes

#### `GET /login`
- **Purpose:** Renders the authentication portal and one-click academic demo credentials.
- **Authentication:** None.
- **Allowed Roles:** Public / unauthenticated.
- **Response:** HTML (`login.html`) with HTTP 200.

#### `POST /login`
- **Purpose:** Authenticates user credentials and establishes a signed session.
- **Authentication:** None.
- **Input Fields:**
  - `username` (string, required)
  - `password` (string, required)
- **Validation:** Username checked against `users` table; password validated via Werkzeug `check_password_hash`.
- **Database Operation:** `SELECT * FROM users WHERE username = ?`
- **Response:**
  - On Success: Sets `session['user_id']`, `session['username']`, `session['role']`, `session['display_name']`; redirects to `/dashboard` with success flash.
  - On Failure: Re-renders `login.html` with error flash (`Invalid credentials`).

#### `GET /logout`
- **Purpose:** Terminates the current session.
- **Authentication:** None.
- **Response:** Clears `session`; redirects to `/login` with info flash.

#### `GET /switch_user/<username>`
- **Purpose:** One-click academic demo persona switcher for testing different role permissions without manual logout.
- **Authentication:** None.
- **URL Parameter:** `username` (string, e.g., `'Dharshini'`, `'Madhu'`, `'Kavi'`).
- **Validation:** Verifies username exists in `users` table.
- **Response:** Updates session to target user; redirects to referring URL or `/dashboard`.

---

### 2. Dashboard & Navigation Routes

#### `GET /`
- **Purpose:** Root redirector.
- **Authentication:** None.
- **Response:** Redirects to `/dashboard` if authenticated, else `/login`.

#### `GET /dashboard`
- **Purpose:** Main academic dashboard showing operational counts, recent communications, and demo scenario triggers.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`, `family`.
- **Database Operation:** Computes counts for residents, care events, pending reviews, approved comms, blocked comms, active consents, questions; selects recent communications.
- **Response:** HTML (`dashboard.html`) with HTTP 200.

---

### 3. Residents & Profiles

#### `GET /residents`
- **Purpose:** Displays directory of facility residents, independence tiers, and authorized family contacts.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`, `family`.
- **Database Operation:** `SELECT r.*, GROUP_CONCAT(...) FROM residents r LEFT JOIN family_members f ...`
- **Response:** HTML (`residents.html`) with HTTP 200.

#### `GET /residents/<resident_id>`
- **Purpose:** Displays detailed resident profile, care timeline, and associated family consent matrix.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`, `family`.
- **URL Parameter:** `resident_id` (string, e.g., `'RES001'`).
- **Validation:** Checks if resident exists; if not, redirects to `/residents` with danger flash.
- **Database Operation:** Queries `residents`, joins `family_members` with `consent`, and selects `care_events`.
- **Response:** HTML (`resident_detail.html`) with HTTP 200.

---

### 4. Care Events Management

#### `GET /care_events`
- **Purpose:** Displays care event log with resident and urgency filters.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`, `family`.
- **Query Parameters (Optional):**
  - `resident_id` (string)
  - `urgency` (string: `'Low'`, `'Normal'`, `'High'`)
- **Database Operation:** Queries `care_events` joined with `residents`.
- **Response:** HTML (`care_events.html`) with HTTP 200.

#### `POST /care_events/add`
- **Purpose:** Allows care staff to record a new operational care event.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`.
- **Input Fields (Form Data):**
  - `resident_id` (string, required)
  - `event_type` (string, required)
  - `assistance_level` (string, required: `'Independent'`, `'Minimal'`, `'Moderate'`, `'High'`)
  - `urgency` (string, required: `'Low'`, `'Normal'`, `'High'`)
  - `observation` (string, required)
  - `staff_note` (string, optional: confidential internal note)
  - `exception_flag` (string: `'1'` if marked, else omitted)
- **Validation:** Auto-generates sequential `event_id` (`EVT{count:03d}`); sets `created_by` from session.
- **Database Operation:** `INSERT INTO care_events (...) VALUES (...)`
- **Response:** Redirects to `/care_events` with success flash.

---

### 5. Family Directory & Consent Matrix

#### `GET /family_members`
- **Purpose:** Displays family members directory, relationships, and designated operational roles.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`, `family`.
- **Database Operation:** Queries `family_members` joined with `residents`.
- **Response:** HTML (`family_members.html`) with HTTP 200.

#### `GET /consent`
- **Purpose:** Displays granular resident information-sharing consent matrix across update categories.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`, `family`.
- **Database Operation:** Queries `consent` joined with `residents` and `family_members`.
- **Response:** HTML (`consent.html`) with HTTP 200.

#### `POST /consent/toggle/<consent_id>`
- **Purpose:** Toggles consent status between `'Active'` and `'Revoked'`.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`.
- **URL Parameter:** `consent_id` (string, e.g., `'CON001'`).
- **Database Operation:** `UPDATE consent SET consent_status = ? WHERE consent_id = ?`
- **Response:** Redirects to `/consent` with info flash.

---

### 6. Operational Communication & Pipeline Execution

#### `GET /communication`
- **Purpose:** Dual-pane inspection view and family update generator. Evaluates authorization gates and renders family summary.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`, `family`.
- **Query Parameters (Optional):**
  - `event_id` (string, defaults to latest event)
  - `family_id` (string, defaults to linked family contact)
- **Processing:** Invokes `process_care_event_for_family(conn, event_id, family_id, save_to_db=False)`.
- **Response:** HTML (`communication.html`) with HTTP 200 containing pipeline trace and delivered history.

#### `POST /api/generate_update`
- **Purpose:** REST API endpoint for programmatic communication pipeline evaluation.
- **Authentication:** None (Public REST-style endpoint).
- **Request Headers:** `Content-Type: application/json`
- **Request Body (JSON):**
  ```json
  {
    "event_id": "EVT001",
    "family_id": "FAM001"
  }
  ```
- **Validation:** Requires both `event_id` and `family_id`. Returns HTTP 400 if missing.
- **Database Operation:** Runs `process_care_event_for_family(..., save_to_db=True)`, writes to `communications`.
- **Response (JSON):**
  ```json
  {
    "success": true,
    "comm_id": "COM-E4A28B10",
    "event_id": "EVT001",
    "resident_id": "RES001",
    "resident_name": "Devi Raman",
    "family_id": "FAM001",
    "family_name": "Kavi",
    "family_role": "Primary Family Contact",
    "consent_status": "Active",
    "role_check": { "passed": true, "reason": "Primary Family Contact has full operational update access." },
    "consent_check": { "passed": true, "reason": "Authorized by active resident consent for care activity updates." },
    "safety_check": { "passed": true, "flagged": [] },
    "completeness_check": { "passed": true, "missing": [] },
    "original_observation": "Resident participated in the afternoon music session with minimal assistance.",
    "internal_staff_note": "Devi enjoyed playing the tambourine...",
    "generated_summary": "Your daughter participated in the music session with minimal assistance.",
    "disclosure_status": "Approved",
    "review_status": "Auto-Approved",
    "review_triggers": [],
    "block_reason": null
  }
  ```

---

### 7. Human Review Queue

#### `GET /review_queue`
- **Purpose:** Displays communications awaiting supervisory review and immutable review audit trail.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`.
- **Database Operation:** Queries `communications` where `review_status = 'Pending Review'` and `review_logs`.
- **Response:** HTML (`review_queue.html`) with HTTP 200.

#### `POST /review/submit`
- **Purpose:** Records staff supervisory decision on a gated communication item.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`.
- **Input Fields (Form Data):**
  - `comm_id` (string, required)
  - `action_taken` (string, required: `'Approve'`, `'Edit'`, `'Reject'`, `'Escalate'`)
  - `edited_summary` (string, optional: replacement summary text if edited)
  - `decision_notes` (string, required: justification reason)
- **Processing:** Updates `communications` status; creates entry in `review_logs`.
- **Database Operations:**
  - `UPDATE communications SET disclosure_status = ?, review_status = ? ... WHERE comm_id = ?`
  - `INSERT INTO review_logs (log_id, comm_id, question_id, reviewer_name, action_taken, action_timestamp, notes) VALUES (...)`
- **Response:** Redirects to `/review_queue` with success flash.

---

### 8. Family Questions & Q&A

#### `GET /questions`
- **Purpose:** Displays family Q&A portal with questions history and staff answers.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`, `family`.
- **Database Operation:** Queries `questions` joined with `residents` and `family_members`.
- **Response:** HTML (`questions.html`) with HTTP 200.

#### `POST /questions/submit`
- **Purpose:** Submits an inquiry to staff. Evaluates role permissions, consent, and intercepts medical advice inquiries.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`, `family`.
- **Input Fields (Form Data):**
  - `resident_id` (string, required)
  - `category` (string, required: `'Activity'`, `'Meal'`, `'Routine'`, `'Schedule'`, `'General'`)
  - `question_text` (string, required)
- **Validation & Safety Rules:**
  1. Calls `can_submit_questions(role)`: Blocks View-Only and Emergency contacts.
  2. Calls `check_question_consent(consent)`: Blocks if resident disabled questions.
  3. Calls `classify_question(text)`: If medical terms detected (`fever`, `dosage`, `medicine`, `diagnose`), marks status as `'Flagged Medical'` and generates non-medical disclaimer redirecting inquiry to nursing staff.
- **Database Operation:** `INSERT INTO questions (...) VALUES (...)`
- **Response:** Redirects to `/questions` with appropriate success/warning flash.

#### `POST /questions/answer`
- **Purpose:** Records staff operational answer to a pending question.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`.
- **Input Fields (Form Data):**
  - `question_id` (string, required)
  - `staff_response` (string, required)
- **Database Operation:** `UPDATE questions SET staff_response = ?, status = 'Answered', answered_by = ?, answered_at = ? WHERE question_id = ?`
- **Response:** Redirects to `/questions` with success flash.

---

### 9. Academic Experiment & Evaluation

#### `GET /experiment`
- **Purpose:** Displays comparative benchmark results (Baseline vs. Prototype), metric definitions, and matplotlib chart.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`, `family`.
- **Processing:** Reads `experiments/results/experiment_results.json` (computes if missing).
- **Response:** HTML (`experiment.html`) with HTTP 200.

#### `POST /experiment/run`
- **Purpose:** Re-executes the empirical evaluation benchmark across all synthetic care events.
- **Authentication:** Required (`@login_required`).
- **Allowed Roles:** `admin`, `staff`.
- **Processing:** Executes `run_experiment()`, recalculates metrics, regenerates `metrics_comparison.png`.
- **Response:** Redirects to `/experiment` with success flash.

#### `GET /experiment/download_notebook`
- **Purpose:** Serves the standalone Jupyter analysis notebook (`experiments/experiment.ipynb`) as a downloadable attachment.
- **Authentication:** Required (`@login_required`).
- **Response:** File attachment download (`experiment.ipynb`).

---

### 10. Academic Demo Scenario Triggers

#### `GET /run_scenario/<scenario>`
- **Purpose:** One-click launcher for key evaluation journeys and failure modes.
- **Authentication:** Required (`@login_required`).
- **Allowed Scenarios:**
  - `journey_1`: `EVT001` with `FAM001` (Normal music session -> Approved update to Kavi).
  - `journey_2`: `EVT002` with `FAM001` (High-urgency missed mobility session -> Gated for Review).
  - `case_1`: `EVT003` with `FAM004` (Revoked consent -> Disclosure Blocked).
  - `case_2`: `EVT004` with `FAM004` (View-Only role accessing personal care -> Disclosure Blocked).
  - `case_3`: `EVT005` with `FAM003` (Medical terminology in observation -> Gated for Review).
  - `case_4`: `EVT006` with `FAM005` (Missing observation facts -> Gated for Review).
- **Response:** Redirects to `/communication?event_id=...&family_id=...` with informative demo flash notice.
