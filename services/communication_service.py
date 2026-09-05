"""Communication Service
Coordinates the end-to-end operational communication pipeline:
Care Event -> Role Verification -> Consent Verification -> Summary Generation -> Safety Inspection -> Human Review Routing -> Output.
"""

import uuid
from datetime import datetime
from services.role_checker import check_role_permission
from services.consent_checker import check_consent
from services.safety_checker import (
    check_text_safety,
    check_missing_information,
    requires_human_review
)
from services.summary_generator import generate_operational_summary

def process_care_event_for_family(conn, event_id: str, family_id: str, save_to_db: bool = True) -> dict:
    """
    Executes the end-to-end authorization, safety, and summarization pipeline for a care event.
    
    Args:
        conn: sqlite3 database connection
        event_id: Care event primary key
        family_id: Family member primary key
        save_to_db: Whether to persist the generated communication entry
        
    Returns:
        Dictionary representing the complete pipeline result, checks, and family update payload.
    """
    cursor = conn.cursor()

    # 1. Fetch Care Event
    cursor.execute("SELECT * FROM care_events WHERE event_id = ?", (event_id,))
    event_row = cursor.fetchone()
    if not event_row:
        return {
            'success': False,
            'error': f"Care event '{event_id}' not found."
        }
    event = dict(event_row)

    # 2. Fetch Resident
    cursor.execute("SELECT * FROM residents WHERE resident_id = ?", (event['resident_id'],))
    resident_row = cursor.fetchone()
    resident = dict(resident_row) if resident_row else {}

    # 3. Fetch Family Member
    cursor.execute("SELECT * FROM family_members WHERE family_id = ?", (family_id,))
    family_row = cursor.fetchone()
    if not family_row:
        return {
            'success': False,
            'error': f"Family member '{family_id}' not found."
        }
    family = dict(family_row)

    # Verify family is linked to the resident
    if family.get('resident_id') != event.get('resident_id'):
        return {
            'success': False,
            'disclosure_status': 'Blocked',
            'review_status': 'Rejected',
            'block_reason': "Information cannot be displayed: Family member is not linked to this resident.",
            'generated_summary': None
        }

    # 4. Fetch Consent
    cursor.execute(
        "SELECT * FROM consent WHERE resident_id = ? AND family_id = ?",
        (event['resident_id'], family_id)
    )
    consent_row = cursor.fetchone()
    consent = dict(consent_row) if consent_row else None

    # Step A: Missing Information Check
    is_complete, missing_fields, missing_reason = check_missing_information(event)

    # Step B: Role Check
    role_ok, role_reason = check_role_permission(
        role=family.get('role'),
        event_type=event.get('event_type'),
        urgency=event.get('urgency', 'Normal'),
        exception_flag=event.get('exception_flag', 0)
    )

    # Step C: Consent Check
    consent_ok, consent_reason = check_consent(
        consent_record=consent,
        event_type=event.get('event_type'),
        urgency=event.get('urgency', 'Normal'),
        exception_flag=event.get('exception_flag', 0)
    )

    # If Role or Consent fails, STOP immediately. DO NOT reveal protected info.
    if not role_ok or not consent_ok:
        if not role_ok:
            block_msg = role_reason
        elif not consent:
            block_msg = "Information cannot be displayed because the current family member does not have permission to receive this update."
        else:
            block_msg = consent_reason

        comm_id = f"COM-{uuid.uuid4().hex[:8].upper()}"
        if save_to_db:
            cursor.execute("""
                INSERT INTO communications (
                    comm_id, event_id, resident_id, family_id,
                    original_observation, generated_summary,
                    disclosure_status, review_status, block_reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                comm_id, event_id, event['resident_id'], family_id,
                event.get('observation', ''), None,
                'Blocked', 'Rejected', block_msg,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            conn.commit()

        return {
            'success': True,
            'comm_id': comm_id,
            'event_id': event_id,
            'resident_id': event['resident_id'],
            'resident_name': resident.get('resident_name'),
            'family_id': family_id,
            'family_name': family.get('family_name'),
            'family_role': family.get('role'),
            'consent_status': consent.get('consent_status') if consent else 'None',
            'role_check': {'passed': role_ok, 'reason': role_reason},
            'consent_check': {'passed': consent_ok, 'reason': consent_reason},
            'original_observation': event.get('observation'),
            'internal_staff_note': event.get('staff_note'),
            'generated_summary': None,
            'disclosure_status': 'Blocked',
            'review_status': 'Rejected',
            'block_reason': block_msg,
            'review_triggers': ["Authorization failed"]
        }

    # Step D: Generate Summary
    relationship = family.get('relationship', 'family member').lower()
    summary = generate_operational_summary(event, family_relation=relationship)

    # Step E: Safety Check on Raw Observation and Generated Summary
    safe_obs, flagged_obs, reason_obs = check_text_safety(event.get('observation', ''))
    safe_summary, flagged_summary, reason_summary = check_text_safety(summary)
    
    is_safe = safe_obs and safe_summary
    all_flagged = list(set(flagged_obs + flagged_summary))

    # Step F: Determine Human Review Requirement
    review_needed, review_triggers = requires_human_review(
        care_event=event,
        role_authorized=role_ok,
        consent_granted=consent_ok,
        is_safe=is_safe,
        flagged_terms=all_flagged,
        is_complete=is_complete
    )

    if review_needed:
        disclosure_status = 'Pending Review'
        review_status = 'Pending Review'
    else:
        disclosure_status = 'Approved'
        review_status = 'Auto-Approved'

    comm_id = f"COM-{uuid.uuid4().hex[:8].upper()}"
    if save_to_db:
        cursor.execute("""
            INSERT INTO communications (
                comm_id, event_id, resident_id, family_id,
                original_observation, generated_summary,
                disclosure_status, review_status, block_reason, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            comm_id, event_id, event['resident_id'], family_id,
            event.get('observation', ''), summary,
            disclosure_status, review_status, None,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()

    return {
        'success': True,
        'comm_id': comm_id,
        'event_id': event_id,
        'resident_id': event['resident_id'],
        'resident_name': resident.get('resident_name'),
        'family_id': family_id,
        'family_name': family.get('family_name'),
        'family_role': family.get('role'),
        'consent_status': consent.get('consent_status', 'Active'),
        'role_check': {'passed': role_ok, 'reason': role_reason},
        'consent_check': {'passed': consent_ok, 'reason': consent_reason},
        'safety_check': {'passed': is_safe, 'flagged': all_flagged},
        'completeness_check': {'passed': is_complete, 'missing': missing_fields},
        'original_observation': event.get('observation'),
        'internal_staff_note': event.get('staff_note'), # Kept internal, exposed only to staff UI
        'generated_summary': summary,
        'disclosure_status': disclosure_status,
        'review_status': review_status,
        'review_triggers': review_triggers,
        'block_reason': None
    }
