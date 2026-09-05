"""Safety Checker Service
Enforces strict boundaries between operational observations and medical conclusions.
Intercepts clinical terminology, flags missing information, and validates question scopes.
"""

import re

# Comprehensive list of clinical / medical vocabulary to detect
PROHIBITED_MEDICAL_TERMS = [
    # Diagnoses & Conditions
    r'\bdementia\b', r'\balzheimer\'?s?\b', r'\binfection\b', r'\buti\b', r'\bpneumonia\b',
    r'\bcovid\b', r'\bstroke\b', r'\bdiabetes\b', r'\bhypertension\b', r'\bdepression\b',
    r'\bdelirium\b', r'\bbronchitis\b', r'\bfracture\b', r'\bsepsis\b', r'\bconcussion\b',
    # Clinical Symptoms & Vitals
    r'\bfever\b', r'\bchest pain\b', r'\bdyspnea\b', r'\bhypoglycemia\b', r'\bseizure\b',
    r'\bhemorrhage\b', r'\bvomiting blood\b', r'\btachycardia\b', r'\barrhythmia\b',
    r'\bblood pressure\b', r'\boxygen saturation\b', r'\bspo2\b', r'\bvital signs?\b',
    # Medications & Dosages
    r'\bmedication\b', r'\bmedicine\b', r'\btylenol\b', r'\bparacetamol\b', r'\bantibiotics?\b',
    r'\binsulin\b', r'\bdosage\b', r'\b\d+\s*mg\b', r'\bprescription\b', r'\bdose\b',
    r'\binfusion\b', r'\binhaler\b', r'\bprescribe\b', r'\baspirin\b', r'\bibuprofen\b',
    r'\bnarcotic\b', r'\bsedative\b', r'\bpill\b', r'\bpills\b',
    # Clinical Conclusions & Prognoses
    r'\bdeteriorat(e|ing|ion)\b', r'\bworsening condition\b', r'\bmedical emergency\b',
    r'\bclinical intervention\b', r'\bprognosis\b', r'\bpathology\b', r'\bdiagnos(is|ed|e)\b',
    r'\bmedical condition\b'
]

# Medical question intent patterns
MEDICAL_QUESTION_PATTERNS = [
    r'\b(diagnos|treatment|cure|medicat|medicine|dosage|pill|drug|symptom)\b',
    r'\b(fever|painkiller|blood pressure|infection|inhaler|insulin)\b',
    r'\b(is (he|she|my mother|my father) sick|is it serious)\b',
    r'\b(should (he|she) take|can you give (him|her))\b'
]

def check_text_safety(text: str) -> tuple:
    """
    Scans text for prohibited medical terminology or clinical conclusions.
    
    Returns:
        (is_safe: bool, flagged_terms: list, reason: str)
    """
    if not text:
        return True, [], "No content to evaluate."

    flagged_terms = []
    text_lower = text.lower()

    for pattern in PROHIBITED_MEDICAL_TERMS:
        matches = re.findall(pattern, text_lower)
        if matches:
            # Clean match if tuple or string
            matched_str = matches[0] if isinstance(matches[0], str) else matches[0][0]
            if matched_str not in flagged_terms:
                flagged_terms.append(matched_str)

    if flagged_terms:
        return (
            False,
            flagged_terms,
            f"Safety boundary violation: Text contains clinical or medical terminology: {', '.join(flagged_terms)}."
        )

    return True, [], "Adheres strictly to operational non-medical boundary."

def check_missing_information(care_event: dict) -> tuple:
    """
    Validates that essential operational fields are populated without relying on hallucination.
    
    Returns:
        (is_complete: bool, missing_fields: list, reason: str)
    """
    required_fields = ['resident_id', 'event_type', 'observation', 'assistance_level', 'urgency']
    missing_fields = []

    for field in required_fields:
        val = care_event.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            missing_fields.append(field)

    if missing_fields:
        return (
            False,
            missing_fields,
            f"Care event record has missing required fields: {', '.join(missing_fields)}. Cannot invent missing facts."
        )

    return True, [], "All mandatory operational event attributes are present."

def classify_question(question_text: str) -> tuple:
    """
    Determines whether a family question is strictly operational or encroaches on medical advice.
    
    Returns:
        (is_operational: bool, response_or_reason: str)
    """
    if not question_text or not question_text.strip():
        return False, "Question is empty."

    text_lower = question_text.lower()
    for pattern in MEDICAL_QUESTION_PATTERNS:
        if re.search(pattern, text_lower):
            return (
                False,
                "Operational Support Only — This system communicates care activities and operational observations. "
                "It does not provide medical diagnosis, treatment recommendations, or medical advice. "
                "Your inquiry has been flagged and redirected to facility staff for direct consultation."
            )

    return True, "Question falls within general operational communication scope."

def requires_human_review(
    care_event: dict,
    role_authorized: bool,
    consent_granted: bool,
    is_safe: bool,
    flagged_terms: list,
    is_complete: bool
) -> tuple:
    """
    Evaluates whether an operational communication requires mandatory human review.
    
    Returns:
        (review_required: bool, triggers: list[str])
    """
    triggers = []

    if not is_complete:
        triggers.append("Missing operational event information")

    if not is_safe or flagged_terms:
        triggers.append(f"Potential medical language detected: {', '.join(flagged_terms)}")

    if care_event.get('urgency') == 'High':
        triggers.append("High-urgency operational event")

    if care_event.get('exception_flag') == 1:
        triggers.append("Operational exception logged")

    if not consent_granted:
        triggers.append("Consent verification blocked/pending")

    if not role_authorized:
        triggers.append("Role permission restricted/unauthorized")

    return (len(triggers) > 0, triggers)
