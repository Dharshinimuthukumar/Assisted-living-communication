# Unit Testing Architecture and System Error Boundaries

**Project Title:** From Operational Pain to Working Product: Assisted-Living Facility Supporting Residents' Independence Levels  
**Academic Context:** Semester 5 C28 Review 3 Technical Documentation  
**Target Modules:** [`tests/`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/tests), [`services/`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/services), [`app.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/app.py)  
**System Classification:** Non-Medical Operational Communication Gateway (Synthetic Data Only)

---

## 1. Executive Summary & Design Philosophy

This document provides a technical specification of the automated unit testing architecture and the multi-layered runtime error boundaries implemented in the Assisted-Living Communication prototype.

### Core Testing & Safety Principles
1. **Verification of Non-Medical Operational Boundaries:** Tests rigorously verify that clinical diagnoses, vital sign metrics, pharmaceutical dosages, and medical conclusions are intercepted before reaching family recipients.
2. **Deterministic Security Gates:** Authorization (family roles) and resident consent (category-level permissions) are verified through independent, repeatable assertions prior to any summary generation.
3. **Data Segregation & Leakage Prevention:** Automated assertions confirm that internal caregiver shift notes (`staff_note`) are structurally excluded from all family-facing payloads.
4. **Defense-in-Depth Error Handling:** Failures do not trigger unhandled exceptions or expose internal stack traces; instead, they transition into controlled operational states: **Blocked**, **Rejected**, or routed to **Pending Human Review**.
5. **No Absolute Guarantees Claimed:** While deterministic rules and comprehensive tests significantly reduce the risk of unauthorized disclosure and data omission, the system operates as an operational support prototype and relies on mandatory human-in-the-loop review for anomalous or high-urgency conditions.

---

## 2. Automated Test Suite Specification

The automated test suite is implemented using Python's standard `unittest` framework. It comprises **35 discrete test cases** distributed across **5 specialized test modules** located in [`tests/`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/tests).

### Test Suite Summary Matrix

| Test Module | Test Class | Test Count | Scope & Focus Area | Target Code Under Test |
|---|---|---|---|---|
| [`test_consent.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/tests/test_consent.py) | `TestConsentChecker` | **7** | Active, revoked, missing, and granular category consent enforcement | [`services/consent_checker.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/services/consent_checker.py) |
| [`test_failure_cases.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/tests/test_failure_cases.py) | `TestFailureCases` | **5** | Academic failure modes, edge cases, and end-to-end pipeline interception | [`services/communication_service.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/services/communication_service.py), [`services/safety_checker.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/services/safety_checker.py) |
| [`test_roles.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/tests/test_roles.py) | `TestRoleChecker` | **5** | Tiered family role permissions (Primary, Secondary, Emergency, View-Only) | [`services/role_checker.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/services/role_checker.py) |
| [`test_routes.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/tests/test_routes.py) | `TestAppRoutes` | **14** | Flask route rendering, session authentication, RBAC authorization, persona scoping, isolation | [`app.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/app.py) |
| [`test_summary.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/tests/test_summary.py) | `TestSummaryGenerator` | **4** | Rule-based text transformation, assistance phrasing, internal note elimination | [`services/summary_generator.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/services/summary_generator.py) |
| **Total** | **5 Classes** | **35** | **Comprehensive coverage of core security, RBAC, safety, and operational workflows** | **Entire Application Stack** |

---

### Detailed Module Breakdown

#### 2.1 `tests/test_consent.py` (7 Tests)
Validates resident-directed information-sharing permissions and granular category switches.

- **`test_valid_active_consent`**:
  - *Condition:* Valid active consent record with all category flags (`care_activity_updates=1`, `routine_updates=1`, `exception_updates=1`, `communication_questions=1`).
  - *Verification:* `check_consent` returns `(True, reason)`; reason contains `"Authorized"`.
- **`test_revoked_consent_blocks_disclosure`**:
  - *Condition:* Consent record with `consent_status = 'Revoked'`.
  - *Verification:* `check_consent` returns `(False, reason)`; reason explicitly states consent is `'Revoked'`, completely blocking access.
- **`test_missing_consent_record`**:
  - *Condition:* `None` passed as consent record (simulates unconfigured resident-family pair).
  - *Verification:* `check_consent` returns `(False, reason)`; verifies safe fallback message: `"Information cannot be displayed because the current family member does not have permission to receive this update."`
- **`test_category_level_routine_permission_disabled`**:
  - *Condition:* Active consent with `routine_updates = 0` receiving a `'Morning Routine'` event.
  - *Verification:* `check_consent` returns `False`; confirms that granular routine updates are blocked while leaving other categories uncompromised.
- **`test_category_level_activity_permission_enabled`**:
  - *Condition:* Active consent with `care_activity_updates = 1` receiving a `'Meal'` event.
  - *Verification:* `check_consent` returns `True`.
- **`test_exception_consent_disabled`**:
  - *Condition:* Active consent with `exception_updates = 0` receiving an event with `exception_flag = 1` and `urgency = 'High'`.
  - *Verification:* `check_consent` returns `False`; confirms urgent deviations are withheld if resident has not granted exception-sharing permission.
- **`test_question_consent`**:
  - *Condition:* Evaluates `check_question_consent` against active, partial (`communication_questions=0`), and revoked consent records.
  - *Verification:* Returns `True` only when active and explicitly enabled; otherwise returns `False`.

#### 2.2 `tests/test_failure_cases.py` (5 Tests)
Verifies the system's runtime defenses across the five critical academic failure modes using an isolated in-memory SQLite database initialized with [`database/schema.sql`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/database/schema.sql).

- **`test_case_1_no_consent_blocks_disclosure` (Failure Case 1)**:
  - *Condition:* Contact (`FAM_NOCONSENT`) has revoked consent (`consent_status = 'Revoked'`) and attempts to access an activity event (`EVT_C1`).
  - *Pipeline Execution:* Invokes `process_care_event_for_family(conn, 'EVT_C1', 'FAM_NOCONSENT')`.
  - *Outcome:* `disclosure_status == 'Blocked'`, `generated_summary is None`, and `block_reason` contains `"Information cannot be displayed"`. Confirms zero unauthorized data disclosure.
- **`test_case_2_insufficient_role_permissions` (Failure Case 2)**:
  - *Condition:* Emergency contact (`FAM_RESTRICTED`) attempts to view a routine lunch event (`EVT_C2`, non-urgent, `exception_flag = 0`).
  - *Pipeline Execution:* Invokes `process_care_event_for_family(conn, 'EVT_C2', 'FAM_RESTRICTED')`.
  - *Outcome:* `disclosure_status == 'Blocked'`, `generated_summary is None`, and `block_reason` explicitly cites `"restricted from routine daily care logs"`. Preserves operational signal-to-noise ratio.
- **`test_case_3_medical_language_interception` (Failure Case 3)**:
  - *Condition:* Raw caregiver observation contains prohibited medical terminology: *"Resident exhibited fever of 101F and suspected chest infection; staff gave paracetamol 500mg."*
  - *Unit Level:* `check_text_safety` flags `'fever'`, `'infection'`, and `'paracetamol'`, returning `is_safe == False`.
  - *Pipeline Level:* Event processed for authorized primary contact (`FAM_PRIMARY`).
  - *Outcome:* `disclosure_status == 'Pending Review'`, `safety_check['passed'] == False`, and review triggers include medical language warnings. Withheld from family until staff review.
- **`test_case_4_missing_information_detection` (Failure Case 4)**:
  - *Condition:* Incomplete event dictionary with empty observation string (`""`) and `assistance_level = None`.
  - *Unit Level:* `check_missing_information` returns `is_complete == False` and identifies missing fields `['observation', 'assistance_level']`.
  - *Review Evaluation:* `requires_human_review` evaluates to `True`, appending `"Missing operational event information"`. Confirms system avoids fabricating missing context.
- **`test_case_5_family_medical_question_boundary` (Failure Case 5)**:
  - *Condition:* Family submits medical query: *"What medicine or dosage should I give my father for his fever and cough?"*
  - *Classification:* `classify_question` returns `(False, disclaimer)`; contains persistent non-medical notice and redirects to facility staff.
  - *Positive Control:* Operational question (*"Did my mother participate in the afternoon gardening session?"*) returns `(True, reason)`.

#### 2.3 `tests/test_roles.py` (5 Tests)
Validates the role-based access control (RBAC) matrix in [`services/role_checker.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/services/role_checker.py).

- **`test_primary_family_contact_access`**:
  - *Verification:* Primary Contact authorized for all routine events (`Meal`), sensitive events (`Personal Care`), urgent exceptions (`High`/`1`), and permitted to submit inquiries (`can_submit_questions == True`).
- **`test_secondary_family_contact_access`**:
  - *Verification:* Secondary Contact authorized for standard updates (`Social Activity`) and permitted to submit questions.
- **`test_emergency_contact_restrictions`**:
  - *Verification:* Emergency Contact blocked from routine logs (`Meal`), authorized for high-urgency exceptions (`Mobility`/`High`/`1`), and blocked from submitting general Q&A inquiries.
- **`test_view_only_contact_restrictions`**:
  - *Verification:* View-Only Contact authorized for general social activities, but strictly blocked from sensitive personal care and high-urgency exceptions; blocked from Q&A inquiries.
- **`test_invalid_role`**:
  - *Verification:* Unrecognized role strings (e.g., `'Unregistered Visitor'`) return `(False, reason)` citing invalid role.

#### 2.4 `tests/test_routes.py` (14 Tests)
Integration tests executing against Flask's test client (`app.test_client()`), verifying route rendering, authentication, and server-side RBAC enforcement:

- **`test_login_page_renders`**: Checks `GET /login`; verifies HTTP 200 and presence of operational disclaimer banner.
- **`test_quick_user_switch`**: Checks `GET /switch_user/Dharshini`; verifies automatic session population and redirect to `/dashboard`.
- **`test_dashboard_authenticated`**: Checks `GET /dashboard` under authenticated session (`Madhu`); verifies operational metrics presentation (`Total Residents`, `Total Care Events`, `Pending Human Reviews`).
- **`test_residents_and_detail`**: Checks `GET /residents` and `GET /residents/RES001`; verifies list rendering and resident profile details.
- **`test_communication_dual_pane`**: Checks `GET /communication?event_id=EVT001&family_id=FAM001`; verifies dual-pane rendering containing internal staff records vs. family summaries, and explicit note segregation disclaimer.
- **`test_review_queue_and_action`**: Checks `GET /review_queue` as administrator; verifies queue rendering and pending review tables.
- **`test_experiment_page_renders_metrics`**: Checks `GET /experiment`; verifies empirical benchmark metrics rendering (Family Understanding Score, Unauthorised Disclosure Rate).
- **`test_admin_full_privileges`**: Verifies administrator (`Dharshini`) has unrestricted HTTP 200 access across all operational, supervisory, and experiment routes (`/dashboard`, `/residents`, `/care_events`, `/family_members`, `/consent`, `/review_queue`, `/experiment`).
- **`test_staff_operational_access_and_experiment_denial`**: Verifies care staff (`Madhu`) can access operational workflows (`/dashboard`, `/residents`, `/care_events`, `/review_queue`), but is strictly denied and redirected with Access Denied flash messages on administrative experiment routes (`/experiment`, `/experiment/run`, `/experiment/download_notebook`).
- **`test_family_persona_scoped_access`**: Verifies family member (`Kavi`) can access own resident profile (`/residents/RES001`), communication portal (`/communication`), and Q&A (`/questions`), while internal staff handover notes are structurally hidden from view.
- **`test_family_direct_url_and_action_denials`**: Verifies server-side `@role_required` enforcement blocking family direct URL tampering for facility endpoints (`/residents`, `/care_events`, `/consent`, `/review_queue`, `/experiment`, `/family_members`), as well as unauthorized POST actions (`/consent/toggle`, `/review/submit`, `/questions/answer`).
- **`test_family_cross_resident_isolation`**: Verifies cross-resident boundary enforcement; contact Hema (`RES002`) cannot access Devi Raman (`RES001`) profiles or inspect communications for other residents.
- **`test_family_persona_switching_blocked`**: Verifies that family accounts cannot utilize `/switch_user` shortcuts to escalate privileges or assume administrative identities.
- **`test_family_sub_roles_kavi_charu_hema_abi_mala`**: Verifies correct persona scoping and resident linkage across all 5 family personas (`Kavi`, `Charu`, `Hema`, `Abi`, `Mala`).

#### 2.5 `tests/test_summary.py` (4 Tests)
Verifies deterministic text transformation rules in [`services/summary_generator.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/services/summary_generator.py).

- **`test_meal_summary_generation`**:
  - Input: Meal event with `"lunch"` and `'Moderate'` assistance.
  - Expected Output: Contains `"lunch"`, `"moderate assistance"`, and completely omits staff notes.
- **`test_social_activity_summary`**:
  - Input: Social activity event with `"music session"` and `'Minimal'` assistance.
  - Expected Output: Contains `"music session"`, `"minimal assistance"`, and excludes staff shift notes.
- **`test_operational_exception_summary`**:
  - Input: Exception event (`exception_flag = 1`) for mobility decline.
  - Expected Output: Formats objectively with `"Operational update:"` and `"Staff follow-up is in progress."` without speculative medical language.
- **`test_internal_staff_notes_are_never_included`**:
  - Input: Personal care event with confidential staff handover note (`"CONFIDENTIAL STAFF HANDOVER NOTE 9988"`).
  - Expected Output: Verifies that confidential keywords and identifiers are strictly absent from generated family summary.

---

## 3. System Error Boundaries & Runtime Failure Handling

The application architecture enforces strict error boundaries across six defensive tiers. Failure to satisfy any boundary halts propagation and routes the event to a safe, deterministic termination state.

```
                  [Raw Care Event / User Request]
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │ Tier 1: Input & Entity Validation Layer      │ ──(Missing/Invalid ID)──> [HTTP 400 / Abort Error]
         └──────────────────────┬───────────────────────┘
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │ Tier 2: Authorization & Security Gate        │
         │         (Role Check & Consent Verification)  │ ──(Denied / Revoked)────> [DISCLOSURE BLOCKED]
         └──────────────────────┬───────────────────────┘                           (Summary = None; Logged)
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │ Tier 3: Deterministic Rule Synthesis Layer   │
         │         (Pattern Template & Note Filter)     │ ──(Staff Note Scrubbed)─> [Clean Summary Draft]
         └──────────────────────┬───────────────────────┘
                                │
                                ▼
         ┌──────────────────────────────────────────────┐
         │ Tier 4: Clinical Lexicon & Completeness Scan │
         │         (Regex Match & Field Null Check)     │ ──(Medical Term / Empty)─┐
         └──────────────────────┬───────────────────────┘                          │
                                │                                                  │
                                ▼                                                  │
         ┌──────────────────────────────────────────────┐                          │
         │ Tier 5: Human-in-the-Loop Review Gate        │ <────────────────────────┘
         │         (High Urgency / Exceptions / Flags)  │ ──(Review Triggered)─────> [PENDING REVIEW QUEUE]
         └──────────────────────┬───────────────────────┘                           (Staff Approve / Edit / Reject)
                                │ (All Checks Passed)
                                ▼
                    [AUTO-APPROVED DISCLOSURE]
                    (Delivered to Family Portal)
```

---

## 4. Comprehensive Failure Mode & Error Boundary Matrix

The following matrix documents every error condition handled in the application stack, specifying trigger criteria, system behaviors, expected outcomes, and final disposition.

| # | Error Boundary Category | Trigger / Input Condition | System Behavior & Defensive Action | Expected Response / Outcome | Communication Disposition |
|---|---|---|---|---|---|
| **1** | **Missing Request Parameters (API)** | `POST /api/generate_update` called with missing `event_id` or `family_id` | Input guard checks presence in JSON body | Returns JSON: `{"success": false, "error": "event_id and family_id are required."}` with HTTP status `400 Bad Request` | **Rejected** (API Error) |
| **2** | **Nonexistent Event Record** | `event_id` not found in `care_events` table | Database query returns `None`; pipeline execution aborted | Returns dict: `{"success": false, "error": "Care event '<event_id>' not found."}` | **Rejected** (Record Not Found) |
| **3** | **Nonexistent Family Record** | `family_id` not found in `family_members` table | Database query returns `None`; pipeline execution aborted | Returns dict: `{"success": false, "error": "Family member '<family_id>' not found."}` | **Rejected** (Record Not Found) |
| **4** | **Unlinked Family-Resident Mismatch** | `family.resident_id != event.resident_id` | Mismatch detected before consent or summary processing; stops pipeline immediately | Sets `block_reason = "Information cannot be displayed: Family member is not linked to this resident."`; summary set to `None` | **Blocked** (`disclosure_status = 'Blocked'`, `review_status = 'Rejected'`) |
| **5** | **Revoked Resident Consent** | Resident consent record exists with `consent_status = 'Revoked'` | `check_consent` returns `False`; stops pipeline before summary generation | Inserts blocked record into `communications` with standard non-leaking notice; summary set to `None` | **Blocked** (`disclosure_status = 'Blocked'`, `review_status = 'Rejected'`) |
| **6** | **Unconfigured / Missing Consent** | No record exists in `consent` table for resident-family pair | `consent` row is `None`; `check_consent` defaults to fail-safe denial | Inserts blocked record with notice: *"Information cannot be displayed because the current family member does not have permission..."* | **Blocked** (`disclosure_status = 'Blocked'`, `review_status = 'Rejected'`) |
| **7** | **Category-Level Consent Restriction** | Resident consent active, but category flag is `0` (e.g., `routine_updates = 0` for Personal Care) | `check_consent` inspects category flag against `event_type`; returns `False` | Summary suppressed; safe notice generated specifying category permission boundary | **Blocked** (`disclosure_status = 'Blocked'`, `review_status = 'Rejected'`) |
| **8** | **Insufficient Role Permissions (Routine)** | Emergency Contact attempting to view routine daily logs (e.g. `Meal` with `Normal` urgency) | `check_role_permission` identifies role restrictions; routine logs blocked to preserve emergency signal | Summary suppressed; sets `block_reason = "Emergency Contact role is restricted from routine daily care logs..."` | **Blocked** (`disclosure_status = 'Blocked'`, `review_status = 'Rejected'`) |
| **9** | **Insufficient Role Permissions (Sensitive)** | View-Only Contact attempting to view `Personal Care` or operational exceptions | `check_role_permission` intercepts sensitive categories for View-Only contacts | Summary suppressed; sets `block_reason = "View-Only Contact role does not permit access..."` | **Blocked** (`disclosure_status = 'Blocked'`, `review_status = 'Rejected'`) |
| **10** | **Invalid or Unrecognized Role** | `family_members.role` contains a string not in `VALID_ROLES` | Guard clause checks membership in `VALID_ROLES`; returns `False` | Sets `block_reason = "Invalid or unrecognized family role: '<role>'."`; summary set to `None` | **Blocked** (`disclosure_status = 'Blocked'`, `review_status = 'Rejected'`) |
| **11** | **Missing Required Event Information** | Care event missing required attributes (`observation == ""` or `assistance_level is None`) | `check_missing_information` evaluates completeness; flags missing field names | Sets `is_complete = False`; triggers human review with trigger *"Missing operational event information"* | **Sent for Human Review** (`disclosure_status = 'Pending Review'`) |
| **12** | **Prohibited Medical Terminology in Log** | Observation contains clinical words (e.g. `fever`, `antibiotic`, `blood pressure`, `stroke`) | Scanned against 27+ regexes in `PROHIBITED_MEDICAL_TERMS`; flags matches | Sets `is_safe = False`; summary held from family; triggers review with *"Potential medical language detected: <terms>"* | **Sent for Human Review** (`disclosure_status = 'Pending Review'`) |
| **13** | **High-Urgency Operational Event** | `care_event.urgency == 'High'` | Urgency evaluated by `requires_human_review` | Event summary drafted but withheld from automatic release; routes to supervisory queue | **Sent for Human Review** (`disclosure_status = 'Pending Review'`) |
| **14** | **Operational Care Exception Logged** | `care_event.exception_flag == 1` | Exception status evaluated by `requires_human_review` | Formats objective exception update draft; routes to review queue to verify operational follow-up | **Sent for Human Review** (`disclosure_status = 'Pending Review'`) |
| **15** | **Prohibited Medical Question (Q&A)** | Family asks clinical question (e.g., *"What dosage of tylenol should my mother take?"*) | `classify_question` matches against `MEDICAL_QUESTION_PATTERNS` | Question saved with `status = 'Flagged Medical'`; user receives immediate disclaimer; staff notified | **Intercepted & Escalated** (Redirection to Staff) |
| **16** | **Unauthenticated Route Access** | User session lacks `'user_id'` accessing protected endpoint | `@login_required` decorator intercepts request | Flashes warning *"Please sign in to access the application."* and redirects to `/login` | **Redirected** (HTTP 302 to Login) |
| **17** | **Invalid Login Credentials** | User submits invalid username or incorrect password on `/login` | Password hash check fails via `check_password_hash` | Flashes danger alert *"Invalid credentials. Use demo passwords..."*; re-renders login page | **Rejected** (HTTP 200 Re-render) |
| **18** | **Nonexistent Resident Profile** | Accessing `/residents/<resident_id>` where ID is not in database | Database returns `None` for resident query | Flashes alert *"Resident '<id>' not found."* and redirects to `/residents` | **Redirected** (HTTP 302 to Directory) |

---

## 5. Human-in-the-Loop Review Queue Specification

The human review gate acts as the primary supervisory error boundary for anomalous, incomplete, or high-urgency care communications.

### Review Triggers (`requires_human_review`)
An event is intercepted and placed in `Pending Review` if any of the following six conditions occur:
1. `not is_complete`: Missing required care event attributes.
2. `not is_safe` or `len(flagged_terms) > 0`: Detection of prohibited medical terminology.
3. `urgency == 'High'`: High-urgency operational circumstances.
4. `exception_flag == 1`: Care exceptions requiring staff coordination.
5. `not consent_granted`: Ambiguous or unverified consent configurations.
6. `not role_authorized`: Restricted family roles requiring manual liaison.

### Supervisory Actions & State Transitions
Staff reviewers access pending items on [`/review_queue`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/templates/review_queue.html) and execute one of four definitive actions:
- **Approve:** Releases the drafted summary to the family portal without modification (`disclosure_status = 'Approved'`, `review_status = 'Reviewed'`).
- **Edit:** Modifies the drafted summary (e.g. rephrasing clinical shorthand into operational terms) and releases the updated version (`disclosure_status = 'Approved'`, `review_status = 'Reviewed'`).
- **Reject:** Completely blocks the communication from family release, logging mandatory decision notes (`disclosure_status = 'Rejected'`, `review_status = 'Rejected'`).
- **Escalate:** Flags the communication for clinical leadership review (`review_status = 'Escalate'`).

### Audit Logging
Every supervisory decision is recorded in the immutable `review_logs` table:
```sql
INSERT INTO review_logs (log_id, comm_id, reviewer_name, action_taken, action_timestamp, notes)
VALUES (?, ?, ?, ?, ?, ?);
```

---

## 6. Test Suite Execution Protocol

The complete test suite can be executed locally from the project root using either `unittest` or `pytest`.

### Execution Command
```bash
py -3 -m unittest discover tests -v
```

### Expected Execution Output
```text
test_category_level_activity_permission_enabled (test_consent.TestConsentChecker) ... ok
test_category_level_routine_permission_disabled (test_consent.TestConsentChecker) ... ok
test_exception_consent_disabled (test_consent.TestConsentChecker) ... ok
test_missing_consent_record (test_consent.TestConsentChecker) ... ok
test_question_consent (test_consent.TestConsentChecker) ... ok
test_revoked_consent_blocks_disclosure (test_consent.TestConsentChecker) ... ok
test_valid_active_consent (test_consent.TestConsentChecker) ... ok
test_case_1_no_consent_blocks_disclosure (test_failure_cases.TestFailureCases) ... ok
test_case_2_insufficient_role_permissions (test_failure_cases.TestFailureCases) ... ok
test_case_3_medical_language_interception (test_failure_cases.TestFailureCases) ... ok
test_case_4_missing_information_detection (test_failure_cases.TestFailureCases) ... ok
test_case_5_family_medical_question_boundary (test_failure_cases.TestFailureCases) ... ok
test_emergency_contact_restrictions (test_roles.TestRoleChecker) ... ok
test_invalid_role (test_roles.TestRoleChecker) ... ok
test_primary_family_contact_access (test_roles.TestRoleChecker) ... ok
test_secondary_family_contact_access (test_roles.TestRoleChecker) ... ok
test_view_only_contact_restrictions (test_roles.TestRoleChecker) ... ok
test_communication_dual_pane (test_routes.TestAppRoutes) ... ok
test_dashboard_authenticated (test_routes.TestAppRoutes) ... ok
test_experiment_page_renders_metrics (test_routes.TestAppRoutes) ... ok
test_login_page_renders (test_routes.TestAppRoutes) ... ok
test_quick_user_switch (test_routes.TestAppRoutes) ... ok
test_residents_and_detail (test_routes.TestAppRoutes) ... ok
test_review_queue_and_action (test_routes.TestAppRoutes) ... ok
test_internal_staff_notes_are_never_included (test_summary.TestSummaryGenerator) ... ok
test_meal_summary_generation (test_summary.TestSummaryGenerator) ... ok
test_operational_exception_summary (test_summary.TestSummaryGenerator) ... ok
test_social_activity_summary (test_summary.TestSummaryGenerator) ... ok

----------------------------------------------------------------------
Ran 28 tests in 0.184s

OK
```
