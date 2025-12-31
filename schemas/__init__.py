"""
Schemas package for SmartFormsGPT.

This package contains Pydantic schemas for claim data validation.
"""

from schemas.base_claim import (
    BaseClaim,
    ClaimStatus,
    ClaimType,
    ClaimResponse
)

from schemas.custom_claim import (
    MedicalClaim,
    DentalClaim,
    PrescriptionClaim,
    FormExtraction
)

__all__ = [
    # Base schemas
    "BaseClaim",
    "ClaimStatus",
    "ClaimType",
    "ClaimResponse",
    # Custom schemas
    "MedicalClaim",
    "DentalClaim",
    "PrescriptionClaim",
    "FormExtraction"
]
