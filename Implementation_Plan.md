# Implementation Plan: RAMA Pharmacy Counter-Verification System

This document outlines the detailed plan and structure for building the RAMA Pharmacy Counter-Verification System based on the architectural design.

## Phase 1: Foundation and Referral Intake (MVP)
- **Objective:** Establish the project structure and core data flow for incoming referrals.
- **Components:**
  - `backend/logic/schema.py`: Defines the Firestore collection and document structure.
  - `backend/logic/referral_manager.py`: Logic for creating referrals and initializing cases.
  - `frontend/referral_intake.py`: Streamlit interface for compliance officers to submit pharmacy referrals.
  - `frontend/lead_dashboard.py`: Dashboard for Lead CVOs to allocate cases to staff.

## Phase 2: Document Retrieval and Automated Analysis
- **Objective:** Automate the extraction of data from vouchers and run the initial rules engine.
- **Components:**
  - `backend/functions/document_processor.py`: Integration with GCS and Cloud Vision API for OCR processing.
  - `backend/logic/rules_engine.py`: Core logic for pharmacology, eligibility, and pricing checks.
  - `frontend/analysis_viewer.py`: UI for CVOs to review flagged items and perform manual overrides.

## Phase 3: Reconciliation and Report Sign-off
- **Objective:** Enable partner interaction and finalize the verification through electronic signatures.
- **Components:**
  - `frontend/pharmacy_portal.py`: Secure portal for pharmacy partners to respond to proposed deductions.
  - `backend/logic/report_builder.py`: Logic for generating the final Counter-Verification Report PDF.
  - `backend/functions/docusign_service.py`: Sequential sign-off workflow via DocuSign API.

## Phase 4: Deduction Application and Audit
- **Objective:** Close the loop by applying deductions and maintaining a complete audit trail.
- **Components:**
  - `backend/functions/deduction_service.py`: Posting final agreed deductions to the IHBS API.
  - `backend/logic/audit_trail.py`: Centralized logging for all system actions.
  - `config/firestore.rules`: Security rules for role-based access control.

## Project Structure
- `frontend/`: Streamlit application files.
- `backend/logic/`: Pure Python business logic and data management.
- `backend/functions/`: Integration services and cloud-triggered functions.
- `config/`: Infrastructure and security configuration.
- `tests/`: Unit and integration tests.
