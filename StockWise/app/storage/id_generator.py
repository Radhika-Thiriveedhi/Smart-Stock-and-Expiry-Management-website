import re
from typing import List, Dict, Any

def generate_id(prefix: str, records: List[Dict[str, Any]], field: str = "id") -> str:
    """
    Generate the next sequential ID with a given prefix (e.g., 'PRD-001', 'BAT-014').
    Finds the maximum integer suffix existing in the given records.
    """
    max_num = 0
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    
    for item in records:
        val = str(item.get(field, ""))
        match = pattern.match(val)
        if match:
            try:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
                
    next_num = max_num + 1
    return f"{prefix}-{next_num:03d}"
