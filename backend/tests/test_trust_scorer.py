import pytest
from app.services.trust_scorer import TrustScorerService
from unittest.mock import Mock, MagicMock

class TestTrustScorerService:
    
    @pytest.fixture
    def trust_scorer(self):
        return TrustScorerService()
    
    @pytest.fixture
    def mock_db(self):
        return MagicMock()
    
    def test_voice_biometrics_high_similarity(self, trust_scorer):
        """Test voice biometrics score with high similarity"""
        score = trust_scorer._calculate_voice_biometrics(0.95)
        assert 90 <= score <= 100
    
    def test_voice_biometrics_strong_match(self, trust_scorer):
        """Test voice biometrics score at strong match threshold"""
        score = trust_scorer._calculate_voice_biometrics(0.75)
        assert 75 <= score <= 87
    
    def test_voice_biometrics_uncertain(self, trust_scorer):
        """Test voice biometrics score in uncertain range"""
        score = trust_scorer._calculate_voice_biometrics(0.60)
        assert 35 <= score <= 70
    
    def test_voice_biometrics_imposter(self, trust_scorer):
        """Test voice biometrics score for imposter (low similarity)"""
        score = trust_scorer._calculate_voice_biometrics(0.30)
        assert 0 <= score <= 25
    
    def test_overall_trust_calculation(self, trust_scorer):
        """Test weighted average calculation"""
        trust_scores = {
            "voice_biometrics": 80,
            "speech_consistency": 70,
            "behavioral_pattern": 75,
            "device_integrity": 85,
            "contextual_anomaly": 90
        }
        
        overall = trust_scorer.calculate_overall_trust(trust_scores)
        
        # Should be weighted average (voice_biometrics has 40% weight)
        expected = (80 * 0.40 + 70 * 0.20 + 75 * 0.15 + 85 * 0.15 + 90 * 0.10)
        assert overall == int(expected)
    
    def test_overall_trust_low_voice_biometrics(self, trust_scorer):
        """Test that low voice biometrics significantly reduces overall score"""
        trust_scores = {
            "voice_biometrics": 20,  # Very low
            "speech_consistency": 80,
            "behavioral_pattern": 85,
            "device_integrity": 90,
            "contextual_anomaly": 95
        }
        
        overall = trust_scorer.calculate_overall_trust(trust_scores)
        
        # Overall should be low despite other high scores
        assert overall < 70
    
    def test_all_scores_returned(self, trust_scorer, mock_db):
        """Test that all 5 trust scores are returned"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        scores = trust_scorer.calculate_trust_scores(
            similarity=0.85,
            user_id=1,
            db=mock_db,
            user_agent="test",
            ip_address="127.0.0.1"
        )
        
        required_keys = [
            "voice_biometrics",
            "speech_consistency",
            "behavioral_pattern",
            "device_integrity",
            "contextual_anomaly"
        ]
        
        for key in required_keys:
            assert key in scores
            assert isinstance(scores[key], int)
            assert 0 <= scores[key] <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])