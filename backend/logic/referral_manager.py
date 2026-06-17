from datetime import datetime
from firebase_admin import firestore
from backend.logic.schema import COLLECTIONS

def create_referral(db, referral_data):
    """
    Creates a new referral in Firestore.
    """
    referral_data['submitted_date'] = datetime.now()
    referral_data['status'] = 'PENDING_ALLOCATION'

    # Add to referrals collection
    ref_ref = db.collection(COLLECTIONS['REFERRALS']).add(referral_data)
    return ref_ref[1].id

def initialize_case(db, referral_id, assigned_to=None):
    """
    Initializes a new case from a referral.
    """
    referral_ref = db.collection(COLLECTIONS['REFERRALS']).document(referral_id)
    referral = referral_ref.get().to_dict()

    if not referral:
        raise ValueError(f"Referral {referral_id} not found")

    # Generate Case ID (RAMA-CV-YYYY-XXXX)
    # For a real implementation, we'd use a transaction to increment a counter
    year = datetime.now().year
    case_count = len(db.collection(COLLECTIONS['CASES']).get()) + 1
    case_id = f"RAMA-CV-{year}-{case_count:04d}"

    case_data = {
        'pharmacy_id': referral['pharmacy_id'],
        'referral_id': referral_id,
        'case_type': 'counter_verification',
        'status': 'ALLOCATED' if assigned_to else 'REFERRAL_RECEIVED',
        'created_date': datetime.now(),
        'created_by': referral['submitted_by'],
        'assigned_to': assigned_to,
        'months_under_review': referral.get('period', []),
        'timeline': {
            'referral_received': referral['submitted_date'],
            'case_initialized': datetime.now()
        }
    }

    db.collection(COLLECTIONS['CASES']).document(case_id).set(case_data)

    # Update referral status
    referral_ref.update({'status': 'ALLOCATED' if assigned_to else 'CASE_CREATED'})

    return case_id
