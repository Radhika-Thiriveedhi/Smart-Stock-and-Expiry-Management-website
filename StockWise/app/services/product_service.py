from datetime import datetime
from typing import List, Dict, Any, Optional
from app.storage.json_store import load_data, insert_record, update_record, find_by_id

def list_products(active_only: bool = False, category_id: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    products = load_data("products", default=[])
    categories = {c["id"]: c["name"] for c in load_data("categories", default=[])}
    
    results = []
    search_lower = search.lower().strip() if search else None
    
    for p in products:
        if active_only and not p.get("active", True):
            continue
        if category_id and p.get("category_id") != category_id:
            continue
        if search_lower:
            match_name = search_lower in p.get("name", "").lower()
            match_sku = search_lower in p.get("sku", "").lower()
            if not (match_name or match_sku):
                continue
                
        p_copy = dict(p)
        p_copy["category_name"] = categories.get(p.get("category_id"), "Uncategorized")
        results.append(p_copy)
        
    return sorted(results, key=lambda x: x.get("name", ""))

def get_product(product_id: str) -> Optional[Dict[str, Any]]:
    prod = find_by_id("products", product_id)
    if prod:
        categories = {c["id"]: c["name"] for c in load_data("categories", default=[])}
        prod_copy = dict(prod)
        prod_copy["category_name"] = categories.get(prod.get("category_id"), "Uncategorized")
        return prod_copy
    return None

def get_product_by_sku(sku: str) -> Optional[Dict[str, Any]]:
    products = load_data("products", default=[])
    for p in products:
        if p.get("sku", "").strip().upper() == sku.strip().upper():
            return p
    return None

def create_product(sku: str, name: str, category_id: str, unit: str, selling_price: float, reorder_level: int = 10) -> Dict[str, Any]:
    sku = sku.strip().upper()
    existing = get_product_by_sku(sku)
    if existing:
        raise ValueError(f"Product with SKU '{sku}' already exists.")
        
    record = {
        "sku": sku,
        "name": name.strip(),
        "category_id": category_id,
        "unit": unit.strip().lower(),
        "selling_price": round(float(selling_price), 2),
        "reorder_level": int(reorder_level),
        "active": True
    }
    return insert_record("products", record, prefix="PRD")

def update_product(product_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if "sku" in updates:
        existing = get_product_by_sku(updates["sku"])
        if existing and existing.get("id") != product_id:
            raise ValueError(f"SKU '{updates['sku']}' is already used by another product.")
    return update_record("products", product_id, updates)

def toggle_product_status(product_id: str) -> Optional[Dict[str, Any]]:
    prod = find_by_id("products", product_id)
    if not prod:
        return None
    new_status = not prod.get("active", True)
    return update_record("products", product_id, {"active": new_status})

# Category functions
def list_categories() -> List[Dict[str, Any]]:
    return sorted(load_data("categories", default=[]), key=lambda x: x.get("name", ""))

def get_category(category_id: str) -> Optional[Dict[str, Any]]:
    return find_by_id("categories", category_id)

def create_category(name: str, description: str = "") -> Dict[str, Any]:
    record = {
        "name": name.strip(),
        "description": description.strip(),
        "created_at": datetime.now().isoformat()
    }
    return insert_record("categories", record, prefix="CAT")
