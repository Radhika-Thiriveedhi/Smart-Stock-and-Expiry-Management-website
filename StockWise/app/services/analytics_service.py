from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from collections import defaultdict
from app.storage.json_store import load_data
from app.services.inventory_service import get_all_inventory_summary
from app.services.batch_service import list_batches
from app.utils.dates import parse_date, get_current_date

def get_daily_financial_ledger(days_back: int = 14) -> Dict[str, Any]:
    """
    Computes a comprehensive day-by-day financial breakdown:
    - Daily Money In (Sales Revenue)
    - Wholesale Product Cost (COGS)
    - Daily Profit (Gross Profit & Margin %)
    - Daily Loss (Expired, Damaged, or Discarded Stock)
    - Daily Net Profit/Loss (Gross Profit - Wastage Loss)
    - Orders & Waste Incidents
    """
    sales = load_data("sales", default=[])
    waste_records = load_data("waste_records", default=[])
    today = get_current_date()
    yesterday = today - timedelta(days=1)
    month_start = date(today.year, today.month, 1)

    # 1. Establish date keys (default last N days plus any active dates)
    date_keys_set = set((today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days_back))
    
    for s in sales:
        s_dt = parse_date(s.get("created_at"))
        if s_dt:
            date_keys_set.add(s_dt.strftime("%Y-%m-%d"))
            
    for w in waste_records:
        w_dt = parse_date(w.get("created_at"))
        if w_dt:
            date_keys_set.add(w_dt.strftime("%Y-%m-%d"))

    date_keys = sorted(list(date_keys_set), reverse=True)

    daily_map = {}
    for d_str in date_keys:
        d_obj = parse_date(d_str)
        is_today = (d_obj == today)
        is_yesterday = (d_obj == yesterday)
        
        if is_today:
            label = "Today"
        elif is_yesterday:
            label = "Yesterday"
        else:
            label = d_obj.strftime("%a, %b %d") if d_obj else d_str
            
        daily_map[d_str] = {
            "date": d_str,
            "date_obj": d_obj,
            "label": label,
            "formatted_date": d_obj.strftime("%d %b %Y") if d_obj else d_str,
            "is_today": is_today,
            "is_yesterday": is_yesterday,
            "revenue": 0.0,
            "cogs": 0.0,
            "gross_profit": 0.0,
            "loss": 0.0,
            "waste_units": 0,
            "waste_reasons": defaultdict(int),
            "orders": 0,
            "items_sold": 0
        }

    # Aggregate Sales
    for s in sales:
        s_dt = parse_date(s.get("created_at"))
        if not s_dt:
            continue
        d_str = s_dt.strftime("%Y-%m-%d")
        if d_str in daily_map:
            rev = float(s.get("total_amount", 0.0))
            cost = float(s.get("total_cost", 0.0))
            prof = float(s.get("gross_profit", rev - cost))
            
            daily_map[d_str]["revenue"] += rev
            daily_map[d_str]["cogs"] += cost
            daily_map[d_str]["gross_profit"] += prof
            daily_map[d_str]["orders"] += 1
            for item in s.get("items", []):
                daily_map[d_str]["items_sold"] += int(item.get("quantity", 0))

    # Aggregate Wastage / Loss
    for w in waste_records:
        w_dt = parse_date(w.get("created_at"))
        if not w_dt:
            continue
        d_str = w_dt.strftime("%Y-%m-%d")
        if d_str in daily_map:
            loss = float(w.get("total_loss", 0.0))
            qty = int(w.get("quantity", 0))
            reason = w.get("reason", "OTHER").replace("_", " ").title()
            
            daily_map[d_str]["loss"] += loss
            daily_map[d_str]["waste_units"] += qty
            daily_map[d_str]["waste_reasons"][reason] += qty

    today_str = today.strftime("%Y-%m-%d")
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    
    ledger = []
    for d_str in date_keys:
        item = daily_map[d_str]
        rev = round(item["revenue"], 2)
        cogs = round(item["cogs"], 2)
        g_prof = round(item["gross_profit"], 2)
        loss = round(item["loss"], 2)
        net = round(g_prof - loss, 2)
        margin = round((g_prof / rev * 100), 1) if rev > 0 else 0.0
        
        reasons_summary = ", ".join([f"{r}: {q}" for r, q in item["waste_reasons"].items()]) if item["waste_reasons"] else "None"
        
        if rev > 0 or loss > 0:
            if net > 0:
                status = "PROFIT"
            elif net < 0:
                status = "LOSS"
            else:
                status = "BREAK_EVEN"
        else:
            status = "IDLE"
            
        ledger.append({
            "date": d_str,
            "label": item["label"],
            "formatted_date": item["formatted_date"],
            "is_today": item["is_today"],
            "is_yesterday": item["is_yesterday"],
            "revenue": rev,
            "cogs": cogs,
            "gross_profit": g_prof,
            "margin_pct": margin,
            "loss": loss,
            "waste_units": item["waste_units"],
            "waste_reasons_summary": reasons_summary,
            "net_profit": net,
            "orders": item["orders"],
            "items_sold": item["items_sold"],
            "status": status
        })

    today_item = daily_map.get(today_str, {})
    yesterday_item = daily_map.get(yesterday_str, {})

    today_rev = round(today_item.get("revenue", 0.0), 2)
    today_cogs = round(today_item.get("cogs", 0.0), 2)
    today_profit = round(today_item.get("gross_profit", 0.0), 2)
    today_loss = round(today_item.get("loss", 0.0), 2)
    today_net = round(today_profit - today_loss, 2)
    today_margin = round((today_profit / today_rev * 100), 1) if today_rev > 0 else 0.0

    yesterday_rev = round(yesterday_item.get("revenue", 0.0), 2)
    yesterday_cogs = round(yesterday_item.get("cogs", 0.0), 2)
    yesterday_profit = round(yesterday_item.get("gross_profit", 0.0), 2)
    yesterday_loss = round(yesterday_item.get("loss", 0.0), 2)
    yesterday_net = round(yesterday_profit - yesterday_loss, 2)

    # Month to date
    month_items = [v for k, v in daily_map.items() if v["date_obj"] and v["date_obj"] >= month_start]
    month_rev = round(sum(v["revenue"] for v in month_items), 2)
    month_cogs = round(sum(v["cogs"] for v in month_items), 2)
    month_prof = round(sum(v["gross_profit"] for v in month_items), 2)
    month_loss = round(sum(v["loss"] for v in month_items), 2)
    month_net = round(month_prof - month_loss, 2)
    month_orders = sum(v["orders"] for v in month_items)

    return {
        "ledger": ledger,
        "today": {
            "revenue": today_rev,
            "cogs": today_cogs,
            "gross_profit": today_profit,
            "loss": today_loss,
            "net_profit": today_net,
            "orders": today_item.get("orders", 0),
            "items_sold": today_item.get("items_sold", 0),
            "waste_units": today_item.get("waste_units", 0),
            "margin_pct": today_margin,
            "status": "PROFIT" if today_net > 0 else ("LOSS" if today_net < 0 else "IDLE")
        },
        "yesterday": {
            "revenue": yesterday_rev,
            "cogs": yesterday_cogs,
            "gross_profit": yesterday_profit,
            "loss": yesterday_loss,
            "net_profit": yesterday_net,
            "orders": yesterday_item.get("orders", 0),
            "waste_units": yesterday_item.get("waste_units", 0)
        },
        "month": {
            "revenue": month_rev,
            "cogs": month_cogs,
            "gross_profit": month_prof,
            "loss": month_loss,
            "net_profit": month_net,
            "orders": month_orders
        }
    }

def get_sales_analytics() -> Dict[str, Any]:
    sales = load_data("sales", default=[])
    today = get_current_date()
    week_start = today - timedelta(days=today.weekday())
    month_start = date(today.year, today.month, 1)
    
    today_sales = 0.0
    today_profit = 0.0
    today_orders = 0
    
    week_sales = 0.0
    week_profit = 0.0
    week_orders = 0
    
    month_sales = 0.0
    month_profit = 0.0
    month_orders = 0
    
    total_sales = 0.0
    total_profit = 0.0
    
    # Daily breakdown for chart/table (last 7 days)
    last_7_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    daily_trend = {d.strftime("%Y-%m-%d"): {"sales": 0.0, "profit": 0.0, "orders": 0} for d in last_7_days}
    
    # Product sales aggregation for fast/slow moving
    product_sales_counter = defaultdict(lambda: {"quantity": 0, "revenue": 0.0, "name": ""})
    
    for s in sales:
        sale_dt = parse_date(s.get("created_at"))
        amt = float(s.get("total_amount", 0.0))
        profit = float(s.get("gross_profit", 0.0))
        
        total_sales += amt
        total_profit += profit
        
        if sale_dt:
            if sale_dt == today:
                today_sales += amt
                today_profit += profit
                today_orders += 1
            if sale_dt >= week_start:
                week_sales += amt
                week_profit += profit
                week_orders += 1
            if sale_dt >= month_start:
                month_sales += amt
                month_profit += profit
                month_orders += 1
                
            d_str = sale_dt.strftime("%Y-%m-%d")
            if d_str in daily_trend:
                daily_trend[d_str]["sales"] += amt
                daily_trend[d_str]["profit"] += profit
                daily_trend[d_str]["orders"] += 1
                
        for it in s.get("items", []):
            pid = it.get("product_id")
            product_sales_counter[pid]["quantity"] += it.get("quantity", 0)
            product_sales_counter[pid]["revenue"] += it.get("subtotal", 0.0)
            product_sales_counter[pid]["name"] = it.get("product_name", pid)
            
    # Fast moving items
    fast_moving = sorted(
        [{"product_id": k, **v} for k, v in product_sales_counter.items()],
        key=lambda x: x["quantity"],
        reverse=True
    )
    
    # Slow moving items (items with active stock but zero/low sales)
    inventory = get_all_inventory_summary(active_only=True)
    slow_moving = []
    for inv in inventory:
        sales_info = product_sales_counter.get(inv["product_id"], {"quantity": 0, "revenue": 0.0})
        if sales_info["quantity"] <= 2 and inv["total_quantity"] > 0:
            slow_moving.append({
                "product_id": inv["product_id"],
                "name": inv["name"],
                "sku": inv["sku"],
                "stock": inv["total_quantity"],
                "cost_value": inv["cost_value"],
                "units_sold": sales_info["quantity"]
            })
    slow_moving.sort(key=lambda x: x["stock"], reverse=True)
    
    daily_pnl = get_daily_financial_ledger(days_back=14)
    
    return {
        "today_sales": round(today_sales, 2),
        "today_profit": round(today_profit, 2),
        "today_orders": today_orders,
        "week_sales": round(week_sales, 2),
        "week_profit": round(week_profit, 2),
        "week_orders": week_orders,
        "month_sales": round(month_sales, 2),
        "month_profit": round(month_profit, 2),
        "month_orders": month_orders,
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "daily_trend": [{"date": k, **v} for k, v in daily_trend.items()],
        "fast_moving": fast_moving[:5],
        "slow_moving": slow_moving[:5],
        "daily_ledger": daily_pnl["ledger"],
        "today_pnl": daily_pnl["today"],
        "yesterday_pnl": daily_pnl["yesterday"],
        "month_pnl": daily_pnl["month"]
    }

def get_waste_analytics() -> Dict[str, Any]:
    waste_records = load_data("waste_records", default=[])
    today = get_current_date()
    total_waste_cost = sum(float(w.get("total_loss", 0.0)) for w in waste_records)
    total_waste_items = sum(int(w.get("quantity", 0)) for w in waste_records)
    
    today_waste_cost = 0.0
    today_waste_items = 0
    
    by_reason = defaultdict(lambda: {"cost": 0.0, "quantity": 0, "count": 0})
    for w in waste_records:
        r = w.get("reason", "OTHER")
        loss = float(w.get("total_loss", 0.0))
        qty = int(w.get("quantity", 0))
        
        by_reason[r]["cost"] += loss
        by_reason[r]["quantity"] += qty
        by_reason[r]["count"] += 1
        
        w_dt = parse_date(w.get("created_at"))
        if w_dt == today:
            today_waste_cost += loss
            today_waste_items += qty
        
    return {
        "total_waste_cost": round(total_waste_cost, 2),
        "total_waste_items": total_waste_items,
        "today_waste_cost": round(today_waste_cost, 2),
        "today_waste_items": today_waste_items,
        "records_count": len(waste_records),
        "by_reason": [{"reason": k, **v} for k, v in by_reason.items()],
        "recent_waste": sorted(waste_records, key=lambda x: x.get("created_at", ""), reverse=True)[:10]
    }

def get_inventory_valuation_analytics() -> Dict[str, Any]:
    batches = list_batches(hide_depleted=True)
    total_units = sum(b.get("quantity_remaining", 0) for b in batches)
    total_cost_val = sum(b.get("quantity_remaining", 0) * b.get("unit_cost", 0.0) for b in batches)
    
    # Value at risk by expiry window
    expired_cost = sum(b.get("quantity_remaining", 0) * b.get("unit_cost", 0.0) for b in batches if b["expiry_status"] == "EXPIRED")
    critical_cost = sum(b.get("quantity_remaining", 0) * b.get("unit_cost", 0.0) for b in batches if b["expiry_status"] == "CRITICAL")
    warning_cost = sum(b.get("quantity_remaining", 0) * b.get("unit_cost", 0.0) for b in batches if b["expiry_status"] == "WARNING")
    healthy_cost = sum(b.get("quantity_remaining", 0) * b.get("unit_cost", 0.0) for b in batches if b["expiry_status"] in ["UPCOMING", "HEALTHY"])
    
    # Category stock breakdown
    from app.services.product_service import list_products, list_categories
    products = {p["id"]: p for p in list_products(active_only=False)}
    categories = {c["id"]: c["name"] for c in list_categories()}
    category_totals = defaultdict(float)
    
    for b in batches:
        p = products.get(b.get("product_id"), {})
        cat_name = categories.get(p.get("category_id"), "General")
        category_totals[cat_name] += b.get("quantity_remaining", 0) * b.get("unit_cost", 0.0)
        
    category_distribution = [{"name": k, "value": round(v, 2)} for k, v in category_totals.items() if v > 0]
    category_distribution.sort(key=lambda x: x["value"], reverse=True)
    
    return {
        "total_units": total_units,
        "total_cost_valuation": round(total_cost_val, 2),
        "expired_cost": round(expired_cost, 2),
        "critical_cost": round(critical_cost, 2),
        "warning_cost": round(warning_cost, 2),
        "healthy_cost": round(healthy_cost, 2),
        "at_risk_cost": round(critical_cost + warning_cost, 2),
        "category_distribution": category_distribution
    }

def get_shop_owner_command_center() -> Dict[str, Any]:
    """
    Unified master metrics for the Shop Owner:
    1. Daily Sales & Revenue (Today & Month)
    2. Profit vs. Loss (Gross profit vs. Waste write-offs)
    3. Expiry Days Countdown (Exact days left & expired items)
    4. Fast-Moving vs. Slow-Moving products
    5. Restock Needed (Low stock reorder list)
    """
    sales_info = get_sales_analytics()
    waste_info = get_waste_analytics()
    val_info = get_inventory_valuation_analytics()
    
    # Net profit after deducting waste write-offs
    total_sales = sales_info["total_sales"]
    gross_profit = sales_info["total_profit"]
    total_loss = waste_info["total_waste_cost"]
    net_earnings = round(gross_profit - total_loss, 2)
    
    # Batches sorted by exact days until expiry
    batches = list_batches(hide_depleted=True)
    expired_list = [b for b in batches if b["expiry_status"] == "EXPIRED"]
    critical_list = [b for b in batches if b["expiry_status"] == "CRITICAL"]
    warning_list = [b for b in batches if b["expiry_status"] == "WARNING"]
    healthy_list = [b for b in batches if b["expiry_status"] in ["UPCOMING", "HEALTHY"]]
    
    # Reorders
    from app.services.inventory_service import get_reorder_recommendations
    reorder_list = get_reorder_recommendations()
    
    return {
        # 1. Sales & Revenue
        "today_sales": sales_info["today_sales"],
        "today_profit": sales_info["today_profit"],
        "today_orders": sales_info["today_orders"],
        "month_sales": sales_info["month_sales"],
        "month_profit": sales_info["month_profit"],
        "month_orders": sales_info["month_orders"],
        "total_sales": total_sales,
        
        # Daily Detailed P&L
        "daily_ledger": sales_info["daily_ledger"],
        "today_pnl": sales_info["today_pnl"],
        "yesterday_pnl": sales_info["yesterday_pnl"],
        "month_pnl": sales_info["month_pnl"],
        "today_revenue": sales_info["today_pnl"]["revenue"],
        "today_cogs": sales_info["today_pnl"]["cogs"],
        "today_gross_profit": sales_info["today_pnl"]["gross_profit"],
        "today_loss": sales_info["today_pnl"]["loss"],
        "today_net_profit": sales_info["today_pnl"]["net_profit"],
        "today_waste_units": sales_info["today_pnl"]["waste_units"],
        "today_status": sales_info["today_pnl"]["status"],
        "today_margin_pct": sales_info["today_pnl"]["margin_pct"],
        
        # 2. Profit vs Loss
        "gross_profit": gross_profit,
        "total_loss": total_loss,
        "net_earnings": net_earnings,
        "inventory_value": val_info["total_cost_valuation"],
        "total_stock_units": val_info["total_units"],
        
        # 3. Expiry Countdown
        "expired_batches": expired_list,
        "critical_batches": critical_list,
        "warning_batches": warning_list,
        "healthy_batches": healthy_list,
        "expired_count": len(expired_list),
        "critical_count": len(critical_list),
        "warning_count": len(warning_list),
        "healthy_count": len(healthy_list),
        "at_risk_capital": val_info["at_risk_cost"],
        
        # 4. Fast vs Slow Moving
        "fast_moving": sales_info["fast_moving"],
        "slow_moving": sales_info["slow_moving"],
        
        # 5. Restock Needed
        "reorder_needed": reorder_list,
        "reorder_count": len(reorder_list),
        
        # Chart Data
        "daily_trend": sales_info["daily_trend"],
        "category_distribution": val_info["category_distribution"],
        "healthy_cost": val_info["healthy_cost"],
        "warning_cost": val_info["warning_cost"],
        "critical_cost": val_info["critical_cost"],
        "expired_cost": val_info["expired_cost"]
    }



def get_supplier_performance() -> List[Dict[str, Any]]:
    suppliers = load_data("suppliers", default=[])
    pos = load_data("purchase_orders", default=[])
    
    supplier_stats = {s["id"]: {
        "id": s["id"],
        "name": s["name"],
        "lead_time_days": s.get("lead_time_days", 0),
        "total_orders": 0,
        "completed_orders": 0,
        "total_spent": 0.0
    } for s in suppliers}
    
    for po in pos:
        sid = po.get("supplier_id")
        if sid in supplier_stats:
            supplier_stats[sid]["total_orders"] += 1
            if po.get("status") == "COMPLETED":
                supplier_stats[sid]["completed_orders"] += 1
            supplier_stats[sid]["total_spent"] += float(po.get("total_cost", 0.0))
            
    return list(supplier_stats.values())
