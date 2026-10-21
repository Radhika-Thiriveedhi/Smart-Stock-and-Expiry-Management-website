import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.batch_service import list_batches, get_batch, get_batches_for_sale_fefo
from app.utils.dates import calculate_expiry_status, parse_date
from datetime import date, timedelta

class TestBatches(unittest.TestCase):
    def test_list_batches(self):
        batches = list_batches()
        self.assertGreater(len(batches), 0)
        first = batches[0]
        self.assertIn("expiry_date", first)
        self.assertIn("quantity_remaining", first)
        self.assertIn("expiry_status", first)

    def test_fefo_sort_order(self):
        # Product PRD-001 has multiple batches
        batches = list_batches(product_id="PRD-001", hide_depleted=True)
        if len(batches) >= 2:
            d1 = parse_date(batches[0]["expiry_date"])
            d2 = parse_date(batches[1]["expiry_date"])
            self.assertLessEqual(d1, d2)

    def test_fefo_allocation(self):
        allocations, shortfall = get_batches_for_sale_fefo("PRD-001", 10)
        self.assertEqual(shortfall, 0)
        self.assertGreater(len(allocations), 0)
        total_allocated = sum(a["quantity"] for a in allocations)
        self.assertEqual(total_allocated, 10)

    def test_expiry_status_logic(self):
        today = date.today()
        
        past = today - timedelta(days=5)
        res_past = calculate_expiry_status(past.isoformat(), ref_date=today)
        self.assertEqual(res_past["status"], "EXPIRED")

        crit = today + timedelta(days=2)
        res_crit = calculate_expiry_status(crit.isoformat(), ref_date=today)
        self.assertEqual(res_crit["status"], "CRITICAL")

        warn = today + timedelta(days=6)
        res_warn = calculate_expiry_status(warn.isoformat(), ref_date=today)
        self.assertEqual(res_warn["status"], "WARNING")

        good = today + timedelta(days=60)
        res_good = calculate_expiry_status(good.isoformat(), ref_date=today)
        self.assertEqual(res_good["status"], "HEALTHY")

if __name__ == "__main__":
    unittest.main()
