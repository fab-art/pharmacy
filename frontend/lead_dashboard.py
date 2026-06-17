import streamlit as st
import firebase_admin
from firebase_admin import firestore
from backend.logic.schema import COLLECTIONS
from backend.logic.referral_manager import initialize_case

if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

st.set_page_config(layout="wide")
st.title("👨‍💼 Lead CVO Dashboard")

st.subheader("Unallocated Referrals")

referrals_ref = db.collection(COLLECTIONS['REFERRALS']).where("status", "==", "PENDING_ALLOCATION").stream()
referrals = [{"id": r.id, **r.to_dict()} for r in referrals_ref]

if not referrals:
    st.info("No unallocated referrals.")
else:
    for ref in referrals:
        with st.expander(f"Referral {ref['id']} - {ref.get('pharmacy_name', 'Unknown Pharmacy')}"):
            st.write(f"**Source:** {ref['source']}")
            st.write(f"**Reason:** {ref['reason']}")
            st.write(f"**Period:** {', '.join(ref['period'])}")

            cvo_staff = ["Ahmed", "Sarah", "John", "Grace"]
            assigned_to = st.selectbox("Assign to CVO", cvo_staff, key=f"assign_{ref['id']}")

            if st.button("Allocate & Initialize Case", key=f"btn_{ref['id']}"):
                try:
                    case_id = initialize_case(db, ref['id'], assigned_to=f"{assigned_to.lower()}@rssb.rw")
                    st.success(f"Case {case_id} initialized and assigned to {assigned_to}.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error initializing case: {e}")

st.divider()
st.subheader("Active Cases")
cases_ref = db.collection(COLLECTIONS['CASES']).stream()
cases = [{"id": c.id, **c.to_dict()} for c in cases_ref]

if not cases:
    st.info("No active cases.")
else:
    st.table(cases)
