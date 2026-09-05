"""Tests for Summary Generator Service
Verifies concise generation, factual accuracy, exclusion of staff notes, and non-medical phrasing.
"""

import unittest
from services.summary_generator import generate_operational_summary

class TestSummaryGenerator(unittest.TestCase):

    def test_meal_summary_generation(self):
        """Meal events are transformed into concise, respectful family summaries."""
        event = {
            'event_type': 'Meal',
            'observation': 'Resident attended lunch at 12:30. Required moderate assistance. Finished meal.',
            'assistance_level': 'Moderate',
            'urgency': 'Normal',
            'exception_flag': 0,
            'staff_note': 'Do not show: internal note about bib placement.'
        }
        summary = generate_operational_summary(event, family_relation="mother")
        self.assertIn("lunch", summary.lower())
        self.assertIn("moderate assistance", summary.lower())
        self.assertNotIn("Do not show", summary)
        self.assertNotIn("bib", summary)

    def test_social_activity_summary(self):
        """Social activity events highlight participation and level of assistance."""
        event = {
            'event_type': 'Social Activity',
            'observation': 'Resident participated in the afternoon music session with minimal assistance.',
            'assistance_level': 'Minimal',
            'urgency': 'Low',
            'exception_flag': 0,
            'staff_note': 'Staff shift note #12.'
        }
        summary = generate_operational_summary(event, family_relation="father")
        self.assertIn("music session", summary.lower())
        self.assertIn("minimal assistance", summary.lower())
        self.assertNotIn("shift note", summary)

    def test_operational_exception_summary(self):
        """Exceptions are stated objectively without clinical panic or diagnosis."""
        event = {
            'event_type': 'Mobility',
            'observation': 'Resident declined scheduled physical mobility session due to feeling fatigued; resting in room.',
            'assistance_level': 'Moderate',
            'urgency': 'High',
            'exception_flag': 1,
            'staff_note': 'Check vital signs later.'
        }
        summary = generate_operational_summary(event, family_relation="mother")
        self.assertTrue(summary.startswith("Operational update:"))
        self.assertIn("Staff follow-up is in progress", summary)
        self.assertNotIn("vital signs", summary)

    def test_internal_staff_notes_are_never_included(self):
        """Internal staff notes must strictly never be appended to family summaries."""
        event = {
            'event_type': 'Personal Care',
            'observation': 'Staff provided assistance with evening transfer and personal care routine.',
            'assistance_level': 'Moderate',
            'urgency': 'Normal',
            'exception_flag': 0,
            'staff_note': 'CONFIDENTIAL STAFF HANDOVER NOTE 9988'
        }
        summary = generate_operational_summary(event)
        self.assertNotIn("CONFIDENTIAL", summary)
        self.assertNotIn("9988", summary)

if __name__ == '__main__':
    unittest.main()
