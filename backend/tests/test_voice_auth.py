import pytest
import numpy as np
from app.services.voice_auth import VoiceAuthService

class TestVoiceAuthService:
    
    @pytest.fixture
    def voice_service(self):
        return VoiceAuthService()
    
    def test_compute_similarity_identical_embeddings(self, voice_service):
        """Test similarity between identical embeddings"""
        embedding1 = np.random.rand(192)
        embedding2 = embedding1.copy()
        
        similarity = voice_service.compute_similarity(embedding1, embedding2)
        
        assert similarity == pytest.approx(1.0, abs=0.01)
    
    def test_compute_similarity_different_embeddings(self, voice_service):
        """Test similarity between different embeddings"""
        embedding1 = np.random.rand(192)
        embedding2 = np.random.rand(192)
        
        similarity = voice_service.compute_similarity(embedding1, embedding2)
        
        assert 0.0 <= similarity <= 1.0
        assert similarity < 0.95  # Should not be highly similar
    
    def test_embedding_serialization(self, voice_service):
        """Test embedding to string and back conversion"""
        original_embedding = np.random.rand(192)
        
        # Convert to string
        embedding_str = voice_service.embedding_to_string(original_embedding)
        assert isinstance(embedding_str, str)
        assert len(embedding_str) > 0
        
        # Convert back to array
        recovered_embedding = voice_service.string_to_embedding(embedding_str)
        
        # Check if recovered embedding matches original
        np.testing.assert_array_almost_equal(original_embedding, recovered_embedding)
    
    def test_similarity_symmetry(self, voice_service):
        """Test that similarity is symmetric"""
        embedding1 = np.random.rand(192)
        embedding2 = np.random.rand(192)
        
        sim1 = voice_service.compute_similarity(embedding1, embedding2)
        sim2 = voice_service.compute_similarity(embedding2, embedding1)
        
        assert sim1 == pytest.approx(sim2, abs=0.0001)
    
    def test_orthogonal_embeddings(self, voice_service):
        """Test similarity of orthogonal embeddings"""
        # Create orthogonal vectors
        embedding1 = np.zeros(192)
        embedding1[0] = 1.0
        
        embedding2 = np.zeros(192)
        embedding2[1] = 1.0
        
        similarity = voice_service.compute_similarity(embedding1, embedding2)
        
        # Orthogonal vectors should have similarity near 0
        assert similarity == pytest.approx(0.0, abs=0.1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])