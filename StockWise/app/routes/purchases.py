from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import manager_required
from app.services.purchase_service import list_purchase_orders, get_purchase_order, create_purchase_order, receive_po_delivery, list_suppliers
from app.services.product_service import list_products

bp = Blueprint("purchases", __name__, url_prefix="/inventory/purchase-orders")

@bp.route("")
@manager_required
def index():
    status = request.args.get("status")
    supplier_id = request.args.get("supplier_id")
    pos = list_purchase_orders(status=status, supplier_id=supplier_id)
    suppliers = list_suppliers(active_only=False)
    return render_template("inventory/purchase_orders.html", purchase_orders=pos, suppliers=suppliers, current_status=status)

@bp.route("/new", methods=["GET", "POST"])
@manager_required
def new_po():
    if request.method == "POST":
        supplier_id = request.form.get("supplier_id")
        expected_date = request.form.get("expected_delivery_date")
        notes = request.form.get("notes", "").strip()
        
        product_ids = request.form.getlist("product_id[]")
        quantities = request.form.getlist("quantity[]")
        costs = request.form.getlist("unit_cost[]")
        
        items = []
        for pid, q_str, c_str in zip(product_ids, quantities, costs):
            if pid and q_str and c_str:
                try:
                    q = int(q_str)
                    c = float(c_str)
                    if q > 0 and c >= 0:
                        items.append({"product_id": pid, "quantity_ordered": q, "unit_cost": c})
                except ValueError:
                    pass
                    
        try:
            po = create_purchase_order(
                supplier_id=supplier_id,
                expected_delivery_date=expected_date,
                items_data=items,
                notes=notes,
                user_id=session.get("user_id")
            )
            flash(f"Purchase Order {po['po_number']} created successfully!", "success")
            return redirect(url_for("purchases.po_detail", po_id=po["id"]))
        except Exception as e:
            flash(f"Error creating PO: {str(e)}", "danger")
            
    suppliers = list_suppliers(active_only=True)
    products = list_products(active_only=True)
    prefill_product_id = request.args.get("product_id")
    prefill_qty = request.args.get("suggested_order", "20")
    
    return render_template(
        "inventory/po_form.html",
        suppliers=suppliers,
        products=products,
        prefill_product_id=prefill_product_id,
        prefill_qty=prefill_qty
    )

@bp.route("/<po_id>")
@manager_required
def po_detail(po_id):
    po = get_purchase_order(po_id)
    if not po:
        flash("Purchase order not found.", "warning")
        return redirect(url_for("purchases.index"))
    return render_template("inventory/po_detail.html", po=po)

@bp.route("/<po_id>/receive", methods=["GET", "POST"])
@manager_required
def receive_goods(po_id):
    po = get_purchase_order(po_id)
    if not po:
        flash("Purchase order not found.", "warning")
        return redirect(url_for("purchases.index"))
        
    if request.method == "POST":
        product_ids = request.form.getlist("product_id[]")
        quantities = request.form.getlist("received_quantity[]")
        expiry_dates = request.form.getlist("expiry_date[]")
        costs = request.form.getlist("unit_cost[]")
        
        deliveries = []
        for pid, q_str, exp, c_str in zip(product_ids, quantities, expiry_dates, costs):
            if pid and q_str and exp:
                try:
                    q = int(q_str)
                    c = float(c_str) if c_str else 0.0
                    if q > 0:
                        deliveries.append({
                            "product_id": pid,
                            "quantity": q,
                            "expiry_date": exp,
                            "unit_cost": c
                        })
                except ValueError:
                    pass
                    
        try:
            receive_po_delivery(po_id, deliveries, session.get("user_id"))
            flash(f"Delivery received and recorded into stock batches for {po['po_number']}.", "success")
            return redirect(url_for("purchases.po_detail", po_id=po_id))
        except Exception as e:
            flash(f"Failed to receive goods: {str(e)}", "danger")
            
    return render_template("inventory/po_receive.html", po=po)
