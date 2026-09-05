"""Role Checker Service
Validates family member roles against information access policies.
"""

VALID_ROLES = [
    'Primary Family Contact',
    'Secondary Family Contact',
    'Emergency Contact',
    'View-Only Contact'
]

def check_role_permission(role: str, event_type: str, urgency: str = 'Normal', exception_flag: int = 0) -> tuple:
    """
    Evaluates whether the given family role has permission to receive the specific event update.
    
    Returns:
        (is_authorized: bool, reason: str)
    """
    if not role or role not in VALID_ROLES:
        return False, f"Invalid or unrecognized family role: '{role}'."

    # View-Only Contact has heavily restricted access
    if role == 'View-Only Contact':
        # Can only see routine social activities or low urgency events; cannot see exceptions or high urgency details
        if exception_flag == 1 or urgency == 'High':
            return False, "View-Only Contact role does not permit access to operational exceptions or high-urgency logs."
        if event_type in ['Personal Care']:
            return False, "View-Only Contact role does not permit access to sensitive personal care details."
        return True, "Authorized for view-only general operational updates."

    # Emergency Contact
    if role == 'Emergency Contact':
        # Primarily designated for high urgency and exception updates
        if exception_flag == 1 or urgency == 'High':
            return True, "Emergency Contact is authorized for exception and high-urgency operational alerts."
        # Routine daily events are restricted to preserve operational signal-to-noise
        return False, "Emergency Contact role is restricted from routine daily care logs (reserved for exceptions/emergencies)."

    # Secondary Family Contact
    if role == 'Secondary Family Contact':
        if urgency == 'High' and exception_flag == 1:
            # Requires Primary Contact coordination, but can receive with review
            return True, "Secondary Family Contact authorized for operational update."
        return True, "Secondary Family Contact authorized for standard operational updates."

    # Primary Family Contact
    if role == 'Primary Family Contact':
        return True, "Primary Family Contact has full operational update access."

    return False, "Role permission could not be verified."

def can_submit_questions(role: str) -> bool:
    """Determines if the role is permitted to submit operational questions to staff."""
    return role in ['Primary Family Contact', 'Secondary Family Contact']

def get_role_capabilities(role: str) -> dict:
    """Returns a dictionary explaining the capabilities of each role for UI tooltips."""
    capabilities = {
        'Primary Family Contact': {
            'description': 'Primary designated family liaison with comprehensive access to all operational updates and direct Q&A.',
            'access_level': 'Comprehensive',
            'can_ask_questions': True
        },
        'Secondary Family Contact': {
            'description': 'Authorized family member receiving routine and activity updates, with Q&A capabilities.',
            'access_level': 'Standard',
            'can_ask_questions': True
        },
        'Emergency Contact': {
            'description': 'Designated solely for urgent operational exceptions and safety follow-ups.',
            'access_level': 'Urgent Exceptions Only',
            'can_ask_questions': False
        },
        'View-Only Contact': {
            'description': 'Restricted access for general social and activity updates only. Sensitive personal care and exceptions blocked.',
            'access_level': 'Restricted Read-Only',
            'can_ask_questions': False
        }
    }
    return capabilities.get(role, {})
