import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.product_service import list_products, get_product
from app.services.inventory_service import get_product_stock_summary, get_all_inventory_summary, get_reorder_recommendations

class TestInventory(unittest.TestCase):
    def test_list_products(self):
        prods = list_products()
        self.assertGreater(len(prods), 0)
        first = prods[0]
        self.assertIn("sku", first)
        self.assertIn("selling_price", first)

    def test_product_stock_summary(self):
        prods = list_products()
        if prods:
            pid = prods[0]["id"]
            summary = get_product_stock_summary(pid)
            self.assertEqual(summary["product_id"], pid)
            self.assertIn("total_quantity", summary)
            self.assertIn("saleable_quantity", summary)
            self.assertIn("is_low_stock", summary)

    def test_reorder_recommendations(self):
        reorders = get_reorder_recommendations()
        self.assertIsInstance(reorders, list)
        for r in reorders:
            self.assertTrue(r["is_low_stock"])
            self.assertGreaterEqual(r["suggested_order"], 1)

if __name__ == "__main__":
    unittest.main()
