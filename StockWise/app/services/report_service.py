import csv
import io
from app.storage.json_store import load_data
from app.services.inventory_service import get_all_inventory_summary
from app.services.batch_service import list_batches

def generate_sales_csv() -> str:
    sales = load_data("sales", default=[])
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "Receipt No", "Date Time", "Cashier", "Payment Method", 
        "Product SKU", "Product Name", "Batch ID", "Quantity", 
        "Unit Price", "Unit Cost", "Subtotal", "Cost Subtotal", "Gross Profit"
    ])
    
    for s in sales:
        receipt_no = s.get("receipt_no", "")
        dt = s.get("created_at", "")
        cashier = s.get("cashier_name", "")
        payment = s.get("payment_method", "")
        
        for item in s.get("items", []):
            line_profit = round(item.get("subtotal", 0.0) - item.get("cost_subtotal", 0.0), 2)
            writer.writerow([
                receipt_no, dt, cashier, payment,
                item.get("product_sku", ""),
                item.get("product_name", ""),
                item.get("batch_id", ""),
                item.get("quantity", 0),
                item.get("unit_price", 0.0),
                item.get("unit_cost", 0.0),
                item.get("subtotal", 0.0),
                item.get("cost_subtotal", 0.0),
                line_profit
            ])
            
    return output.getvalue()

def generate_inventory_csv() -> str:
    summary = get_all_inventory_summary(active_only=False)
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "SKU", "Product Name", "Category", "Unit", "Selling Price", 
        "Reorder Level", "Total Stock", "Saleable Stock", "Expired Stock", 
        "Cost Valuation", "Retail Valuation", "Status"
    ])
    
    for item in summary:
        status = "Out of Stock" if item["is_out_of_stock"] else ("Low Stock" if item["is_low_stock"] else "Healthy")
        writer.writerow([
            item["sku"],
            item["name"],
            item["category_name"],
            item["unit"],
            item["selling_price"],
            item["reorder_level"],
            item["total_quantity"],
            item["saleable_quantity"],
            item["expired_quantity"],
            item["cost_value"],
            item["retail_value"],
            status
        ])
        
    return output.getvalue()

def generate_waste_csv() -> str:
    waste = load_data("waste_records", default=[])
    users = {u["id"]: u["name"] for u in load_data("users", default=[])}
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "Waste ID", "Date Time", "Product Name", "Batch ID", 
        "Quantity", "Unit Cost", "Total Loss", "Reason", "Reported By", "Notes"
    ])
    
    for w in waste:
        writer.writerow([
            w.get("id"),
            w.get("created_at"),
            w.get("product_name"),
            w.get("batch_id"),
            w.get("quantity"),
            w.get("unit_cost"),
            w.get("total_loss"),
            w.get("reason"),
            users.get(w.get("reported_by"), w.get("reported_by")),
            w.get("notes", "")
        ])
        
    return output.getvalue()

def generate_daily_pnl_csv() -> str:
    from app.services.analytics_service import get_daily_financial_ledger
    pnl = get_daily_financial_ledger(days_back=30)
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "Date", "Label", "Customer Orders", "Money In (Revenue)", 
        "Product Cost (COGS)", "Gross Profit", "Profit Margin %", 
        "Wastage Loss", "Loss Units", "Net Profit / Loss", "Financial Status"
    ])
    
    for row in pnl.get("ledger", []):
        writer.writerow([
            row.get("date"),
            row.get("label"),
            row.get("orders"),
            row.get("revenue"),
            row.get("cogs"),
            row.get("gross_profit"),
            f"{row.get('margin_pct')}%",
            row.get("loss"),
            row.get("waste_units"),
            row.get("net_profit"),
            row.get("status")
        ])
        
    return output.getvalue()

