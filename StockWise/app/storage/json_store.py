import json
import os
import shutil
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from app.config import Config
from app.storage.file_lock import locked_file
from app.storage.id_generator import generate_id

def get_file_path(filename: str) -> str:
    """Return the absolute path to a JSON data file."""
    if not filename.endswith(".json"):
        filename = f"{filename}.json"
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    return os.path.join(Config.DATA_DIR, filename)

def load_data(filename: str, default: Any = None) -> Any:
    """Safely read and parse a JSON file."""
    if default is None:
        default = []
    filepath = get_file_path(filename)
    if not os.path.exists(filepath):
        return default
        
    with locked_file(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return default
                return json.loads(content)
        except (json.JSONDecodeError, OSError):
            return default

def save_data(filename: str, data: Any) -> bool:
    """
    Safely write data to a JSON file atomically using a temporary file and lock.
    """
    filepath = get_file_path(filename)
    temp_path = f"{filepath}.tmp"
    
    with locked_file(filepath):
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            
            # Atomic replace
            if os.path.exists(filepath):
                os.replace(temp_path, filepath)
            else:
                os.rename(temp_path, filepath)
            return True
        except Exception as e:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise e

def find_by_id(filename: str, record_id: str, id_field: str = "id") -> Optional[Dict[str, Any]]:
    records = load_data(filename, default=[])
    for item in records:
        if str(item.get(id_field)) == str(record_id):
            return item
    return None

def query(filename: str, predicate: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
    records = load_data(filename, default=[])
    return [item for item in records if predicate(item)]

def insert_record(filename: str, record: Dict[str, Any], prefix: Optional[str] = None, id_field: str = "id") -> Dict[str, Any]:
    """
    Insert a record. If prefix is given and record has no ID, automatically generate one.
    """
    filepath = get_file_path(filename)
    with locked_file(filepath):
        records = load_data(filename, default=[])
        if prefix and not record.get(id_field):
            record[id_field] = generate_id(prefix, records, field=id_field)
            
        records.append(record)
        save_data(filename, records)
        return record

def update_record(filename: str, record_id: str, updates: Dict[str, Any], id_field: str = "id") -> Optional[Dict[str, Any]]:
    filepath = get_file_path(filename)
    with locked_file(filepath):
        records = load_data(filename, default=[])
        updated_item = None
        for i, item in enumerate(records):
            if str(item.get(id_field)) == str(record_id):
                records[i].update(updates)
                updated_item = records[i]
                break
        if updated_item is not None:
            save_data(filename, records)
        return updated_item

def delete_record(filename: str, record_id: str, id_field: str = "id") -> bool:
    filepath = get_file_path(filename)
    with locked_file(filepath):
        records = load_data(filename, default=[])
        new_records = [item for item in records if str(item.get(id_field)) != str(record_id)]
        if len(new_records) != len(records):
            save_data(filename, new_records)
            return True
        return False

def create_backup(tag: str = "manual") -> str:
    """Create a timestamped backup folder containing all JSON data files."""
    os.makedirs(Config.BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = os.path.join(Config.BACKUP_DIR, f"backup_{timestamp}_{tag}")
    os.makedirs(backup_folder, exist_ok=True)
    
    if os.path.exists(Config.DATA_DIR):
        for fname in os.listdir(Config.DATA_DIR):
            if fname.endswith(".json"):
                src = os.path.join(Config.DATA_DIR, fname)
                dst = os.path.join(backup_folder, fname)
                shutil.copy2(src, dst)
    return backup_folder

def log_audit(user_id: str, action: str, target_type: str, target_id: str, details: str = "") -> Dict[str, Any]:
    """Record an audit trail event in audit_log.json."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "details": details
    }
    return insert_record("audit_log", entry, prefix="AUD")
