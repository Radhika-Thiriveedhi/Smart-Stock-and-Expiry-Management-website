import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.stock_movement_service import list_movements, record_damage_or_waste, record_delivery
from app.services.batch_service import list_batches, get_batch

class TestStockMovements(unittest.TestCase):
    def test_list_movements(self):
        movs = list_movements(limit=10)
        self.assertGreater(len(movs), 0)
        first = movs[0]
        self.assertIn("type", first)
        self.assertIn("quantity", first)
        self.assertIn("batch_id", first)

    def test_prevent_excess_waste_deduction(self):
        batches = list_batches(hide_depleted=True)
        if batches:
            b = batches[0]
            excess_qty = b["quantity_remaining"] + 999
            with self.assertRaises(ValueError):
                record_damage_or_waste(
                    batch_id=b["id"],
                    quantity=excess_qty,
                    reason="DAMAGED_IN_STORE",
                    notes="Test excess",
                    user_id="USR-003"
                )

    def test_record_delivery_success(self):
        batch = record_delivery(
            product_id="PRD-001",
            supplier_id="SUP-001",
            quantity=15,
            unit_cost=22.50,
            expiry_date="2026-12-31",
            user_id="USR-001",
            notes="Automated test delivery"
        )
        self.assertIsNotNone(batch)
        self.assertIn("id", batch)
        self.assertEqual(batch["product_id"], "PRD-001")
        self.assertEqual(batch["quantity_remaining"], 15)

if __name__ == "__main__":
    unittest.main()
