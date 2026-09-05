# Experimental Methodology & Empirical Benchmark

## 1. Academic Rationale & Research Context
The central hypothesis of this Semester 5 C28 academic project is:
> *"A structured, rule-based operational communication pipeline with pre-disclosure authorization gates and medical boundary classifiers will yield significantly higher family understanding and zero unauthorized disclosures compared to the conventional status-quo baseline of raw care log sharing."*

To test this hypothesis without compromising patient privacy or relying on simulated LLM APIs, an empirical evaluation is conducted using a standardized synthetic dataset of 100 assisted-living care events paired across diverse family contact configurations.

---

## 2. Experimental Cohort & Setup
- **Sample Size:** 100 synthetic care events generated across 5 residents spanning 4 distinct independence levels.
- **Evaluation Conditions:**
  - **Condition A (Baseline / Status Quo):** Represents facilities that export raw daily notes or shift handovers directly to family portals. Observations and staff shift logs are disclosed without role filtering, consent checking, or medical screening.
  - **Condition B (Prototype / Guarded System):** Evaluates events through the end-to-end pipeline: role-based access checking -> resident consent validation -> rule-based operational summarization -> non-medical safety classification -> human review gating.

---

## 3. Metric Formulations & Measurement Protocols

### 1. Family Understanding Score (%)
- **Definition:** Simulated cognitive comprehension score measuring whether a family member accurately understands observable operational events without confusion or cognitive overload.
- **Formulation:** Evaluated based on message conciseness, absence of administrative shift jargon, and focus on observable daily facts. Penalties are assessed for clinical terms ($25\%$) and excessive length/clutter ($0.4\%$ per extraneous word).
$$\text{Understanding Score} = \frac{1}{N} \sum_{i=1}^N \max(35, \min(100, 100 - \text{JargonPenalty}_i - \text{ClutterPenalty}_i))$$

### 2. Unnecessary Disclosure Rate (%)
- **Definition:** Percentage of communications that unnecessarily expose internal operational handover notes, staff shift notes, or administrative reminders.
$$\text{Unnecessary Disclosure Rate} = \frac{\text{Communications exposing internal staff notes}}{\text{Total delivered communications}} \times 100$$

### 3. Unauthorised Disclosure Rate (%)
- **Definition:** Percentage of communications disclosed despite missing/revoked resident consent or insufficient family role permissions.
$$\text{Unauthorised Disclosure Rate} = \frac{\text{Disclosures delivered without valid consent or role}}{\text{Total requested updates}} \times 100$$

### 4. Information Omission Rate (%)
- **Definition:** Percentage of critical operational events or safety follow-ups that were erroneously dropped or suppressed for an authorized contact.
$$\text{Information Omission Rate} = \frac{\text{Critical events improperly suppressed}}{\text{Total critical events with active consent}} \times 100$$

### 5. Medical-Boundary Violation Rate (%)
- **Definition:** Percentage of communications containing prohibited clinical terminology (e.g. diagnoses, vital sign readings, prescription medications, or medical predictions).
$$\text{Medical Violation Rate} = \frac{\text{Communications containing clinical terms}}{\text{Total delivered communications}} \times 100$$

### 6. Human Review Trigger Rate (%)
- **Definition:** Percentage of communications safely intercepted and routed to supervisory staff for human-in-the-loop review.
$$\text{Human Review Rate} = \frac{\text{Communications routed to Review Queue}}{\text{Total processed events}} \times 100$$

---

## 4. Empirical Benchmark Results

The following results were computed dynamically by `experiments/run_experiment.py` over 100 synthetic care event pairings:

| Metric | Baseline (Raw Care Logs) | Prototype (Guarded Pipeline) | Empirical Delta | Significance |
|---|---|---|---|---|
| **Family Understanding Score** | **59.2%** | **91.8%** | **+32.6%** | Dramatic increase in cognitive clarity and reassurance. |
| **Unnecessary Disclosure Rate** | **100.0%** | **0.0%** | **-100.0%** | Complete elimination of internal shift notes from family summaries. |
| **Unauthorised Disclosure Rate** | **33.3%** | **0.0%** | **-33.3%** | Complete prevention of privacy leaks to revoked/restricted contacts. |
| **Information Omission Rate** | **0.0%** | **0.0%** | **0.0%** | Zero loss of vital operational event facts. |
| **Medical-Boundary Violation Rate** | **6.7%** | **0.0%** | **-6.7%** | Interception of 100% of clinical terminology. |
| **Human Review Trigger Rate** | **0.0%** | **18.7%** | **+18.7%** | Sustainable staff workload while protecting institutional safety. |

---

## 5. Architectural Trade-Off: Why Rule-Based over Raw LLM APIs?
For an assisted-living operational communication gateway, a **deterministic, rule-based pipeline** was selected over commercial generative LLM APIs for four reasons:

1. **Zero Hallucination Guarantee:** Rule-based summarization strictly binds output phrases to observed data fields without inventing unobserved symptoms.
2. **Absolute Privacy Compliance:** No resident care observations are transmitted across third-party cloud LLM endpoints.
3. **Reproducibility & Predictability:** The software behaves deterministically during academic and clinical audit reviews.
4. **Offline Capability & Cost:** Operates locally on facility hardware without latency, token costs, or network failure modes.
