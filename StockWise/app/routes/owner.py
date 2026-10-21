from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import owner_required
from app.services.inventory_service import get_dashboard_metrics, get_all_inventory_summary
from app.services.analytics_service import get_sales_analytics, get_waste_analytics, get_inventory_valuation_analytics, get_supplier_performance, get_shop_owner_command_center
from app.services.auth_service import list_users, create_user, update_user
from app.services.product_service import list_products
from app.services.purchase_service import list_suppliers
from app.storage.json_store import load_data, save_data, log_audit, create_backup

bp = Blueprint("owner", __name__, url_prefix="/owner")

@bp.route("/dashboard")
@owner_required
def dashboard():
    cc = get_shop_owner_command_center()
    supplier_stats = get_supplier_performance()
    products = list_products(active_only=True)
    suppliers = list_suppliers(active_only=True)
    
    return render_template(
        "owner/dashboard.html",
        cc=cc,
        suppliers_stats=supplier_stats,
        products=products,
        suppliers=suppliers,
        current_user=session
    )


@bp.route("/sales-report")
@owner_required
def sales_report():
    sales_data = get_sales_analytics()
    all_sales = load_data("sales", default=[])
    all_sales.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return render_template("owner/sales_report.html", analytics=sales_data, sales_list=all_sales)

@bp.route("/inventory-report")
@owner_required
def inventory_report():
    valuation = get_inventory_valuation_analytics()
    inventory_items = get_all_inventory_summary(active_only=False)
    return render_template("owner/inventory_report.html", valuation=valuation, items=inventory_items)

@bp.route("/waste-report")
@owner_required
def waste_report():
    waste = get_waste_analytics()
    return render_template("owner/waste_report.html", waste=waste)

@bp.route("/staff", methods=["GET", "POST"])
@owner_required
def staff():
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "create":
            username = request.form.get("username", "").strip()
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            role = request.form.get("role", "employee")
            password = request.form.get("password", "")
            
            try:
                create_user(username=username, name=name, email=email, role=role, password=password)
                log_audit(session.get("user_id"), "CREATE_STAFF", "USER", username, f"Added staff {name} as {role}")
                flash(f"Staff account for {name} ({username}) created successfully.", "success")
            except Exception as e:
                flash(f"Failed to create staff: {str(e)}", "danger")
                
        elif action == "toggle_active":
            uid = request.form.get("user_id")
            users = list_users()
            for u in users:
                if u["id"] == uid:
                    new_val = not u.get("active", True)
                    update_user(uid, {"active": new_val})
                    log_audit(session.get("user_id"), "TOGGLE_STAFF_STATUS", "USER", uid, f"User active set to {new_val}")
                    flash(f"Staff status updated.", "info")
                    break
                    
        elif action == "reset_password":
            uid = request.form.get("user_id")
            new_pw = request.form.get("new_password")
            if new_pw:
                update_user(uid, {"password": new_pw})
                flash(f"Password reset successfully.", "success")
                
        return redirect(url_for("owner.staff"))
        
    staff_list = list_users()
    return render_template("owner/staff.html", staff_list=staff_list)

@bp.route("/settings", methods=["GET", "POST"])
@owner_required
def settings():
    current_settings = load_data("settings", default={})
    
    if request.method == "POST":
        action = request.form.get("action")
        if action == "backup":
            folder = create_backup(tag="manual_owner")
            flash(f"Data backup created successfully in {folder}", "success")
            return redirect(url_for("owner.settings"))
            
        store_name = request.form.get("store_name", "").strip()
        address = request.form.get("address", "").strip()
        phone = request.form.get("phone", "").strip()
        currency = request.form.get("currency_symbol", "$").strip()
        near_expiry = int(request.form.get("near_expiry_days", 7))
        critical_expiry = int(request.form.get("critical_expiry_days", 3))
        receipt_footer = request.form.get("receipt_footer", "").strip()
        
        current_settings.update({
            "store_name": store_name,
            "address": address,
            "phone": phone,
            "currency_symbol": currency,
            "near_expiry_days": near_expiry,
            "critical_expiry_days": critical_expiry,
            "receipt_footer": receipt_footer
        })
        save_data("settings", current_settings)
        log_audit(session.get("user_id"), "UPDATE_SETTINGS", "SYSTEM", "SETTINGS", "Updated store settings")
        flash("Store settings updated successfully.", "success")
        return redirect(url_for("owner.settings"))
        
    audit_logs = load_data("audit_log", default=[])
    audit_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return render_template("owner/settings.html", settings=current_settings, audit_logs=audit_logs[:20])
