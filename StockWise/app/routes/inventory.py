from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import manager_required
from app.services.inventory_service import get_dashboard_metrics, get_all_inventory_summary, get_reorder_recommendations
from app.services.product_service import list_products, get_product, create_product, update_product, toggle_product_status, list_categories, create_category
from app.services.batch_service import list_batches, get_batch
from app.services.purchase_service import list_suppliers, create_supplier, update_supplier
from app.services.stock_movement_service import list_movements, record_damage_or_waste
from app.storage.json_store import log_audit

bp = Blueprint("inventory", __name__, url_prefix="/inventory")

@bp.route("/dashboard")
@manager_required
def dashboard():
    metrics = get_dashboard_metrics()
    reorders = get_reorder_recommendations()[:5]
    near_expiry_batches = [b for b in list_batches(hide_depleted=True) if b["expiry_status"] in ["EXPIRED", "CRITICAL", "WARNING"]][:8]
    recent_movements = list_movements(limit=6)
    return render_template(
        "inventory/dashboard.html",
        metrics=metrics,
        reorders=reorders,
        near_expiry_batches=near_expiry_batches,
        recent_movements=recent_movements,
        current_user=session
    )

@bp.route("/products")
@manager_required
def products():
    category_id = request.args.get("category_id")
    search = request.args.get("q")
    show_all = request.args.get("show_all") == "1"
    
    product_list = list_products(active_only=not show_all, category_id=category_id, search=search)
    categories = list_categories()
    inventory_map = {item["product_id"]: item for item in get_all_inventory_summary(active_only=False)}
    
    for p in product_list:
        p["stock_info"] = inventory_map.get(p["id"], {})
        
    return render_template(
        "inventory/products.html",
        products=product_list,
        categories=categories,
        selected_category=category_id,
        search=search,
        show_all=show_all
    )

@bp.route("/products/new", methods=["GET", "POST"])
@manager_required
def product_create():
    if request.method == "POST":
        sku = request.form.get("sku", "").strip()
        name = request.form.get("name", "").strip()
        category_id = request.form.get("category_id")
        unit = request.form.get("unit", "units").strip()
        selling_price = request.form.get("selling_price", "0.0")
        reorder_level = request.form.get("reorder_level", "10")
        
        try:
            prod = create_product(
                sku=sku,
                name=name,
                category_id=category_id,
                unit=unit,
                selling_price=float(selling_price),
                reorder_level=int(reorder_level)
            )
            log_audit(session.get("user_id"), "CREATE_PRODUCT", "PRODUCT", prod["id"], f"Added product {name} ({sku})")
            flash(f"Product '{name}' created successfully.", "success")
            return redirect(url_for("inventory.products"))
        except Exception as e:
            flash(f"Error creating product: {str(e)}", "danger")
            
    categories = list_categories()
    return render_template("inventory/product_form.html", product=None, categories=categories, title="Add New Product")

@bp.route("/products/<product_id>/edit", methods=["GET", "POST"])
@manager_required
def product_edit(product_id):
    prod = get_product(product_id)
    if not prod:
        flash("Product not found.", "warning")
        return redirect(url_for("inventory.products"))
        
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category_id = request.form.get("category_id")
        unit = request.form.get("unit", "units").strip()
        selling_price = float(request.form.get("selling_price", 0.0))
        reorder_level = int(request.form.get("reorder_level", 10))
        
        try:
            update_product(product_id, {
                "name": name,
                "category_id": category_id,
                "unit": unit,
                "selling_price": selling_price,
                "reorder_level": reorder_level
            })
            log_audit(session.get("user_id"), "UPDATE_PRODUCT", "PRODUCT", product_id, f"Updated details for {name}")
            flash(f"Product '{name}' updated successfully.", "success")
            return redirect(url_for("inventory.products"))
        except Exception as e:
            flash(f"Error updating product: {str(e)}", "danger")
            
    categories = list_categories()
    return render_template("inventory/product_form.html", product=prod, categories=categories, title="Edit Product")

@bp.route("/products/<product_id>/toggle-status", methods=["POST"])
@manager_required
def product_toggle_status(product_id):
    prod = toggle_product_status(product_id)
    if prod:
        status_label = "activated" if prod.get("active") else "deactivated"
        log_audit(session.get("user_id"), "TOGGLE_PRODUCT_STATUS", "PRODUCT", product_id, f"Product {status_label}")
        flash(f"Product has been {status_label}.", "info")
    return redirect(url_for("inventory.products"))

@bp.route("/batches")
@manager_required
def batches():
    product_id = request.args.get("product_id")
    supplier_id = request.args.get("supplier_id")
    status = request.args.get("status")
    
    batch_list = list_batches(product_id=product_id, supplier_id=supplier_id, status_filter=status, hide_depleted=False)
    products = list_products(active_only=False)
    suppliers = list_suppliers(active_only=False)
    
    return render_template(
        "inventory/batches.html",
        batches=batch_list,
        products=products,
        suppliers=suppliers,
        selected_product=product_id,
        selected_supplier=supplier_id,
        selected_status=status
    )

@bp.route("/batches/<batch_id>")
@manager_required
def batch_detail(batch_id):
    batch = get_batch(batch_id)
    if not batch:
        flash("Batch not found.", "warning")
        return redirect(url_for("inventory.batches"))
    movements = [m for m in list_movements(limit=200) if m.get("batch_id") == batch_id]
    return render_template("inventory/batch_detail.html", batch=batch, movements=movements)

@bp.route("/batches/<batch_id>/discard", methods=["POST"])
@manager_required
def batch_discard(batch_id):
    batch = get_batch(batch_id)
    if not batch:
        flash("Batch not found.", "danger")
        return redirect(url_for("inventory.batches"))
    rem = batch.get("quantity_remaining", 0)
    if rem <= 0:
        flash("Batch has no remaining stock to discard.", "warning")
        return redirect(url_for("inventory.batches"))
        
    reason = request.form.get("reason", "EXPIRED")
    notes = request.form.get("notes", f"Manager discarded {batch_id} due to expiry.")
    
    try:
        record_damage_or_waste(
            batch_id=batch_id,
            quantity=rem,
            reason=reason,
            notes=notes,
            user_id=session.get("user_id")
        )
        flash(f"Batch {batch_id} fully discarded ({rem} units recorded as waste).", "success")
    except Exception as e:
        flash(f"Error discarding batch: {str(e)}", "danger")
        
    return redirect(url_for("inventory.batches"))

@bp.route("/low-stock")
@manager_required
def low_stock():
    recommendations = get_reorder_recommendations()
    return render_template("inventory/low_stock.html", recommendations=recommendations)

@bp.route("/expiry-alerts")
@manager_required
def expiry_alerts():
    batches = list_batches(hide_depleted=True)
    expired = [b for b in batches if b["expiry_status"] == "EXPIRED"]
    critical = [b for b in batches if b["expiry_status"] == "CRITICAL"]
    warning = [b for b in batches if b["expiry_status"] == "WARNING"]
    upcoming = [b for b in batches if b["expiry_status"] == "UPCOMING"]
    
    return render_template(
        "inventory/expiry_alerts.html",
        expired=expired,
        critical=critical,
        warning=warning,
        upcoming=upcoming
    )

@bp.route("/suppliers", methods=["GET", "POST"])
@manager_required
def suppliers():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        contact = request.form.get("contact_person", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        lead_time = request.form.get("lead_time_days", "2")
        
        try:
            sup = create_supplier(name=name, contact_person=contact, phone=phone, email=email, lead_time_days=int(lead_time))
            log_audit(session.get("user_id"), "CREATE_SUPPLIER", "SUPPLIER", sup["id"], f"Added supplier {name}")
            flash(f"Supplier '{name}' added successfully.", "success")
            return redirect(url_for("inventory.suppliers"))
        except Exception as e:
            flash(f"Failed to add supplier: {str(e)}", "danger")
            
    suppliers_list = list_suppliers(active_only=False)
    return render_template("inventory/suppliers.html", suppliers=suppliers_list)

@bp.route("/audit", methods=["GET", "POST"])
@manager_required
def audit():
    products_summary = get_all_inventory_summary(active_only=True)
    
    if request.method == "POST":
        product_id = request.form.get("product_id")
        counted_qty = request.form.get("counted_quantity")
        reason = request.form.get("reason", "PHYSICAL_COUNT_RECONCILIATION")
        notes = request.form.get("notes", "").strip()
        
        try:
            counted = int(counted_qty)
            batches = list_batches(product_id=product_id, hide_depleted=False)
            current_total = sum(b.get("quantity_remaining", 0) for b in batches)
            variance = counted - current_total
            
            if variance < 0:
                # Stock is missing (shrinkage / lost)
                loss_qty = abs(variance)
                # Deduct from earliest batch
                for b in batches:
                    if loss_qty <= 0:
                        break
                    rem = b.get("quantity_remaining", 0)
                    if rem > 0:
                        take = min(rem, loss_qty)
                        record_damage_or_waste(
                            batch_id=b["id"],
                            quantity=take,
                            reason="MISSING_AUDIT",
                            notes=f"Audit discrepancy: counted {counted} vs recorded {current_total}. {notes}",
                            user_id=session.get("user_id")
                        )
                        loss_qty -= take
                flash(f"Audit recorded: Stock adjusted down by {abs(variance)} units due to variance.", "warning")
            elif variance > 0:
                # Surplus found, create adjustment batch
                from app.services.stock_movement_service import record_delivery
                prod = get_product(product_id)
                cost = prod.get("selling_price", 10.0) * 0.6  # estimated cost basis
                from app.utils.dates import get_current_date
                from datetime import timedelta
                exp = (get_current_date() + timedelta(days=90)).isoformat()
                record_delivery(
                    product_id=product_id,
                    supplier_id="SUP-001",
                    quantity=variance,
                    unit_cost=cost,
                    expiry_date=exp,
                    user_id=session.get("user_id"),
                    notes=f"Audit surplus adjustment (+{variance}). {notes}"
                )
                flash(f"Audit recorded: Stock adjusted up by +{variance} units.", "success")
            else:
                flash("Audit verified: Physical count matches recorded inventory exactly!", "success")
                
            return redirect(url_for("inventory.audit"))
        except Exception as e:
            flash(f"Error during audit reconciliation: {str(e)}", "danger")
            
    return render_template("inventory/audit.html", products=products_summary)

