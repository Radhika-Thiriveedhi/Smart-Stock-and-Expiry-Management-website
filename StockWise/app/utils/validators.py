import re
from datetime import datetime
from typing import Tuple, Optional, Any

def validate_sku(sku: str) -> Tuple[bool, Optional[str]]:
    sku = (sku or "").strip().upper()
    if not sku:
        return False, "SKU is required."
    if not re.match(r"^[A-Z0-9\-_]{2,30}$", sku):
        return False, "SKU must be 2-30 characters containing only letters, numbers, hyphens or underscores."
    return True, None

def validate_positive_int(val: Any, field_name: str, allow_zero: bool = True) -> Tuple[bool, Optional[str], int]:
    try:
        num = int(val)
        if allow_zero and num < 0:
            return False, f"{field_name} cannot be negative.", 0
        if not allow_zero and num <= 0:
            return False, f"{field_name} must be greater than zero.", 0
        return True, None, num
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid whole number.", 0

def validate_positive_float(val: Any, field_name: str, allow_zero: bool = False) -> Tuple[bool, Optional[str], float]:
    try:
        num = float(val)
        if allow_zero and num < 0.0:
            return False, f"{field_name} cannot be negative.", 0.0
        if not allow_zero and num <= 0.0:
            return False, f"{field_name} must be greater than zero.", 0.0
        return True, None, round(num, 2)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid decimal number.", 0.0

def validate_date_string(date_str: str, field_name: str) -> Tuple[bool, Optional[str]]:
    date_str = (date_str or "").strip()
    if not date_str:
        return False, f"{field_name} is required."
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, None
    except ValueError:
        return False, f"{field_name} must be a valid date in YYYY-MM-DD format."
