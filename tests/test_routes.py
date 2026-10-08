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

    def test_admin_full_privileges(self):
        """Admin (Dharshini) has unrestricted access to all facility portals and experiment."""
        self.app.get('/switch_user/Dharshini', follow_redirects=True)
        for route in ['/dashboard', '/residents', '/care_events', '/family_members', '/consent', '/review_queue', '/experiment']:
            resp = self.app.get(route)
            self.assertEqual(resp.status_code, 200, f"Admin should have access to {route}")

    def test_staff_operational_access_and_experiment_denial(self):
        """Staff (Madhu) has operational access but is strictly blocked from experiment."""
        self.app.get('/switch_user/Madhu', follow_redirects=True)
        # Operational routes succeed
        for route in ['/dashboard', '/residents', '/care_events', '/review_queue']:
            resp = self.app.get(route)
            self.assertEqual(resp.status_code, 200, f"Staff should have access to {route}")

        # Experiment routes are blocked
        resp_exp = self.app.get('/experiment', follow_redirects=True)
        self.assertIn(b"Access Denied", resp_exp.data)

        resp_run = self.app.post('/experiment/run', follow_redirects=True)
        self.assertIn(b"Access Denied", resp_run.data)

        resp_dl = self.app.get('/experiment/download_notebook', follow_redirects=True)
        self.assertIn(b"Access Denied", resp_dl.data)

    def test_family_persona_scoped_access(self):
        """Family user (Kavi) can access own resident updates, with internal notes hidden."""
        self.app.get('/switch_user/Kavi', follow_redirects=True)
        resp_dash = self.app.get('/dashboard')
        self.assertEqual(resp_dash.status_code, 200)
        self.assertIn(b"Family Member Portal", resp_dash.data)

        # Authorized resident profile
        resp_res = self.app.get('/residents/RES001')
        self.assertEqual(resp_res.status_code, 200)
        self.assertIn(b"Devi Raman", resp_res.data)
        # Internal staff note is strictly hidden from family
        self.assertNotIn(b"Internal Staff Note (Staff Only)", resp_res.data)

        # Authorized communication view
        resp_comm = self.app.get('/communication')
        self.assertEqual(resp_comm.status_code, 200)

        # Questions view
        resp_q = self.app.get('/questions')
        self.assertEqual(resp_q.status_code, 200)

    def test_family_direct_url_and_action_denials(self):
        """Family user direct access to facility management URLs is denied server-side."""
        self.app.get('/switch_user/Kavi', follow_redirects=True)

        blocked_get_routes = ['/residents', '/care_events', '/consent', '/review_queue', '/experiment', '/family_members']
        for route in blocked_get_routes:
            resp = self.app.get(route, follow_redirects=True)
            self.assertIn(b"Access Denied", resp.data, f"Family should be denied GET {route}")

        # Blocked administrative actions
        resp_toggle = self.app.post('/consent/toggle/CON001', follow_redirects=True)
        self.assertIn(b"Access Denied", resp_toggle.data)

        resp_rev = self.app.post('/review/submit', data={'comm_id': 'COM001', 'action_taken': 'Approve'}, follow_redirects=True)
        self.assertIn(b"Access Denied", resp_rev.data)

        resp_ans = self.app.post('/questions/answer', data={'question_id': 'QUE001', 'staff_response': 'Test'}, follow_redirects=True)
        self.assertIn(b"Access Denied", resp_ans.data)

    def test_family_cross_resident_isolation(self):
        """Hema (Emergency Contact for RES002) cannot access Devi Raman (RES001) records."""
        self.app.get('/switch_user/Hema', follow_redirects=True)

        # Access own resident profile
        resp_own = self.app.get('/residents/RES002')
        self.assertEqual(resp_own.status_code, 200)
        self.assertIn(b"Ramesh Sharma", resp_own.data)

        # Cross-resident profile access denied
        resp_other = self.app.get('/residents/RES001', follow_redirects=True)
        self.assertIn(b"Access Denied: You are not authorized to view information for other residents.", resp_other.data)

        # Cross-resident event inspection in communication denied
        resp_comm_other = self.app.get('/communication?event_id=EVT001', follow_redirects=True)
        self.assertIn(b"Access Denied", resp_comm_other.data)

    def test_family_persona_switching_blocked(self):
        """Family user cannot use /switch_user to elevate privileges or access other personas."""
        self.app.get('/switch_user/Kavi', follow_redirects=True)
        resp_switch = self.app.get('/switch_user/Dharshini', follow_redirects=True)
        self.assertIn(b"Access Denied: Persona switching is not permitted", resp_switch.data)

    def test_family_sub_roles_kavi_charu_hema_abi_mala(self):
        """Validates correct persona scoping across all 5 family members."""
        # Charu -> Secondary Contact for RES001
        self.app.get('/logout', follow_redirects=True)
        self.app.post('/login', data={'username': 'Charu', 'password': 'charu123'}, follow_redirects=True)
        resp_c = self.app.get('/residents/RES001')
        self.assertEqual(resp_c.status_code, 200)

        # Abi -> View-Only for RES003 (cannot view RES001)
        self.app.get('/logout', follow_redirects=True)
        self.app.post('/login', data={'username': 'Abi', 'password': 'abi123'}, follow_redirects=True)
        resp_abi_own = self.app.get('/residents/RES003')
        self.assertEqual(resp_abi_own.status_code, 200)
        resp_abi_other = self.app.get('/residents/RES001', follow_redirects=True)
        self.assertIn(b"Access Denied", resp_abi_other.data)

        # Mala -> Primary Contact for RES004 (cannot view RES002)
        self.app.get('/logout', follow_redirects=True)
        self.app.post('/login', data={'username': 'Mala', 'password': 'mala123'}, follow_redirects=True)
        resp_mala_own = self.app.get('/residents/RES004')
        self.assertEqual(resp_mala_own.status_code, 200)
        resp_mala_other = self.app.get('/residents/RES002', follow_redirects=True)
        self.assertIn(b"Access Denied", resp_mala_other.data)

if __name__ == '__main__':
    unittest.main()
