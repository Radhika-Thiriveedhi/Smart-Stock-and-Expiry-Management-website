from datetime import datetime
from typing import Optional, Dict, Any, List
from werkzeug.security import generate_password_hash, check_password_hash
from app.storage.json_store import load_data, insert_record, update_record, find_by_id

def verify_password(stored_hash: str, raw_password: str) -> bool:
    if not stored_hash or not raw_password:
        return False
    if stored_hash.startswith(("scrypt:", "pbkdf2:")):
        try:
            return check_password_hash(stored_hash, raw_password)
        except Exception:
            return False
    # Backward compatibility fallback
    return stored_hash == raw_password

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    return find_by_id("users", user_id)

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    users = load_data("users", default=[])
    for u in users:
        if u.get("username", "").lower() == (username or "").strip().lower():
            return u
    return None

def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
    user = get_user_by_username(username)
    if not user:
        return None
    if not user.get("active", True):
        return None
    if verify_password(user.get("password_hash", ""), password):
        return user
    return None

def create_user(username: str, name: str, email: str, role: str, password: str) -> Dict[str, Any]:
    username = username.strip().lower()
    if get_user_by_username(username):
        raise ValueError(f"Username '{username}' is already taken.")
        
    if role not in ["owner", "manager", "employee"]:
        raise ValueError(f"Invalid role: {role}. Must be owner, manager, or employee.")
        
    password_hash = generate_password_hash(password)
    user_record = {
        "username": username,
        "name": name.strip(),
        "role": role,
        "password_hash": password_hash,
        "email": email.strip(),
        "active": True,
        "created_at": datetime.now().isoformat()
    }
    return insert_record("users", user_record, prefix="USR")

def update_user(user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if "password" in updates and updates["password"]:
        updates["password_hash"] = generate_password_hash(updates.pop("password"))
    return update_record("users", user_id, updates)

def list_users() -> List[Dict[str, Any]]:
    return load_data("users", default=[])
