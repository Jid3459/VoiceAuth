from typing import Dict
from sqlalchemy.orm import Session
from ..models import AuthLog
from ..logger import get_logger

logger = get_logger(__name__)


def _clamp(value: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, value))


class TrustScorerService:

    def __init__(self):
        # Default weights (overridden at startup from SystemSettings)
        self.weights = {
            "voice_biometrics": 0.40,
            "speech_consistency": 0.20,
            "behavioral_pattern": 0.15,
            "device_integrity": 0.15,
            "contextual_anomaly": 0.10,
        }
        logger.info("Trust Scorer Service initialized with default weights")

    def update_weights(
        self,
        voice_biometrics: float = None,
        speech_consistency: float = None,
        behavioral_pattern: float = None,
        device_integrity: float = None,
        contextual_anomaly: float = None,
    ):
        if voice_biometrics is not None:
            self.weights["voice_biometrics"] = voice_biometrics
        if speech_consistency is not None:
            self.weights["speech_consistency"] = speech_consistency
        if behavioral_pattern is not None:
            self.weights["behavioral_pattern"] = behavioral_pattern
        if device_integrity is not None:
            self.weights["device_integrity"] = device_integrity
        if contextual_anomaly is not None:
            self.weights["contextual_anomaly"] = contextual_anomaly
        logger.info(f"Trust scorer weights updated: {self.weights}")

    def calculate_trust_scores(
        self,
        similarity: float,
        user_id: int,
        db: Session,
        user_agent: str = "",
        ip_address: str = "",
    ) -> Dict[str, int]:
        logger.debug(f"Calculating trust scores: user={user_id}, sim={similarity:.3f}")

        scores = {
            "voice_biometrics": self._calculate_voice_biometrics(similarity),
            "speech_consistency": self._calculate_speech_consistency(similarity, user_id, db),
            "behavioral_pattern": self._calculate_behavioral_pattern(user_id, db),
            "device_integrity": self._calculate_device_integrity(ip_address, user_agent, user_id, db),
            "contextual_anomaly": self._calculate_contextual_anomaly(user_id, db),
        }
        logger.debug(f"Trust scores: {scores}")
        return scores

    def _calculate_voice_biometrics(self, similarity: float) -> int:
        """Deterministic piecewise-linear mapping of cosine similarity to 0..100."""
        s = max(0.0, min(1.0, similarity))
        # Below 0.30 cosine sim → near zero; above 0.95 → 100
        if s < 0.30:
            score = (s / 0.30) * 15.0
        elif s < 0.50:
            score = 15.0 + (s - 0.30) / 0.20 * 25.0      # 15 → 40
        elif s < 0.65:
            score = 40.0 + (s - 0.50) / 0.15 * 20.0      # 40 → 60
        elif s < 0.75:
            score = 60.0 + (s - 0.65) / 0.10 * 18.0      # 60 → 78
        elif s < 0.85:
            score = 78.0 + (s - 0.75) / 0.10 * 12.0      # 78 → 90
        elif s < 0.95:
            score = 90.0 + (s - 0.85) / 0.10 * 8.0       # 90 → 98
        else:
            score = 100.0
        return _clamp(int(round(score)))

    def _calculate_speech_consistency(self, similarity: float, user_id: int, db: Session) -> int:
        """Compare current similarity to user's recent average similarity."""
        recent = (
            db.query(AuthLog)
            .filter(AuthLog.user_id == user_id)
            .order_by(AuthLog.created_at.desc())
            .limit(5)
            .all()
        )

        if not recent:
            # Cold start: anchor consistency to current similarity itself
            return _clamp(int(round(similarity * 100)))

        sims = [log.speechbrain_similarity for log in recent if log.speechbrain_similarity is not None]
        if not sims:
            return _clamp(int(round(similarity * 100)))

        avg = sum(sims) / len(sims)
        # Distance penalty: 0 distance → 100, distance 0.5 → 0
        distance = abs(similarity - avg)
        consistency = max(0.0, 1.0 - (distance / 0.5))
        return _clamp(int(round(consistency * 100)))

    def _calculate_behavioral_pattern(self, user_id: int, db: Session) -> int:
        """Penalise users with many recent DENY decisions."""
        recent = (
            db.query(AuthLog)
            .filter(AuthLog.user_id == user_id)
            .order_by(AuthLog.created_at.desc())
            .limit(10)
            .all()
        )

        if not recent:
            return 90  # cold-start: no denies on record = trustworthy

        deny_count = sum(1 for log in recent if log.decision == "DENY")
        # 0 denies → 95, each deny costs 8 points
        score = 95 - deny_count * 8
        return _clamp(score)

    def _calculate_device_integrity(self, ip_address: str, user_agent: str, user_id: int, db: Session) -> int:
        """Score based on whether IP/user-agent matches recent history."""
        recent = (
            db.query(AuthLog)
            .filter(AuthLog.user_id == user_id)
            .order_by(AuthLog.created_at.desc())
            .limit(10)
            .all()
        )

        if not recent:
            return 85  # cold-start: no prior device data = neutral-positive

        known_ips = {log.ip_address for log in recent if log.ip_address}
        known_uas = {log.user_agent for log in recent if log.user_agent}

        ip_match = bool(ip_address) and ip_address in known_ips
        ua_match = bool(user_agent) and user_agent in known_uas

        if ip_match and ua_match:
            return 95
        if ip_match:
            return 90
        if ua_match:
            return 75
        # Unknown device with established history → suspicious
        return 50

    def _calculate_contextual_anomaly(self, user_id: int, db: Session) -> int:
        """Detect bursts of requests (rapid-fire = likely automated/replay)."""
        recent = (
            db.query(AuthLog)
            .filter(AuthLog.user_id == user_id)
            .order_by(AuthLog.created_at.desc())
            .limit(10)
            .all()
        )

        if len(recent) < 2:
            return 92  # cold-start: no burst data = no anomaly signal

        # Time span of last N requests; tighter span = more anomalous
        span_seconds = (recent[0].created_at - recent[-1].created_at).total_seconds()
        n = len(recent)

        if span_seconds <= 0:
            return 20

        avg_gap = span_seconds / max(1, n - 1)
        if avg_gap < 5:
            return 15
        if avg_gap < 15:
            return 35
        if avg_gap < 60:
            return 60
        if avg_gap < 300:
            return 80
        return 90

    def calculate_overall_trust(self, trust_scores: Dict[str, int]) -> int:
        overall = sum(trust_scores[k] * self.weights[k] for k in self.weights)
        return _clamp(int(round(overall)))


# Singleton instance
trust_scorer_service = TrustScorerService()
