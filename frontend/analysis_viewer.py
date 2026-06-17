import streamlit as st
import firebase_admin
from firebase_admin import firestore
from backend.logic.schema import COLLECTIONS
from backend.logic.rules_engine import run_counter_verification_analysis

if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

st.title("🔍 Case Analysis Viewer")

# Select a case to view
assigned_to = "ahmed@rssb.rw" # Mock logged-in user
cases_ref = db.collection(COLLECTIONS['CASES']).where("assigned_to", "==", assigned_to).stream()
cases = [{"id": c.id, **c.to_dict()} for c in cases_ref]

if not cases:
    st.info("No cases assigned to you.")
else:
    case_ids = [c['id'] for c in cases]
    selected_case_id = st.selectbox("Select Case", case_ids)

    case_data = next(c for c in cases if c['id'] == selected_case_id)
    st.subheader(f"Case: {selected_case_id} ({case_data['status']})")

    if st.button("Run/Rerun Rules Engine"):
        with st.spinner("Analyzing vouchers..."):
            results, total = run_counter_verification_analysis(db, selected_case_id)
            st.success(f"Analysis complete. Total deduction proposed: {total} RWF")
            st.rerun()

    # Load results
    results_doc = db.collection(COLLECTIONS['CASES']).document(selected_case_id)\
        .collection('analysis_results').document('summary').get()

    if results_doc.exists:
        data = results_doc.to_dict()
        st.write(f"### Proposed Deductions: {data['total_deduction']} RWF")

        for item in data['results']:
            with st.expander(f"{item['item']} - {item['line_id']} ({item['severity']})"):
                st.write(f"**Reason:** {item['reason']}")
                st.write(f"**Flags:** {', '.join(item['flags'])}")
                st.write(f"**Amount:** {item['deduction']} RWF")

                override = st.number_input("Override Deduction", value=float(item['deduction']), key=f"ov_{item['line_id']}")
                notes = st.text_area("Notes", key=f"nt_{item['line_id']}")

        if st.button("Finalize Analysis & Send to Pharmacy"):
            db.collection(COLLECTIONS['CASES']).document(selected_case_id).update({
                'status': 'RECONCILE_IN_PROGRESS',
                'timeline.reconcile_started': firestore.SERVER_TIMESTAMP
            })
            st.success("Case status updated to RECONCILE_IN_PROGRESS")
            st.rerun()
    else:
        st.warning("No analysis results found. Please run the rules engine.")
