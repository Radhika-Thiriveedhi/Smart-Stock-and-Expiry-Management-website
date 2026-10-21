from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import login_required
from app.services.inventory_service import get_dashboard_metrics, get_all_inventory_summary
from app.services.product_service import list_products
from app.services.batch_service import list_batches, get_batches_for_sale_fefo
from app.services.purchase_service import list_suppliers
from app.services.stock_movement_service import record_delivery, record_sale, record_damage_or_waste, list_movements
from app.storage.json_store import find_by_id, load_data

bp = Blueprint("employee", __name__, url_prefix="/employee")

@bp.route("/dashboard")
@login_required
def dashboard():
    metrics = get_dashboard_metrics()
    products = get_all_inventory_summary(active_only=True)
    recent_batches = list_batches(hide_depleted=True)[:10]
    recent_movements = list_movements(limit=8)
    return render_template(
        "employee/dashboard.html",
        metrics=metrics,
        products=products,
        recent_batches=recent_batches,
        recent_movements=recent_movements,
        current_user=session
    )

@bp.route("/receive-stock", methods=["GET", "POST"])
@login_required
def receive_stock():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        supplier_id = request.form.get("supplier_id")
        quantity = request.form.get("quantity")
        unit_cost = request.form.get("unit_cost")
        expiry_date = request.form.get("expiry_date")
        notes = request.form.get("notes", "").strip()
        
        try:
            qty = int(quantity)
            cost = float(unit_cost)
            batch = record_delivery(
                product_id=product_id,
                supplier_id=supplier_id,
                quantity=qty,
                unit_cost=cost,
                expiry_date=expiry_date,
                user_id=session.get("user_id") or "USR-001",
                notes=notes
            )
            flash(f"Delivery recorded successfully! Created batch {batch['id']} with {qty} units.", "success")
            role = session.get("role")
            if role == "owner":
                return redirect(url_for("owner.dashboard"))
            elif role == "manager":
                return redirect(url_for("inventory.batches"))
            return redirect(url_for("employee.dashboard"))
        except Exception as e:
            flash(f"Failed to record delivery: {str(e)}", "danger")
            
    products = list_products(active_only=True)
    suppliers = list_suppliers(active_only=True)
    return render_template("employee/receive_stock.html", products=products, suppliers=suppliers)

@bp.route("/record-sale", methods=["GET", "POST"])
@login_required
def record_sale_view():
    if request.method == "POST":
        product_ids = request.form.getlist("product_id[]")
        quantities = request.form.getlist("quantity[]")
        payment_method = request.form.get("payment_method", "CASH")
        notes = request.form.get("notes", "").strip()
        
        items_request = []
        for pid, qty_str in zip(product_ids, quantities):
            if pid and qty_str:
                try:
                    q = int(qty_str)
                    if q > 0:
                        items_request.append({"product_id": pid, "quantity": q})
                except ValueError:
                    pass
                    
        try:
            sale = record_sale(
                items_request=items_request,
                user_id=session.get("user_id"),
                cashier_name=session.get("name", "Staff"),
                payment_method=payment_method,
                notes=notes
            )
            flash(f"Sale {sale['receipt_no']} completed successfully! Total: ${sale['total_amount']:.2f}", "success")
            return redirect(url_for("employee.view_receipt", sale_id=sale["id"]))
        except Exception as e:
            flash(f"Sale could not be processed: {str(e)}", "danger")
            
    products = get_all_inventory_summary(active_only=True)
    # Filter products that have saleable stock > 0
    in_stock_products = [p for p in products if p["saleable_quantity"] > 0]
    return render_template("employee/record_sale.html", products=in_stock_products)

@bp.route("/receipt/<sale_id>")
@login_required
def view_receipt(sale_id):
    sale = find_by_id("sales", sale_id)
    if not sale:
        flash("Sale receipt not found.", "warning")
        return redirect(url_for("employee.dashboard"))
    settings = load_data("settings", default={})
    return render_template("employee/receipt.html", sale=sale, settings=settings)

@bp.route("/report-damage", methods=["GET", "POST"])
@login_required
def report_damage():
    if request.method == "POST":
        batch_id = request.form.get("batch_id")
        quantity = request.form.get("quantity")
        reason = request.form.get("reason", "DAMAGED_IN_STORE")
        notes = request.form.get("notes", "").strip()
        
        try:
            qty = int(quantity)
            record_damage_or_waste(
                batch_id=batch_id,
                quantity=qty,
                reason=reason,
                notes=notes,
                user_id=session.get("user_id")
            )
            flash(f"Waste/Damage reported successfully. Deducted {qty} units from batch {batch_id}.", "success")
            return redirect(url_for("employee.dashboard"))
        except Exception as e:
            flash(f"Failed to record waste/damage: {str(e)}", "danger")
            
    batches = list_batches(hide_depleted=True)
    return render_template("employee/report_damage.html", batches=batches)

@bp.route("/movements")
@login_required
def movements():
    mov_type = request.args.get("type")
    movements_list = list_movements(limit=100, movement_type=mov_type)
    return render_template("employee/movement_history.html", movements=movements_list, current_type=mov_type)
