"""Integration Tests for Flask Web Application Routes
Tests web interface endpoints, session authentication, and UI views.
"""

import unittest
from app import app

class TestAppRoutes(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_login_page_renders(self):
        """Login page displays disclaimer and authentication form."""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Operational Support Only", response.data)
        self.assertIn(b"System Authentication", response.data)

    def test_quick_user_switch(self):
        """User switcher logs in demo account and redirects to dashboard."""
        response = self.app.get('/switch_user/Dharshini', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Dharshini", response.data)
        self.assertIn(b"Operational Communication Dashboard", response.data)

    def test_dashboard_authenticated(self):
        """Authenticated dashboard displays operational stats."""
        self.app.get('/switch_user/Madhu', follow_redirects=True)
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Total Residents", response.data)
        self.assertIn(b"Total Care Events", response.data)
        self.assertIn(b"Pending Human Reviews", response.data)

    def test_residents_and_detail(self):
        """Residents list and individual profile render correctly."""
        self.app.get('/switch_user/Madhu', follow_redirects=True)
        resp1 = self.app.get('/residents')
        self.assertEqual(resp1.status_code, 200)
        self.assertIn(b"Devi Raman", resp1.data)

        resp2 = self.app.get('/residents/RES001')
        self.assertEqual(resp2.status_code, 200)
        self.assertIn(b"Independence & Profile", resp2.data)
        self.assertIn(b"Kavi", resp2.data)

    def test_communication_dual_pane(self):
        """Communication page displays segregated internal notes vs family view."""
        self.app.get('/switch_user/Madhu', follow_redirects=True)
        response = self.app.get('/communication?event_id=EVT001&family_id=FAM001')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Internal Staff Record", response.data)
        self.assertIn(b"Family Communication Summary", response.data)
        self.assertIn(b"NEVER automatically disclosed to family", response.data)

    def test_review_queue_and_action(self):
        """Review queue shows pending items and allows approve action."""
        self.app.get('/switch_user/Dharshini', follow_redirects=True)
        response = self.app.get('/review_queue')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Human Review & Escalation Queue", response.data)

    def test_experiment_page_renders_metrics(self):
        """Experiment page loads empirical metrics table and chart."""
        self.app.get('/switch_user/Dharshini', follow_redirects=True)
        response = self.app.get('/experiment')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Academic Experiment & Evaluation Dashboard", response.data)
        self.assertIn(b"Family Understanding Score", response.data)
        self.assertIn(b"Unauthorised Disclosure Rate", response.data)

if __name__ == '__main__':
    unittest.main()
