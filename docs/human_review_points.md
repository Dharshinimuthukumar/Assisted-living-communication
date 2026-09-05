# Human Review Points & Supervisory Protocol

## 1. Rationale for Human-in-the-Loop (HITL)
In sociotechnical care environments such as assisted living, total automation of family communication introduces severe vulnerabilities:
1. Subtle nuances in resident mood or physical comfort can be misinterpreted by algorithms.
2. Inadvertent staff notes containing raw internal jargon may cause panic if released unchecked.
3. High-urgency events and operational exceptions require human empathy and verified context.

Therefore, our system integrates a **Mandatory Supervisory Review Gate** for high-risk or ambiguous care events while allowing safe, routine updates to flow efficiently.

```
+-------------------------------------------------------------------------+
|                    HUMAN REVIEW ACTIVATION MATRIX                       |
|                                                                         |
| Event Characteristics       | Action Required   | Reviewer Gating       |
|-----------------------------|-------------------|-----------------------|
| Routine Meal / Activity     | Direct Release    | Automated (No Queue)  |
| Low Urgency / Safe Content  | Direct Release    | Automated (No Queue)  |
| High Urgency Event          | Mandatory Review  | Gated in Review Queue |
| Operational Exception       | Mandatory Review  | Gated in Review Queue |
| Clinical Language Detected  | Mandatory Review  | Gated in Review Queue |
| Incomplete Event Record     | Mandatory Review  | Gated in Review Queue |
| Ambiguous / Revoked Role    | Direct Block      | Blocked & Logged      |
+-------------------------------------------------------------------------+
```

## 2. Review Triggers & Criteria
A care event is intercepted and placed in `review_queue.html` when any of the following conditions evaluate to true:

1. **High Urgency Classification:** Any event marked `urgency == 'High'`.
2. **Operational Exception Flag:** Any event where `exception_flag == 1` (e.g. resident refused meal, missed scheduled mobility session, or experienced minor stumble without injury).
3. **Clinical Terminology Interception:** The safety checker identified prohibited terms (e.g., diagnoses, symptoms, medication dosages).
4. **Missing or Corrupt Data:** The observation or assistance level fields are empty or invalid.
5. **Medical Question Escalation:** Family questions that cross into medical advice are flagged for nurse consultation.

## 3. Reviewer Action Definitions

When a supervisor (Admin `Dharshini` or Care Staff `Madhu`) inspects an item in the Review Queue, four standardized actions are available:

### 1. Approve
- **Meaning:** The reviewer verifies that the draft summary is factual, objective, and strictly non-medical.
- **System Effect:** Updates `disclosure_status = 'Approved'` and `review_status = 'Reviewed'`. The update is immediately delivered to the family portal.

### 2. Edit & Approve
- **Meaning:** The draft summary requires rephrasing (e.g., removing technical jargon or softening an observation to prevent panic).
- **System Effect:** Overwrites `generated_summary` with the reviewer's edited text, sets `disclosure_status = 'Approved'`, and records the edit in the audit log.

### 3. Reject
- **Meaning:** The communication should not be sent to the family (e.g., duplicate entry, inappropriate note, or invalid event).
- **System Effect:** Sets `disclosure_status = 'Rejected'` and `review_status = 'Rejected'`. The record remains internal.

### 4. Escalate
- **Meaning:** The event involves institutional complexity requiring facility director or nursing director intervention.
- **System Effect:** Sets `review_status = 'Escalate'` and triggers administrative alerts.

## 4. Immutable Audit Trail (`review_logs`)
Every review decision records:
- `log_id`: Unique identifier (e.g. `LOG001`).
- `comm_id`: Associated communication reference.
- `reviewer_name`: Full name and title of staff member (e.g., `Madhu (Care Staff)`).
- `action_taken`: Approve, Edit, Reject, or Escalate.
- `action_timestamp`: ISO 8601 timestamp.
- `notes`: Justification and operational explanation.
