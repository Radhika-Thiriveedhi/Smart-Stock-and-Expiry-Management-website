from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional

def parse_date(date_str: str) -> Optional[date]:
    """Parse YYYY-MM-DD string into date object."""
    if not date_str:
        return None
    try:
        # Handle full ISO timestamp or just date
        if "T" in date_str:
            return datetime.fromisoformat(date_str).date()
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

def format_date(d: Optional[date]) -> str:
    """Format date object into YYYY-MM-DD."""
    if not d:
        return ""
    return d.strftime("%Y-%m-%d")

def get_current_date() -> date:
    """Return the current system date."""
    return datetime.now().date()

def calculate_expiry_status(expiry_date_str: str, near_days: int = 7, critical_days: int = 3, ref_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Calculate expiry status for a given batch expiry date.
    Returns:
      {
        'status': 'EXPIRED' | 'CRITICAL' | 'WARNING' | 'UPCOMING' | 'HEALTHY',
        'days_left': int,
        'label': str,
        'badge_class': str
      }
    """
    exp_date = parse_date(expiry_date_str)
    if not exp_date:
        return {
            "status": "UNKNOWN",
            "days_left": 9999,
            "label": "No Expiry Date",
            "badge_class": "badge-muted"
        }
        
    today = ref_date or get_current_date()
    delta = (exp_date - today).days
    
    if delta < 0:
        days_ago = abs(delta)
        return {
            "status": "EXPIRED",
            "days_left": delta,
            "label": f"Expired {days_ago} day{'s' if days_ago != 1 else ''} ago",
            "badge_class": "badge-danger"
        }
    elif delta == 0:
        return {
            "status": "CRITICAL",
            "days_left": 0,
            "label": "Expires Today",
            "badge_class": "badge-danger"
        }
    elif delta <= critical_days:
        return {
            "status": "CRITICAL",
            "days_left": delta,
            "label": f"Expires in {delta} day{'s' if delta != 1 else ''}",
            "badge_class": "badge-danger"
        }
    elif delta <= near_days:
        return {
            "status": "WARNING",
            "days_left": delta,
            "label": f"Expires in {delta} days",
            "badge_class": "badge-warning"
        }
    elif delta <= 30:
        return {
            "status": "UPCOMING",
            "days_left": delta,
            "label": f"Expires in {delta} days",
            "badge_class": "badge-info"
        }
    else:
        return {
            "status": "HEALTHY",
            "days_left": delta,
            "label": f"Good ({delta} days left)",
            "badge_class": "badge-success"
        }

def get_date_ranges():
    """Return common date boundaries (today, this week start, this month start)."""
    today = get_current_date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = date(today.year, today.month, 1)
    return {
        "today": today,
        "week_start": start_of_week,
        "month_start": start_of_month
    }
