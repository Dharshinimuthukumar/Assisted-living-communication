"""Consent Checker Service
Enforces resident consent policies and fine-grained information-sharing permissions.
"""

def check_consent(consent_record: dict, event_type: str, urgency: str = 'Normal', exception_flag: int = 0) -> tuple:
    """
    Validates whether resident consent permits disclosure of the care event.
    
    Args:
        consent_record: Dictionary with consent attributes:
            - consent_status: 'Active', 'Revoked', 'Pending'
            - care_activity_updates: int (0 or 1)
            - routine_updates: int (0 or 1)
            - exception_updates: int (0 or 1)
            - communication_questions: int (0 or 1)
        event_type: The category of the care event
        urgency: Urgency level ('Low', 'Normal', 'High')
        exception_flag: 1 if event is an operational exception, else 0
        
    Returns:
        (is_consented: bool, reason: str)
    """
    if not consent_record:
        return False, "Information cannot be displayed because the current family member does not have permission to receive this update."

    status = consent_record.get('consent_status', 'Pending')
    if status != 'Active':
        return False, f"Information cannot be displayed because consent status is '{status}'."

    # Check urgent / exception permission
    if exception_flag == 1 or urgency == 'High':
        if not consent_record.get('exception_updates', 0):
            return False, "Information cannot be displayed: Resident consent does not permit sharing exception updates with this contact."
        return True, "Authorized by active resident consent for exception updates."

    # Check routine care updates permission
    if event_type in ['Morning Routine', 'Personal Care', 'Mobility']:
        if not consent_record.get('routine_updates', 0):
            return False, "Information cannot be displayed: Resident consent does not permit sharing routine personal care updates with this contact."
        return True, "Authorized by active resident consent for routine care updates."

    # Check general activity / meal updates permission
    if event_type in ['Meal', 'Activity', 'Social Activity', 'Scheduled Appointment', 'Other Operational Event']:
        if not consent_record.get('care_activity_updates', 0):
            return False, "Information cannot be displayed: Resident consent does not permit sharing care activity updates with this contact."
        return True, "Authorized by active resident consent for care activity updates."

    return False, "Information cannot be displayed: Category not permitted under current consent."

def check_question_consent(consent_record: dict) -> tuple:
    """
    Validates whether the resident has consented to allowing this family member to submit Q&A inquiries.
    """
    if not consent_record:
        return False, "Family member lacks consent configuration."
    
    if consent_record.get('consent_status') != 'Active':
        return False, f"Consent status is '{consent_record.get('consent_status')}', questions blocked."
        
    if not consent_record.get('communication_questions', 0):
        return False, "Resident consent has not enabled family Q&A privileges for this contact."
        
    return True, "Family Q&A permitted by resident consent."
