import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.alert_service import refresh_system_notifications, get_active_notifications
from app.services.inventory_service import get_dashboard_metrics

class TestExpiryAlerts(unittest.TestCase):
    def test_metrics_alerts(self):
        metrics = get_dashboard_metrics()
        self.assertIn("near_expiry_count", metrics)
        self.assertIn("expired_count", metrics)
        self.assertIn("needs_attention", metrics)

    def test_notifications_generation(self):
        notifs = refresh_system_notifications()
        self.assertIsInstance(notifs, list)
        for n in notifs:
            self.assertIn("type", n)
            self.assertIn("severity", n)
            self.assertIn("message", n)

if __name__ == "__main__":
    unittest.main()
