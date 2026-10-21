from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.auth_service import authenticate, create_user, list_users

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        role = session.get("role")
        if role == "owner":
            return redirect(url_for("owner.dashboard"))
        elif role == "manager":
            return redirect(url_for("inventory.dashboard"))
        return redirect(url_for("employee.dashboard"))
        
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        next_url = request.form.get("next") or request.args.get("next")
        
        user = authenticate(username, password)
        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            
            flash(f"Welcome back, {user['name']}!", "success")
            
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
                
            if user["role"] == "owner":
                return redirect(url_for("owner.dashboard"))
            elif user["role"] == "manager":
                return redirect(url_for("inventory.dashboard"))
            else:
                return redirect(url_for("employee.dashboard"))
        else:
            flash("Invalid username or password, or account is disabled.", "danger")
            
    return render_template("login.html")

@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("auth.login"))

@bp.route("/setup-owner", methods=["GET", "POST"])
def setup_owner():
    # Only allow if no owner currently exists
    existing_users = list_users()
    has_owner = any(u.get("role") == "owner" for u in existing_users)
    if has_owner:
        flash("Owner account already initialized. Please sign in.", "info")
        return redirect(url_for("auth.login"))
        
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        
        if not (username and name and password):
            flash("Please fill in all required fields.", "danger")
            return render_template("setup_owner.html")
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("setup_owner.html")
            
        try:
            create_user(username=username, name=name, email=email, role="owner", password=password)
            flash("Owner account created successfully! Please sign in.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            flash(str(e), "danger")
            
    return render_template("setup_owner.html")
