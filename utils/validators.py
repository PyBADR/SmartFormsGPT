# validators.py - Data Validators

from typing import List, Optional, Tuple
from datetime import datetime
import re
from logger import get_logger

logger = get_logger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class ClaimValidator:
    """Validator for claim data."""
    
    @staticmethod
    def validate_patient_id(patient_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate patient ID format.
        Returns: (is_valid, error_message)
        """
        if not patient_id or len(patient_id.strip()) == 0:
            return False, "Patient ID cannot be empty"
        
        # Check length (typically 6-20 characters)
        if len(patient_id) < 6 or len(patient_id) > 20:
            return False, "Patient ID must be between 6 and 20 characters"
        
        # Check format (alphanumeric with optional hyphens)
        if not re.match(r'^[A-Z0-9\-]+$', patient_id.upper()):
            return False, "Patient ID must contain only letters, numbers, and hyphens"
        
        return True, None
    
    @staticmethod
    def validate_provider_npi(npi: str) -> Tuple[bool, Optional[str]]:
        """
        Validate NPI (National Provider Identifier) format.
        NPI is a 10-digit number.
        """
        if not npi:
            return True, None  # NPI is optional
        
        # Remove any spaces or hyphens
        cleaned_npi = re.sub(r'[\s\-]', '', npi)
        
        # Check if it's exactly 10 digits
        if not re.match(r'^\d{10}$', cleaned_npi):
            return False, "NPI must be exactly 10 digits"
        
        # Luhn algorithm check for NPI validation
        if not ClaimValidator._luhn_check(cleaned_npi):
            return False, "Invalid NPI checksum"
        
        return True, None
    
    @staticmethod
    def _luhn_check(number: str) -> bool:
        """
        Validate number using Luhn algorithm.
        """
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        
        return checksum % 10 == 0
    
    @staticmethod
    def validate_diagnosis_code(code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate ICD-10 diagnosis code format.
        """
        if not code:
            return False, "Diagnosis code cannot be empty"
        
        # ICD-10 format: Letter + 2 digits + optional decimal + up to 4 more digits
        pattern = r'^[A-Z]\d{2}(?:\.\d{1,4})?$'
        
        if not re.match(pattern, code.upper()):
            return False, "Invalid ICD-10 code format (e.g., A00, A00.1, A00.12)"
        
        return True, None
    
    @staticmethod
    def validate_procedure_code(code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate CPT procedure code format.
        """
        if not code:
            return False, "Procedure code cannot be empty"
        
        # CPT codes are 5 digits
        if not re.match(r'^\d{5}$', code):
            return False, "CPT code must be exactly 5 digits"
        
        return True, None
    
    @staticmethod
    def validate_amount(amount: float, min_amount: float = 0.01, max_amount: float = 1000000) -> Tuple[bool, Optional[str]]:
        """
        Validate claim amount.
        """
        if amount < min_amount:
            return False, f"Amount must be at least ${min_amount}"
        
        if amount > max_amount:
            return False, f"Amount cannot exceed ${max_amount}"
        
        # Check for reasonable decimal places (max 2)
        if round(amount, 2) != amount:
            return False, "Amount can have at most 2 decimal places"
        
        return True, None
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> Tuple[bool, Optional[str]]:
        """
        Validate date range.
        """
        if start_date > end_date:
            return False, "Start date must be before end date"
        
        # Check if dates are not too far in the past (e.g., 10 years)
        max_age = datetime.utcnow().replace(year=datetime.utcnow().year - 10)
        if start_date < max_age:
            return False, "Date is too far in the past"
        
        # Check if dates are not in the future
        if end_date > datetime.utcnow():
            return False, "Date cannot be in the future"
        
        return True, None
    
    @staticmethod
    def validate_all(claim_data: dict) -> List[str]:
        """
        Validate all claim data and return list of errors.
        """
        errors = []
        
        # Validate patient ID
        if 'patient_id' in claim_data:
            is_valid, error = ClaimValidator.validate_patient_id(claim_data['patient_id'])
            if not is_valid:
                errors.append(f"Patient ID: {error}")
        
        # Validate provider NPI
        if 'provider_id' in claim_data and claim_data['provider_id']:
            is_valid, error = ClaimValidator.validate_provider_npi(claim_data['provider_id'])
            if not is_valid:
                errors.append(f"Provider NPI: {error}")
        
        # Validate amount
        if 'total_amount' in claim_data:
            is_valid, error = ClaimValidator.validate_amount(claim_data['total_amount'])
            if not is_valid:
                errors.append(f"Amount: {error}")
        
        # Validate diagnosis codes
        if 'diagnosis_codes' in claim_data:
            for code in claim_data['diagnosis_codes']:
                is_valid, error = ClaimValidator.validate_diagnosis_code(code)
                if not is_valid:
                    errors.append(f"Diagnosis code '{code}': {error}")
        
        # Validate procedure codes
        if 'procedure_codes' in claim_data:
            for code in claim_data['procedure_codes']:
                is_valid, error = ClaimValidator.validate_procedure_code(code)
                if not is_valid:
                    errors.append(f"Procedure code '{code}': {error}")
        
        logger.info(f"Validation complete: {len(errors)} errors found")
        return errors

# Export
__all__ = ["ClaimValidator", "ValidationError"]
