# streamlit_app.py - SmartFormsGPT Main Application

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from logger import get_logger
from schemas.base_claim import BaseClaim, ClaimStatus, ClaimType
from schemas.custom_claim import MedicalClaim, DentalClaim, PrescriptionClaim
from logic.decision_engine import DecisionEngine
from utils.helpers import generate_claim_id, format_currency
from utils.validators import ClaimValidator

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="SmartFormsGPT - Insurance Claim Processing",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'claims' not in st.session_state:
    st.session_state.claims = []
if 'decision_engine' not in st.session_state:
    st.session_state.decision_engine = DecisionEngine()

def main():
    """Main application function."""
    
    # Header
    st.title("📋 SmartFormsGPT")
    st.markdown("### AI-Powered Insurance Claim Processing")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
            ["Submit Claim", "View Claims", "Batch Processing", "Analytics"]
        )
        
        st.markdown("---")
        st.markdown("### System Info")
        st.info(f"Version: {os.getenv('APP_VERSION', '1.0.0')}")
        st.info(f"Total Claims: {len(st.session_state.claims)}")
    
    # Main content based on selected page
    if page == "Submit Claim":
        submit_claim_page()
    elif page == "View Claims":
        view_claims_page()
    elif page == "Batch Processing":
        batch_processing_page()
    elif page == "Analytics":
        analytics_page()

def submit_claim_page():
    """Page for submitting a new claim."""
    
    st.header("Submit New Claim")
    
    # Claim type selection
    claim_type = st.selectbox(
        "Claim Type",
        ["Medical", "Dental", "Prescription", "Other"]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Patient Information")
        patient_name = st.text_input("Patient Name *")
        patient_id = st.text_input("Patient ID *")
        dob = st.date_input("Date of Birth *")
    
    with col2:
        st.subheader("Provider Information")
        provider_name = st.text_input("Provider Name *")
        provider_id = st.text_input("Provider NPI (optional)")
        service_date = st.date_input("Service Date *")
    
    st.subheader("Claim Details")
    col3, col4 = st.columns(2)
    
    with col3:
        total_amount = st.number_input("Total Amount ($) *", min_value=0.01, step=0.01)
        description = st.text_area("Description")
    
    with col4:
        diagnosis_codes = st.text_input("Diagnosis Codes (comma-separated)")
        procedure_codes = st.text_input("Procedure Codes (comma-separated)")
    
    # File upload
    st.subheader("Supporting Documents")
    uploaded_file = st.file_uploader(
        "Upload claim form (PDF, PNG, JPG)",
        type=['pdf', 'png', 'jpg', 'jpeg']
    )
    
    # Submit button
    if st.button("Submit Claim", type="primary"):
        # Validate required fields
        if not all([patient_name, patient_id, provider_name, total_amount]):
            st.error("Please fill in all required fields marked with *")
            return
        
        try:
            # Create claim object
            claim_data = {
                "claim_type": claim_type.lower(),
                "patient_name": patient_name,
                "patient_id": patient_id,
                "date_of_birth": datetime.combine(dob, datetime.min.time()),
                "provider_name": provider_name,
                "provider_id": provider_id if provider_id else None,
                "service_date": datetime.combine(service_date, datetime.min.time()),
                "total_amount": total_amount,
                "description": description if description else None,
                "diagnosis_codes": [c.strip() for c in diagnosis_codes.split(',')] if diagnosis_codes else [],
                "procedure_codes": [c.strip() for c in procedure_codes.split(',')] if procedure_codes else []
            }
            
            # Generate claim ID
            claim_id = generate_claim_id(patient_id, claim_data["service_date"])
            claim_data["claim_id"] = claim_id
            
            # Create claim based on type
            if claim_type.lower() == "medical":
                claim = MedicalClaim(**claim_data)
            elif claim_type.lower() == "dental":
                claim = DentalClaim(**claim_data)
            elif claim_type.lower() == "prescription":
                claim = PrescriptionClaim(**claim_data)
            else:
                claim = BaseClaim(**claim_data)
            
            # Evaluate claim
            status, reasons, confidence = st.session_state.decision_engine.evaluate_claim(claim)
            claim.status = status
            
            # Add to session state
            st.session_state.claims.append(claim)
            
            # Display result
            st.success(f"✅ Claim submitted successfully! Claim ID: {claim_id}")
            
            # Show decision
            st.info(f"**Status:** {status.value.upper()}")
            st.info(f"**Confidence:** {confidence:.1%}")
            
            with st.expander("Decision Details"):
                for reason in reasons:
                    st.write(f"• {reason}")
            
            logger.info(f"Claim {claim_id} submitted with status {status}")
            
        except Exception as e:
            st.error(f"Error submitting claim: {str(e)}")
            logger.error(f"Error submitting claim: {e}")

def view_claims_page():
    """Page for viewing submitted claims."""
    
    st.header("View Claims")
    
    if not st.session_state.claims:
        st.info("No claims submitted yet.")
        return
    
    # Display claims in a table
    for claim in reversed(st.session_state.claims):  # Show newest first
        with st.expander(f"Claim {claim.claim_id} - {claim.status.value.upper()}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Patient:**", claim.patient_name)
                st.write("**Patient ID:**", claim.patient_id)
                st.write("**Type:**", claim.claim_type.value)
            
            with col2:
                st.write("**Provider:**", claim.provider_name)
                st.write("**Service Date:**", claim.service_date.strftime("%Y-%m-%d"))
                st.write("**Amount:**", format_currency(claim.total_amount))
            
            with col3:
                st.write("**Status:**", claim.status.value.upper())
                st.write("**Created:**", claim.created_at.strftime("%Y-%m-%d %H:%M"))
            
            if claim.description:
                st.write("**Description:**", claim.description)

def batch_processing_page():
    """Page for batch claim processing."""
    
    st.header("Batch Processing")
    st.info("Upload multiple claims for batch processing (Coming Soon)")
    
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file with claims",
        type=['csv', 'xlsx']
    )
    
    if uploaded_file:
        st.warning("Batch processing feature is under development.")

def analytics_page():
    """Page for analytics and reporting."""
    
    st.header("Analytics Dashboard")
    
    if not st.session_state.claims:
        st.info("No data available for analytics.")
        return
    
    # Calculate statistics
    total_claims = len(st.session_state.claims)
    total_amount = sum(c.total_amount for c in st.session_state.claims)
    
    status_counts = {}
    for claim in st.session_state.claims:
        status = claim.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Claims", total_claims)
    with col2:
        st.metric("Total Amount", format_currency(total_amount))
    with col3:
        st.metric("Approved", status_counts.get('approved', 0))
    with col4:
        st.metric("Pending", status_counts.get('under_review', 0) + status_counts.get('pending_info', 0))
    
    # Status breakdown
    st.subheader("Claims by Status")
    st.bar_chart(status_counts)

if __name__ == "__main__":
    main()
