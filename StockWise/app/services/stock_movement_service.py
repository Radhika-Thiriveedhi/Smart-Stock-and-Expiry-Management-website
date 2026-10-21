from datetime import datetime
from typing import List, Dict, Any, Optional
from app.storage.json_store import load_data, insert_record, find_by_id, log_audit, create_backup
from app.services.batch_service import create_batch, deduct_batch_quantity, get_batches_for_sale_fefo, get_batch
from app.services.product_service import get_product

def list_movements(limit: int = 100, movement_type: Optional[str] = None, product_id: Optional[str] = None) -> List[Dict[str, Any]]:
    movements = load_data("stock_movements", default=[])
    products = {p["id"]: p for p in load_data("products", default=[])}
    users = {u["id"]: u["name"] for u in load_data("users", default=[])}
    
    results = []
    for m in movements:
        if movement_type and m.get("type") != movement_type:
            continue
        if product_id and m.get("product_id") != product_id:
            continue
            
        m_copy = dict(m)
        prod = products.get(m.get("product_id"), {})
        m_copy["product_name"] = prod.get("name", "Unknown Product")
        m_copy["product_sku"] = prod.get("sku", "")
        m_copy["product_unit"] = prod.get("unit", "units")
        m_copy["user_name"] = users.get(m.get("created_by"), m.get("created_by", "System"))
        results.append(m_copy)
        
    # Sort descending by timestamp
    results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return results[:limit]

def record_delivery(product_id: str, 
                    supplier_id: str, 
                    quantity: int, 
                    unit_cost: float, 
                    expiry_date: str, 
                    user_id: str, 
                    notes: str = "", 
                    po_id: Optional[str] = None) -> Dict[str, Any]:
    prod = get_product(product_id)
    if not prod:
        raise ValueError("Invalid product selected.")
    if quantity <= 0:
        raise ValueError("Delivery quantity must be at least 1.")
    if unit_cost < 0:
        raise ValueError("Unit cost cannot be negative.")
        
    # Snapshot backup before modifying inventory
    create_backup(tag="pre_delivery")
    
    # 1. Create Batch
    batch = create_batch(
        product_id=product_id,
        supplier_id=supplier_id,
        quantity=quantity,
        unit_cost=unit_cost,
        expiry_date=expiry_date
    )
    
    # 2. Record Stock Movement
    mov_record = {
        "product_id": product_id,
        "batch_id": batch["id"],
        "type": "RECEIVE",
        "quantity": quantity,
        "unit_cost": unit_cost,
        "reason": notes or f"Delivery of {quantity} {prod.get('unit')} - Batch {batch['id']}",
        "created_at": datetime.now().isoformat(),
        "created_by": user_id,
        "reference_id": po_id or batch["id"]
    }
    insert_record("stock_movements", mov_record, prefix="MOV")
    
    # 3. Log Audit
    log_audit(user_id, "RECEIVE_STOCK", "BATCH", batch["id"], f"Received {quantity} of {prod['name']}")
    
    return batch

def record_sale(items_request: List[Dict[str, Any]], 
                user_id: str, 
                cashier_name: str, 
                payment_method: str = "CASH", 
                notes: str = "") -> Dict[str, Any]:
    """
    Process sale of products using First Expired, First Out (FEFO).
    items_request format: [{'product_id': 'PRD-001', 'quantity': 2}, ...]
    """
    if not items_request:
        raise ValueError("No items in sale transaction.")
        
    create_backup(tag="pre_sale")
    
    # Phase 1: Validate all items and plan FEFO allocations
    allocations_plan = []
    
    for item in items_request:
        pid = item["product_id"]
        qty = int(item["quantity"])
        if qty <= 0:
            continue
            
        prod = get_product(pid)
        if not prod:
            raise ValueError(f"Product {pid} not found.")
            
        allocations, shortfall = get_batches_for_sale_fefo(pid, qty)
        if shortfall > 0:
            raise ValueError(f"Insufficient saleable stock for {prod['name']}. Requested: {qty}, Shortfall: {shortfall}")
            
        allocations_plan.append({
            "product": prod,
            "requested_qty": qty,
            "allocations": allocations
        })
        
    if not allocations_plan:
        raise ValueError("No valid items to sell.")
        
    # Phase 2: Execute deductions and build receipt line items
    now_iso = datetime.now().isoformat()
    receipt_no = f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    sale_line_items = []
    total_amount = 0.0
    total_cost = 0.0
    
    for plan in allocations_plan:
        prod = plan["product"]
        unit_price = prod.get("selling_price", 0.0)
        
        for alloc in plan["allocations"]:
            b_id = alloc["batch_id"]
            alloc_qty = alloc["quantity"]
            unit_cost = alloc["unit_cost"]
            
            # Deduct from batch
            deduct_batch_quantity(b_id, alloc_qty)
            
            # Record Movement
            mov_record = {
                "product_id": prod["id"],
                "batch_id": b_id,
                "type": "SALE",
                "quantity": alloc_qty,
                "unit_cost": unit_cost,
                "reason": f"Sale via receipt {receipt_no}",
                "created_at": now_iso,
                "created_by": user_id,
                "reference_id": receipt_no
            }
            insert_record("stock_movements", mov_record, prefix="MOV")
            
            line_subtotal = round(alloc_qty * unit_price, 2)
            line_cost = round(alloc_qty * unit_cost, 2)
            
            total_amount += line_subtotal
            total_cost += line_cost
            
            sale_line_items.append({
                "product_id": prod["id"],
                "product_name": prod["name"],
                "product_sku": prod["sku"],
                "batch_id": b_id,
                "quantity": alloc_qty,
                "unit_price": unit_price,
                "unit_cost": unit_cost,
                "subtotal": line_subtotal,
                "cost_subtotal": line_cost
            })
            
    gross_profit = round(total_amount - total_cost, 2)
    
    # Phase 3: Store sale record
    sale_record = {
        "receipt_no": receipt_no,
        "created_at": now_iso,
        "cashier_id": user_id,
        "cashier_name": cashier_name,
        "items": sale_line_items,
        "total_amount": round(total_amount, 2),
        "total_cost": round(total_cost, 2),
        "gross_profit": gross_profit,
        "payment_method": payment_method,
        "notes": notes
    }
    created_sale = insert_record("sales", sale_record, prefix="SAL")
    log_audit(user_id, "RECORD_SALE", "SALE", created_sale["id"], f"Receipt {receipt_no}: Total {total_amount}")
    
    return created_sale

def record_damage_or_waste(batch_id: str, 
                           quantity: int, 
                           reason: str, 
                           notes: str, 
                           user_id: str) -> Dict[str, Any]:
    batch = get_batch(batch_id)
    if not batch:
        raise ValueError(f"Batch {batch_id} not found.")
    if quantity <= 0:
        raise ValueError("Quantity must be at least 1.")
    if batch.get("quantity_remaining", 0) < quantity:
        raise ValueError(f"Batch only has {batch.get('quantity_remaining', 0)} items remaining.")
        
    create_backup(tag="pre_waste")
    
    unit_cost = batch.get("unit_cost", 0.0)
    total_loss = round(quantity * unit_cost, 2)
    now_iso = datetime.now().isoformat()
    
    # 1. Deduct from batch
    deduct_batch_quantity(batch_id, quantity)
    
    # 2. Add to waste records
    waste_entry = {
        "product_id": batch["product_id"],
        "product_name": batch["product_name"],
        "batch_id": batch_id,
        "quantity": quantity,
        "unit_cost": unit_cost,
        "total_loss": total_loss,
        "reason": reason,
        "notes": notes,
        "reported_by": user_id,
        "created_at": now_iso
    }
    created_waste = insert_record("waste_records", waste_entry, prefix="WST")
    
    # 3. Add to movements
    mov_record = {
        "product_id": batch["product_id"],
        "batch_id": batch_id,
        "type": "WASTE",
        "quantity": quantity,
        "unit_cost": unit_cost,
        "reason": f"Waste ({reason}): {notes}",
        "created_at": now_iso,
        "created_by": user_id,
        "reference_id": created_waste["id"]
    }
    insert_record("stock_movements", mov_record, prefix="MOV")
    
    # 4. Log audit
    log_audit(user_id, "REPORT_WASTE", "BATCH", batch_id, f"Recorded {quantity} waste units, loss: {total_loss}")
    
    return created_waste
