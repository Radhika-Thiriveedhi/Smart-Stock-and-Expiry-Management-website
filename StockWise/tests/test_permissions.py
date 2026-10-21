import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app

class TestPermissions(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_unauthenticated_redirects_to_login(self):
        # Accessing employee dashboard without session
        resp = self.client.get("/employee/dashboard", follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login", resp.headers.get("Location", ""))

    def test_employee_cannot_access_owner_dashboard(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = "USR-003"
            sess["username"] = "employee"
            sess["role"] = "employee"

        resp = self.client.get("/owner/dashboard")
        self.assertEqual(resp.status_code, 403)

    def test_employee_cannot_access_inventory_dashboard(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = "USR-003"
            sess["username"] = "employee"
            sess["role"] = "employee"

        resp = self.client.get("/inventory/dashboard")
        self.assertEqual(resp.status_code, 403)

    def test_manager_cannot_access_owner_staff(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = "USR-002"
            sess["username"] = "manager"
            sess["role"] = "manager"

        resp = self.client.get("/owner/staff")
        self.assertEqual(resp.status_code, 403)

    def test_owner_can_access_owner_dashboard(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = "USR-001"
            sess["username"] = "owner"
            sess["role"] = "owner"

        resp = self.client.get("/owner/dashboard")
        self.assertEqual(resp.status_code, 200)

if __name__ == "__main__":
    unittest.main()
