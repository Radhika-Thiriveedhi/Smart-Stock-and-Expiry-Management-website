from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from app.storage.json_store import load_data, insert_record, update_record, find_by_id
from app.utils.dates import calculate_expiry_status, parse_date, get_current_date

def list_batches(product_id: Optional[str] = None, 
                 supplier_id: Optional[str] = None, 
                 status_filter: Optional[str] = None, 
                 hide_depleted: bool = False) -> List[Dict[str, Any]]:
    batches = load_data("batches", default=[])
    products = {p["id"]: p for p in load_data("products", default=[])}
    suppliers = {s["id"]: s["name"] for s in load_data("suppliers", default=[])}
    
    results = []
    for b in batches:
        if product_id and b.get("product_id") != product_id:
            continue
        if supplier_id and b.get("supplier_id") != supplier_id:
            continue
        if hide_depleted and b.get("quantity_remaining", 0) <= 0:
            continue
            
        b_copy = dict(b)
        prod = products.get(b.get("product_id"), {})
        b_copy["product_name"] = prod.get("name", "Unknown Product")
        b_copy["product_sku"] = prod.get("sku", "")
        b_copy["product_unit"] = prod.get("unit", "units")
        b_copy["supplier_name"] = suppliers.get(b.get("supplier_id"), "Unknown Supplier")
        
        # Calculate expiry metrics
        exp_info = calculate_expiry_status(b.get("expiry_date", ""))
        b_copy.update({
            "expiry_status": exp_info["status"],
            "days_left": exp_info["days_left"],
            "expiry_label": exp_info["label"],
            "badge_class": exp_info["badge_class"]
        })
        
        if status_filter and status_filter.upper() != "ALL":
            if b_copy["expiry_status"] != status_filter.upper():
                continue
                
        results.append(b_copy)
        
    # Sort by expiry date ascending
    return sorted(results, key=lambda x: (x.get("expiry_date", "9999-12-31"), x.get("id")))

def get_batch(batch_id: str) -> Optional[Dict[str, Any]]:
    batch = find_by_id("batches", batch_id)
    if not batch:
        return None
    products = {p["id"]: p for p in load_data("products", default=[])}
    suppliers = {s["id"]: s["name"] for s in load_data("suppliers", default=[])}
    
    b_copy = dict(batch)
    prod = products.get(b_copy.get("product_id"), {})
    b_copy["product_name"] = prod.get("name", "Unknown Product")
    b_copy["product_sku"] = prod.get("sku", "")
    b_copy["product_unit"] = prod.get("unit", "units")
    b_copy["supplier_name"] = suppliers.get(b_copy.get("supplier_id"), "Unknown Supplier")
    
    exp_info = calculate_expiry_status(b_copy.get("expiry_date", ""))
    b_copy.update({
        "expiry_status": exp_info["status"],
        "days_left": exp_info["days_left"],
        "expiry_label": exp_info["label"],
        "badge_class": exp_info["badge_class"]
    })
    return b_copy

def create_batch(product_id: str, 
                 supplier_id: str, 
                 quantity: int, 
                 unit_cost: float, 
                 expiry_date: str, 
                 received_date: Optional[str] = None) -> Dict[str, Any]:
    if quantity <= 0:
        raise ValueError("Batch quantity must be greater than zero.")
    if unit_cost < 0:
        raise ValueError("Unit cost cannot be negative.")
        
    rec_date = received_date or datetime.now().date().isoformat()
    record = {
        "product_id": product_id,
        "supplier_id": supplier_id,
        "received_date": rec_date,
        "expiry_date": expiry_date,
        "quantity_received": int(quantity),
        "quantity_remaining": int(quantity),
        "unit_cost": round(float(unit_cost), 2)
    }
    return insert_record("batches", record, prefix="BAT")

def deduct_batch_quantity(batch_id: str, quantity: int) -> Dict[str, Any]:
    batch = find_by_id("batches", batch_id)
    if not batch:
        raise ValueError(f"Batch {batch_id} not found.")
    curr = batch.get("quantity_remaining", 0)
    if curr < quantity:
        raise ValueError(f"Insufficient quantity in batch {batch_id}. Requested: {quantity}, Remaining: {curr}")
    new_qty = curr - quantity
    return update_record("batches", batch_id, {"quantity_remaining": new_qty})

def get_batches_for_sale_fefo(product_id: str, required_qty: int) -> Tuple[List[Dict[str, Any]], int]:
    """
    First Expired, First Out (FEFO) allocation engine.
    Allocates the requested quantity across batches, picking the earliest expiring non-expired batches first.
    Returns: (allocations, shortfall)
    where allocations is a list of {batch_id, expiry_date, quantity, unit_cost}
    and shortfall is remaining unallocated units if stock is insufficient.
    """
    all_batches = list_batches(product_id=product_id, hide_depleted=True)
    # Filter out already expired batches so expired food/goods are never sold!
    valid_batches = [b for b in all_batches if b["expiry_status"] != "EXPIRED"]
    
    allocations = []
    remaining_needed = required_qty
    
    for b in valid_batches:
        if remaining_needed <= 0:
            break
        available = b["quantity_remaining"]
        take_qty = min(available, remaining_needed)
        allocations.append({
            "batch_id": b["id"],
            "expiry_date": b["expiry_date"],
            "unit_cost": b["unit_cost"],
            "quantity": take_qty
        })
        remaining_needed -= take_qty
        
    return allocations, remaining_needed
