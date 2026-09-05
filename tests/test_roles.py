"""Tests for Role Checker Service
Verifies permission boundaries across Primary, Secondary, Emergency, and View-Only contacts.
"""

import unittest
from services.role_checker import check_role_permission, can_submit_questions

class TestRoleChecker(unittest.TestCase):

    def test_primary_family_contact_access(self):
        """Primary Contact has full operational update authorization."""
        role = 'Primary Family Contact'
        is_ok, _ = check_role_permission(role, 'Meal', 'Normal', 0)
        self.assertTrue(is_ok)
        is_ok, _ = check_role_permission(role, 'Personal Care', 'High', 1)
        self.assertTrue(is_ok)
        self.assertTrue(can_submit_questions(role))

    def test_secondary_family_contact_access(self):
        """Secondary Contact has routine and activity access."""
        role = 'Secondary Family Contact'
        is_ok, _ = check_role_permission(role, 'Social Activity', 'Low', 0)
        self.assertTrue(is_ok)
        self.assertTrue(can_submit_questions(role))

    def test_emergency_contact_restrictions(self):
        """Emergency contact is blocked from routine logs but authorized for urgent exceptions."""
        role = 'Emergency Contact'
        # Routine meal blocked to avoid noise
        is_ok, reason = check_role_permission(role, 'Meal', 'Normal', 0)
        self.assertFalse(is_ok)
        self.assertIn("restricted from routine daily care logs", reason)

        # Urgent exception allowed
        is_ok, reason = check_role_permission(role, 'Mobility', 'High', 1)
        self.assertTrue(is_ok)
        self.assertFalse(can_submit_questions(role))

    def test_view_only_contact_restrictions(self):
        """View-Only contact is restricted from personal care and high urgency exceptions."""
        role = 'View-Only Contact'
        # Allowed for general social activities
        is_ok, _ = check_role_permission(role, 'Social Activity', 'Low', 0)
        self.assertTrue(is_ok)

        # Blocked for sensitive personal care
        is_ok, reason = check_role_permission(role, 'Personal Care', 'Normal', 0)
        self.assertFalse(is_ok)
        self.assertIn("sensitive personal care", reason)

        # Blocked for high urgency exceptions
        is_ok, reason = check_role_permission(role, 'Mobility', 'High', 1)
        self.assertFalse(is_ok)
        self.assertIn("does not permit access to operational exceptions", reason)

        self.assertFalse(can_submit_questions(role))

    def test_invalid_role(self):
        """Invalid or unrecognized role strings are rejected."""
        is_ok, reason = check_role_permission('Unregistered Visitor', 'Activity', 'Low', 0)
        self.assertFalse(is_ok)
        self.assertIn("Invalid or unrecognized", reason)

if __name__ == '__main__':
    unittest.main()
