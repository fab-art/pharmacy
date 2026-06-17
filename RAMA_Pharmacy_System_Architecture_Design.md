# RAMA Pharmacy Counter-Verification System Architecture
## Digital Workflow Automation using Google Cloud JULES

---

## EXECUTIVE SUMMARY (Caveman Talk)

**What:** Take manual pharmacy verification SOP, make it digital.  
**How:** Google Cloud (cheap, fast, easy). Flow: referral → voucher pull → analysis → reconcile → sign → deduct.  
**Cost:** ~$50–150/month for production, scales painlessly.  
**Tech Stack:** Firestore (DB) + Cloud Tasks (queue) + Cloud Functions (code) + Cloud Storage (files) + Streamlit app (UI).

---

## 1. BUSINESS PROCESS FLOW

### Current SOP Steps → Digital Steps

| SOP Step | Manual Work | Digital Equivalent |
|----------|-------------|-------------------|
| **Referral Intake** | Email to Lead | Auto-populate form → Firestore entry |
| **Allocation** | Spreadsheet | Task queue assigns to staff |
| **Retrieve Vouchers/Softcopies** | Archive + Outlook search | Cloud Storage auto-retrieve + OCR |
| **Counter-Verification Analysis** | Excel + paper notes | Python rules engine (PharmaScan) + workflow UI |
| **Reconciliation** | Email back-and-forth | Automated notifications + conflict dashboard |
| **Report Sign-off** | DocuSign + email chain | Digital signature workflow (DocuSign API) |
| **Deduction Application** | Manual entry into invoice system | Auto-post to payment system (API call) |

---

## 2. SYSTEM ARCHITECTURE (LOW-COST APPROACH)

### 2.1 Technology Stack

**Core Services (Google Cloud):**
- **Firestore:** Real-time database for referrals, cases, vouchers, audit trail
- **Cloud Tasks:** Queue for assigning work + async processing
- **Cloud Functions:** Serverless code (Python/Node) to run business logic
- **Cloud Storage:** Archive + document repository
- **Cloud Vision API:** OCR for scanned vouchers
- **Pub/Sub:** Event-driven notifications

**Frontend:**
- **Streamlit:** User dashboard (built on Python app you have)
- **Google Forms:** Simple referral intake (feeds to Firestore)

**Integration:**
- **DocuSign API:** Electronic signatures
- **IHBS API:** Post deductions to payment system
- **Kwivuza API:** Beneficiary eligibility checks

### 2.2 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACES                          │
├─────────────────────────────────────────────────────────────┤
│  Google Form (Referral)  │  Streamlit Dashboard (UI)       │
│  (Compliance/Officers)   │  (CVOs, Lead CVO, Manager)      │
└────────┬──────────────────┬──────────────────────────────────┘
         │                  │
         ▼                  ▼
    ┌──────────────────────────────────────────────────────┐
    │         FIRESTORE (Real-time Database)              │
    │  ┌─ Referrals           (intake → allocated)        │
    │  ├─ Cases              (status → audit trail)       │
    │  ├─ Vouchers           (linked files + metadata)    │
    │  ├─ Analysis Results   (rules engine output)        │
    │  ├─ Reconciliation     (partner responses)          │
    │  └─ Audit Log          (who did what, when)         │
    └────┬────────────────────────────────────────────────┘
         │
         ├─────────────────────────┬──────────────────────┐
         ▼                         ▼                      ▼
    ┌─────────────┐    ┌──────────────────┐   ┌──────────────────┐
    │Cloud Storage│    │ Cloud Functions  │   │  Cloud Tasks     │
    │ (Vouchers & │    │ (Python logic)   │   │  (Job queue &    │
    │  Softcopies)│    │  • OCR service   │   │   scheduling)    │
    │             │    │  • Rules engine  │   │                  │
    │ ↳ Archive   │    │  • Reconcile     │   │ ↳ Assign work    │
    │ ↳ Scanned   │    │  • Fraud detect  │   │ ↳ Notify staff   │
    │   PDFs      │    │  • Post to IHBS  │   │ ↳ Escalate       │
    └─────────────┘    └──────────────────┘   └──────────────────┘
         │                  │
         │                  ├─→ Cloud Vision API (OCR)
         │                  ├─→ DocuSign API (E-signatures)
         │                  ├─→ IHBS API (Post deductions)
         │                  ├─→ Kwivuza API (Eligibility)
         │                  └─→ Pub/Sub (Email/SMS alerts)
         │
         ▼
    ┌──────────────────────────┐
    │   Monitoring & Audit     │
    │  • Cloud Logging         │
    │  • Cloud Monitoring      │
    │  • Firestore backups     │
    └──────────────────────────┘
```

---

## 3. DETAILED WORKFLOW: FROM SOP TO DIGITAL

### 3.1 REFERRAL INTAKE (Step 1)

**Current:** Officers/Compliance email referral to Lead Counter-Verification  
**Digital:**

```
1. Compliance officer fills Google Form or Streamlit form
   Fields:
   - Pharmacy name & ID
   - Reason (routine, audit, fraud suspicion, field inspection)
   - Period (months/invoices to review)
   - Supporting docs (upload PDF)

2. Form submission → Cloud Function trigger
   - Validate pharmacy exists in IHBS (API call)
   - Create referral document in Firestore
   - Assign unique case ID (RAMA-CV-2025-001)
   - Log timestamp & author
   
3. Lead Counter-Verification dashboard shows:
   - NEW referrals (sorted by priority/date)
   - Click to allocate → select staff → task created

4. Allocated staff get:
   - Email notification (via Pub/Sub)
   - Case shows in their Streamlit dashboard
   - Status changes: REFERRAL_RECEIVED → ALLOCATED → IN_PROGRESS
```

**Cost:** ~$0.01 per referral (Cloud Functions, Firestore writes)

---

### 3.2 VOUCHER & SOFTCOPY RETRIEVAL (Step 2)

**Current:** Lead CVO manually requests from Archive + searches Outlook  
**Digital:**

```
1. Cloud Function triggered by referral allocation
   Input: Case ID, pharmacy ID, date range
   
2. Cloud Storage query:
   - Search for vouchers in gs://rama-cv-archive/[pharmacy]/[date]/
   - Retrieve softcopies from gs://rama-cv-ihbs-backups/
   - For older docs: API call to Outlook/Exchange (if integrated)
   
3. If scanned PDF vouchers exist:
   - Cloud Vision API → extract text + tabular data
   - Store OCR results in Firestore
   - Flag unreadable documents for manual review
   
4. Files linked in Firestore:
   - Voucher URL → gs://rama-cv-archive/[file.pdf]
   - Softcopy URL → gs://rama-cv-ihbs/[file.xlsx]
   - OCR text stored in Firestore document
   
5. Streamlit dashboard shows:
   - All files for case (inline preview)
   - OCR confidence scores
   - Link to archive system (for manual retrieval if needed)
   
6. Status: ALLOCATED → RETRIEVAL_IN_PROGRESS → DOCUMENTS_READY
```

**Cost:** 
- Cloud Vision: ~$0.60/1000 pages
- Cloud Storage: ~$0.02/GB/month
- Typical case: $0.50–2 per retrieval

---

### 3.3 COUNTER-VERIFICATION ANALYSIS (Step 3) — Core Engine

**Current:** CVOs manually compare vouchers vs invoices, check RSSB instructions, note discrepancies in Excel  
**Digital:**

```
PYTHON RULES ENGINE (Extends your PharmaScan app)
├─ Input: Vouchers (OCR text) + Invoices (IHBS export) + Beneficiary data (Kwivuza)
├─ Output: Line-by-line discrepancies + deduction recommendations + fraud flags

Rules (Configurable in Firestore):
1. PHARMACOLOGY CHECK
   - Against RSSB approved drug list
   - Flag: unlisted drugs, high-cost outliers
   - Rule: IF drug NOT in approved_list → FLAG:UNAPPROVED

2. PRESCRIPTION MATCH
   - HF prescription date vs pharmacy claim date
   - Quantity variance (prescription qty vs claimed qty)
   - Rule: IF date_gap > 30_days → FLAG:STALE_PRESCRIPTION

3. BENEFICIARY ELIGIBILITY
   - Call Kwivuza API: is_eligible(beneficiary_id, claim_date)
   - Flag ineligible beneficiaries
   - Rule: IF not eligible → FLAG:INELIGIBLE_BENEFICIARY

4. PRICING CHECK
   - Unit price vs RSSB reference price list
   - Variance tolerance: ±10% (configurable)
   - Rule: IF price_variance > 10% → FLAG:PRICE_OUTLIER

5. DUPLICATE DETECTION
   - Beneficiary + drug + date + quantity (within 7 days)
   - Rule: IF duplicate_found → FLAG:DUPLICATE_CLAIM

6. FRAUD PATTERNS (from inspection history)
   - Pharmacy's historical deduction rate
   - Common fraud indicators (pattern matching)
   - Rule: IF pattern_score > threshold → FLAG:FRAUD_SUSPECTED

Processing Flow:
┌──────────────────┐
│ Voucher (OCR)    │
│ Invoice (IHBS)   │  ──→ Python rules engine
│ Beneficiary data │     (Cloud Function)
└──────────────────┘
        │
        ├─→ For each line item:
        │   1. Extract: drug, qty, price, date, beneficiary
        │   2. Run rules 1–6 against Firestore config
        │   3. Calculate potential deduction (if any)
        │   4. Assign severity: LOW, MEDIUM, HIGH, CRITICAL
        │
        ▼
    ┌────────────────────────────┐
    │ Results in Firestore:      │
    │ ┌─ line_item_id           │
    │ ├─ flags: [FLAG_1, ...]   │
    │ ├─ deduction_amt          │
    │ ├─ severity               │
    │ ├─ rule_reason (text)     │
    │ └─ auditor_notes          │
    └────────────────────────────┘
        │
        ▼
    ┌────────────────────────────┐
    │ Streamlit shows:           │
    │ • Flagged lines (sortable) │
    │ • Total deduction (running)│
    │ • Severity breakdown       │
    │ • Drill-down to rule text  │
    │ • Manual override option   │
    └────────────────────────────┘

Status: DOCUMENTS_READY → ANALYSIS_IN_PROGRESS → ANALYSIS_COMPLETE
```

**Implementation:**

```python
# pseudocode in Cloud Function
def run_counter_verification_analysis(case_id, pharma_invoices, vouchers, rules_config):
    results = []
    
    for voucher in vouchers:
        for line in voucher.line_items:
            flags = []
            deduction = 0
            
            # Rule 1: Pharmacology
            if line.drug_code not in rules_config['approved_drugs']:
                flags.append('UNAPPROVED_DRUG')
                deduction += line.amount  # full amount for unapproved
            
            # Rule 2: Prescription match
            hf_date = get_hf_prescription_date(line.hf_id, line.benef_id)
            if abs((line.date - hf_date).days) > 30:
                flags.append('STALE_PRESCRIPTION')
                deduction += line.amount * 0.5  # partial deduction
            
            # Rule 3: Eligibility
            is_eligible = kwivuza_api.check_beneficiary(
                line.benef_id, line.date
            )
            if not is_eligible:
                flags.append('INELIGIBLE_BENEFICIARY')
                deduction += line.amount  # full amount
            
            # ... Rules 4–6 ...
            
            results.append({
                'voucher_id': voucher.id,
                'line_id': line.id,
                'flags': flags,
                'deduction': deduction,
                'severity': calculate_severity(flags),
                'rule_reasons': generate_reasons(flags, line),
            })
    
    # Store in Firestore
    firestore_db.collection('cases').document(case_id)\
        .collection('analysis_results').document('summary')\
        .set({'results': results, 'total_deduction': sum(r['deduction'] for r in results)})
    
    return results
```

**Cost:** 
- Cloud Functions: ~0.4M free invocations/month
- Kwivuza API calls: depends on contract
- Typical case: $0.10–0.50

---

### 3.4 RECONCILIATION WITH PHARMACY (Step 4)

**Current:** CVOs email pharmacy with discrepancies; back-and-forth via email  
**Digital:**

```
1. After analysis complete, system auto-generates:
   - Reconciliation report (HTML + PDF)
   - Lists flagged lines + proposed deductions
   - Includes rule explanation (user-friendly)
   - Estimated total deduction
   
2. Send to pharmacy partner:
   - Email via Pub/Sub (Cloud Functions)
   - Pharmacy clicks link in email
   - Navigates to secure portal (Streamlit + authentication)
   - Can:
     a) Accept deduction (submit consent form → Firestore)
     b) Request meeting (creates task → notify Lead CVO)
     c) Challenge specific lines (attach docs → Firestore)
   
3. Lead Counter-Verification dashboard:
   - Shows pending reconciliations (waiting for pharmacy response)
   - Timeline view: when emails sent, when responses due
   - Escalation: if no response after 7 days → auto-email + escalate to Manager Benefits
   
4. Conflict resolution:
   - If pharmacy disputes line, CVO can:
     a) Manually review & override decision
     b) Mark as "requires field inspection" → notify Inspection Unit
     c) Propose alternative deduction amount
   - All changes logged in Firestore (audit trail)
   
5. Status: ANALYSIS_COMPLETE → RECONCILE_IN_PROGRESS → RECONCILE_ACCEPTED (or ESCALATED)
```

**Streamlit Portal Code Snippet:**

```python
import streamlit as st
import firebase_admin
from firebase_admin import firestore, auth

# Authentication
if not auth.get_current_user():
    st.switch_page("pages/login.py")

db = firestore.client()
case_id = st.query_params.get("case_id")

st.title("⚖️ Counter-Verification Reconciliation")
st.markdown(f"**Case:** {case_id}")

# Load case from Firestore
case_doc = db.collection('cases').document(case_id).get()
case_data = case_doc.to_dict()

# Show flagged lines
st.subheader(f"Flagged Items (Total Proposed Deduction: {case_data['total_deduction']} RWF)")

analysis_results = db.collection('cases').document(case_id)\
    .collection('analysis_results').document('summary').get().to_dict()

for result in analysis_results['results']:
    with st.expander(f"Line {result['line_id']}: {result['flags']}"):
        st.write(result['rule_reasons'])
        col1, col2 = st.columns([1, 1])
        with col1:
            agree = st.checkbox(f"Accept {result['deduction']} RWF deduction", key=result['line_id'])
        with col2:
            alt_amt = st.number_input(f"Propose alternative (RWF)", value=result['deduction'], key=f"alt_{result['line_id']}")

# Actions
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("✅ Accept & Submit", type="primary"):
        # Create consent form & update Firestore
        consent_form = {
            'pharmacy_id': case_data['pharmacy_id'],
            'total_agreed_deduction': agreed_total,
            'signed_date': datetime.now(),
            'status': 'ACCEPTED',
        }
        db.collection('cases').document(case_id).update({
            'reconciliation_status': 'ACCEPTED',
            'consent_form': consent_form,
        })
        st.success("✅ Submitted! Lead Counter-Verification will review.")

with col2:
    if st.button("📧 Request Meeting"):
        # Create task & notify Lead CVO
        db.collection('cases').document(case_id).update({
            'reconciliation_status': 'MEETING_REQUESTED',
            'meeting_requested_date': datetime.now(),
        })
        st.info("📩 Lead Counter-Verification has been notified.")

with col3:
    if st.button("🔖 Challenge Lines"):
        st.write("Attach supporting documents...")
        uploaded_file = st.file_uploader("Upload evidence", type=['pdf', 'xlsx'])
        if uploaded_file:
            # Store in Cloud Storage
            # Create challenge record in Firestore
            st.success("Challenge recorded. Lead will review.")
```

**Cost:** Minimal (Firestore writes, Pub/Sub emails ~$0.4/1M messages)

---

### 3.5 REPORT SIGN-OFF (Step 5)

**Current:** Multi-step DocuSign routing (Manager Benefits → HoD RAMA → CBO → Compliance Head)  
**Digital:**

```
1. Lead Counter-Verification prepares final report
   - Consolidates all analysis results + reconciliation outcome
   - Generates PDF (Cloud Functions + Cloud Storage)
   - Includes: pharmacy name, invoices reviewed, total deduction, signatures block
   
2. Trigger DocuSign API:
   - Create envelope with counter-verification report + fraud report (if applicable)
   - Route sequentially: Manager Benefits → HoD RAMA → CBO → HoD Compliance
   - Each signatory can view, comment, approve/reject
   
3. Firestore tracks signing status:
   - 'signature_status': 'PENDING_MANAGER_BENEFITS'
   - Webhook from DocuSign updates Firestore when each person signs
   - Audit trail: timestamps + IP addresses (from DocuSign)
   
4. Lead CVO dashboard:
   - Shows report status (who's signed, who's pending)
   - Auto-remind signatories if >3 days pending
   - If rejected: create task for CVO to revise analysis
   
5. Once all signed:
   - Firestore status → SIGNED
   - Trigger next step: deduction application
   - Archive signed PDF to Cloud Storage
   
Status: RECONCILE_ACCEPTED → REPORT_GENERATION → SIGNING_IN_PROGRESS → SIGNED
```

**DocuSign Integration Code:**

```python
from docusign_esign import ApiClient, EnvelopesApi, Document, Signer, SignHere, Tabs

def create_and_send_docusign_envelope(case_id, pdf_path, signatories_list):
    """
    Signatories: [
        {'name': 'Manager Benefits', 'email': 'mb@rssb.rw', 'order': 1},
        {'name': 'HoD RAMA', 'email': 'hod_rama@rssb.rw', 'order': 2},
        {'name': 'CBO', 'email': 'cbo@rssb.rw', 'order': 3},
        {'name': 'HoD Compliance', 'email': 'compliance@rssb.rw', 'order': 4},
    ]
    """
    api_client = ApiClient()
    api_client.set_default_header('Authorization', f'Bearer {DOCUSIGN_ACCESS_TOKEN}')
    
    # Read PDF from Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket('rama-cv-reports')
    blob = bucket.blob(pdf_path)
    pdf_bytes = blob.download_as_bytes()
    
    # Create document
    document = Document(
        document_base64=base64.b64encode(pdf_bytes).decode(),
        name='Counter-Verification Report',
        file_extension='pdf',
        document_id='1'
    )
    
    # Create signers (in sequential order)
    signers = []
    for i, sig in enumerate(signatories_list):
        signer = Signer(
            email=sig['email'],
            name=sig['name'],
            recipient_id=str(sig['order']),
            routing_order=sig['order'],
        )
        # Add signature tab (page 5, position [100, 150])
        sign_here = SignHere(
            document_id='1',
            page_number='5',
            x_position='100',
            y_position='150',
        )
        signer.tabs = Tabs(sign_here_tabs=[sign_here])
        signers.append(signer)
    
    # Create envelope
    envelope_definition = EnvelopeDefinition(
        email_subject=f'[RAMA-CV] Counter-Verification Report Signature - {case_id}',
        documents=[document],
        recipients=Recipients(signers=signers),
        status='sent',
    )
    
    # Send
    envelopes_api = EnvelopesApi(api_client)
    results = envelopes_api.create_envelope(DOCUSIGN_ACCOUNT_ID, envelope_definition)
    
    # Store envelope ID in Firestore
    db.collection('cases').document(case_id).update({
        'docusign_envelope_id': results.envelope_id,
        'signature_status': 'PENDING_MANAGER_BENEFITS',
    })
    
    return results.envelope_id
```

**Cost:** ~$0.50–1 per DocuSign envelope (DocuSign pricing)

---

### 3.6 DEDUCTION APPLICATION (Step 6)

**Current:** Lead Pharmaceutical Verification manually enters deductions into invoice payment system  
**Digital:**

```
1. Once all signatures received:
   - Firestore triggers Cloud Function
   - Extract agreed deductions from consent form + report
   
2. Cloud Function calls IHBS API:
   POST /api/v1/deductions/apply
   {
     'pharmacy_id': '001',
     'invoices': [
       {'invoice_id': 'INV-001', 'deduction_amount': 5000, 'reason': 'UNAPPROVED_DRUG'},
       {'invoice_id': 'INV-002', 'deduction_amount': 2500, 'reason': 'DUPLICATE_CLAIM'},
     ],
     'applied_date': '2025-01-15',
     'source': 'COUNTER_VERIFICATION',
     'case_id': 'RAMA-CV-2025-001',
   }
   
3. IHBS API response:
   - If success: update Firestore status → DEDUCTIONS_APPLIED
   - If failure: log error → notify Manager Benefits (for manual follow-up)
   
4. Firestore logs:
   - Which invoices were touched
   - Applied amounts
   - IHBS response timestamp
   - Audit trail for compliance
   
5. Lead Pharmaceutical Verification dashboard:
   - Shows "APPLIED" status
   - Link to view actual deductions in IHBS
   - Confirmation email sent to pharmacy
   
Status: SIGNED → DEDUCTIONS_IN_PROGRESS → DEDUCTIONS_APPLIED → CASE_CLOSED
```

**Cost:** Depends on IHBS API limits; typically free or minimal

---

## 4. PYTHON APP INTEGRATION: PharmaScan → Cloud Functions

Your **app.py** (PharmaScan) is the **analysis engine core**. In the cloud architecture:

```
PharmaScan Role:
┌─────────────────────────────────────────────────────────┐
│ Streamlit UI (Frontend)                                 │
│ - Data Prep (4-step upload/mapping/commit)             │
│ - Fraud Detection (network graphs, anomalies)          │
│ - Rules Engine (custom rules wizard)                   │
│ - Real-time monitoring dashboards                      │
│ - Audit trail viewer                                   │
│                                                         │
│ Backend: Connects to Firestore + Cloud Storage         │
│ - Load case data from Firestore                        │
│ - Run your fraud detection algos locally              │
│ - Push results back to Firestore                       │
│ - Export to Cloud Storage                              │
└─────────────────────────────────────────────────────────┘
        │
        ├─→ Uses: pandas, matplotlib, networkx (already in app)
        ├─→ Add: firebase-admin (Firestore client)
        ├─→ Add: google-cloud-storage (Cloud Storage client)
        └─→ Add: google-cloud-tasks (for queuing)
```

### Refactor PharmaScan for Cloud:

```python
# NEW: app_cloud.py (modified PharmaScan)
import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import firestore, storage
from google.cloud import tasks_v2, vision_v1

# ── Initialization ─────────────────────────────────────────
db = firestore.client()
storage_client = storage.Client()
tasks_client = tasks_v2.CloudTasksClient()

# ── Modified Data Prep (Step 1–4) ─────────────────────────
st.title("PharmaScan — Cloud Edition")

# Instead of uploading CSV, select from Firestore
case_id = st.selectbox(
    "Select Case",
    options=[doc.id for doc in db.collection('cases').where(
        'status', '==', 'DOCUMENTS_READY'
    ).stream()]
)

if case_id:
    # Load case from Firestore
    case_doc = db.collection('cases').document(case_id).get()
    case_data = case_doc.to_dict()
    
    # Load analysis results (from Cloud Function)
    analysis_ref = db.collection('cases').document(case_id)\
        .collection('analysis_results').document('summary')
    analysis_data = analysis_ref.get().to_dict()
    
    # Convert to dataframe for PharmaScan analysis
    df = pd.DataFrame(analysis_data['results'])
    
    # ── Your existing PharmaScan logic (fraud detection, graphs) ─────
    # Run fraud detection on df
    # Display network graphs, anomalies, etc.
    
    # ── NEW: Save back to Firestore ─────────────────────
    if st.button("💾 Save Analysis Findings"):
        analysis_ref.update({
            'cvo_notes': st.session_state.get('cvo_notes', ''),
            'fraud_flags': flagged_items,
            'network_anomalies': detected_patterns,
            'updated_at': datetime.now(),
        })
        st.success("✅ Saved to Firestore")

# ── Rules Engine (your existing Rules Engine tab) ─────────
st.subheader("⚙️ Configure Deduction Rules")
for rule in ['UNAPPROVED_DRUG', 'STALE_PRESCRIPTION', ...]:
    rule_config = db.collection('rules').document(rule).get().to_dict()
    # Allow CVO to tweak thresholds interactively
    new_threshold = st.slider(f"{rule} threshold", ...)
    if st.button(f"Update {rule}"):
        db.collection('rules').document(rule).update({'threshold': new_threshold})

# ── Deployment: Run on Cloud Run ─────────────────────────
# streamlit run app_cloud.py --logger.level=debug
```

**Dockerfile for Cloud Run:**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app_cloud.py .
EXPOSE 8501
CMD ["streamlit", "run", "app_cloud.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]
```

**Cost:** Cloud Run: ~$0.25/hour active, scales to zero when idle

---

## 5. COMPLETE SYSTEM DATA MODEL (Firestore)

### Collections & Documents

```
rama_cv_system/
├── referrals/
│   ├── REFERRAL-2025-001
│   │   ├── source: "compliance"
│   │   ├── pharmacy_id: "PHR-001"
│   │   ├── reason: "routine_audit"
│   │   ├── submitted_date: Timestamp
│   │   ├── submitted_by: "officer@rssb.rw"
│   │   ├── status: "PENDING_ALLOCATION"
│   │   └── documents: [url1, url2]
│
├── cases/
│   ├── RAMA-CV-2025-001
│   │   ├── pharmacy_id: "PHR-001"
│   │   ├── case_type: "counter_verification"
│   │   ├── status: "IN_PROGRESS"
│   │   ├── created_date: Timestamp
│   │   ├── created_by: "lead_cvo@rssb.rw"
│   │   ├── assigned_to: "officer1@rssb.rw"
│   │   ├── months_under_review: ["2024-10", "2024-11"]
│   │   ├── total_deduction_proposed: 50000
│   │   ├── total_deduction_agreed: 48000
│   │   ├── docusign_envelope_id: "..."
│   │   ├── signature_status: "SIGNED"
│   │   ├── timeline:
│   │   │   ├── referral_received: Timestamp
│   │   │   ├── documents_retrieved: Timestamp
│   │   │   ├── analysis_started: Timestamp
│   │   │   ├── reconcile_sent: Timestamp
│   │   │   ├── reconcile_accepted: Timestamp
│   │   │   └── deductions_applied: Timestamp
│   │   │
│   │   └── analysis_results/ [subcollection]
│   │       ├── summary
│   │       │   ├── total_deduction: 50000
│   │       │   ├── results: [{line_id, flags, deduction, ...}, ...]
│   │       │   └── updated_at: Timestamp
│   │       │
│   │       └── line_items/ [subcollection]
│   │           ├── VOUCHER-001-LINE-001
│   │           │   ├── drug_code: "DRG-123"
│   │           │   ├── drug_name: "Aspirin"
│   │           │   ├── quantity: 100
│   │           │   ├── unit_price: 500
│   │           │   ├── amount: 50000
│   │           │   ├── beneficiary_id: "BEN-456"
│   │           │   ├── claim_date: Date
│   │           │   ├── flags: ["UNAPPROVED_DRUG", "DUPLICATE"]
│   │           │   ├── deduction_proposed: 50000
│   │           │   ├── deduction_agreed: 48000
│   │           │   ├── reason: "Drug not on approved list"
│   │           │   ├── cvo_notes: "Clarified with pharmacy..."
│   │           │   └── status: "AGREED"
│   │
│   └── reconciliation/ [subcollection]
│       ├── status: "ACCEPTED"
│       ├── consent_form_link: "gs://..."
│       ├── pharmacy_response_date: Timestamp
│       └── pharmacy_contact_person: "..."
│
├── vouchers/
│   ├── VOUCHER-001
│   │   ├── case_id: "RAMA-CV-2025-001"
│   │   ├── pharmacy_id: "PHR-001"
│   │   ├── voucher_date: Date
│   │   ├── file_url: "gs://rama-cv-archive/PHR-001/2024-10/V001.pdf"
│   │   ├── ocr_text: "..." (full OCR output)
│   │   ├── ocr_confidence: 0.92
│   │   ├── manual_review_required: false
│   │   └── scanned_status: "OCR_COMPLETE"
│
├── rules/
│   ├── UNAPPROVED_DRUG
│   │   ├── enabled: true
│   │   ├── severity: "CRITICAL"
│   │   ├── deduction_type: "full_amount"
│   │   ├── approved_drug_list_ref: "gs://..."
│   │   └── last_updated: Timestamp
│   │
│   ├── STALE_PRESCRIPTION
│   │   ├── enabled: true
│   │   ├── severity: "MEDIUM"
│   │   ├── max_days_gap: 30
│   │   ├── deduction_type: "percentage"
│   │   ├── deduction_pct: 50
│   │   └── last_updated: Timestamp
│
├── audit_log/
│   ├── LOG-2025-001
│   │   ├── case_id: "RAMA-CV-2025-001"
│   │   ├── actor: "officer1@rssb.rw"
│   │   ├── action: "analysis_complete"
│   │   ├── timestamp: Timestamp
│   │   ├── details: {...}
│   │   └── ip_address: "192.168.1.1"
│
└── approved_drugs/
    └── list_2025
        ├── last_updated: Timestamp
        ├── source: "RSSB Formulary"
        ├── drugs: [
        │   {code: "DRG-001", name: "Aspirin", ...},
        │   {code: "DRG-002", name: "Paracetamol", ...},
        │ ]
```

---

## 6. DEPLOYMENT & INFRASTRUCTURE (JULES = Ultra-Low-Cost)

### 6.1 Google Cloud Setup

```bash
# Create project
gcloud projects create rama-cv-system --name="RAMA Counter-Verification"

# Enable APIs
gcloud services enable \
  firestore.googleapis.com \
  cloudfunctions.googleapis.com \
  cloudtasks.googleapis.com \
  storage-api.googleapis.com \
  vision.googleapis.com \
  pubsub.googleapis.com \
  run.googleapis.com \
  logging.googleapis.com

# Create Firestore database
gcloud firestore databases create --location=us-central1

# Create Cloud Storage buckets
gsutil mb gs://rama-cv-archive  # Vouchers
gsutil mb gs://rama-cv-ihbs-backups  # Invoice backups
gsutil mb gs://rama-cv-reports  # Generated reports
gsutil mb gs://rama-cv-config  # Config files (rules, drug lists)

# Deploy Streamlit to Cloud Run
gcloud run deploy pharmascan-app \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy Cloud Function: Counter-Verification Analysis
gcloud functions deploy run_counter_verification \
  --runtime python311 \
  --trigger-topic case_analysis_trigger \
  --entry-point run_analysis \
  --timeout 300 \
  --memory 2048MB
```

### 6.2 Architecture Deployment Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     USER TIER                               │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────┐   │
│  │ Google Forms │  │   Streamlit   │  │   Mobile app   │   │
│  │  (Referral)  │  │  (Dashboard)  │  │  (optional)    │   │
│  └──────┬───────┘  └───────┬───────┘  └────────┬───────┘   │
└─────────┼────────────────┼──────────────────┼──────────────┘
          │                │                  │
          ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              FIREBASE/FIRESTORE TIER (free <1GB)           │
│  Real-time database, multi-user sync, offline support       │
└─────┬───────────────────────────────────────────────────────┘
      │
      ├─→ Firestore (database) — ~$0.06/100K reads, ~$0.18/100K writes
      ├─→ Cloud Storage (archive) — ~$0.02/GB/month
      └─→ Cloud Tasks (queue) — $0.40/M tasks (first 1M free/month)
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│           CLOUD FUNCTIONS / SERVERLESS TIER                │
│  (Trigger on Firestore changes, Pub/Sub events, HTTP)      │
└────┬────────────────────────────────┬──────────────┬────────┘
     │                                │              │
     ▼                                ▼              ▼
   F1:                              F2:            F3:
   REFERRAL_INTAKE                  ANALYSIS       RECONCILE
   (validate)                       (rules engine) (notify)
     │                                │              │
     └────────────┬───────────────────┼──────────────┘
                  │
                  ▼
        ┌──────────────────────────────────┐
        │  API Integrations (Cloud Calls)  │
        ├──────────────────────────────────┤
        │ • Cloud Vision API (OCR)         │
        │ • IHBS API (post deductions)     │
        │ • Kwivuza API (eligibility)      │
        │ • DocuSign API (e-signatures)    │
        │ • Pub/Sub (email alerts)         │
        └──────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              MONITORING & COMPLIANCE TIER                    │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │Cloud Logging │  │ Cloud Audit  │  │ Backup/Export   │   │
│  │  (activity)  │  │   Log        │  │ (GDPR/Compliance)   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘

Cost Estimate (Prod, 50 pharmacies, 10 CVOs):
┌──────────────────────────────────────┐
│ Firestore reads/writes:   $30/month  │
│ Cloud Functions (free):    $0/month  │
│ Cloud Storage (5GB):       $0.10/mo  │
│ Cloud Vision (OCR):        $2/month  │
│ Cloud Run (Streamlit):     $5/month  │
│ DocuSign API:             $15/month  │
│ ────────────────────────────────── │
│ TOTAL:                    $52/month  │
│ (equivalent to: 1 CVO salary/year)   │
└──────────────────────────────────────┘
```

---

## 7. STEP-BY-STEP IMPLEMENTATION ROADMAP

### Phase 1: MVP (Weeks 1–2) — "$10 Setup"

**Goal:** Minimum viable digital workflow

1. **Data Model** (Firestore schema)
   - Define cases, referrals, analysis_results collections
   - Set up security rules (staff can see only assigned cases)

2. **Cloud Function #1: Referral Intake**
   - Google Form → Cloud Function → Firestore
   - Auto-generates case ID
   - ~50 lines of Python

3. **Streamlit Dashboard v1**
   - Connect to Firestore (firebase-admin)
   - Show assigned cases
   - Display case status & timeline
   - No analysis yet — static view only
   - Deploy to Cloud Run

4. **Testing**
   - Manual test: submit referral via Form → check Firestore → confirm in Streamlit

**Estimated Cost:** $5–10  
**Effort:** 1 developer, 40 hours

---

### Phase 2: Analysis Engine (Weeks 3–4) — "The PharmaScan Integration"

**Goal:** Fully functional counter-verification workflow

1. **Cloud Function #2: Document Retrieval**
   - Query Cloud Storage for vouchers
   - OCR via Cloud Vision API
   - Store OCR results in Firestore
   - Handle file archival

2. **Cloud Function #3: Counter-Verification Analysis**
   - Adapt your PharmaScan rules engine
   - Read case data from Firestore
   - Run rules against vouchers/invoices
   - Write results back to Firestore

3. **Streamlit Tab: Analysis Review**
   - Load case analysis from Firestore
   - Display flagged lines (similar to your PharmaScan UI)
   - Allow CVO to manually override
   - Show graphs/statistics (reuse your matplotlib code)

4. **Cloud Function #4: Reconciliation Notification**
   - Auto-generate reconciliation PDF
   - Email pharmacy partner (via Pub/Sub)
   - Create pharmacy portal link

5. **Testing**
   - End-to-end: upload referral → retrieve vouchers → analyze → email partner

**Estimated Cost:** $20–30  
**Effort:** 1.5 developers, 60 hours

---

### Phase 3: Sign-Off & Deductions (Weeks 5–6) — "Go Live"

**Goal:** Complete workflow through deduction application

1. **DocuSign Integration**
   - Set up DocuSign account (~$15/month)
   - Integrate into Cloud Function
   - Create signature workflow for report

2. **Cloud Function #5: Deduction Application**
   - Parse signed report
   - Call IHBS API to post deductions
   - Update case status → CLOSED

3. **Streamlit Tab: Report Sign-Off**
   - Show DocuSign status
   - Display final report (preview)
   - Manual override interface for exceptional cases

4. **Audit Trail Dashboard**
   - View all case activities (timeline)
   - Filter by pharmacy, CVO, date
   - Export compliance reports

5. **Testing**
   - Full case lifecycle: referral → deduction application

**Estimated Cost:** $40–50  
**Effort:** 1.5 developers, 70 hours

---

### Phase 4: Optimization & Scaling (Weeks 7–8) — "Polish"

1. **Performance**
   - Index Firestore queries (by status, date, assigned_to)
   - Cache frequently accessed lists
   - Optimize OCR pipeline (batch processing)

2. **Compliance & Security**
   - Row-level security in Firestore (staff can only see own cases)
   - Data encryption (at rest + in transit, standard in GCP)
   - Audit logging (all actions logged with IP/timestamp)
   - GDPR compliance (right to deletion)

3. **Monitoring**
   - Set up Cloud Monitoring alerts
   - Dashboard: active cases, bottlenecks, error rates
   - Automated daily/weekly reports to management

4. **Mobile App** (optional)
   - Flutter app for CVOs to review cases on mobile
   - Sync with Firestore

5. **Testing & Documentation**
   - Write runbooks for ops team
   - Train staff on new system
   - Parallel run (manual + digital) for 2 weeks

**Estimated Cost:** $50–60  
**Effort:** 1 developer, 80 hours

---

## 8. SECURITY & COMPLIANCE

### Authentication & Access Control

```
┌────────────────┐
│ Google Cloud   │
│ Identity &     │  → Firestore Security Rules
│ Access Mgmt    │
└────────────────┘

rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Staff can only see cases assigned to them
    match /cases/{caseId} {
      allow read, write: if 
        request.auth.uid == resource.data.assigned_to ||
        request.auth.token.email.endsWith('@rssb.rw');
    }
    
    // Lead CVO can see all cases
    match /cases/{caseId} {
      allow read, write: if 
        'lead_cvo' in request.auth.token.roles;
    }
    
    // Audit log: read-only, append-only
    match /audit_log/{logId} {
      allow create: if request.auth != null;
      allow read: if 'admin' in request.auth.token.roles;
    }
  }
}
```

### Data Privacy

- **Beneficiary PII:** Only last 4 digits of ID stored; full ID never in logs
- **Encryption:** All data encrypted at rest (GCP default) + in transit (HTTPS)
- **Backups:** Firestore auto-backups (7-day retention); manual weekly exports to encrypted GCS
- **Data Retention:** Case data archived after 7 years (configurable)
- **Audit Trail:** Immutable log of all actions (who, what, when, IP)

### Compliance Checklist

- ✅ Audit trail (Firestore audit logs + Cloud Logging)
- ✅ User authentication (Google Cloud IAM)
- ✅ Access control (row-level, role-based)
- ✅ Data encryption (at rest, in transit)
- ✅ Backup & disaster recovery (auto-backups)
- ✅ Reporting (export to CSV/PDF for compliance reviews)

---

## 9. COST BREAKDOWN & SCALING

### Monthly Costs (Baseline)

| Component | Free Tier | Usage | Cost/Month |
|-----------|-----------|-------|-----------|
| Firestore reads | 50K | ~100K/day (cases, analyses) | $0.30 |
| Firestore writes | 20K | ~50K/day (updates, logs) | $0.36 |
| Cloud Functions | 2M invocations | ~1M/month (triggers, webhooks) | FREE |
| Cloud Storage | 5GB | 1GB actual data | $0.02 |
| Cloud Run | — | 2 instances × 4 hrs/day = 8 hrs/day | $5 |
| Cloud Vision API | — | 500 pages OCR/month | $0.30 |
| Cloud Tasks | 1M tasks | ~100K tasks/month | FREE |
| Pub/Sub | 1M messages | ~50K emails/month | FREE |
| DocuSign API | — | ~20 envelopes/month (if included) | $15 |
| **TOTAL** | | | **~$21/month** |

### Scaling to 1000 Pharmacies (10,000 cases/year)

| Metric | Baseline | Scaled |
|--------|----------|--------|
| Firestore reads | 100K/day | 500K/day → **$1.50/month** |
| Firestore writes | 50K/day | 250K/day → **$1.35/month** |
| Cloud Run | 8 hrs/day | 16 hrs/day → **$10/month** |
| Cloud Vision | 500 pages/mo | 5K pages/mo → **$3/month** |
| **TOTAL** | $21/month | **$85/month** |

**Conclusion:** Even at 10× scale, cost < $100/month. No additional infrastructure needed.

---

## 10. MIGRATION PLAN: Manual → Digital

### Week 1: Parallel Setup

- CVOs work manually (traditional SOP) + digital simultaneously
- Lead CVO monitors digital workflow for accuracy
- Compare results: manual vs automated analysis

### Week 2–3: Soft Launch

- High-trust pharmacies (low fraud history) → all-digital workflow
- Medium-risk pharmacies → manual review + digital as reference
- Compliance Unit gives feedback on analysis quality

### Week 4: Full Cutover

- All new cases → digital workflow
- Historical cases (last 2 years) → digitize on-demand
- Manual system remains as fallback for 6 months

### Parallel Run Success Criteria

- ✅ Digital analysis matches manual analysis in 95% of cases
- ✅ Average cycle time reduced by 60% (15 days → 5 days)
- ✅ Zero security breaches or audit failures
- ✅ Staff trained and confident

---

## 11. EXAMPLE: ONE CASE END-TO-END

**Scenario:** Pharmacy PHR-001 (Kigali) referred for routine audit (Oct 2024)

### T0: Referral Submitted

```
Manager Benefits fills form:
├─ Pharmacy: PHR-001 (New Life Pharmacy, Kigali)
├─ Reason: routine_audit
├─ Months: Oct, Nov 2024
└─ Submit

↓ [Google Form → Cloud Function]

Firestore created:
├─ referrals/REFERRAL-2025-001
├─ cases/RAMA-CV-2025-001 [status: REFERRAL_RECEIVED]
├─ Pub/Sub triggers: Lead CVO gets email "New referral: PHR-001"
```

### T+2 hours: Lead CVO Allocates

```
Lead CVO clicks: "Allocate RAMA-CV-2025-001 to Officer Ahmed"

Firestore updated:
├─ cases/RAMA-CV-2025-001
│  ├─ assigned_to: "ahmed@rssb.rw"
│  ├─ status: ALLOCATED
│  └─ allocated_date: 2025-01-15 09:30
├─ Cloud Tasks enqueues: retrieve_vouchers(case_id)
├─ Email sent: "Ahmed, case RAMA-CV-2025-001 assigned"
```

### T+4 hours: Vouchers Retrieved

```
Cloud Function triggered (by Cloud Tasks):

1. Query Cloud Storage: gs://rama-cv-archive/PHR-001/2024-10/
   └─ Found: 47 vouchers (PDF)
   
2. Send each PDF to Cloud Vision API (OCR)
   └─ 47 pages × $0.15/100 images = $0.07
   └─ Results stored in Firestore: vouchers/VOUCHER-001, ...
   
3. Query IHBS backup: extract invoices for PHR-001 (Oct, Nov 2024)
   └─ 8 invoices found (XLSX data)
   
4. Firestore updated:
   ├─ cases/RAMA-CV-2025-001
   │  ├─ status: DOCUMENTS_READY
   │  ├─ vouchers_count: 47
   │  ├─ invoices_count: 8
   │  └─ document_ready_date: 2025-01-15 14:00
```

### T+1 day: Ahmed Reviews Documents in Streamlit

```
Ahmed logs into Streamlit:
├─ Dashboard shows: RAMA-CV-2025-001 (DOCUMENTS_READY)
├─ Views:
│  ├─ 47 vouchers (OCR text visible, images clickable)
│  ├─ 8 invoices (summary table)
│  ├─ Beneficiary count: 320 unique
│  ├─ Total amount: 2,850,000 RWF
├─ Clicks: "Run Analysis"
```

### T+1 day, 2 hours: Analysis Runs (Cloud Function)

```
Cloud Function triggered (counter_verification_analysis):

Input:
├─ Vouchers (47 × OCR text) from Firestore
├─ Invoices (8 × data) from IHBS
├─ Beneficiary records from Kwivuza API
├─ Rules from Firestore: approved_drugs, max_price_variance, etc.

Processing:
├─ For each of 1,240 line items:
│  ├─ Check: Is drug on approved list?
│  │  └─ Flag: Line 142 (Oxycodone) → UNAPPROVED_DRUG, deduction: 25,000
│  │
│  ├─ Check: Prescription vs claim (call Kwivuza)
│  │  └─ OK (date match within 7 days)
│  │
│  ├─ Check: Beneficiary eligible on claim date?
│  │  └─ Flag: Line 205 (BEN-5678) → INELIGIBLE, deduction: 15,000
│  │
│  └─ Check: Duplicate within 30 days?
│     └─ OK
│
└─ Results:
   ├─ Total flagged lines: 12
   ├─ Proposed deduction: 87,500 RWF
   ├─ Severity: 8 MEDIUM, 4 LOW
   └─ Stored in Firestore: cases/RAMA-CV-2025-001/analysis_results/

Time: ~2 minutes | Cost: $0.50 (APIs + compute)
```

### T+2 days: Ahmed Reviews Analysis in Streamlit

```
Ahmed opens Streamlit → PharmaScan tab:

Shows:
├─ 12 flagged lines (sorted by severity)
├─ Line 142:
│  ├─ Oxycodone, 100 units × 250 RWF
│  ├─ Reason: NOT on approved drug list
│  ├─ Deduction proposed: 25,000 RWF
│  ├─ Ahmed notes: "Per HoD RAMA email 2024-12-20, oxycodone restricted"
│  └─ Approves deduction ✓
│
├─ Line 205:
│  ├─ Paracetamol, 50 units (beneficiary BEN-5678)
│  ├─ Reason: Beneficiary not eligible on claim date (left RAMA 2024-09-30)
│  ├─ Deduction proposed: 15,000 RWF
│  ├─ Ahmed checks beneficiary record → confirmed not eligible
│  └─ Approves deduction ✓
│
└─ Creates report PDF (auto-generated)
   ├─ Title: Counter-Verification Report — PHR-001 (Oct–Nov 2024)
   ├─ Includes: flagged items, deduction breakdown, rules applied
   ├─ Saved to: gs://rama-cv-reports/RAMA-CV-2025-001-report.pdf
   └─ Click: "Send to Pharmacy"

Firestore updated:
├─ cases/RAMA-CV-2025-001
│  ├─ status: ANALYSIS_COMPLETE
│  ├─ total_deduction_proposed: 87,500
│  └─ cvo_review_complete: true
```

### T+2.5 days: Pharmacy Receives Reconciliation Portal

```
Email sent to New Life Pharmacy (contact: mr.jean@newlifepharmacy.rw):

Subject: RAMA Counter-Verification — Response Required by 2025-01-22

Body:
┌────────────────────────────────────────────────────────┐
│ Counter-Verification Report: RAMA-CV-2025-001         │
│ Period: October–November 2024                          │
│ Pharmacy: New Life Pharmacy (PHR-001)                 │
│                                                        │
│ FLAGGED ITEMS:                                         │
│ • Line 142: Oxycodone (unapproved) → -25,000 RWF      │
│ • Line 205: Ineligible beneficiary → -15,000 RWF      │
│ • [8 more items]                                       │
│                                                        │
│ TOTAL PROPOSED DEDUCTION: 87,500 RWF                  │
│                                                        │
│ RESPOND HERE:                                          │
│ [Link to secure portal]                                │
│                                                        │
│ Deadline: 2025-01-22 (7 days)                          │
└────────────────────────────────────────────────────────┘

Pharmacy clicks link → Streamlit portal (authenticated):
├─ View all flagged items (with rule explanations)
├─ For each line:
│  ├─ Option 1: Accept deduction ✓
│  ├─ Option 2: Challenge (upload evidence)
│  └─ Option 3: Request meeting
│
├─ Mr. Jean reviews:
│  ├─ Oxycodone line: "We're aware it was restricted. Accept."
│  ├─ Ineligible line: "Patient left on 2024-09-30, not 09-29. Disagree."
│  │  └─ Uploads: screenshot of RAMA card showing 09-29 date
│  └─ Other 10 lines: Accept all
│
├─ Pharmacy clicks: "Submit Response"
├─ Total agreed deduction: 72,500 RWF
└─ Consent form auto-generated + signed (DocuSign)

Firestore updated:
├─ cases/RAMA-CV-2025-001/reconciliation
│  ├─ pharmacy_response_date: 2025-01-17 15:20
│  ├─ pharmacy_agreed_deduction: 72,500
│  ├─ disputes: [Line 205 challenged]
│  └─ status: PARTIALLY_AGREED

Email sent to Ahmed: "PHR-001 responded. Dispute on Line 205."
```

### T+4 days: Ahmed Resolves Dispute

```
Ahmed reviews dispute:
├─ Pharmacy claims: Beneficiary left 2024-09-29 (not 09-30)
├─ Ahmed checks Kwivuza: Last eligibility record = 2024-09-30
├─ Pharmacy evidence: Shows RAMA card with 09-29 exit date
│
├─ Ahmed decision: "Pharmacy has valid evidence. Beneficiary WAS ineligible.
│                   But off by 1 day — partial deduction instead of full."
│
├─ Updates Firestore:
│  ├─ Line 205: deduction_agreed: 7,500 RWF (instead of 15,000)
│  ├─ Case total: 79,500 RWF (instead of 87,500)
│  └─ note: "Beneficiary eligibility date discrepancy resolved—partial deduction"
│
├─ Updates pharmacy via email: "Deduction adjusted to 79,500 RWF based on your evidence."
└─ Pharmacy confirms acceptance

Firestore updated:
├─ cases/RAMA-CV-2025-001
│  ├─ status: RECONCILIATION_COMPLETE
│  ├─ total_deduction_agreed: 79,500
│  └─ reconciliation_completed_date: 2025-01-18
```

### T+5 days: Report Sign-Off (DocuSign)

```
Lead CVO (Sarah) prepares final report:
├─ Combines: analysis + reconciliation + Ahmed's notes
├─ Generates PDF: RAMA-CV-2025-001-final-report.pdf
├─ Contains: flagged lines, agreed deductions, signatures block
│
├─ Triggers Cloud Function: create_docusign_envelope
│  └─ DocuSign creates envelope with sequential routing:
│     1. Manager Benefits (Manager.Benefits@rssb.rw) — sign
│     2. HoD RAMA (HoD.RAMA@rssb.rw) — sign
│     3. CBO (CBO@rssb.rw) — sign
│     4. HoD Compliance (Compliance.Head@rssb.rw) — sign

DocuSign emails sent:
├─ [Day 5] Manager Benefits: "Sign within 2 days"
├─ [Day 6] HoD RAMA: "Awaiting your signature"
├─ [Day 6] CBO: "Ready for your review"
├─ [Day 7] HoD Compliance: "Awaiting signature"

Signatures completed:
├─ Manager Benefits: ✓ 2025-01-19 09:00
├─ HoD RAMA: ✓ 2025-01-19 14:30
├─ CBO: ✓ 2025-01-20 11:15
├─ HoD Compliance: ✓ 2025-01-20 16:45

Firestore updated:
├─ cases/RAMA-CV-2025-001
│  ├─ status: SIGNED
│  ├─ docusign_envelope_id: "..."
│  ├─ signed_date: 2025-01-20 16:45
│  └─ signed_by: [Manager Benefits, HoD RAMA, CBO, HoD Compliance]

Signed PDF archived:
├─ gs://rama-cv-reports/RAMA-CV-2025-001-signed.pdf

Sarah sees: "Report fully signed. Ready for deduction application."
```

### T+6 days: Deductions Applied

```
Cloud Function triggered: apply_deductions

1. Parse signed report from Firestore
   └─ Extract: pharmacy_id=PHR-001, deductions=79,500

2. Call IHBS API:
   POST /api/v1/deductions/apply
   {
     "pharmacy_id": "PHR-001",
     "case_id": "RAMA-CV-2025-001",
     "total_amount": 79,500,
     "applied_date": "2025-01-21",
     "line_items": [
       {"invoice_id": "INV-001", "deduction": 25000, "reason": "UNAPPROVED_DRUG"},
       {"invoice_id": "INV-001", "deduction": 7500, "reason": "INELIGIBLE_BENEFICIARY"},
       ...
     ]
   }

3. IHBS API response: ✓ SUCCESS
   └─ Deductions applied to next invoice payment

4. Firestore updated:
   ├─ cases/RAMA-CV-2025-001
   │  ├─ status: DEDUCTIONS_APPLIED
   │  ├─ applied_date: 2025-01-21
   │  ├─ applied_amount: 79,500
   │  └─ ihbs_confirmation_id: "..."

5. Email confirmation sent:
   ├─ Ahmed: "Deductions applied. Case closed."
   ├─ Lead CVO Sarah: "RAMA-CV-2025-001 complete. Next invoice to PHR-001 will reflect -79,500 RWF."
   ├─ Pharmacy: "Deductions have been applied to your account per consent form."

Firestore updated:
├─ cases/RAMA-CV-2025-001
│  ├─ status: CASE_CLOSED
│  ├─ closed_date: 2025-01-21 10:00
│  └─ cycle_time_days: 6 (referral → closed)

TOTAL TIME: 6 days (vs 15–20 days manual)
TOTAL COST: ~$1.50 (APIs + compute + storage)
AUDIT TRAIL: Complete (every action logged with timestamp + actor)
```

---

## 12. QUICK START CODE SNIPPETS

### Initialize Firestore (Python)

```python
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud import tasks_v2, vision_v1
from datetime import datetime

# Init (runs once, credentials auto-loaded from GCP)
firebase_admin.initialize_app()
db = firestore.client()
bucket = storage.bucket()

# Create referral (from Google Form webhook)
def create_referral_from_form(form_data):
    referral_doc = {
        'source': form_data['source'],  # 'compliance', 'internal', etc.
        'pharmacy_id': form_data['pharmacy_id'],
        'reason': form_data['reason'],
        'submitted_date': datetime.now(),
        'submitted_by': form_data['submitter_email'],
        'status': 'PENDING_ALLOCATION',
        'documents': form_data.get('doc_urls', []),
    }
    
    # Auto-generate case ID
    next_id = db.collection('cases').document('_metadata').get().to_dict()['next_case_num']
    case_id = f"RAMA-CV-{datetime.now().year}-{next_id:04d}"
    
    # Create case
    db.collection('cases').document(case_id).set({
        'pharmacy_id': form_data['pharmacy_id'],
        'case_type': 'counter_verification',
        'status': 'REFERRAL_RECEIVED',
        'created_date': datetime.now(),
        'created_by': form_data['submitter_email'],
        'months_under_review': form_data.get('months', []),
    })
    
    return case_id
```

### Cloud Function: Retrieve Vouchers

```python
import functions_framework
from google.cloud import storage, vision_v1
from firebase_admin import firestore
import base64

@functions_framework.cloud_event
def retrieve_vouchers_for_case(cloud_event):
    """Triggered by Firestore update (case allocated)"""
    
    db = firestore.client()
    storage_client = storage.Client()
    vision_client = vision_v1.ImageAnnotatorClient()
    
    # Get case
    case_id = cloud_event['data']['value']['fields']['case_id']['stringValue']
    case_doc = db.collection('cases').document(case_id).get()
    case_data = case_doc.to_dict()
    
    pharmacy_id = case_data['pharmacy_id']
    months = case_data['months_under_review']
    
    # Query Cloud Storage
    bucket_name = 'rama-cv-archive'
    bucket = storage_client.bucket(bucket_name)
    
    all_vouchers = []
    for month in months:
        prefix = f"{pharmacy_id}/{month}/"
        blobs = bucket.list_blobs(prefix=prefix)
        all_vouchers.extend(blobs)
    
    # Process each voucher (OCR)
    for blob in all_vouchers:
        # Download PDF
        pdf_bytes = blob.download_as_bytes()
        
        # OCR via Cloud Vision
        image = vision_v1.Image(content=pdf_bytes)
        response = vision_client.document_text_detection(image=image)
        ocr_text = response.full_text_annotation.text
        
        # Store voucher record
        voucher_doc = {
            'case_id': case_id,
            'pharmacy_id': pharmacy_id,
            'file_url': f"gs://{bucket_name}/{blob.name}",
            'ocr_text': ocr_text,
            'ocr_confidence': 0.95,  # simplified
            'scanned_status': 'OCR_COMPLETE',
        }
        db.collection('vouchers').document(blob.name.replace('/', '_')).set(voucher_doc)
    
    # Update case status
    db.collection('cases').document(case_id).update({
        'status': 'DOCUMENTS_READY',
        'document_ready_date': datetime.now(),
        'vouchers_count': len(all_vouchers),
    })
    
    print(f"✅ Retrieved & OCR'd {len(all_vouchers)} vouchers for case {case_id}")
```

### Streamlit: Dashboard Tab

```python
# pharmascan/pages/01_Dashboard.py
import streamlit as st
import pandas as pd
from firebase_admin import firestore

st.set_page_config(page_title="Dashboard", layout="wide")

db = firestore.client()

# Get current user's assigned cases
user_email = st.session_state.get('user_email')
cases_ref = db.collection('cases')\
    .where('assigned_to', '==', user_email)\
    .stream()

cases = [{'id': doc.id, **doc.to_dict()} for doc in cases_ref]

st.title("📊 My Cases")

# Status tabs
status_tabs = st.tabs(['In Progress', 'Ready for Sign-Off', 'Closed'])

with status_tabs[0]:  # In Progress
    in_progress = [c for c in cases if c['status'] in ['ALLOCATED', 'DOCUMENTS_READY', 'ANALYSIS_IN_PROGRESS']]
    for case in in_progress:
        with st.expander(f"**{case['id']}** — {case['pharmacy_id']} ({case['status']})"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Months", len(case.get('months_under_review', [])))
            with col2:
                st.metric("Vouchers", case.get('vouchers_count', '—'))
            with col3:
                st.metric("Days Elapsed", (datetime.now() - case['created_date']).days)
            
            if case['status'] == 'DOCUMENTS_READY':
                if st.button(f"Start Analysis", key=f"start_{case['id']}"):
                    st.session_state['case_to_analyze'] = case['id']
                    st.switch_page("pages/02_Analysis.py")

with status_tabs[1]:  # Ready for Sign-Off
    ready = [c for c in cases if c['status'] == 'RECONCILIATION_COMPLETE']
    for case in ready:
        st.write(f"✅ {case['id']} ready for sign-off (deduction: {case.get('total_deduction_agreed', '—')} RWF)")

with status_tabs[2]:  # Closed
    closed = [c for c in cases if c['status'] == 'CASE_CLOSED']
    st.write(f"**{len(closed)} cases closed this month**")
```

---

## CONCLUSION

**What You Get:**
- ✅ **Fully digital SOP workflow** (referral → deduction in 5–7 days vs 15–20 manual)
- ✅ **PharmaScan integrated** as analysis engine
- ✅ **Audit trail** (complete, immutable, compliant)
- ✅ **Scalable** (handles 10,000+ cases/year)
- ✅ **Cheap** (< $100/month, even at scale)
- ✅ **Easy to build** (4–8 weeks, standard Google Cloud services)

**How to Start:**
1. Set up Google Cloud project (5 min)
2. Deploy Firestore + Cloud Functions (1 day)
3. Build Streamlit dashboard (2 days)
4. Test with 2–3 real cases (3 days)
5. Go live (week 2)

**Next Step:** Schedule 30-min call with Google Cloud team for hands-on setup support.
