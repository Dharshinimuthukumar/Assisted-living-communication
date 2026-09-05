"""Summary Generator Service
Rule-based operational summarization engine.
Transforms raw care events into concise, family-friendly updates without relying on external LLMs.
Strictly eliminates internal staff notes and adheres to observable facts.
"""

def generate_operational_summary(care_event: dict, family_relation: str = "family member") -> str:
    """
    Generates a concise operational summary from a raw care event.
    
    Args:
        care_event: Dictionary of event details:
            - event_type: str
            - observation: str
            - assistance_level: str ('Independent', 'Minimal', 'Moderate', 'High')
            - urgency: str ('Low', 'Normal', 'High')
            - exception_flag: int
            - staff_note: str (EXCLUDED FROM SUMMARY)
        family_relation: Relationship context (default 'family member')
        
    Returns:
        Concise, human-readable operational summary string.
    """
    if not care_event:
        return "No care event details provided."

    event_type = care_event.get('event_type', 'Activity')
    observation = care_event.get('observation', '').strip()
    assistance_level = care_event.get('assistance_level', 'Minimal').lower()
    is_exception = care_event.get('exception_flag', 0) == 1

    # Assistance phrasing helper
    if assistance_level == 'independent':
        assist_text = "independently"
    elif assistance_level in ['minimal', 'moderate', 'high']:
        assist_text = f"with {assistance_level} assistance"
    else:
        assist_text = "with staff assistance"

    # Handle operational exceptions first
    if is_exception:
        # Simplify observation for family reassurance without medical speculation
        clean_obs = observation.rstrip('.')
        return f"Operational update: {clean_obs}. Staff follow-up is in progress."

    # Pattern-based operational summarization by event type
    if event_type == 'Meal':
        # E.g., Lunch, Breakfast, Dinner
        if "lunch" in observation.lower():
            meal_name = "lunch"
        elif "breakfast" in observation.lower():
            meal_name = "breakfast"
        elif "dinner" in observation.lower() or "supper" in observation.lower():
            meal_name = "dinner"
        else:
            meal_name = "their meal"
        return f"Your {family_relation} attended {meal_name} today {assist_text}."

    elif event_type in ['Social Activity', 'Activity']:
        # Extract activity name if present
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

    elif event_type == 'Morning Routine':
        return f"Staff supported your {family_relation} through their morning routine {assist_text}."

    elif event_type == 'Personal Care':
        return f"Staff provided operational assistance with daily personal care {assist_text}."

    elif event_type == 'Mobility':
        return f"Your {family_relation} completed their daily walking and mobility routine {assist_text}."

    elif event_type == 'Scheduled Appointment':
        return f"Your {family_relation} completed their scheduled facility operational appointment on time."

    else: # Other Operational Event
        if observation:
            # Clean sentence capitalization
            clean_obs = observation.rstrip('.')
            return f"Operational note: {clean_obs} ({assist_text})."
        return f"An operational care event was recorded {assist_text}."
