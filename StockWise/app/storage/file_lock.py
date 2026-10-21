import os
import threading
from contextlib import contextmanager

# In-memory lock registry for file paths to prevent race conditions within the process
# Using RLock (Reentrant Lock) so nested calls on the same thread (e.g., insert_record -> save_data) do not deadlock
_locks = {}
_registry_lock = threading.Lock()

def get_file_lock(filepath: str) -> threading.RLock:
    norm_path = os.path.normcase(os.path.abspath(filepath))
    with _registry_lock:
        if norm_path not in _locks:
            _locks[norm_path] = threading.RLock()
        return _locks[norm_path]

@contextmanager
def locked_file(filepath: str):
    """
    Context manager that acquires an exclusive re-entrant thread lock on a specific file path
    to ensure atomic read-modify-write sequences without self-deadlock.
    """
    lock = get_file_lock(filepath)
    lock.acquire()
    try:
        yield
    finally:
        lock.release()

