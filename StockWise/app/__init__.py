import os
from datetime import datetime
from flask import Flask, render_template, session
from app.config import Config
from app.storage.json_store import load_data

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure data and backup directories exist
    os.makedirs(app.config["DATA_DIR"], exist_ok=True)
    os.makedirs(app.config["BACKUP_DIR"], exist_ok=True)
    
    # Register blueprints
    from app.routes.public import bp as public_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.employee import bp as employee_bp
    from app.routes.inventory import bp as inventory_bp
    from app.routes.purchases import bp as purchases_bp
    from app.routes.owner import bp as owner_bp
    from app.routes.reports import bp as reports_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(owner_bp)
    app.register_blueprint(reports_bp)
    
    # Context Processors for templates
    @app.context_processor
    def inject_global_data():
        settings = load_data("settings", default={})
        notifs = load_data("notifications", default=[])
        unread_notifs = [n for n in notifs if not n.get("read", False)]
        
        return {
            "store_settings": settings,
            "currency_symbol": settings.get("currency_symbol", "$"),
            "unread_alert_count": len(unread_notifs),
            "current_year": datetime.now().year,
            "current_user_role": session.get("role"),
            "current_user_name": session.get("name")
        }
        
    # Custom template filters
    @app.template_filter("currency")
    def currency_filter(value):
        try:
            settings = load_data("settings", default={})
            sym = settings.get("currency_symbol", "$")
            val = float(value)
            if val < 0:
                return f"-{sym}{abs(val):,.2f}"
            return f"{sym}{val:,.2f}"
        except (ValueError, TypeError):
            return "$0.00"
            
    @app.template_filter("datetime_format")
    def datetime_format_filter(value_str):
        if not value_str:
            return ""
        try:
            if "T" in value_str:
                dt = datetime.fromisoformat(value_str)
                return dt.strftime("%b %d, %Y %I:%M %p")
            dt = datetime.strptime(value_str, "%Y-%m-%d")
            return dt.strftime("%b %d, %Y")
        except Exception:
            return value_str
            
    @app.template_filter("date_short")
    def date_short_filter(value_str):
        if not value_str:
            return ""
        try:
            if "T" in value_str:
                dt = datetime.fromisoformat(value_str)
                return dt.strftime("%b %d, %Y")
            dt = datetime.strptime(value_str, "%Y-%m-%d")
            return dt.strftime("%b %d, %Y")
        except Exception:
            return value_str
            
    # Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("404.html", message="An unexpected error occurred on the server."), 500

    return app
