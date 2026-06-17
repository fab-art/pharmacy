import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from backend.logic.referral_manager import create_referral

# Initialize Firebase (assuming creds are handled by environment in GCP)
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

st.title("📋 Counter-Verification Referral Intake")

with st.form("referral_form"):
    st.subheader("Pharmacy Details")
    pharmacy_name = st.text_input("Pharmacy Name")
    pharmacy_id = st.text_input("Pharmacy ID")

    st.subheader("Referral Information")
    source = st.selectbox("Source", ["Compliance", "Manager Benefits", "Internal Audit", "Fraud Detection"])
    reason = st.text_area("Reason for Referral")

    st.subheader("Review Period")
    start_month = st.date_input("Start Month")
    end_month = st.date_input("End Month")

    st.subheader("Supporting Documents")
    uploaded_files = st.file_uploader("Upload Referral Documents", accept_multiple_files=True)

    submitted = st.form_submit_button("Submit Referral")

    if submitted:
        if not pharmacy_id or not reason:
            st.error("Pharmacy ID and Reason are required.")
        else:
            referral_data = {
                'pharmacy_name': pharmacy_name,
                'pharmacy_id': pharmacy_id,
                'source': source.lower(),
                'reason': reason,
                'period': [start_month.strftime('%Y-%m'), end_month.strftime('%Y-%m')],
                'submitted_by': 'officer@rssb.rw' # Mock user
            }

            try:
                ref_id = create_referral(db, referral_data)
                st.success(f"Referral successfully submitted! ID: {ref_id}")
            except Exception as e:
                st.error(f"Error submitting referral: {e}")
