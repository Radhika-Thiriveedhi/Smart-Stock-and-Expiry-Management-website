from datetime import datetime
from typing import List, Dict, Any
from app.storage.json_store import load_data, insert_record, update_record
from app.services.inventory_service import get_all_inventory_summary
from app.services.batch_service import list_batches

def get_active_notifications() -> List[Dict[str, Any]]:
    return load_data("notifications", default=[])

def mark_notification_read(notification_id: str) -> bool:
    res = update_record("notifications", notification_id, {"read": True})
    return res is not None

def mark_all_notifications_read() -> bool:
    notifs = load_data("notifications", default=[])
    for n in notifs:
        n["read"] = True
    from app.storage.json_store import save_data
    return save_data("notifications", notifs)

def refresh_system_notifications() -> List[Dict[str, Any]]:
    """
    Scan batches and inventory levels to dynamically regenerate active alerts.
    """
    batches = list_batches(hide_depleted=True)
    summaries = get_all_inventory_summary(active_only=True)
    
    current_notifs = []
    
    # 1. Expired batches
    for b in batches:
        if b["expiry_status"] == "EXPIRED":
            current_notifs.append({
                "type": "EXPIRED",
                "title": f"Batch Expired: {b['product_name']}",
                "message": f"Batch {b['id']} expired on {b['expiry_date']} ({b['quantity_remaining']} {b['product_unit']} left).",
                "severity": "danger",
                "created_at": datetime.now().isoformat(),
                "read": False,
                "target_id": b["id"]
            })
            
    # 2. Critical & near expiry batches
    for b in batches:
        if b["expiry_status"] == "CRITICAL":
            current_notifs.append({
                "type": "EXPIRY_WARNING",
                "title": f"Expiring Soon: {b['product_name']}",
                "message": f"Batch {b['id']} {b['expiry_label']} ({b['quantity_remaining']} {b['product_unit']} left).",
                "severity": "danger",
                "created_at": datetime.now().isoformat(),
                "read": False,
                "target_id": b["id"]
            })
        elif b["expiry_status"] == "WARNING":
            current_notifs.append({
                "type": "EXPIRY_WARNING",
                "title": f"Near Expiry: {b['product_name']}",
                "message": f"Batch {b['id']} {b['expiry_label']}.",
                "severity": "warning",
                "created_at": datetime.now().isoformat(),
                "read": False,
                "target_id": b["id"]
            })
            
    # 3. Low stock alerts
    for s in summaries:
        if s["is_low_stock"]:
            current_notifs.append({
                "type": "LOW_STOCK",
                "title": f"Low Stock: {s['name']}",
                "message": f"Remaining {s['saleable_quantity']} {s['unit']}, below reorder level ({s['reorder_level']}).",
                "severity": "danger" if s["is_out_of_stock"] else "warning",
                "created_at": datetime.now().isoformat(),
                "read": False,
                "target_id": s["product_id"]
            })
            
    # Save active alerts
    from app.storage.json_store import save_data
    save_data("notifications", current_notifs)
    return current_notifs
