import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.auth_service import authenticate, verify_password, get_user_by_username
from werkzeug.security import generate_password_hash

class TestAuth(unittest.TestCase):
    def test_verify_password_hash(self):
        pw = "secretPass123"
        hashed = generate_password_hash(pw)
        self.assertTrue(verify_password(hashed, pw))
        self.assertFalse(verify_password(hashed, "wrongPass"))

    def test_preseeded_users_exist(self):
        owner = get_user_by_username("owner")
        manager = get_user_by_username("manager")
        employee = get_user_by_username("employee")

        self.assertIsNotNone(owner)
        self.assertEqual(owner["role"], "owner")

        self.assertIsNotNone(manager)
        self.assertEqual(manager["role"], "manager")

        self.assertIsNotNone(employee)
        self.assertEqual(employee["role"], "employee")

    def test_invalid_login(self):
        user = authenticate("nonexistent_user", "invalid")
        self.assertIsNone(user)

if __name__ == "__main__":
    unittest.main()
