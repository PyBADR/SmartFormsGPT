# decision_engine.py - Claim Decision Engine

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from schemas.base_claim import BaseClaim, ClaimStatus
from logic.rules import ClaimRules
from logger import get_logger

logger = get_logger(__name__)

class DecisionEngine:
    """Engine for automated claim decision making."""
    
    def __init__(self):
        self.rules = ClaimRules()
        self.decision_history = []
    
    def evaluate_claim(self, claim: BaseClaim) -> Tuple[ClaimStatus, List[str], float]:
        """
        Evaluate a claim and return decision.
        
        Returns:
            Tuple of (status, reasons, confidence_score)
        """
        logger.info(f"Evaluating claim: {claim.claim_id}")
        
        reasons = []
        confidence = 1.0
        
        # Check basic validation
        if not self.rules.validate_basic_info(claim):
            reasons.append("Missing or invalid basic information")
            return ClaimStatus.PENDING_INFO, reasons, 0.0
        
        # Check amount limits
        if not self.rules.check_amount_limit(claim):
            reasons.append(f"Claim amount ${claim.total_amount} exceeds policy limit")
            return ClaimStatus.REJECTED, reasons, 1.0
        
        # Check service date validity
        if not self.rules.check_service_date(claim):
            reasons.append("Service date is outside acceptable range")
            return ClaimStatus.REJECTED, reasons, 1.0
        
        # Check for duplicate claims
        if self.rules.check_duplicate(claim):
            reasons.append("Potential duplicate claim detected")
            confidence *= 0.7
        
        # Check documentation completeness
        doc_score = self.rules.check_documentation(claim)
        if doc_score < 0.5:
            reasons.append("Insufficient documentation provided")
            return ClaimStatus.PENDING_INFO, reasons, doc_score
        
        confidence *= doc_score
        
        # Auto-approve if all checks pass and amount is below threshold
        if claim.total_amount < 1000 and confidence > 0.8:
            reasons.append("Auto-approved: All criteria met")
            return ClaimStatus.APPROVED, reasons, confidence
        
        # Otherwise, send for manual review
        reasons.append("Requires manual review")
        return ClaimStatus.UNDER_REVIEW, reasons, confidence
    
    def process_batch(self, claims: List[BaseClaim]) -> Dict[str, any]:
        """Process multiple claims in batch."""
        logger.info(f"Processing batch of {len(claims)} claims")
        
        results = {
            "total": len(claims),
            "approved": 0,
            "rejected": 0,
            "under_review": 0,
            "pending_info": 0,
            "details": []
        }
        
        for claim in claims:
            status, reasons, confidence = self.evaluate_claim(claim)
            
            results["details"].append({
                "claim_id": claim.claim_id,
                "status": status,
                "reasons": reasons,
                "confidence": confidence
            })
            
            # Update counters
            if status == ClaimStatus.APPROVED:
                results["approved"] += 1
            elif status == ClaimStatus.REJECTED:
                results["rejected"] += 1
            elif status == ClaimStatus.UNDER_REVIEW:
                results["under_review"] += 1
            elif status == ClaimStatus.PENDING_INFO:
                results["pending_info"] += 1
        
        logger.info(f"Batch processing complete: {results['approved']} approved, "
                   f"{results['rejected']} rejected, {results['under_review']} under review")
        
        return results
    
    def get_decision_explanation(self, claim: BaseClaim) -> str:
        """Generate human-readable explanation for decision."""
        status, reasons, confidence = self.evaluate_claim(claim)
        
        explanation = f"Claim Decision: {status.value.upper()}\n"
        explanation += f"Confidence Score: {confidence:.2%}\n\n"
        explanation += "Reasons:\n"
        
        for i, reason in enumerate(reasons, 1):
            explanation += f"{i}. {reason}\n"
        
        return explanation

# Export
__all__ = ["DecisionEngine"]
