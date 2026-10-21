import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.analytics_service import get_sales_analytics, get_waste_analytics, get_inventory_valuation_analytics, get_shop_owner_command_center

class TestAnalytics(unittest.TestCase):
    def test_sales_analytics(self):
        analytics = get_sales_analytics()
        self.assertIn("today_sales", analytics)
        self.assertIn("week_sales", analytics)
        self.assertIn("month_sales", analytics)
        self.assertIn("total_sales", analytics)
        self.assertIn("total_profit", analytics)
        self.assertIn("fast_moving", analytics)

    def test_waste_analytics(self):
        waste = get_waste_analytics()
        self.assertIn("total_waste_cost", waste)
        self.assertIn("total_waste_items", waste)
        self.assertIn("by_reason", waste)

    def test_valuation_analytics(self):
        val = get_inventory_valuation_analytics()
        self.assertIn("total_units", val)
        self.assertIn("total_cost_valuation", val)
        self.assertIn("at_risk_cost", val)
        self.assertIn("category_distribution", val)

    def test_shop_owner_command_center(self):
        cc = get_shop_owner_command_center()
        # Verify 5 Pillars of Shop Owner
        self.assertIn("today_sales", cc)
        self.assertIn("month_sales", cc)
        self.assertIn("gross_profit", cc)
        self.assertIn("total_loss", cc)
        self.assertIn("net_earnings", cc)
        self.assertIn("expired_batches", cc)
        self.assertIn("critical_batches", cc)
        self.assertIn("fast_moving", cc)
        self.assertIn("slow_moving", cc)
        self.assertIn("reorder_needed", cc)
        self.assertIn("daily_ledger", cc)
        self.assertIn("today_pnl", cc)
        self.assertIn("yesterday_pnl", cc)

    def test_daily_financial_ledger(self):
        from app.services.analytics_service import get_daily_financial_ledger
        pnl = get_daily_financial_ledger(days_back=7)
        self.assertIn("ledger", pnl)
        self.assertIn("today", pnl)
        self.assertIn("yesterday", pnl)
        self.assertIn("month", pnl)
        
        # Check today structure
        today_data = pnl["today"]
        self.assertIn("revenue", today_data)
        self.assertIn("gross_profit", today_data)
        self.assertIn("loss", today_data)
        self.assertIn("net_profit", today_data)

if __name__ == "__main__":
    unittest.main()

