from typing import Tuple
from ..logger import get_logger

logger = get_logger(__name__)

class AuthorizationService:
    
    def __init__(self):
        # Default thresholds (can be updated dynamically)
        self.amount_threshold_low = 500.0
        self.amount_threshold_medium = 2000.0
        self.amount_threshold_high = 10000.0
        
        self.trust_score_low = 50
        self.trust_score_medium = 70
        self.trust_score_high = 85
        
        # Backwards-compatible alias for the "weak" similarity floor.
        # Calibrated for browser-recorded audio (webm/opus via MediaRecorder):
        # legitimate same-speaker cosine similarity routinely lands in 0.45-0.75
        # because of mic differences, AGC, and ambient noise. A 0.50 floor
        # rejects honest users; 0.40 is permissive enough to let them through
        # while still catching obvious imposters (which sit near 0.0-0.25).
        self.similarity_threshold = 0.40
        self.similarity_threshold_weak = 0.40
        self.similarity_threshold_strong = 0.65

        logger.info("Authorization Service initialized with default thresholds")
    
    def update_thresholds(
        self,
        amount_threshold_low: float = None,
        amount_threshold_medium: float = None,
        amount_threshold_high: float = None,
        trust_score_low: int = None,
        trust_score_medium: int = None,
        trust_score_high: int = None,
        similarity_threshold: float = None,
        similarity_threshold_weak: float = None,
        similarity_threshold_strong: float = None,
    ):
        """Update authorization thresholds dynamically"""
        if amount_threshold_low is not None:
            self.amount_threshold_low = amount_threshold_low
            logger.info(f"Amount threshold (low) updated to: {amount_threshold_low}")
        
        if amount_threshold_medium is not None:
            self.amount_threshold_medium = amount_threshold_medium
            logger.info(f"Amount threshold (medium) updated to: {amount_threshold_medium}")
        
        if amount_threshold_high is not None:
            self.amount_threshold_high = amount_threshold_high
            logger.info(f"Amount threshold (high) updated to: {amount_threshold_high}")
        
        if trust_score_low is not None:
            self.trust_score_low = trust_score_low
            logger.info(f"Trust score requirement (low) updated to: {trust_score_low}")
        
        if trust_score_medium is not None:
            self.trust_score_medium = trust_score_medium
            logger.info(f"Trust score requirement (medium) updated to: {trust_score_medium}")
        
        if trust_score_high is not None:
            self.trust_score_high = trust_score_high
            logger.info(f"Trust score requirement (high) updated to: {trust_score_high}")
        
        if similarity_threshold is not None:
            self.similarity_threshold = similarity_threshold
            self.similarity_threshold_weak = similarity_threshold
            logger.info(f"Similarity threshold updated to: {similarity_threshold}")

        if similarity_threshold_weak is not None:
            self.similarity_threshold_weak = similarity_threshold_weak
            self.similarity_threshold = similarity_threshold_weak
            logger.info(f"Similarity threshold (weak) updated to: {similarity_threshold_weak}")

        if similarity_threshold_strong is not None:
            self.similarity_threshold_strong = similarity_threshold_strong
            logger.info(f"Similarity threshold (strong) updated to: {similarity_threshold_strong}")
    
    def authorize_transaction(
        self,
        amount: float,
        trust_score: int,
        similarity: float
    ) -> Tuple[str, str]:
        """
        Determine if transaction should be ALLOWED or DENIED
        Returns: (decision, reason)
        """
        logger.debug(f"Authorization check: amount={amount}, trust={trust_score}, similarity={similarity}")
        
        # CRITICAL OVERRIDE: Low similarity = likely imposter
        if similarity < self.similarity_threshold_weak and amount >= self.amount_threshold_low:
            decision = "DENY"
            reason = f"Low SpeechBrain similarity ({similarity:.2f}) indicates different speaker. Transaction denied for security."
            logger.warning(f"Transaction DENIED - Low similarity: {similarity:.2f} for amount ₹{amount}")
            return decision, reason
        
        # Rule 1: amount < threshold_low → ALWAYS ALLOW
        if amount < self.amount_threshold_low:
            decision = "ALLOW"
            reason = f"Amount ₹{amount:.2f} is below ₹{self.amount_threshold_low} threshold. Auto-approved."
            logger.info(f"Transaction ALLOWED - Below threshold: ₹{amount}")
            return decision, reason
        
        # Rule 2: threshold_low - threshold_medium → Require trust_score_low
        if self.amount_threshold_low <= amount < self.amount_threshold_medium:
            if trust_score >= self.trust_score_low:
                decision = "ALLOW"
                reason = f"Amount ₹{amount:.2f} approved with trust score {trust_score}/100."
                logger.info(f"Transaction ALLOWED - Amount: ₹{amount}, Trust: {trust_score}")
                return decision, reason
            else:
                decision = "DENY"
                reason = f"Trust score {trust_score}/100 below required {self.trust_score_low} for ₹{amount:.2f} transaction."
                logger.warning(f"Transaction DENIED - Insufficient trust: {trust_score} for amount ₹{amount}")
                return decision, reason
        
        # Rule 3: threshold_medium - threshold_high → Require trust_score_medium
        if self.amount_threshold_medium <= amount < self.amount_threshold_high:
            if trust_score >= self.trust_score_medium:
                decision = "ALLOW"
                reason = f"Amount ₹{amount:.2f} approved with trust score {trust_score}/100."
                logger.info(f"Transaction ALLOWED - Amount: ₹{amount}, Trust: {trust_score}")
                return decision, reason
            else:
                decision = "DENY"
                reason = f"Trust score {trust_score}/100 below required {self.trust_score_medium} for ₹{amount:.2f} transaction."
                logger.warning(f"Transaction DENIED - Insufficient trust: {trust_score} for amount ₹{amount}")
                return decision, reason
        
        # Rule 4: amount >= threshold_high → Require trust_score_high
        if amount >= self.amount_threshold_high:
            if trust_score >= self.trust_score_high:
                decision = "ALLOW"
                reason = f"High-value amount ₹{amount:.2f} approved with trust score {trust_score}/100."
                logger.info(f"Transaction ALLOWED - High value: ₹{amount}, Trust: {trust_score}")
                return decision, reason
            else:
                decision = "DENY"
                reason = f"Trust score {trust_score}/100 below required {self.trust_score_high} for high-value ₹{amount:.2f} transaction."
                logger.warning(f"Transaction DENIED - Insufficient trust for high value: {trust_score} for amount ₹{amount}")
                return decision, reason
        
        logger.error(f"Authorization logic error for amount: {amount}")
        return "DENY", "Unknown error in authorization logic."

# Singleton instance
authorization_service = AuthorizationService()