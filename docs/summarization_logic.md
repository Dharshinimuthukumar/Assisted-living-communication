# Deterministic Rule-Based Summarization Logic

**Project Title:** From Operational Pain to Working Product: Assisted-Living Facility Supporting Residents' Independence Levels  
**Academic Context:** Semester 5 C28 Review 2 Technical Specification  
**Module Implementation:** [`services/summary_generator.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/services/summary_generator.py), [`services/safety_checker.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/services/safety_checker.py)  
**System Classification:** Non-Medical Operational Communication Gateway (Synthetic Data Only)

---

## 1. Architectural Overview & Design Philosophy

The summarization engine in this prototype is **strictly deterministic and rule-based**. 

> [!IMPORTANT]
> **No Machine Learning or Large Language Models (LLMs):**  
> The application does **NOT** use neural networks, probabilistic text generation, natural language processing (NLP) models, large language models (LLMs), or black-box predictive algorithms. All family summaries are synthesized through explicit Python string formatting templates, deterministic conditional branches, and strict dictionary lookups.

### Why Rule-Based Summarization?
1. Reduced generation risk: Because outputs are produced from predefined templates and rules rather than generative models, the system reduces the risk of fabricated information.
2. **Predictable Safety Auditing:** Every output string maps 1:1 to explicit code branches and verifiable event inputs.
3. **Strict Non-Medical Boundary:** Prevents the conversion of benign operational observations (e.g., *"Walked with walker"*) into clinical assertions (e.g., *"Mobility deterioration detected"*).
4. **Data Leakage Prevention:** Eliminates the accidental leakage of confidential internal staff shift notes (`staff_note`), because internal fields are structurally excluded from summary templates.

---

## 2. Event Attribute Extraction & Input Boundary

The primary entry point is `generate_operational_summary(care_event: dict, family_relation: str = "family member") -> str` in [`services/summary_generator.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/services/summary_generator.py).

### Attributes Extracted from `care_event`:
| Attribute Name | Source Field | Type | Handling in Summarization Engine |
|---|---|---|---|
| `event_type` | `care_event['event_type']` | `str` | Determines template category branch (e.g., `'Meal'`, `'Social Activity'`, `'Mobility'`). Defaults to `'Activity'`. |
| `observation` | `care_event['observation']` | `str` | Stripped of whitespace and trailing punctuation (`.rstrip('.')`) for clean sentence integration. |
| `assistance_level` | `care_event['assistance_level']` | `str` | Lowercased and mapped to human-readable phrasing (`'independently'`, `'with {level} assistance'`). Defaults to `'Minimal'`. |
| `urgency` | `care_event['urgency']` | `str` | Evaluated by [`safety_checker.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/services/safety_checker.py) for workflow routing. Not embedded into routine output text to prevent alarming family. |
| `exception_flag` | `care_event['exception_flag']` | `int` | When `== 1`, immediately routes to the standardized exception reassurance template. |
| `family_relation` | Argument | `str` | Lowercased relationship descriptor (e.g., `'mother'`, `'father'`, `'sister'`). Defaults to `'family member'`. |

### Explicitly Excluded Attributes:
- **`staff_note` (Internal Shift Log):**  
  The internal caregiver note (`staff_note`) is **NEVER passed or interpolated** into the family-facing string. It is preserved strictly for internal staff viewing on the administrative UI and is omitted unconditionally from all family payloads.

---

## 3. Assistance Level Mapping

Resident independence is the core operational dimension communicated to families. The engine converts raw categorical levels into polite, non-clinical English phrasing:

```python
if assistance_level == 'independent':
    assist_text = "independently"
elif assistance_level in ['minimal', 'moderate', 'high']:
    assist_text = f"with {assistance_level} assistance"
else:
    assist_text = "with staff assistance"
```

### Mapping Examples:
- `'Independent'` $\to$ `"independently"`
- `'Minimal'` $\to$ `"with minimal assistance"`
- `'Moderate'` $\to$ `"with moderate assistance"`
- `'High'` $\to$ `"with high assistance"`
- Missing / Non-standard $\to$ `"with staff assistance"`

---

## 4. Category-Specific Template Rules

When an event is processed, the engine executes deterministic branching based on `is_exception` and `event_type`:

### 4.1 Operational Exceptions (`exception_flag == 1`)
If an operational exception is logged (e.g., resident refused an activity or experienced a minor non-injury slip):
- **Code Logic:**
  ```python
  clean_obs = observation.rstrip('.')
  return f"Operational update: {clean_obs}. Staff follow-up is in progress."
  ```
- **Design Intent:** Immediately provides transparent, calm operational notification while confirming staff attentiveness, avoiding speculative medical language.

### 4.2 Meal Events (`event_type == 'Meal'`)
- **Code Logic:**
  ```python
  if "lunch" in observation.lower():
      meal_name = "lunch"
  elif "breakfast" in observation.lower():
      meal_name = "breakfast"
  elif "dinner" in observation.lower() or "supper" in observation.lower():
      meal_name = "dinner"
  else:
      meal_name = "their meal"
  return f"Your {family_relation} attended {meal_name} today {assist_text}."
  ```

### 4.3 Social Activities (`event_type in ['Social Activity', 'Activity']`)
- **Code Logic:**
  ```python
  obs_lower = observation.lower()
  if "gardening" in obs_lower:
      act = "the gardening activity"
  elif "music" in obs_lower:
      act = "the music session"
  elif "craft" in obs_lower:
      act = "the arts and crafts session"
  elif "bingo" in obs_lower:
      act = "the social bingo gathering"
  elif "reading" in obs_lower or "book" in obs_lower:
      act = "the afternoon reading group"
  else:
      act = "the scheduled facility activity"
  return f"Your {family_relation} participated in {act} {assist_text}."
  ```

### 4.4 Morning Routine (`event_type == 'Morning Routine'`)
- **Code Logic:**
  ```python
  return f"Staff supported your {family_relation} through their morning routine {assist_text}."
  ```

### 4.5 Personal Care (`event_type == 'Personal Care'`)
- **Code Logic:**
  ```python
  return f"Staff provided operational assistance with daily personal care {assist_text}."
  ```

### 4.6 Mobility (`event_type == 'Mobility'`)
- **Code Logic:**
  ```python
  return f"Your {family_relation} completed their daily walking and mobility routine {assist_text}."
  ```

### 4.7 Scheduled Appointment (`event_type == 'Scheduled Appointment'`)
- **Code Logic:**
  ```python
  return f"Your {family_relation} completed their scheduled facility operational appointment on time."
  ```

### 4.8 Other Operational Events (Fallback Branch)
- **Code Logic:**
  ```python
  if observation:
      clean_obs = observation.rstrip('.')
      return f"Operational note: {clean_obs} ({assist_text})."
  return f"An operational care event was recorded {assist_text}."
  ```

---

## 5. Concrete Rule Lookup Table

The following table documents the exact rules implemented in [`services/summary_generator.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/services/summary_generator.py):

| # | Raw Event Condition | Rule Applied | Sample Input Observation | Family-Facing Generated Summary |
|---|---|---|---|---|
| 1 | `care_event is None` or empty | Input guard clause | `None` | `"No care event details provided."` |
| 2 | `exception_flag == 1` | Exception Reassurance Pattern | *"Resident declined afternoon tea service"* | `"Operational update: Resident declined afternoon tea service. Staff follow-up is in progress."` |
| 3 | `event_type == 'Meal'`, observation contains `"lunch"` | Meal parsing (lunch) | *"Resident ate 80% lunch in dining room"* | `"Your mother attended lunch today with minimal assistance."` |
| 4 | `event_type == 'Meal'`, observation contains `"breakfast"` | Meal parsing (breakfast) | *"Ate breakfast independently"* | `"Your father attended breakfast today independently."` |
| 5 | `event_type == 'Meal'`, observation contains `"dinner"` or `"supper"` | Meal parsing (dinner) | *"Joined community dinner in hall"* | `"Your mother attended dinner today with moderate assistance."` |
| 6 | `event_type == 'Meal'`, generic observation | Meal parsing (fallback) | *"Dining room attendance observed"* | `"Your mother attended their meal today with minimal assistance."` |
| 7 | `event_type in ['Social Activity', 'Activity']`, contains `"gardening"` | Activity keyword match (gardening) | *"Assisted with potting plants in garden"* | `"Your mother participated in the gardening activity with minimal assistance."` |
| 8 | `event_type in ['Social Activity', 'Activity']`, contains `"music"` | Activity keyword match (music) | *"Attended live acoustic music concert"* | `"Your father participated in the music session independently."` |
| 9 | `event_type in ['Social Activity', 'Activity']`, contains `"craft"` | Activity keyword match (crafts) | *"Made paper crafts in activity lounge"* | `"Your sister participated in the arts and crafts session with minimal assistance."` |
| 10 | `event_type in ['Social Activity', 'Activity']`, contains `"bingo"` | Activity keyword match (bingo) | *"Played 4 rounds of bingo"* | `"Your mother participated in the social bingo gathering independently."` |
| 11 | `event_type in ['Social Activity', 'Activity']`, contains `"reading"` or `"book"` | Activity keyword match (reading) | *"Reading library book in parlor"* | `"Your father participated in the afternoon reading group independently."` |
| 12 | `event_type in ['Social Activity', 'Activity']`, generic observation | Activity keyword match (general) | *"Facility community time"* | `"Your mother participated in the scheduled facility activity with staff assistance."` |
| 13 | `event_type == 'Morning Routine'` | Routine template | *"Got dressed and brushed teeth"* | `"Staff supported your mother through their morning routine with minimal assistance."` |
| 14 | `event_type == 'Personal Care'` | Personal care template | *"Assisted with afternoon grooming"* | `"Staff provided operational assistance with daily personal care with moderate assistance."` |
| 15 | `event_type == 'Mobility'` | Walking routine template | *"Walked 300 meters in courtyard garden"* | `"Your father completed their daily walking and mobility routine independently."` |
| 16 | `event_type == 'Scheduled Appointment'` | Appointment template | *"Hairdressing salon visit"* | `"Your mother completed their scheduled facility operational appointment on time."` |
| 17 | Unknown / Other category with observation | Fallback with observation | *"Resident rearranged bedroom bookcase"* | `"Operational note: Resident rearranged bedroom bookcase (independently)."` |
| 18 | Unknown / Other category without observation | Fallback generic | `""` (empty) | `"An operational care event was recorded with staff assistance."` |

---

## 6. Safety Verification, Missing Data & Human Review Triggers

Once a summary string is generated, it does **not** proceed directly to family release. It must pass through the validation mechanisms defined in [`services/safety_checker.py`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/services/safety_checker.py):

### 6.1 Missing Information Inspection (`check_missing_information`)
The engine checks five required fields:
- `resident_id`, `event_type`, `observation`, `assistance_level`, `urgency`
- If any required field is missing or empty, `is_complete` is set to `False`. The system avoids fabricating missing context. Instead, it logs the missing fields and triggers mandatory human review.

### 6.2 Prohibited Medical Lexicon Scan (`check_text_safety`)
Both the raw observation and generated summary are scanned against `PROHIBITED_MEDICAL_TERMS` containing regex patterns across four clinical domains:
1. **Diagnoses & Conditions:** `\bdementia\b`, `\balzheimer\'?s?\b`, `\binfection\b`, `\buti\b`, `\bpneumonia\b`, `\bcovid\b`, `\bstroke\b`, `\bdiabetes\b`, `\bhypertension\b`, `\bdepression\b`, `\bdelirium\b`, `\bfracture\b`, `\bsepsis\b`, etc.
2. **Clinical Symptoms & Vitals:** `\bfever\b`, `\bchest pain\b`, `\bdyspnea\b`, `\bhypoglycemia\b`, `\bseizure\b`, `\bhemorrhage\b`, `\bblood pressure\b`, `\boxygen saturation\b`, `\bspo2\b`, `\bvital signs?\b`, etc.
3. **Medications & Dosages:** `\bmedication\b`, `\bmedicine\b`, `\btylenol\b`, `\bparacetamol\b`, `\bantibiotics?\b`, `\binsulin\b`, `\bdosage\b`, `\b\d+\s*mg\b`, `\bprescription\b`, `\baspirin\b`, `\bibuprofen\b`, `\bpill(s)?\b`, etc.
4. **Clinical Conclusions & Prognoses:** `\bdeteriorat(e|ing|ion)\b`, `\bworsening condition\b`, `\bmedical emergency\b`, `\bclinical intervention\b`, `\bprognosis\b`, `\bdiagnos(is|ed|e)\b`, etc.

If any prohibited term is detected:
- `is_safe = False`
- All matched terms are collected in `flagged_terms`
- The communication is flagged with: *"Safety boundary violation: Text contains clinical or medical terminology: {terms}"*.

### 6.3 Human Review Triggers (`requires_human_review`)
An event is held in the `Pending Review` queue if **any** of the following six triggers occur:
1. **Missing Data:** Incomplete required fields (`not is_complete`).
2. **Clinical Language:** Prohibited medical terminology detected (`not is_safe` or `len(flagged_terms) > 0`).
3. **High Urgency:** Urgent operational circumstances (`urgency == 'High'`).
4. **Operational Exception:** Flagged care exception (`exception_flag == 1`).
5. **Consent Flag:** Consent missing or under dispute (`not consent_granted`).
6. **Role Restriction:** Family role authorization restricted (`not role_authorized`).

---

## 7. Behavior When Summary Cannot Be Safely Released

When safety or authorization constraints are violated, the system executes fail-safe protections:

```
                  ┌───────────────────────────────┐
                  │ Authorization / Safety Gate   │
                  └──────────────┬────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       [Authorization Failure]          [Safety Boundary Hit]
       (Role / Consent Denied)          (Clinical Term / High Urgency)
                 │                               │
                 ▼                               ▼
       • Summary Suppressed             • Summary Draft Preserved
       • disclosure_status = 'Blocked'  • disclosure_status = 'Pending Review'
       • review_status = 'Rejected'     • review_status = 'Pending Review'
       • Standard Non-Leaking Notice    • Routed to Staff Review Queue
       • Zero Care Details Exposed      • Staff May Approve, Edit, Reject
```

1. **Authorization Breach (Unlinked family member, Revoked consent, Restricted role):**
   - The summary generator is completely aborted or suppressed (`generated_summary = None`).
   - The record is persisted with `disclosure_status = 'Blocked'` and `review_status = 'Rejected'`.
   - The family portal displays a standard neutral disclaimer:
     > *"Information cannot be displayed because the current family member does not have permission to receive this update."*
   - Internal observations and staff notes are strictly protected from transmission.

2. **Safety Boundary Interception (Clinical term in observation or High urgency):**
   - The generated summary is drafted but withheld from the family portal (`disclosure_status = 'Pending Review'`).
   - The item appears in the Staff Review Queue ([`/review-queue`](file:///C:/Users/arunk/.gemini/antigravity/scratch/assisted-living-communication/templates/review_queue.html)).
   - A qualified facility staff member must manually inspect the reason, review the draft, and choose to **Approve**, **Edit** (to rephrase into purely operational terms), **Reject**, or **Escalate** to facility clinical leadership.
