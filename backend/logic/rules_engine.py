from datetime import datetime
from backend.logic.schema import COLLECTIONS

def run_counter_verification_analysis(db, case_id):
    """
    Core rules engine for counter-verification.
    """
    case_ref = db.collection(COLLECTIONS['CASES']).document(case_id)
    case_data = case_ref.get().to_dict()

    # Retrieve vouchers for this case
    vouchers = db.collection(COLLECTIONS['VOUCHERS']).where("case_id", "==", case_id).stream()

    # Load rules config
    rules_config = {doc.id: doc.to_dict() for doc in db.collection(COLLECTIONS['RULES']).stream()}

    # Load approved drugs (mocked as a list for now)
    approved_drugs = ["aspirin", "paracetamol", "amoxicillin"]

    analysis_results = []
    total_deduction = 0

    for voucher_doc in vouchers:
        voucher = voucher_doc.to_dict()
        ocr_text = voucher['ocr_text']

        # In a real scenario, we would parse the OCR text into line items
        # For now, we simulate finding some issues in the OCR text

        # Rule 1: Pharmacology Check
        if "oxycodone" in ocr_text.lower():
            res = {
                'line_id': 'V001-L01',
                'item': 'Oxycodone',
                'flags': ['UNAPPROVED_DRUG'],
                'deduction': 25000,
                'severity': 'CRITICAL',
                'reason': 'Drug not on RSSB approved list'
            }
            analysis_results.append(res)
            total_deduction += res['deduction']

        # Rule 2: Eligibility Check
        if "ben-5678" in ocr_text.lower():
            res = {
                'line_id': 'V001-L02',
                'item': 'Paracetamol',
                'beneficiary': 'BEN-5678',
                'flags': ['INELIGIBLE_BENEFICIARY'],
                'deduction': 15000,
                'severity': 'MEDIUM',
                'reason': 'Beneficiary not eligible on claim date'
            }
            analysis_results.append(res)
            total_deduction += res['deduction']

    # Update case with results
    case_ref.update({
        'status': 'ANALYSIS_COMPLETE',
        'total_deduction_proposed': total_deduction,
        'timeline.analysis_complete': datetime.now()
    })

    # Save results to a subcollection or dedicated doc
    case_ref.collection('analysis_results').document('summary').set({
        'results': analysis_results,
        'total_deduction': total_deduction,
        'updated_at': datetime.now()
    })

    return analysis_results, total_deduction
