import pytest
from app.services.authorization import AuthorizationService

class TestAuthorizationService:
    
    @pytest.fixture
    def auth_service(self):
        return AuthorizationService()
    
    def test_amount_below_500_always_allow(self, auth_service):
        """Test that amounts < 500 are always allowed"""
        decision, reason = auth_service.authorize_transaction(
            amount=400,
            trust_score=10,  # Even with very low trust
            similarity=0.30  # Even with low similarity
        )
        assert decision == "ALLOW"
        assert "500" in reason
    
    def test_low_similarity_deny_above_500(self, auth_service):
        """Test that low similarity denies transactions >= 500"""
        decision, reason = auth_service.authorize_transaction(
            amount=1000,
            trust_score=80,  # Even with high trust
            similarity=0.40  # Low similarity
        )
        assert decision == "DENY"
        assert "similarity" in reason.lower()
    
    def test_amount_500_2000_requires_trust_50(self, auth_service):
        """Test amount range 500-2000 requires trust >= 50"""
        # Should ALLOW with trust >= 50
        decision, _ = auth_service.authorize_transaction(
            amount=1500,
            trust_score=55,
            similarity=0.80
        )
        assert decision == "ALLOW"
        
        # Should DENY with trust < 50
        decision, reason = auth_service.authorize_transaction(
            amount=1500,
            trust_score=45,
            similarity=0.80
        )
        assert decision == "DENY"
        assert "50" in reason
    
    def test_amount_2000_10000_requires_trust_70(self, auth_service):
        """Test amount range 2000-10000 requires trust >= 70"""
        # Should ALLOW with trust >= 70
        decision, _ = auth_service.authorize_transaction(
            amount=5000,
            trust_score=75,
            similarity=0.80
        )
        assert decision == "ALLOW"
        
        # Should DENY with trust < 70
        decision, reason = auth_service.authorize_transaction(
            amount=5000,
            trust_score=65,
            similarity=0.80
        )
        assert decision == "DENY"
        assert "70" in reason
    
    def test_amount_above_10000_requires_trust_85(self, auth_service):
        """Test amount > 10000 requires trust >= 85"""
        # Should ALLOW with trust >= 85
        decision, _ = auth_service.authorize_transaction(
            amount=15000,
            trust_score=90,
            similarity=0.85
        )
        assert decision == "ALLOW"
        
        # Should DENY with trust < 85
        decision, reason = auth_service.authorize_transaction(
            amount=15000,
            trust_score=80,
            similarity=0.85
        )
        assert decision == "DENY"
        assert "85" in reason
    
    def test_imposter_scenario(self, auth_service):
        """Test complete imposter scenario"""
        decision, reason = auth_service.authorize_transaction(
            amount=10000,
            trust_score=25,  # Low trust due to low similarity
            similarity=0.25  # Clear imposter
        )
        assert decision == "DENY"
        assert "similarity" in reason.lower() or "speaker" in reason.lower()
    
    def test_genuine_user_high_amount(self, auth_service):
        """Test genuine user with high amount transaction"""
        decision, reason = auth_service.authorize_transaction(
            amount=20000,
            trust_score=92,
            similarity=0.90
        )
        assert decision == "ALLOW"
        assert "approved" in reason.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])