# Failure Mode and Effects Analysis (FMEA)

This document provides a systematic analysis of potential failure modes, their operational impact, the implemented software safeguards, and verification procedures for the assisted-living communication system.

---

## Failure Mode Matrix

| ID | Failure Mode | Trigger Condition | Potential Hazard | Implemented Safeguard | System Outcome |
|---|---|---|---|---|---|
| **CASE 1** | **Unauthorized Disclosure via Missing/Revoked Consent** | Family member requests update when `consent_status == 'Revoked'` or record is absent. | Severe breach of resident privacy autonomy; legal liability. | `consent_checker.py` evaluates active status prior to summary synthesis. | Disclosure is **strictly blocked**. Summary is suppressed. Standard notice returned: *"Information cannot be displayed because the current family member does not have permission..."* |
| **CASE 2** | **Insufficient Family Role Permissions** | View-Only contact attempts to view personal care; or Emergency contact queries routine meals. | Privacy exposure of intimate hygiene care or alert fatigue from routine noise. | `role_checker.py` validates role against permitted categories. | Disclosure is **blocked**. Clear explanation returned: *"View-Only Contact role does not permit access to sensitive personal care details."* |
| **CASE 3** | **Medical Language Contamination** | Staff inadvertently inputs clinical jargon (e.g., *"Resident had fever of 101F, suspected chest infection; give paracetamol"*). | Resident family panics; system misconstrued as medical diagnostic tool. | `safety_checker.py` scans regex patterns for diagnoses, vitals, drugs, and prognoses. | Gated into **Human Review Queue**. Flagged terms highlighted. Reviewer must edit text to strictly operational phrasing before release. |
| **CASE 4** | **Incomplete Care Event Information** | Event logged with empty observation or missing assistance level. | System hallucinates facts or outputs nonsensical fragments to family. | `check_missing_information()` checks mandatory attributes; rejects hallucination. | Disclosure held in **Pending Review**. System logs *"Care event record has missing required fields. Cannot invent missing facts."* |
| **CASE 5** | **Clinical Inquiry from Family** | Family asks: *"What medication dosage should my mother take for her fever?"* | Unlicensed medical advice; potential physical harm to resident. | `classify_question()` scans for medical intent and clinical vocabulary. | Intercepted in real-time. Displays prominent disclaimer and routes inquiry directly to clinical nursing staff. |

---

## Deep Dive: Case Implementations & Verification

### Case 1: No Consent / Revoked Consent
- **Demo Subject:** Resident `Kamala Sundaram` (RES003) and Niece `Abi` (FAM004).
- **Setup:** In `consent.csv`, `CON004` is explicitly set to `consent_status='Revoked'`.
- **Behavior:** When Abi attempts to view Kamala's morning routine or social updates, `communication_service.py` identifies that consent is revoked.
- **Verification:** Tested in `tests/test_failure_cases.py::test_case_1_no_consent_blocks_disclosure`.

### Case 2: Insufficient Role Permissions
- **Demo Subject:** `Abi` holds the `View-Only Contact` role.
- **Setup:** Event `EVT004` represents a sensitive Personal Care evening routine.
- **Behavior:** `role_checker.py` detects that View-Only contacts are permitted to view general social activities only. Access to personal care is denied.
- **Verification:** Tested in `tests/test_roles.py::test_view_only_contact_restrictions`.

### Case 3: Medical Language Interception
- **Demo Subject:** Resident `Ramesh Sharma` (RES002) and Contact `Hema` (FAM003).
- **Setup:** Event `EVT005` contains: *"Resident exhibited fever of 101F and suspected chest infection; staff administered paracetamol 500mg."*
- **Behavior:** Regex patterns identify `fever`, `infection`, and `paracetamol`. The communication is prevented from direct release and routed to `review_queue.html` with red warning badges.
- **Verification:** Tested in `tests/test_failure_cases.py::test_case_3_medical_language_interception`.

### Case 4: Missing Information Handling
- **Demo Subject:** Event `EVT006` recorded with empty `observation` and `assistance_level`.
- **Behavior:** The system detects incomplete fields. Instead of fabricating plausible text, it diverts the record to the review queue and warns staff of incomplete records.
- **Verification:** Tested in `tests/test_failure_cases.py::test_case_4_missing_information_detection`.

### Case 5: Medical Question Boundary Interception
- **Demo Subject:** Family member submits inquiry `QUE002`: *"What dosage of fever medicine or antibiotic should Ramesh take for his chest infection?"*
- **Behavior:** The UI detects clinical terms live as the user types. Upon submission, the backend automatically flags the question as `Flagged Medical` and returns:
  > *"Operational Support Only — This system communicates care activities and operational observations. It does not provide medical diagnosis, treatment recommendations, or medical advice. Your inquiry has been routed to facility nursing staff for clinical consultation."*
- **Verification:** Tested in `tests/test_failure_cases.py::test_case_5_family_medical_question_boundary`.
