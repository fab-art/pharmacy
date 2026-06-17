import streamlit as st
import firebase_admin
from firebase_admin import firestore
from backend.logic.schema import COLLECTIONS

if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

st.title("⚖️ Pharmacy Reconciliation Portal")

# In reality, this would be authenticated via a secure link
case_id = st.text_input("Enter Case ID to view findings (e.g., RAMA-CV-2025-0001)")

if case_id:
    case_ref = db.collection(COLLECTIONS['CASES']).document(case_id)
    case_data = case_ref.get().to_dict()

    if not case_data:
        st.error("Case not found.")
    else:
        st.subheader(f"Findings for {case_data['pharmacy_id']}")

        results_doc = case_ref.collection('analysis_results').document('summary').get()
        if results_doc.exists:
            data = results_doc.to_dict()
            st.write(f"**Total Proposed Deduction:** {data['total_deduction']} RWF")

            responses = {}
            for item in data['results']:
                with st.expander(f"Line {item['line_id']}: {item['item']}"):
                    st.write(f"Reason: {item['reason']}")
                    st.write(f"Proposed Deduction: {item['deduction']} RWF")

                    choice = st.radio("Action", ["Accept", "Dispute"], key=f"resp_{item['line_id']}")
                    if choice == "Dispute":
                        reason = st.text_area("Dispute Reason", key=f"disp_{item['line_id']}")
                        responses[item['line_id']] = {'status': 'disputed', 'reason': reason}
                    else:
                        responses[item['line_id']] = {'status': 'accepted'}

            if st.button("Submit Response"):
                # Update case with pharmacy response
                case_ref.update({
                    'status': 'RECONCILE_ACCEPTED', # Or PARTIALLY_ACCEPTED
                    'pharmacy_response': responses,
                    'timeline.reconcile_completed': firestore.SERVER_TIMESTAMP
                })
                st.success("Your response has been submitted. RSSB will review and generate the final report.")
        else:
            st.warning("Analysis results not yet available for this case.")
