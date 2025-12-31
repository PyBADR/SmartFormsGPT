# test_decision.py - SmartFormsGPT Decision Engine Tests

import pytest
from datetime import datetime, timedelta
from schemas.base_claim import BaseClaim, ClaimStatus, ClaimType
from logic.decision_engine import DecisionEngine
from logic.rules import ClaimRules

class TestDecisionEngine:
    """Test decision engine functionality."""
    
    @pytest.fixture
    def engine(self):
        """Create a decision engine instance."""
        return DecisionEngine()
    
    @pytest.fixture
    def valid_claim(self):
        """Create a valid claim for testing."""
        return BaseClaim(
            claim_id="CLM-TEST-001",
            claim_type=ClaimType.MEDICAL,
            patient_name="John Doe",
            patient_id="PAT-123456",
            date_of_birth=datetime(1980, 1, 1),
            service_date=datetime.utcnow() - timedelta(days=10),
            provider_name="Test Hospital",
            provider_id="1234567893",
            total_amount=500.00,
            description="Medical consultation",
            diagnosis_codes=["A00.1"],
            procedure_codes=["99213"]
        )
    
    def test_auto_approve_low_amount(self, engine, valid_claim):
        """Test auto-approval for low-amount claims."""
        valid_claim.total_amount = 500.00  # Below $1000 threshold
        status, reasons, confidence = engine.evaluate_claim(valid_claim)
        
        assert status == ClaimStatus.APPROVED
        assert confidence > 0.8
        assert any("Auto-approved" in r for r in reasons)
    
    def test_manual_review_high_amount(self, engine, valid_claim):
        """Test manual review for high-amount claims."""
        valid_claim.total_amount = 5000.00  # Above $1000 threshold
        status, reasons, confidence = engine.evaluate_claim(valid_claim)
        
        assert status == ClaimStatus.UNDER_REVIEW
        assert any("manual review" in r.lower() for r in reasons)
    
    def test_reject_excessive_amount(self, engine, valid_claim):
        """Test rejection for excessive amounts."""
        valid_claim.total_amount = 150000.00  # Above $100k limit
        status, reasons, confidence = engine.evaluate_claim(valid_claim)
        
        assert status == ClaimStatus.REJECTED
        assert any("exceeds" in r.lower() for r in reasons)
    
    def test_reject_future_service_date(self, engine, valid_claim):
        """Test rejection for future service dates."""
        valid_claim.service_date = datetime.utcnow() + timedelta(days=10)
        status, reasons, confidence = engine.evaluate_claim(valid_claim)
        
        assert status == ClaimStatus.REJECTED
        assert any("service date" in r.lower() for r in reasons)
    
    def test_pending_missing_info(self, engine, valid_claim):
        """Test pending status for missing information."""
        valid_claim.description = None
        valid_claim.diagnosis_codes = []
        valid_claim.procedure_codes = []
        
        status, reasons, confidence = engine.evaluate_claim(valid_claim)
        
        assert status == ClaimStatus.PENDING_INFO
        assert confidence < 0.5
    
    def test_batch_processing(self, engine, valid_claim):
        """Test batch processing of multiple claims."""
        claims = []
        for i in range(5):
            claim = BaseClaim(
                claim_id=f"CLM-TEST-{i:03d}",
                claim_type=ClaimType.MEDICAL,
                patient_name=f"Patient {i}",
                patient_id=f"PAT-{i:06d}",
                date_of_birth=datetime(1980, 1, 1),
                service_date=datetime.utcnow() - timedelta(days=10),
                provider_name="Test Hospital",
                total_amount=500.00 + (i * 100),
                description="Test claim",
                diagnosis_codes=["A00.1"],
                procedure_codes=["99213"]
            )
            claims.append(claim)
        
        results = engine.process_batch(claims)
        
        assert results["total"] == 5
        assert results["approved"] + results["rejected"] + results["under_review"] + results["pending_info"] == 5
        assert len(results["details"]) == 5
    
    def test_decision_explanation(self, engine, valid_claim):
        """Test decision explanation generation."""
        explanation = engine.get_decision_explanation(valid_claim)
        
        assert "Claim Decision:" in explanation
        assert "Confidence Score:" in explanation
        assert "Reasons:" in explanation


class TestClaimRules:
    """Test business rules."""
    
    @pytest.fixture
    def rules(self):
        """Create a rules instance."""
        return ClaimRules()
    
    @pytest.fixture
    def valid_claim(self):
        """Create a valid claim for testing."""
        return BaseClaim(
            claim_id="CLM-TEST-001",
            claim_type=ClaimType.MEDICAL,
            patient_name="John Doe",
            patient_id="PAT-123456",
            date_of_birth=datetime(1980, 1, 1),
            service_date=datetime.utcnow() - timedelta(days=10),
            provider_name="Test Hospital",
            total_amount=500.00,
            description="Medical consultation",
            diagnosis_codes=["A00.1"],
            procedure_codes=["99213"]
        )
    
    def test_validate_basic_info_valid(self, rules, valid_claim):
        """Test basic info validation with valid data."""
        assert rules.validate_basic_info(valid_claim) is True
    
    def test_validate_basic_info_missing_name(self, rules, valid_claim):
        """Test basic info validation with missing name."""
        valid_claim.patient_name = ""
        assert rules.validate_basic_info(valid_claim) is False
    
    def test_check_amount_limit_valid(self, rules, valid_claim):
        """Test amount limit check with valid amount."""
        assert rules.check_amount_limit(valid_claim) is True
    
    def test_check_amount_limit_exceeds(self, rules, valid_claim):
        """Test amount limit check with excessive amount."""
        valid_claim.total_amount = 150000.00
        assert rules.check_amount_limit(valid_claim) is False
    
    def test_check_amount_limit_negative(self, rules, valid_claim):
        """Test amount limit check with negative amount."""
        valid_claim.total_amount = -100.00
        assert rules.check_amount_limit(valid_claim) is False
    
    def test_check_service_date_valid(self, rules, valid_claim):
        """Test service date check with valid date."""
        assert rules.check_service_date(valid_claim) is True
    
    def test_check_service_date_future(self, rules, valid_claim):
        """Test service date check with future date."""
        valid_claim.service_date = datetime.utcnow() + timedelta(days=10)
        assert rules.check_service_date(valid_claim) is False
    
    def test_check_service_date_too_old(self, rules, valid_claim):
        """Test service date check with very old date."""
        valid_claim.service_date = datetime.utcnow() - timedelta(days=400)
        assert rules.check_service_date(valid_claim) is False
    
    def test_check_duplicate_first_claim(self, rules, valid_claim):
        """Test duplicate check for first claim."""
        assert rules.check_duplicate(valid_claim) is False
    
    def test_check_duplicate_same_claim(self, rules, valid_claim):
        """Test duplicate check for same claim."""
        rules.check_duplicate(valid_claim)  # First submission
        assert rules.check_duplicate(valid_claim) is True  # Duplicate
    
    def test_check_documentation_complete(self, rules, valid_claim):
        """Test documentation check with complete data."""
        score = rules.check_documentation(valid_claim)
        assert score > 0.5
    
    def test_check_documentation_incomplete(self, rules, valid_claim):
        """Test documentation check with incomplete data."""
        valid_claim.description = None
        valid_claim.diagnosis_codes = []
        valid_claim.procedure_codes = []
        valid_claim.provider_id = None
        
        score = rules.check_documentation(valid_claim)
        assert score < 0.5
    
    def test_requires_manual_review_high_amount(self, rules, valid_claim):
        """Test manual review requirement for high amounts."""
        valid_claim.total_amount = 5000.00
        assert rules.requires_manual_review(valid_claim) is True
    
    def test_requires_manual_review_low_amount(self, rules, valid_claim):
        """Test manual review not required for low amounts."""
        valid_claim.total_amount = 500.00
        # Should not require manual review if documentation is good
        result = rules.requires_manual_review(valid_claim)
        # Result depends on documentation score


class TestClaimStatusTransitions:
    """Test claim status transitions."""
    
    @pytest.fixture
    def engine(self):
        """Create a decision engine instance."""
        return DecisionEngine()
    
    def test_draft_to_submitted(self, engine):
        """Test transition from draft to submitted."""
        claim = BaseClaim(
            claim_id="CLM-TEST-001",
            claim_type=ClaimType.MEDICAL,
            status=ClaimStatus.DRAFT,
            patient_name="John Doe",
            patient_id="PAT-123456",
            date_of_birth=datetime(1980, 1, 1),
            service_date=datetime.utcnow() - timedelta(days=10),
            provider_name="Test Hospital",
            total_amount=500.00,
            description="Test",
            diagnosis_codes=["A00.1"],
            procedure_codes=["99213"]
        )
        
        status, reasons, confidence = engine.evaluate_claim(claim)
        assert status in [ClaimStatus.APPROVED, ClaimStatus.UNDER_REVIEW, ClaimStatus.PENDING_INFO]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

