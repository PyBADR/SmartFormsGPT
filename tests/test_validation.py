# test_validation.py - SmartFormsGPT Validation Tests

import pytest
from datetime import datetime, timedelta
from utils.validators import ClaimValidator, ValidationError

class TestPatientIDValidation:
    """Test patient ID validation."""
    
    def test_valid_patient_id(self):
        """Test valid patient ID formats."""
        valid_ids = ["ABC123", "PAT-12345", "MEM-ABC-123", "123456789"]
        for patient_id in valid_ids:
            is_valid, error = ClaimValidator.validate_patient_id(patient_id)
            assert is_valid, f"Expected {patient_id} to be valid"
            assert error is None
    
    def test_invalid_patient_id_too_short(self):
        """Test patient ID that is too short."""
        is_valid, error = ClaimValidator.validate_patient_id("ABC")
        assert not is_valid
        assert "between 6 and 20 characters" in error
    
    def test_invalid_patient_id_too_long(self):
        """Test patient ID that is too long."""
        is_valid, error = ClaimValidator.validate_patient_id("A" * 25)
        assert not is_valid
        assert "between 6 and 20 characters" in error
    
    def test_invalid_patient_id_empty(self):
        """Test empty patient ID."""
        is_valid, error = ClaimValidator.validate_patient_id("")
        assert not is_valid
        assert "cannot be empty" in error
    
    def test_invalid_patient_id_special_chars(self):
        """Test patient ID with invalid special characters."""
        is_valid, error = ClaimValidator.validate_patient_id("ABC@123")
        assert not is_valid
        assert "letters, numbers, and hyphens" in error


class TestNPIValidation:
    """Test NPI (National Provider Identifier) validation."""
    
    def test_valid_npi(self):
        """Test valid NPI number."""
        # Valid NPI with correct Luhn checksum
        is_valid, error = ClaimValidator.validate_provider_npi("1234567893")
        assert is_valid
        assert error is None
    
    def test_npi_optional(self):
        """Test that NPI is optional."""
        is_valid, error = ClaimValidator.validate_provider_npi("")
        assert is_valid
        assert error is None
    
    def test_invalid_npi_length(self):
        """Test NPI with incorrect length."""
        is_valid, error = ClaimValidator.validate_provider_npi("123456")
        assert not is_valid
        assert "exactly 10 digits" in error
    
    def test_invalid_npi_checksum(self):
        """Test NPI with invalid Luhn checksum."""
        is_valid, error = ClaimValidator.validate_provider_npi("1234567890")
        assert not is_valid
        assert "Invalid NPI checksum" in error


class TestDiagnosisCodeValidation:
    """Test ICD-10 diagnosis code validation."""
    
    def test_valid_diagnosis_codes(self):
        """Test valid ICD-10 code formats."""
        valid_codes = ["A00", "A00.1", "Z99.89", "M79.3"]
        for code in valid_codes:
            is_valid, error = ClaimValidator.validate_diagnosis_code(code)
            assert is_valid, f"Expected {code} to be valid"
            assert error is None
    
    def test_invalid_diagnosis_code_format(self):
        """Test invalid ICD-10 code formats."""
        invalid_codes = ["123", "ABC", "A", "A0", "AA00"]
        for code in invalid_codes:
            is_valid, error = ClaimValidator.validate_diagnosis_code(code)
            assert not is_valid, f"Expected {code} to be invalid"
    
    def test_empty_diagnosis_code(self):
        """Test empty diagnosis code."""
        is_valid, error = ClaimValidator.validate_diagnosis_code("")
        assert not is_valid
        assert "cannot be empty" in error


class TestProcedureCodeValidation:
    """Test CPT procedure code validation."""
    
    def test_valid_procedure_codes(self):
        """Test valid CPT code formats."""
        valid_codes = ["99213", "12345", "00100"]
        for code in valid_codes:
            is_valid, error = ClaimValidator.validate_procedure_code(code)
            assert is_valid, f"Expected {code} to be valid"
            assert error is None
    
    def test_invalid_procedure_code_length(self):
        """Test CPT codes with incorrect length."""
        invalid_codes = ["123", "1234", "123456"]
        for code in invalid_codes:
            is_valid, error = ClaimValidator.validate_procedure_code(code)
            assert not is_valid
            assert "exactly 5 digits" in error
    
    def test_invalid_procedure_code_letters(self):
        """Test CPT code with letters."""
        is_valid, error = ClaimValidator.validate_procedure_code("ABC12")
        assert not is_valid
        assert "exactly 5 digits" in error


class TestAmountValidation:
    """Test claim amount validation."""
    
    def test_valid_amounts(self):
        """Test valid claim amounts."""
        valid_amounts = [0.01, 100.00, 1000.50, 50000.99]
        for amount in valid_amounts:
            is_valid, error = ClaimValidator.validate_amount(amount)
            assert is_valid, f"Expected {amount} to be valid"
            assert error is None
    
    def test_amount_too_low(self):
        """Test amount below minimum."""
        is_valid, error = ClaimValidator.validate_amount(0.00)
        assert not is_valid
        assert "at least" in error
    
    def test_amount_too_high(self):
        """Test amount above maximum."""
        is_valid, error = ClaimValidator.validate_amount(2000000.00)
        assert not is_valid
        assert "cannot exceed" in error
    
    def test_amount_too_many_decimals(self):
        """Test amount with too many decimal places."""
        is_valid, error = ClaimValidator.validate_amount(100.123)
        assert not is_valid
        assert "at most 2 decimal places" in error


class TestDateRangeValidation:
    """Test date range validation."""
    
    def test_valid_date_range(self):
        """Test valid date range."""
        start = datetime.utcnow() - timedelta(days=30)
        end = datetime.utcnow() - timedelta(days=1)
        is_valid, error = ClaimValidator.validate_date_range(start, end)
        assert is_valid
        assert error is None
    
    def test_start_after_end(self):
        """Test start date after end date."""
        start = datetime.utcnow()
        end = datetime.utcnow() - timedelta(days=30)
        is_valid, error = ClaimValidator.validate_date_range(start, end)
        assert not is_valid
        assert "before end date" in error
    
    def test_future_date(self):
        """Test future date."""
        start = datetime.utcnow() - timedelta(days=1)
        end = datetime.utcnow() + timedelta(days=1)
        is_valid, error = ClaimValidator.validate_date_range(start, end)
        assert not is_valid
        assert "cannot be in the future" in error
    
    def test_date_too_old(self):
        """Test date too far in the past."""
        start = datetime.utcnow() - timedelta(days=3700)  # >10 years
        end = datetime.utcnow() - timedelta(days=3650)
        is_valid, error = ClaimValidator.validate_date_range(start, end)
        assert not is_valid
        assert "too far in the past" in error


class TestValidateAll:
    """Test comprehensive validation."""
    
    def test_valid_claim_data(self):
        """Test validation of complete valid claim data."""
        claim_data = {
            "patient_id": "PAT-123456",
            "provider_id": "1234567893",
            "total_amount": 500.00,
            "diagnosis_codes": ["A00.1", "Z99.89"],
            "procedure_codes": ["99213", "12345"]
        }
        errors = ClaimValidator.validate_all(claim_data)
        assert len(errors) == 0
    
    def test_invalid_claim_data_multiple_errors(self):
        """Test validation with multiple errors."""
        claim_data = {
            "patient_id": "ABC",  # Too short
            "provider_id": "123",  # Invalid NPI
            "total_amount": -100.00,  # Negative
            "diagnosis_codes": ["123"],  # Invalid format
            "procedure_codes": ["ABC"]  # Invalid format
        }
        errors = ClaimValidator.validate_all(claim_data)
        assert len(errors) > 0
        assert any("Patient ID" in e for e in errors)
        assert any("Provider NPI" in e for e in errors)
        assert any("Amount" in e for e in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

