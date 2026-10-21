from datetime import datetime
from typing import List, Dict, Any, Optional
from app.storage.json_store import load_data, insert_record, update_record, find_by_id, log_audit
from app.services.product_service import get_product
from app.services.stock_movement_service import record_delivery

# Supplier operations
def list_suppliers(active_only: bool = False) -> List[Dict[str, Any]]:
    suppliers = load_data("suppliers", default=[])
    if active_only:
        suppliers = [s for s in suppliers if s.get("active", True)]
    return sorted(suppliers, key=lambda s: s.get("name", ""))

def get_supplier(supplier_id: str) -> Optional[Dict[str, Any]]:
    return find_by_id("suppliers", supplier_id)

def create_supplier(name: str, contact_person: str, phone: str, email: str, lead_time_days: int = 2) -> Dict[str, Any]:
    record = {
        "name": name.strip(),
        "contact_person": contact_person.strip(),
        "phone": phone.strip(),
        "email": email.strip(),
        "lead_time_days": int(lead_time_days),
        "active": True
    }
    return insert_record("suppliers", record, prefix="SUP")

def update_supplier(supplier_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return update_record("suppliers", supplier_id, updates)

# Purchase order operations
def list_purchase_orders(status: Optional[str] = None, supplier_id: Optional[str] = None) -> List[Dict[str, Any]]:
    pos = load_data("purchase_orders", default=[])
    suppliers = {s["id"]: s["name"] for s in load_data("suppliers", default=[])}
    users = {u["id"]: u["name"] for u in load_data("users", default=[])}
    
    results = []
    for po in pos:
        if status and po.get("status") != status:
            continue
        if supplier_id and po.get("supplier_id") != supplier_id:
            continue
            
        po_copy = dict(po)
        po_copy["supplier_name"] = suppliers.get(po.get("supplier_id"), "Unknown Supplier")
        po_copy["creator_name"] = users.get(po.get("created_by"), "Staff")
        
        # Calculate received percentage
        total_ordered = sum(item.get("quantity_ordered", 0) for item in po.get("items", []))
        total_received = sum(item.get("quantity_received", 0) for item in po.get("items", []))
        po_copy["total_ordered"] = total_ordered
        po_copy["total_received"] = total_received
        po_copy["progress_pct"] = round((total_received / total_ordered * 100) if total_ordered > 0 else 0)
        
        results.append(po_copy)
        
    return sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)

def get_purchase_order(po_id: str) -> Optional[Dict[str, Any]]:
    po = find_by_id("purchase_orders", po_id)
    if not po:
        return None
    suppliers = {s["id"]: s["name"] for s in load_data("suppliers", default=[])}
    users = {u["id"]: u["name"] for u in load_data("users", default=[])}
    
    po_copy = dict(po)
    po_copy["supplier_name"] = suppliers.get(po.get("supplier_id"), "Unknown Supplier")
    po_copy["creator_name"] = users.get(po.get("created_by"), "Staff")
    return po_copy

def create_purchase_order(supplier_id: str, 
                          expected_delivery_date: str, 
                          items_data: List[Dict[str, Any]], 
                          notes: str, 
                          user_id: str) -> Dict[str, Any]:
    if not items_data:
        raise ValueError("A purchase order must include at least one product.")
        
    supplier = get_supplier(supplier_id)
    if not supplier:
        raise ValueError("Invalid supplier selected.")
        
    po_items = []
    total_cost = 0.0
    
    for item in items_data:
        pid = item["product_id"]
        qty = int(item["quantity_ordered"])
        cost = float(item["unit_cost"])
        
        if qty <= 0:
            continue
        prod = get_product(pid)
        if not prod:
            continue
            
        subtotal = round(qty * cost, 2)
        total_cost += subtotal
        
        po_items.append({
            "product_id": pid,
            "product_name": prod["name"],
            "quantity_ordered": qty,
            "quantity_received": 0,
            "unit_cost": round(cost, 2),
            "subtotal": subtotal
        })
        
    if not po_items:
        raise ValueError("No valid items in purchase order.")
        
    po_number = f"PO-{datetime.now().strftime('%Y%m%d')}-{len(load_data('purchase_orders')) + 1:03d}"
    
    po_record = {
        "po_number": po_number,
        "supplier_id": supplier_id,
        "status": "ORDERED",
        "created_at": datetime.now().isoformat(),
        "created_by": user_id,
        "expected_delivery_date": expected_delivery_date,
        "total_cost": round(total_cost, 2),
        "notes": notes,
        "items": po_items
    }
    created_po = insert_record("purchase_orders", po_record, prefix="PO")
    log_audit(user_id, "CREATE_PURCHASE_ORDER", "PO", created_po["id"], f"Created {po_number} with {len(po_items)} items")
    return created_po

def receive_po_delivery(po_id: str, deliveries: List[Dict[str, Any]], user_id: str) -> Dict[str, Any]:
    """
    Receive items against a PO.
    deliveries format: [{'product_id': 'PRD-001', 'quantity': 10, 'expiry_date': '2026-11-20', 'unit_cost': 24.0}]
    """
    po = find_by_id("purchase_orders", po_id)
    if not po:
        raise ValueError(f"Purchase order {po_id} not found.")
        
    items = po.get("items", [])
    supplier_id = po.get("supplier_id")
    
    received_any = False
    
    for delivery in deliveries:
        pid = delivery["product_id"]
        qty_to_receive = int(delivery.get("quantity", 0))
        if qty_to_receive <= 0:
            continue
            
        exp_date = delivery.get("expiry_date")
        if not exp_date:
            raise ValueError(f"Expiry date is required for product delivery.")
            
        cost = float(delivery.get("unit_cost", 0.0))
        
        # Find matching PO line
        matched_item = None
        for it in items:
            if it["product_id"] == pid:
                matched_item = it
                break
                
        if not matched_item:
            continue
            
        remaining_expected = matched_item["quantity_ordered"] - matched_item.get("quantity_received", 0)
        if qty_to_receive > remaining_expected:
            # allow receiving up to remaining_expected or slight surplus
            pass
            
        # Record actual stock receipt creating batch
        record_delivery(
            product_id=pid,
            supplier_id=supplier_id,
            quantity=qty_to_receive,
            unit_cost=cost if cost > 0 else matched_item.get("unit_cost", 0.0),
            expiry_date=exp_date,
            user_id=user_id,
            notes=f"Received against {po.get('po_number', po_id)}",
            po_id=po_id
        )
        
        matched_item["quantity_received"] = matched_item.get("quantity_received", 0) + qty_to_receive
        received_any = True
        
    if not received_any:
        raise ValueError("No items were received.")
        
    # Check if fully completed or partially received
    all_completed = True
    any_received = False
    for it in items:
        if it.get("quantity_received", 0) < it.get("quantity_ordered", 0):
            all_completed = False
        if it.get("quantity_received", 0) > 0:
            any_received = True
            
    new_status = "COMPLETED" if all_completed else ("PARTIALLY_RECEIVED" if any_received else po.get("status"))
    
    updated_po = update_record("purchase_orders", po_id, {
        "items": items,
        "status": new_status,
        "last_received_at": datetime.now().isoformat()
    })
    
    log_audit(user_id, "RECEIVE_PO", "PO", po_id, f"Received items against {po.get('po_number')}. Status now: {new_status}")
    return updated_po
