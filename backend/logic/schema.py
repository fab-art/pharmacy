"""
Firestore schema definitions for the RAMA Pharmacy Counter-Verification System.
"""

COLLECTIONS = {
    'REFERRALS': 'referrals',
    'CASES': 'cases',
    'VOUCHERS': 'vouchers',
    'RULES': 'rules',
    'AUDIT_LOG': 'audit_log',
    'APPROVED_DRUGS': 'approved_drugs'
}

# Example document structures for reference/documentation
DOC_STRUCTURES = {
    'referral': {
        'source': str,  # 'compliance', 'internal', etc.
        'pharmacy_id': str,
        'reason': str,
        'submitted_date': 'Timestamp',
        'submitted_by': str,
        'status': str,  # 'PENDING_ALLOCATION', 'ALLOCATED'
        'documents': list,  # URLs to uploaded files
        'period': list,  # ['2024-10', '2024-11']
    },
    'case': {
        'pharmacy_id': str,
        'case_type': str,  # 'counter_verification'
        'status': str,  # 'REFERRAL_RECEIVED', 'ALLOCATED', 'DOCUMENTS_READY', 'ANALYSIS_IN_PROGRESS', 'ANALYSIS_COMPLETE', 'RECONCILE_IN_PROGRESS', 'RECONCILE_ACCEPTED', 'SIGNING_IN_PROGRESS', 'SIGNED', 'DEDUCTIONS_APPLIED', 'CASE_CLOSED'
        'created_date': 'Timestamp',
        'created_by': str,
        'assigned_to': str,
        'months_under_review': list,
        'total_deduction_proposed': float,
        'total_deduction_agreed': float,
        'docusign_envelope_id': str,
        'signature_status': str,
        'timeline': dict,
    },
    'voucher': {
        'case_id': str,
        'pharmacy_id': str,
        'voucher_date': 'Timestamp',
        'file_url': str,
        'ocr_text': str,
        'ocr_confidence': float,
        'scanned_status': str,  # 'PENDING', 'OCR_COMPLETE'
    },
    'rule': {
        'enabled': bool,
        'severity': str,  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
        'deduction_type': str,  # 'full_amount', 'percentage'
        'deduction_pct': float,
        'threshold': float,
        'last_updated': 'Timestamp',
    }
}
