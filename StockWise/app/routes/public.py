from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app.services.inventory_service import get_dashboard_metrics
from app.storage.json_store import load_data

bp = Blueprint("public", __name__)

@bp.route("/")
def home():
    if "user_id" in session:
        role = session.get("role")
        if role == "owner":
            return redirect(url_for("owner.dashboard"))
        elif role == "manager":
            return redirect(url_for("inventory.dashboard"))
        else:
            return redirect(url_for("employee.dashboard"))
            
    metrics = get_dashboard_metrics()
    settings = load_data("settings", default={})
    return render_template("home.html", metrics=metrics, settings=settings)

@bp.route("/demo-login/<role>")
def demo_login(role):
    """
    Convenient one-click role preview switcher for testing and demonstration.
    Logs in as the pre-seeded owner, manager, or employee account.
    """
    role = role.lower()
    users = load_data("users", default=[])
    target_user = None
    
    for u in users:
        if u.get("role") == role and u.get("active", True):
            target_user = u
            break
            
    if not target_user:
        flash(f"Demo user for role '{role}' not found.", "warning")
        return redirect(url_for("auth.login"))
        
    session.clear()
    session["user_id"] = target_user["id"]
    session["username"] = target_user["username"]
    session["name"] = target_user["name"]
    session["role"] = target_user["role"]
    
    flash(f"Signed in as {target_user['name']} ({target_user['role'].title()})", "success")
    
    if role == "owner":
        return redirect(url_for("owner.dashboard"))
    elif role == "manager":
        return redirect(url_for("inventory.dashboard"))
    else:
        return redirect(url_for("employee.dashboard"))

@bp.route("/api/quick-search")
def quick_search_api():
    query = request.args.get("q", "").strip().lower()
    if not query:
        return {"results": []}

    from app.services.product_service import list_products
    from app.services.batch_service import list_batches
    from app.services.purchase_service import list_purchase_orders

    results = []

    # 1. Search Products
    for p in list_products(active_only=False):
        if query in p["name"].lower() or query in p["sku"].lower():
            results.append({
                "title": p["name"],
                "subtitle": f"SKU: {p['sku']} • {p.get('category_name', '')} • ${p['selling_price']}",
                "category": "Products",
                "url": url_for("inventory.products") + f"?q={p['sku']}",
                "badge": "Product"
            })

    # 2. Search Batches
    for b in list_batches(hide_depleted=False):
        if query in b["id"].lower() or query in b["product_name"].lower() or query in b["expiry_date"]:
            results.append({
                "title": f"Batch {b['id']} — {b['product_name']}",
                "subtitle": f"Expires: {b['expiry_date']} • Left: {b['quantity_remaining']} {b['product_unit']} ({b['expiry_label']})",
                "category": "Batches",
                "url": url_for("inventory.batch_detail", batch_id=b["id"]),
                "badge": b["expiry_status"]
            })

    # 3. Search Purchase Orders
    for po in list_purchase_orders():
        if query in po["po_number"].lower() or query in po["supplier_name"].lower():
            results.append({
                "title": f"{po['po_number']} — {po['supplier_name']}",
                "subtitle": f"Status: {po['status']} • Total: ${po['total_cost']}",
                "category": "Orders",
                "url": url_for("purchases.po_detail", po_id=po["id"]),
                "badge": po["status"]
            })

    return {"results": results[:10]}

