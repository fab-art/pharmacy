from datetime import datetime
from backend.logic.schema import COLLECTIONS

def log_action(db, actor, action, case_id=None, details=None):
    """
    Logs an action to the audit_log collection.
    """
    log_entry = {
        'actor': actor,
        'action': action,
        'case_id': case_id,
        'details': details or {},
        'timestamp': datetime.now()
    }

    db.collection(COLLECTIONS['AUDIT_LOG']).add(log_entry)
