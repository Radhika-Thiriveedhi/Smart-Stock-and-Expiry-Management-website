from functools import wraps
from flask import session, redirect, url_for, request, abort, render_template, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    """
    Ensure the logged-in user belongs to one of the specified roles.
    roles can be a string ('owner') or list of strings (['owner', 'manager']).
    """
    if isinstance(roles, str):
        roles = [roles]
        
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please sign in to access this page.", "warning")
                return redirect(url_for("auth.login", next=request.path))
                
            user_role = session.get("role")
            if user_role not in roles:
                return render_template("403.html", user_role=user_role, required_roles=roles), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def owner_required(f):
    return role_required(["owner"])(f)

def manager_required(f):
    return role_required(["owner", "manager"])(f)
