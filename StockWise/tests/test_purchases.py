import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.purchase_service import list_suppliers, get_supplier, list_purchase_orders, get_purchase_order

class TestPurchases(unittest.TestCase):
    def test_list_suppliers(self):
        suppliers = list_suppliers()
        self.assertGreater(len(suppliers), 0)
        first = suppliers[0]
        self.assertIn("name", first)
        self.assertIn("lead_time_days", first)

    def test_list_purchase_orders(self):
        pos = list_purchase_orders()
        self.assertGreater(len(pos), 0)
        first = pos[0]
        self.assertIn("po_number", first)
        self.assertIn("total_cost", first)
        self.assertIn("items", first)

    def test_get_purchase_order(self):
        pos = list_purchase_orders()
        if pos:
            po = get_purchase_order(pos[0]["id"])
            self.assertIsNotNone(po)
            self.assertIn("supplier_name", po)

if __name__ == "__main__":
    unittest.main()
