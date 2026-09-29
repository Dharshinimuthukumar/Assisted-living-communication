# Assisted-Living Facility Operational Communication System

> **ACADEMIC PROOF OF CONCEPT (Semester 5 C28)**
> **PROJECT TITLE:** From Operational Pain to Working Product: Assisted-Living Facility Supporting Residents' Independence Levels
>
> **IMPORTANT SCOPE NOTICE:** This system is **NOT** a medical diagnosis system, clinical decision support system, or medical prediction engine. It supports **operational communication only** between assisted-living staff and authorized family members.

---

## 1. Project Overview

Assisted-living families currently face a communication dilemma: they either receive *too little information* or are overwhelmed by *raw care logs* containing internal staff handover notes and confusing medical jargon.

This working proof-of-concept solves this problem by providing concise, relevant operational updates while enforcing:

- **Resident Consent:** Granular, category-level information-sharing permissions.
- **Family Roles:** Tiered access across Primary, Secondary, Emergency, and View-Only contacts.
- **Strict Non-Medical Boundary:** Intercepts clinical terms, diagnoses, and medication advice.
- **Human-in-the-Loop Review:** Mandatory review queue for high-urgency events and exceptions.
- **Data Segregation:** Internal staff notes are never disclosed to family members.

---

## 2. Directory Structure

```text
assisted-living-communication/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── database/
│   ├── database.db
│   └── schema.sql
│
├── data/
│   ├── residents.csv
│   ├── care_events.csv
│   ├── family_members.csv
│   ├── consent.csv
│   ├── questions.csv
│   └── exceptions.csv
│
├── scripts/
│   ├── generate_data.py
│   └── initialize_database.py
│
├── services/
│   ├── consent_checker.py
│   ├── role_checker.py
│   ├── summary_generator.py
│   ├── safety_checker.py
│   └── communication_service.py
│
├── templates/
├── static/
│
├── experiments/
│   ├── run_experiment.py
│   ├── experiment.ipynb
│   └── results/
│
├── tests/
│   ├── test_consent.py
│   ├── test_roles.py
│   ├── test_summary.py
│   ├── test_failure_cases.py
│   └── test_routes.py
│
└── docs/
    ├── workflow.md
    ├── architecture.md
    ├── failure_mode_analysis.md
    ├── human_review_points.md
    ├── user_validation.md
    ├── experiment_methodology.md
    ├── api_and_schema_reference.md
    ├── summarization_logic.md
    ├── experiment_results.md
    └── review2_improvements.md
