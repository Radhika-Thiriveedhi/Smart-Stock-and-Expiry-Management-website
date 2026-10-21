from flask import Blueprint, Response
from app.utils.decorators import manager_required
from app.services.report_service import generate_sales_csv, generate_inventory_csv, generate_waste_csv, generate_daily_pnl_csv

bp = Blueprint("reports", __name__, url_prefix="/reports")

@bp.route("/export/sales.csv")
@manager_required
def export_sales():
    csv_data = generate_sales_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=stockwise_sales_report.csv"}
    )

@bp.route("/export/daily-pnl.csv")
@manager_required
def export_daily_pnl():
    csv_data = generate_daily_pnl_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=stockwise_daily_profit_loss.csv"}
    )

@bp.route("/export/inventory.csv")
@manager_required
def export_inventory():
    csv_data = generate_inventory_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=stockwise_inventory_report.csv"}
    )

@bp.route("/export/waste.csv")
@manager_required
def export_waste():
    csv_data = generate_waste_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=stockwise_waste_report.csv"}
    )

