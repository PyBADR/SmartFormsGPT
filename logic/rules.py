# rules.py - Business Rules for Claims

from datetime import datetime, timedelta
from typing import List
from schemas.base_claim import BaseClaim
from logger import get_logger

logger = get_logger(__name__)

class ClaimRules:
    """Business rules for claim validation and processing."""
    
    # Configuration
    MAX_CLAIM_AMOUNT = 100000  # $100k
    AUTO_APPROVE_THRESHOLD = 1000  # $1k
    MAX_SERVICE_AGE_DAYS = 365  # 1 year
    MIN_DOCUMENTATION_SCORE = 0.5
    
    def __init__(self):
        self.processed_claims = set()  # For duplicate detection
    
    def validate_basic_info(self, claim: BaseClaim) -> bool:
        """
        Validate basic claim information is present and valid.
        """
        required_fields = [
            claim.patient_name,
            claim.patient_id,
            claim.service_date,
            claim.provider_name,
            claim.total_amount
        ]
        
        if not all(required_fields):
            logger.warning(f"Claim {claim.claim_id} missing required fields")
            return False
        
        # Validate patient name format
        if len(claim.patient_name.strip()) < 2:
            logger.warning(f"Invalid patient name: {claim.patient_name}")
            return False
        
        return True
    
    def check_amount_limit(self, claim: BaseClaim) -> bool:
        """
        Check if claim amount is within acceptable limits.
        """
        if claim.total_amount > self.MAX_CLAIM_AMOUNT:
            logger.warning(f"Claim {claim.claim_id} exceeds maximum amount: ${claim.total_amount}")
            return False
        
        if claim.total_amount <= 0:
            logger.warning(f"Claim {claim.claim_id} has invalid amount: ${claim.total_amount}")
            return False
        
        return True
    
    def check_service_date(self, claim: BaseClaim) -> bool:
        """
        Validate service date is within acceptable range.
        """
        now = datetime.utcnow()
        max_age = now - timedelta(days=self.MAX_SERVICE_AGE_DAYS)
        
        # Service date cannot be in the future
        if claim.service_date > now:
            logger.warning(f"Claim {claim.claim_id} has future service date")
            return False
        
        # Service date cannot be too old
        if claim.service_date < max_age:
            logger.warning(f"Claim {claim.claim_id} service date too old")
            return False
        
        return True
    
    def check_duplicate(self, claim: BaseClaim) -> bool:
        """
        Check if claim might be a duplicate.
        """
        # Create a unique key for the claim
        claim_key = f"{claim.patient_id}_{claim.service_date.date()}_{claim.total_amount}"
        
        if claim_key in self.processed_claims:
            logger.warning(f"Potential duplicate claim detected: {claim_key}")
            return True
        
        self.processed_claims.add(claim_key)
        return False
    
    def check_documentation(self, claim: BaseClaim) -> float:
        """
        Check documentation completeness and return a score (0-1).
        """
        score = 0.0
        max_score = 5.0
        
        # Check for description
        if claim.description and len(claim.description) > 10:
            score += 1.0
        
        # Check for diagnosis codes
        if claim.diagnosis_codes and len(claim.diagnosis_codes) > 0:
            score += 1.5
        
        # Check for procedure codes
        if claim.procedure_codes and len(claim.procedure_codes) > 0:
            score += 1.5
        
        # Check for provider ID
        if claim.provider_id:
            score += 0.5
        
        # Check for reasonable amount documentation
        if claim.total_amount > 5000:
            # High-value claims need more documentation
            if len(claim.diagnosis_codes or []) > 0 and len(claim.procedure_codes or []) > 0:
                score += 0.5
        else:
            score += 0.5
        
        normalized_score = score / max_score
        logger.info(f"Documentation score for claim {claim.claim_id}: {normalized_score:.2f}")
        
        return normalized_score
    
    def requires_manual_review(self, claim: BaseClaim) -> bool:
        """
        Determine if claim requires manual review.
        """
        # High-value claims always need review
        if claim.total_amount > self.AUTO_APPROVE_THRESHOLD:
            return True
        
        # Claims with low documentation score need review
        if self.check_documentation(claim) < self.MIN_DOCUMENTATION_SCORE:
            return True
        
        # Claims with potential duplicates need review
        if self.check_duplicate(claim):
            return True
        
        return False

# Export
__all__ = ["ClaimRules"]
