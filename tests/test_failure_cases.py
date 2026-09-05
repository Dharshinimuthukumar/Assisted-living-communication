"""Tests for System Failure and Edge Cases
Verifies that all 5 critical edge cases are properly intercepted, logged, and prevented from unauthorised disclosure.
"""

import unittest
import sqlite3
import os
from services.safety_checker import (
    check_text_safety,
    check_missing_information,
    classify_question,
    requires_human_review
)
from services.communication_service import process_care_event_for_family

class TestFailureCases(unittest.TestCase):

    def setUp(self):
        # In-memory test database
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.conn.cursor().executescript(f.read())

        cursor = self.conn.cursor()
        # Seed test resident
        cursor.execute("""
            INSERT INTO residents (resident_id, resident_name, age_group, independence_level, preferred_communication_style, active_status)
            VALUES ('RES_T1', 'Test Resident', '75-84', 'Needs Moderate Assistance', 'Brief', 1)
        """)
        # Seed family members
        cursor.execute("""
            INSERT INTO family_members (family_id, family_name, relationship, resident_id, role, active_status)
            VALUES 
                ('FAM_NOCONSENT', 'No Consent User', 'Niece', 'RES_T1', 'View-Only Contact', 1),
                ('FAM_RESTRICTED', 'Restricted Role User', 'Daughter-in-law', 'RES_T1', 'Emergency Contact', 1),
                ('FAM_PRIMARY', 'Authorized User', 'Daughter', 'RES_T1', 'Primary Family Contact', 1)
        """)
        # Seed revoked/no consent for FAM_NOCONSENT
        cursor.execute("""
            INSERT INTO consent (consent_id, resident_id, family_id, care_activity_updates, routine_updates, exception_updates, communication_questions, consent_status, effective_date)
            VALUES 
                ('CON_REVOKED', 'RES_T1', 'FAM_NOCONSENT', 0, 0, 0, 0, 'Revoked', '2026-01-01'),
                ('CON_PRIMARY', 'RES_T1', 'FAM_PRIMARY', 1, 1, 1, 1, 'Active', '2026-01-01'),
                ('CON_EMERGENCY', 'RES_T1', 'FAM_RESTRICTED', 0, 0, 1, 0, 'Active', '2026-01-01')
        """)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_case_1_no_consent_blocks_disclosure(self):
        """CASE 1: Family member has revoked/no consent -> Block disclosure and generate clear notice."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO care_events (event_id, resident_id, event_datetime, event_type, observation, assistance_level, urgency, exception_flag, staff_note, created_by)
            VALUES ('EVT_C1', 'RES_T1', '2026-09-04 10:00:00', 'Activity', 'Resident attended arts and crafts.', 'Minimal', 'Low', 0, 'Internal note', 'Madhu')
        """)
        self.conn.commit()

        res = process_care_event_for_family(self.conn, 'EVT_C1', 'FAM_NOCONSENT', save_to_db=True)
        self.assertEqual(res['disclosure_status'], 'Blocked')
        self.assertIsNone(res['generated_summary'])
        self.assertIn("Information cannot be displayed", res['block_reason'])

    def test_case_2_insufficient_role_permissions(self):
        """CASE 2: Emergency Contact attempting to view routine care event is blocked."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO care_events (event_id, resident_id, event_datetime, event_type, observation, assistance_level, urgency, exception_flag, staff_note, created_by)
            VALUES ('EVT_C2', 'RES_T1', '2026-09-04 10:00:00', 'Meal', 'Resident finished lunch.', 'Independent', 'Normal', 0, 'Internal note', 'Madhu')
        """)
        self.conn.commit()

        res = process_care_event_for_family(self.conn, 'EVT_C2', 'FAM_RESTRICTED', save_to_db=True)
        self.assertEqual(res['disclosure_status'], 'Blocked')
        self.assertIsNone(res['generated_summary'])
        self.assertIn("restricted from routine daily care logs", res['block_reason'])

    def test_case_3_medical_language_interception(self):
        """CASE 3: Care event observation contains medical terminology -> Flagged for human review."""
        medical_obs = "Resident exhibited fever of 101F and suspected chest infection; staff gave paracetamol 500mg."
        is_safe, flagged_terms, reason = check_text_safety(medical_obs)
        self.assertFalse(is_safe)
        self.assertIn('fever', flagged_terms)
        self.assertIn('infection', flagged_terms)
        self.assertIn('paracetamol', flagged_terms)

        # Pipeline test
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO care_events (event_id, resident_id, event_datetime, event_type, observation, assistance_level, urgency, exception_flag, staff_note, created_by)
            VALUES ('EVT_C3', 'RES_T1', '2026-09-04 10:00:00', 'Morning Routine', ?, 'Moderate', 'High', 1, 'Nursing alert', 'Madhu')
        """, (medical_obs,))
        self.conn.commit()

        res = process_care_event_for_family(self.conn, 'EVT_C3', 'FAM_PRIMARY', save_to_db=True)
        self.assertEqual(res['disclosure_status'], 'Pending Review')
        self.assertFalse(res['safety_check']['passed'])
        self.assertTrue(any('medical language' in trigger.lower() for trigger in res['review_triggers']))

    def test_case_4_missing_information_detection(self):
        """CASE 4: Care event with missing observation/assistance is flagged without hallucination."""
        incomplete_event = {
            'resident_id': 'RES_T1',
            'event_type': 'Activity',
            'observation': '', # MISSING
            'assistance_level': None, # MISSING
            'urgency': 'Normal'
        }
        is_complete, missing_fields, reason = check_missing_information(incomplete_event)
        self.assertFalse(is_complete)
        self.assertIn('observation', missing_fields)
        self.assertIn('assistance_level', missing_fields)

        # Triggers review
        req_review, triggers = requires_human_review(
            incomplete_event, True, True, True, [], is_complete
        )
        self.assertTrue(req_review)
        self.assertIn("Missing operational event information", triggers)

    def test_case_5_family_medical_question_boundary(self):
        """CASE 5: Family question asking for medical diagnosis/prescription is intercepted."""
        medical_question = "What medicine or dosage should I give my father for his fever and cough?"
        is_op, response = classify_question(medical_question)
        self.assertFalse(is_op)
        self.assertIn("Operational Support Only", response)
        self.assertIn("does not provide medical diagnosis", response)

        # Operational question passes
        operational_question = "Did my mother participate in the afternoon gardening session?"
        is_op_valid, reason = classify_question(operational_question)
        self.assertTrue(is_op_valid)

if __name__ == '__main__':
    unittest.main()
