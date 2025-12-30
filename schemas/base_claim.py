# base_claim.py - Base Claim Schema

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum

class ClaimStatus(str, Enum):
    """Claim status enumeration."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_INFO = "pending_info"

class ClaimType(str, Enum):
    """Claim type enumeration."""
    MEDICAL = "medical"
    DENTAL = "dental"
    VISION = "vision"
    PRESCRIPTION = "prescription"
    HOSPITAL = "hospital"
    OTHER = "other"

class BaseClaim(BaseModel):
    """Base claim schema with common fields."""
    
    claim_id: Optional[str] = Field(None, description="Unique claim identifier")
    claim_type: ClaimType = Field(..., description="Type of claim")
    status: ClaimStatus = Field(default=ClaimStatus.DRAFT, description="Current claim status")
    
    # Patient Information
    patient_name: str = Field(..., min_length=1, max_length=200, description="Patient full name")
    patient_id: str = Field(..., description="Patient ID or member number")
    date_of_birth: datetime = Field(..., description="Patient date of birth")
    
    # Claim Details
    service_date: datetime = Field(..., description="Date of service")
    provider_name: str = Field(..., description="Healthcare provider name")
    provider_id: Optional[str] = Field(None, description="Provider ID or NPI")
    
    # Financial
    total_amount: float = Field(..., gt=0, description="Total claim amount")
    currency: str = Field(default="USD", description="Currency code")
    
    # Documentation
    description: Optional[str] = Field(None, max_length=1000, description="Claim description")
    diagnosis_codes: Optional[List[str]] = Field(default=[], description="ICD-10 diagnosis codes")
    procedure_codes: Optional[List[str]] = Field(default=[], description="CPT procedure codes")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    
    @validator('total_amount')
    def validate_amount(cls, v):
        """Validate claim amount is positive and reasonable."""
        if v <= 0:
            raise ValueError('Claim amount must be positive')
        if v > 1000000:  # $1M limit
            raise ValueError('Claim amount exceeds maximum limit')
        return round(v, 2)
    
    @validator('service_date')
    def validate_service_date(cls, v):
        """Validate service date is not in the future."""
        if v > datetime.utcnow():
            raise ValueError('Service date cannot be in the future')
        return v
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ClaimResponse(BaseModel):
    """Response schema for claim operations."""
    
    success: bool
    message: str
    claim_id: Optional[str] = None
    status: Optional[ClaimStatus] = None
    
    class Config:
        use_enum_values = True
