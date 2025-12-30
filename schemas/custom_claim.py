# custom_claim.py - Custom Claim Extensions

from typing import Optional, List, Dict, Any
from pydantic import Field, validator
from datetime import datetime
from schemas.base_claim import BaseClaim, ClaimType

class MedicalClaim(BaseClaim):
    """Extended schema for medical claims."""
    
    claim_type: ClaimType = Field(default=ClaimType.MEDICAL, const=True)
    
    # Medical-specific fields
    admission_date: Optional[datetime] = Field(None, description="Hospital admission date")
    discharge_date: Optional[datetime] = Field(None, description="Hospital discharge date")
    room_type: Optional[str] = Field(None, description="Hospital room type")
    attending_physician: Optional[str] = Field(None, description="Attending physician name")
    
    # Treatment details
    treatment_type: Optional[str] = Field(None, description="Type of treatment")
    medications: Optional[List[str]] = Field(default=[], description="Medications prescribed")
    lab_tests: Optional[List[str]] = Field(default=[], description="Laboratory tests performed")
    
    @validator('discharge_date')
    def validate_discharge(cls, v, values):
        """Validate discharge date is after admission date."""
        if v and 'admission_date' in values and values['admission_date']:
            if v < values['admission_date']:
                raise ValueError('Discharge date must be after admission date')
        return v

class DentalClaim(BaseClaim):
    """Extended schema for dental claims."""
    
    claim_type: ClaimType = Field(default=ClaimType.DENTAL, const=True)
    
    # Dental-specific fields
    tooth_number: Optional[str] = Field(None, description="Tooth number(s) treated")
    procedure_type: Optional[str] = Field(None, description="Type of dental procedure")
    is_emergency: bool = Field(default=False, description="Emergency treatment flag")
    x_rays_taken: bool = Field(default=False, description="X-rays taken flag")

class PrescriptionClaim(BaseClaim):
    """Extended schema for prescription claims."""
    
    claim_type: ClaimType = Field(default=ClaimType.PRESCRIPTION, const=True)
    
    # Prescription-specific fields
    medication_name: str = Field(..., description="Name of medication")
    dosage: str = Field(..., description="Medication dosage")
    quantity: int = Field(..., gt=0, description="Quantity prescribed")
    days_supply: int = Field(..., gt=0, description="Days supply")
    pharmacy_name: str = Field(..., description="Pharmacy name")
    pharmacy_npi: Optional[str] = Field(None, description="Pharmacy NPI number")
    is_generic: bool = Field(default=False, description="Generic medication flag")
    refill_number: int = Field(default=0, ge=0, description="Refill number")

class FormExtraction(BaseClaim):
    """Schema for AI-extracted form data."""
    
    # Extraction metadata
    extraction_confidence: float = Field(..., ge=0, le=1, description="AI confidence score")
    extracted_fields: Dict[str, Any] = Field(default={}, description="Extracted field values")
    missing_fields: List[str] = Field(default=[], description="Fields not found in form")
    validation_errors: List[str] = Field(default=[], description="Validation errors found")
    
    # Document info
    document_type: str = Field(..., description="Type of document processed")
    page_count: int = Field(..., gt=0, description="Number of pages processed")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    @validator('extraction_confidence')
    def validate_confidence(cls, v):
        """Validate confidence score is within valid range."""
        if v < 0.5:
            raise ValueError('Extraction confidence too low for automatic processing')
        return v

# Export all claim types
__all__ = [
    "MedicalClaim",
    "DentalClaim",
    "PrescriptionClaim",
    "FormExtraction"
]
