"""Synthetic Data Generator
Generates realistic assisted-living operational care events, family members, consents, and questions.
Outputs CSV files into the data/ directory.
Strictly non-medical operational data.
"""

import os
import csv
import random
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 1. RESIDENTS
RESIDENTS = [
    {
        'resident_id': 'RES001',
        'resident_name': 'Devi Raman',
        'age_group': '75-84',
        'independence_level': 'Needs Moderate Assistance',
        'preferred_communication_style': 'Brief & Timely',
        'active_status': 1
    },
    {
        'resident_id': 'RES002',
        'resident_name': 'Ramesh Sharma',
        'age_group': '85+',
        'independence_level': 'Needs High Assistance',
        'preferred_communication_style': 'Daily Summary',
        'active_status': 1
    },
    {
        'resident_id': 'RES003',
        'resident_name': 'Kamala Sundaram',
        'age_group': '70-74',
        'independence_level': 'Needs Minimal Assistance',
        'preferred_communication_style': 'Weekly Digest',
        'active_status': 1
    },
    {
        'resident_id': 'RES004',
        'resident_name': 'Mohan Patel',
        'age_group': '75-84',
        'independence_level': 'Independent',
        'preferred_communication_style': 'Direct & Independent',
        'active_status': 1
    },
    {
        'resident_id': 'RES005',
        'resident_name': 'Lakshmi Narayanan',
        'age_group': '80-84',
        'independence_level': 'Needs Moderate Assistance',
        'preferred_communication_style': 'Evening Recap',
        'active_status': 1
    }
]

# 2. FAMILY MEMBERS (Using requested demo names: Kavi, Charu, Hema, Abi, Mala)
FAMILY_MEMBERS = [
    {
        'family_id': 'FAM001',
        'family_name': 'Kavi',
        'relationship': 'Daughter',
        'resident_id': 'RES001', # Devi Raman
        'role': 'Primary Family Contact',
        'active_status': 1
    },
    {
        'family_id': 'FAM002',
        'family_name': 'Charu',
        'relationship': 'Son',
        'resident_id': 'RES001', # Devi Raman
        'role': 'Secondary Family Contact',
        'active_status': 1
    },
    {
        'family_id': 'FAM003',
        'family_name': 'Hema',
        'relationship': 'Daughter-in-law',
        'resident_id': 'RES002', # Ramesh Sharma
        'role': 'Emergency Contact',
        'active_status': 1
    },
    {
        'family_id': 'FAM004',
        'family_name': 'Abi',
        'relationship': 'Niece',
        'resident_id': 'RES003', # Kamala Sundaram
        'role': 'View-Only Contact',
        'active_status': 1
    },
    {
        'family_id': 'FAM005',
        'family_name': 'Mala',
        'relationship': 'Sister',
        'resident_id': 'RES004', # Mohan Patel
        'role': 'Primary Family Contact',
        'active_status': 1
    }
]

# 3. CONSENT RECORDS
CONSENTS = [
    {
        'consent_id': 'CON001',
        'resident_id': 'RES001',
        'family_id': 'FAM001', # Kavi (Primary): Full active consent
        'care_activity_updates': 1,
        'routine_updates': 1,
        'exception_updates': 1,
        'communication_questions': 1,
        'consent_status': 'Active',
        'effective_date': '2026-01-10'
    },
    {
        'consent_id': 'CON002',
        'resident_id': 'RES001',
        'family_id': 'FAM002', # Charu (Secondary): Routine & Activity only, exception disabled
        'care_activity_updates': 1,
        'routine_updates': 1,
        'exception_updates': 0,
        'communication_questions': 1,
        'consent_status': 'Active',
        'effective_date': '2026-01-12'
    },
    {
        'consent_id': 'CON003',
        'resident_id': 'RES002',
        'family_id': 'FAM003', # Hema (Emergency Contact): Exception only
        'care_activity_updates': 0,
        'routine_updates': 0,
        'exception_updates': 1,
        'communication_questions': 0,
        'consent_status': 'Active',
        'effective_date': '2026-01-15'
    },
    {
        'consent_id': 'CON004',
        'resident_id': 'RES003',
        'family_id': 'FAM004', # Abi (View-Only): Revoked consent (Case 1 Demo)
        'care_activity_updates': 0,
        'routine_updates': 0,
        'exception_updates': 0,
        'communication_questions': 0,
        'consent_status': 'Revoked',
        'effective_date': '2026-02-01'
    },
    {
        'consent_id': 'CON005',
        'resident_id': 'RES004',
        'family_id': 'FAM005', # Mala: Full consent
        'care_activity_updates': 1,
        'routine_updates': 1,
        'exception_updates': 1,
        'communication_questions': 1,
        'consent_status': 'Active',
        'effective_date': '2026-01-05'
    }
]

# 4. CORE KEY CARE EVENTS (Explicit Journeys & Failure Cases)
KEY_CARE_EVENTS = [
    # JOURNEY 1: Low Urgency / Normal Social Activity (Devi Raman -> Kavi)
    {
        'event_id': 'EVT001',
        'resident_id': 'RES001',
        'event_datetime': '2026-09-03 14:30:00',
        'event_type': 'Social Activity',
        'observation': 'Resident participated in the afternoon music session with minimal assistance.',
        'assistance_level': 'Minimal',
        'urgency': 'Low',
        'exception_flag': 0,
        'staff_note': 'Devi enjoyed playing the tambourine; staff ensured seating was near the front. Internal staff note not for family.',
        'created_by': 'Madhu'
    },
    # JOURNEY 2: High Urgency / Operational Exception (Devi Raman -> Kavi)
    {
        'event_id': 'EVT002',
        'resident_id': 'RES001',
        'event_datetime': '2026-09-04 10:15:00',
        'event_type': 'Mobility',
        'observation': 'Resident declined scheduled physical mobility session due to feeling fatigued; resting in room.',
        'assistance_level': 'Moderate',
        'urgency': 'High',
        'exception_flag': 1,
        'staff_note': 'Devi reported general tiredness after breakfast. Hydration offered. Staff will re-check at 14:00.',
        'created_by': 'Madhu'
    },
    # CASE 1: No Consent / Revoked Consent (Kamala Sundaram -> Abi)
    {
        'event_id': 'EVT003',
        'resident_id': 'RES003',
        'event_datetime': '2026-09-04 09:00:00',
        'event_type': 'Morning Routine',
        'observation': 'Resident completed morning hygiene routine independently and enjoyed breakfast in the dining area.',
        'assistance_level': 'Independent',
        'urgency': 'Normal',
        'exception_flag': 0,
        'staff_note': 'Kamala was in cheerful spirits. Finished tea.',
        'created_by': 'Madhu'
    },
    # CASE 2: Insufficient Role Permissions (Kamala Sundaram -> Abi - View-Only attempting Personal Care)
    {
        'event_id': 'EVT004',
        'resident_id': 'RES003',
        'event_datetime': '2026-09-03 18:00:00',
        'event_type': 'Personal Care',
        'observation': 'Staff provided assistance with evening transfer and personal care routine.',
        'assistance_level': 'Moderate',
        'urgency': 'Normal',
        'exception_flag': 0,
        'staff_note': 'Detailed staff log for night team handover.',
        'created_by': 'Madhu'
    },
    # CASE 3: Care Event Contains Potentially Medical Language (Ramesh Sharma -> Hema)
    {
        'event_id': 'EVT005',
        'resident_id': 'RES002',
        'event_datetime': '2026-09-04 08:30:00',
        'event_type': 'Morning Routine',
        'observation': 'Resident exhibited fever of 101F and suspected chest infection; staff administered paracetamol 500mg.',
        'assistance_level': 'High',
        'urgency': 'High',
        'exception_flag': 1,
        'staff_note': 'Clinical nurse practitioner paged. Handover required immediately.',
        'created_by': 'Madhu'
    },
    # CASE 4: Care Event Has Missing Information (Mohan Patel -> Mala)
    {
        'event_id': 'EVT006',
        'resident_id': 'RES004',
        'event_datetime': '2026-09-04 11:00:00',
        'event_type': 'Activity',
        'observation': '', # MISSING OBSERVATION!
        'assistance_level': '', # MISSING ASSISTANCE!
        'urgency': 'Normal',
        'exception_flag': 0,
        'staff_note': 'Incomplete record test.',
        'created_by': 'Madhu'
    }
]

# Additional synthetic care events for realistic volume and experiment benchmarking (100 total)
OPERATIONAL_OBSERVATIONS = [
    ('Meal', 'Resident attended lunch at 12:30. Finished meal with moderate assistance.', 'Moderate', 'Normal', 0),
    ('Meal', 'Resident enjoyed breakfast in the communal dining hall independently.', 'Independent', 'Low', 0),
    ('Meal', 'Resident requested late supper tray in room. Finished soup.', 'Minimal', 'Normal', 0),
    ('Activity', 'Resident attended the gardening activity in the courtyard with minimal assistance.', 'Minimal', 'Low', 0),
    ('Activity', 'Resident participated in the afternoon reading group and socialized with peers.', 'Independent', 'Low', 0),
    ('Activity', 'Resident joined arts and crafts session and completed watercolor painting.', 'Minimal', 'Low', 0),
    ('Social Activity', 'Resident attended social bingo gathering in the main lounge.', 'Minimal', 'Low', 0),
    ('Social Activity', 'Resident enjoyed evening music session and engaged in group singing.', 'Independent', 'Low', 0),
    ('Morning Routine', 'Staff supported resident through their morning routine with minimal assistance.', 'Minimal', 'Normal', 0),
    ('Morning Routine', 'Resident completed morning routine independently with verbal reminders.', 'Independent', 'Low', 0),
    ('Morning Routine', 'Staff provided moderate assistance with morning hygiene and grooming.', 'Moderate', 'Normal', 0),
    ('Personal Care', 'Staff assisted resident with afternoon personal care and wardrobe change.', 'Moderate', 'Normal', 0),
    ('Personal Care', 'Evening personal care routine completed with moderate staff assistance.', 'Moderate', 'Normal', 0),
    ('Mobility', 'Resident completed their daily walking routine in the hallway with walking frame.', 'Minimal', 'Normal', 0),
    ('Mobility', 'Resident practiced hallway mobility exercises with physical therapy aide.', 'Moderate', 'Normal', 0),
    ('Scheduled Appointment', 'Resident attended scheduled facility podiatry visit on time with staff escort.', 'Minimal', 'Normal', 0),
    ('Scheduled Appointment', 'Resident completed optical review visit at the facility clinic.', 'Independent', 'Low', 0),
    ('Other Operational Event', 'Facility laundry delivered and organized in resident closet by staff.', 'Independent', 'Low', 0),
    # Edge case candidates (inadvertent staff clinical notes or high urgency)
    ('Activity', 'Resident did not attend group activity; rested quietly in room after lunch.', 'Minimal', 'Normal', 1),
    ('Mobility', 'Resident felt dizzy during hallway walk; assisted safely to chair.', 'High', 'High', 1),
    ('Meal', 'Resident declined dinner tray citing lack of appetite; staff offered fruit cup.', 'Minimal', 'Normal', 1),
    ('Morning Routine', 'Staff noted resident coughed frequently and complained of chest congestion.', 'Moderate', 'High', 1),
    ('Personal Care', 'Resident required high assistance during transfer; staff used slide board.', 'High', 'Normal', 0)
]

def generate_all_care_events():
    events = list(KEY_CARE_EVENTS)
    base_time = datetime(2026, 8, 20, 8, 0, 0)
    current_id = 7

    residents_pool = ['RES001', 'RES002', 'RES003', 'RES004', 'RES005']

    while len(events) < 100:
        res_id = random.choice(residents_pool)
        template = random.choice(OPERATIONAL_OBSERVATIONS)
        event_time = base_time + timedelta(
            days=random.randint(0, 15),
            hours=random.randint(0, 12),
            minutes=random.choice([0, 15, 30, 45])
        )

        events.append({
            'event_id': f'EVT{current_id:03d}',
            'resident_id': res_id,
            'event_datetime': event_time.strftime('%Y-%m-%d %H:%M:%S'),
            'event_type': template[0],
            'observation': template[1],
            'assistance_level': template[2],
            'urgency': template[3],
            'exception_flag': template[4],
            'staff_note': f"Staff shift log reference #{current_id}. Handover checked by Madhu.",
            'created_by': 'Madhu'
        })
        current_id += 1

    return events

# 5. QUESTIONS (Operational & Case 5 Medical Inquiry)
QUESTIONS = [
    {
        'question_id': 'QUE001',
        'family_id': 'FAM001', # Kavi
        'resident_id': 'RES001',
        'question_text': 'Could you let me know if Devi enjoyed the afternoon music session today?',
        'category': 'Activity',
        'status': 'Answered',
        'created_at': '2026-09-03 16:00:00',
        'staff_response': 'Yes! Devi actively participated, played the tambourine, and enjoyed singing with peers.',
        'answered_by': 'Madhu',
        'answered_at': '2026-09-03 17:15:00'
    },
    {
        'question_id': 'QUE002',
        'family_id': 'FAM003', # Hema (CASE 5: Medical Question)
        'resident_id': 'RES002',
        'question_text': 'What dosage of fever medicine or antibiotic should Ramesh take for his chest infection?',
        'category': 'Medical Inquiry',
        'status': 'Flagged Medical',
        'created_at': '2026-09-04 09:15:00',
        'staff_response': 'Operational Support Only — This system communicates care activities and operational observations. It does not provide medical diagnosis, treatment recommendations, or medical advice. Your inquiry has been routed to facility nursing staff for clinical consultation.',
        'answered_by': 'Safety Checker (Automated)',
        'answered_at': '2026-09-04 09:15:01'
    },
    {
        'question_id': 'QUE003',
        'family_id': 'FAM005', # Mala
        'resident_id': 'RES004',
        'question_text': 'What time is Mohan scheduled for his courtyard walking routine tomorrow?',
        'category': 'Routine',
        'status': 'Pending',
        'created_at': '2026-09-04 11:30:00',
        'staff_response': None,
        'answered_by': None,
        'answered_at': None
    }
]

# 6. EXCEPTIONS
EXCEPTIONS = [
    {
        'exception_id': 'EXC001',
        'event_id': 'EVT002',
        'resident_id': 'RES001',
        'exception_type': 'Missed Scheduled Session',
        'description': 'Resident declined scheduled physical mobility session due to fatigue.',
        'severity': 'Moderate',
        'review_required': 1,
        'resolution_status': 'Under Review'
    },
    {
        'exception_id': 'EXC002',
        'event_id': 'EVT005',
        'resident_id': 'RES002',
        'exception_type': 'Clinical Terminology Intercepted',
        'description': 'Observation contained medical vocabulary requiring staff review before family communication.',
        'severity': 'High',
        'review_required': 1,
        'resolution_status': 'Open'
    }
]

def write_csv(filename, data, fieldnames):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Generated {filepath} ({len(data)} records)")

def main():
    care_events = generate_all_care_events()

    write_csv('residents.csv', RESIDENTS, list(RESIDENTS[0].keys()))
    write_csv('family_members.csv', FAMILY_MEMBERS, list(FAMILY_MEMBERS[0].keys()))
    write_csv('consent.csv', CONSENTS, list(CONSENTS[0].keys()))
    write_csv('care_events.csv', care_events, list(care_events[0].keys()))
    write_csv('questions.csv', QUESTIONS, list(QUESTIONS[0].keys()))
    write_csv('exceptions.csv', EXCEPTIONS, list(EXCEPTIONS[0].keys()))
    print("All synthetic CSV datasets successfully generated.")

if __name__ == '__main__':
    main()
