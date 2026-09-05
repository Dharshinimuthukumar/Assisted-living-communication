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
- Compares 100 synthetic events between **Baseline (Raw Logs)** and **Prototype (Guarded Pipeline)**.
- Measures:
  1. Family Understanding Score ($59.2\% \to 91.8\%$)
  2. Unnecessary Disclosure Rate ($100\% \to 0\%$)
  3. Unauthorised Disclosure Rate ($33.3\% \to 0\%$)
  4. Information Omission Rate ($0.0\% \to 0.0\%$)
  5. Medical-Boundary Violation Rate ($6.7\% \to 0.0\%$)
  6. Human Review Trigger Rate ($18.7\%$)
- Includes generated matplotlib charts and standalone Jupyter notebook (`experiments/experiment.ipynb`).

---

## 6. Running Automated Tests

Run the full test suite with Python's standard `unittest`:
```bash
python -m unittest discover tests -v
```

All 28 tests will execute, verifying:
- Active and revoked consent handling
- Role-based access policies
- Rule-based concise operational summarization
- All 5 critical failure and edge cases
- Flask web routes and session handling

---

## 7. Known Limitations & Future Work

### Limitations
1. **Rule-Based Phrasing:** The deterministic summarizer uses pattern templates; highly idiosyncratic staff shorthand may be passed to the review queue rather than auto-summarized.
2. **Local Single-Instance Database:** SQLite is ideal for a local prototype but would transition to PostgreSQL in a multi-facility enterprise environment.

### Recommended Next Steps
1. Implement multi-language localization for family summaries (e.g., Tamil, Hindi, Spanish).
2. Add SMS and email webhook notifications for approved communications.
3. Integrate electronic signature captures for resident consent changes.
