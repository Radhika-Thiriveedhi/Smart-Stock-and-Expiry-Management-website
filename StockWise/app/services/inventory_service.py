from typing import List, Dict, Any, Optional
from app.storage.json_store import load_data
from app.services.product_service import list_products, get_product
from app.services.batch_service import list_batches

def get_product_stock_summary(product_id: str) -> Dict[str, Any]:
    prod = get_product(product_id)
    if not prod:
        return {}
        
    batches = list_batches(product_id=product_id, hide_depleted=True)
    
    total_quantity = sum(b.get("quantity_remaining", 0) for b in batches)
    saleable_quantity = sum(b.get("quantity_remaining", 0) for b in batches if b.get("expiry_status") != "EXPIRED")
    expired_quantity = total_quantity - saleable_quantity
    
    reorder_level = prod.get("reorder_level", 10)
    is_low_stock = saleable_quantity <= reorder_level
    is_out_of_stock = saleable_quantity == 0
    
    return {
        "product_id": product_id,
        "product_name": prod.get("name"),
        "sku": prod.get("sku"),
        "unit": prod.get("unit"),
        "selling_price": prod.get("selling_price"),
        "category_name": prod.get("category_name"),
        "reorder_level": reorder_level,
        "total_quantity": total_quantity,
        "saleable_quantity": saleable_quantity,
        "expired_quantity": expired_quantity,
        "is_low_stock": is_low_stock,
        "is_out_of_stock": is_out_of_stock,
        "active_batches_count": len(batches)
    }

def get_all_inventory_summary(active_only: bool = True) -> List[Dict[str, Any]]:
    products = list_products(active_only=active_only)
    batches = list_batches(hide_depleted=True)
    
    # Group batches by product_id
    batch_map = {}
    for b in batches:
        pid = b.get("product_id")
        if pid not in batch_map:
            batch_map[pid] = []
        batch_map[pid].append(b)
        
    summaries = []
    for p in products:
        p_batches = batch_map.get(p["id"], [])
        total_qty = sum(b.get("quantity_remaining", 0) for b in p_batches)
        saleable_qty = sum(b.get("quantity_remaining", 0) for b in p_batches if b.get("expiry_status") != "EXPIRED")
        expired_qty = total_qty - saleable_qty
        
        reorder_level = p.get("reorder_level", 10)
        is_low_stock = saleable_qty <= reorder_level
        is_out_of_stock = saleable_qty == 0
        
        # Calculate valuation for this product
        cost_value = sum(b.get("quantity_remaining", 0) * b.get("unit_cost", 0.0) for b in p_batches)
        retail_value = saleable_qty * p.get("selling_price", 0.0)
        
        summaries.append({
            "product_id": p["id"],
            "name": p["name"],
            "sku": p["sku"],
            "unit": p.get("unit", "units"),
            "category_name": p.get("category_name", "Uncategorized"),
            "category_id": p.get("category_id"),
            "selling_price": p.get("selling_price", 0.0),
            "reorder_level": reorder_level,
            "total_quantity": total_qty,
            "saleable_quantity": saleable_qty,
            "expired_quantity": expired_qty,
            "is_low_stock": is_low_stock,
            "is_out_of_stock": is_out_of_stock,
            "cost_value": round(cost_value, 2),
            "retail_value": round(retail_value, 2),
            "batches_count": len(p_batches)
        })
        
    return summaries

def get_reorder_recommendations() -> List[Dict[str, Any]]:
    summaries = get_all_inventory_summary(active_only=True)
    recommendations = []
    
    for item in summaries:
        if item["is_low_stock"]:
            deficit = item["reorder_level"] - item["saleable_quantity"]
            # Target stock is twice the reorder level
            suggested_order = max(deficit + item["reorder_level"], 10)
            recommendations.append({
                **item,
                "suggested_order": suggested_order,
                "urgency": "CRITICAL" if item["is_out_of_stock"] else "WARNING"
            })
            
    return sorted(recommendations, key=lambda x: (0 if x["urgency"] == "CRITICAL" else 1, x["saleable_quantity"]))

def get_dashboard_metrics() -> Dict[str, Any]:
    summaries = get_all_inventory_summary(active_only=True)
    batches = list_batches(hide_depleted=True)
    
    total_products = len(summaries)
    low_stock_items = [s for s in summaries if s["is_low_stock"]]
    low_stock_count = len(low_stock_items)
    
    # Expiry categorization
    near_expiry_batches = [b for b in batches if b["expiry_status"] in ["CRITICAL", "WARNING"]]
    expired_batches = [b for b in batches if b["expiry_status"] == "EXPIRED"]
    
    # Build needs attention list (curated high-priority items)
    needs_attention = []
    
    # 1. Expired batches needing disposal
    for b in expired_batches:
        needs_attention.append({
            "type": "EXPIRED",
            "title": f"{b['product_name']} ({b['product_sku']})",
            "subtitle": f"Batch {b['id']} expired on {b['expiry_date']} ({b['quantity_remaining']} {b['product_unit']} remaining)",
            "tag": "Expired",
            "badge_class": "badge-danger",
            "action_url": f"/inventory/batches",
            "batch_id": b["id"]
        })
        
    # 2. Near expiry batches
    for b in near_expiry_batches:
        needs_attention.append({
            "type": "NEAR_EXPIRY",
            "title": f"{b['product_name']} ({b['product_sku']})",
            "subtitle": f"Batch {b['id']} {b['expiry_label']} ({b['quantity_remaining']} {b['product_unit']} remaining)",
            "tag": "Near expiry",
            "badge_class": "badge-warning",
            "action_url": f"/inventory/batches",
            "batch_id": b["id"]
        })
        
    # 3. Low-stock products
    for p in low_stock_items:
        needs_attention.append({
            "type": "LOW_STOCK",
            "title": f"{p['name']} ({p['sku']})",
            "subtitle": f"Only {p['saleable_quantity']} {p['unit']} left (reorder at {p['reorder_level']})",
            "tag": "Low stock",
            "badge_class": "badge-danger" if p["is_out_of_stock"] else "badge-warning",
            "action_url": f"/inventory/reorders",
            "product_id": p["product_id"]
        })

    total_cost_valuation = sum(s["cost_value"] for s in summaries)
    total_retail_valuation = sum(s["retail_value"] for s in summaries)
    
    return {
        "total_products": total_products,
        "low_stock_count": low_stock_count,
        "near_expiry_count": len(near_expiry_batches),
        "expired_count": len(expired_batches),
        "needs_attention": needs_attention,
        "total_cost_valuation": round(total_cost_valuation, 2),
        "total_retail_valuation": round(total_retail_valuation, 2)
    }
