"""Tests for Consent Checker Service
Verifies active consent granting, revoked consent denial, and category-level permissions.
"""

import unittest
from services.consent_checker import check_consent, check_question_consent

class TestConsentChecker(unittest.TestCase):

    def setUp(self):
        self.active_consent = {
            'consent_status': 'Active',
            'care_activity_updates': 1,
            'routine_updates': 1,
            'exception_updates': 1,
            'communication_questions': 1
        }
        self.revoked_consent = {
            'consent_status': 'Revoked',
            'care_activity_updates': 1,
            'routine_updates': 1,
            'exception_updates': 1,
            'communication_questions': 1
        }
        self.partial_consent = {
            'consent_status': 'Active',
            'care_activity_updates': 1,
            'routine_updates': 0, # Routine care disabled
            'exception_updates': 0, # Exceptions disabled
            'communication_questions': 0
        }

    def test_valid_active_consent(self):
        """Active consent with all permissions should approve care events."""
        is_ok, reason = check_consent(self.active_consent, 'Activity', 'Low', 0)
        self.assertTrue(is_ok)
        self.assertIn("Authorized", reason)

    def test_revoked_consent_blocks_disclosure(self):
        """Revoked consent must strictly block all information disclosure."""
        is_ok, reason = check_consent(self.revoked_consent, 'Activity', 'Low', 0)
        self.assertFalse(is_ok)
        self.assertIn("Revoked", reason)

    def test_missing_consent_record(self):
        """Null or missing consent must block disclosure with standard unauthorized notice."""
        is_ok, reason = check_consent(None, 'Meal', 'Normal', 0)
        self.assertFalse(is_ok)
        self.assertIn("does not have permission", reason)

    def test_category_level_routine_permission_disabled(self):
        """When routine_updates is 0, Morning Routine events must be blocked."""
        is_ok, reason = check_consent(self.partial_consent, 'Morning Routine', 'Normal', 0)
        self.assertFalse(is_ok)
        self.assertIn("routine personal care updates", reason)

    def test_category_level_activity_permission_enabled(self):
        """When care_activity_updates is 1, Meal/Activity events should pass."""
        is_ok, reason = check_consent(self.partial_consent, 'Meal', 'Normal', 0)
        self.assertTrue(is_ok)

    def test_exception_consent_disabled(self):
        """When exception_updates is 0, urgent exceptions must be blocked."""
        is_ok, reason = check_consent(self.partial_consent, 'Activity', 'High', 1)
        self.assertFalse(is_ok)
        self.assertIn("exception updates", reason)

    def test_question_consent(self):
        """Question submission permission must match communication_questions flag."""
        self.assertTrue(check_question_consent(self.active_consent)[0])
        self.assertFalse(check_question_consent(self.partial_consent)[0])
        self.assertFalse(check_question_consent(self.revoked_consent)[0])

if __name__ == '__main__':
    unittest.main()
