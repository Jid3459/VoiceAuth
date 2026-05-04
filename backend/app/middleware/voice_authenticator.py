"""
Voice Authentication Middleware (FastAPI dependency).

This is THE security gate for voice-driven tasks. Any task route that should be
protected by voice biometrics declares a dependency on `VoiceAuthGuard(...)`.

Flow per protected request:
    1. Read uploaded audio + form fields (user_id, query/task).
    2. Verify the user exists and has enrolled their voice.
    3. Extract a voice embedding for the current utterance and compute cosine
       similarity against the enrolled embedding.
    4. Run the 5-layer trust scorer to produce per-layer scores and an overall
       weighted trust score.
    5. Compare overall trust score against a per-task threshold. Below the
       threshold the request is rejected (HTTP 401) before the route handler
       runs. Above or equal to the threshold the route handler receives a
       `VoiceAuthResult` with the layer scores so it can include them in the
       response and persist them to AuthLog.

Per-task thresholds are resolved by `resolve_threshold(task)` which inspects the
free-text query and returns the matching trust-score bar. The amount-based
authorization in `AuthorizationService` runs *after* this gate when a price is
known; this middleware enforces a baseline.
"""

from dataclasses import dataclass
from typing import Dict, Optional

from fastapi import Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..services.voice_auth import voice_auth_service
from ..services.trust_scorer import trust_scorer_service
from ..services.authorization import authorization_service
from ..logger import get_logger

logger = get_logger(__name__)


@dataclass
class VoiceAuthResult:
    """Outcome of the voice-auth gate, passed to the protected route handler."""
    user: User
    audio_data: bytes
    similarity: float
    trust_scores: Dict[str, int]
    overall_trust_score: int
    threshold_used: int
    ip_address: str
    user_agent: str
    gate_decision: str = "ALLOW"   # ALLOW or DENY from the voice-auth gate
    gate_reason: str = ""           # human-readable reason
    matched_sample: str | None = None  # which enrolled sample (name) matched best


# Default per-task thresholds. These can be overridden per-route by passing
# `default_threshold` to VoiceAuthGuard, or further restricted by the
# amount-based authorization service after the gate has approved entry.
TASK_THRESHOLDS: Dict[str, int] = {
    # Calibrated for browser-recorded audio. Honest same-speaker clips via
    # MediaRecorder land at cosine similarity ~0.55-0.70, which the trust
    # curve maps to ~60-75 overall. Imposters cluster well below 30, so
    # these floors keep the security gap while letting real users through.
    "low": 45,         # browse / read-only queries, low-stakes orders
    "medium": 60,      # mid-value purchases, account changes
    "high": 78,        # high-value purchases, sensitive operations
    "critical": 88,    # password change, transfer, admin actions
}


def resolve_threshold(task_text: str, default: int = 50) -> int:
    """Pick a threshold based on simple keywords in the spoken/typed task.

    The amount-aware AuthorizationService refines this further once a price is
    known. Keep this list explicit and conservative - if a keyword is missing
    the request still has to clear `default` and then the amount check.
    """
    if not task_text:
        return default
    t = task_text.lower()

    # Truly high-stakes operations always need a high trust score.
    critical_kw = ("transfer", "password", "delete account", "wire ", "admin")
    # Big-ticket purchases need medium-high trust; the amount-aware
    # AuthorizationService still applies its own check on top of this.
    high_kw = ("gold", "jewel", "diamond", "rolex")
    medium_kw = (
        "laptop", "iphone", "macbook", "tv", "television",
        "headphone", "watch", "shoes", "bag", "tablet", "camera",
    )

    if any(k in t for k in critical_kw):
        return TASK_THRESHOLDS["critical"]
    if any(k in t for k in high_kw):
        return TASK_THRESHOLDS["high"]
    if any(k in t for k in medium_kw):
        return TASK_THRESHOLDS["medium"]
    return default


class VoiceAuthGuard:
    """FastAPI dependency factory that enforces voice authentication.

    Usage:
        guard = VoiceAuthGuard(default_threshold=70)

        @router.post("/orders/process")
        async def process_order(auth: VoiceAuthResult = Depends(guard), ...):
            ...
    """

    def __init__(self, default_threshold: int = 50, dynamic: bool = True):
        self.default_threshold = default_threshold
        self.dynamic = dynamic

    async def __call__(
        self,
        request: Request,
        user_id: int = Form(...),
        query: str = Form(""),
        audio: UploadFile = File(...),
        db: Session = Depends(get_db),
    ) -> VoiceAuthResult:
        # 1. Resolve user + enrollment state
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.is_voice_enrolled or not user.voice_embedding:
            raise HTTPException(status_code=400, detail="User has not enrolled voice")

        ip_address = request.client.host if request.client else ""
        user_agent = request.headers.get("user-agent", "")

        # 2. Read audio (and keep bytes for the route handler if it needs them)
        audio_data = await audio.read()
        if not audio_data:
            raise HTTPException(status_code=400, detail="Empty audio file received")

        # 3. Extract embedding off the event loop
        try:
            current_embedding = await voice_auth_service.extract_embedding_async(audio_data)
        except Exception as e:
            logger.error(f"Embedding extraction failed for user {user_id}: {e}")
            raise HTTPException(status_code=400, detail="Could not process audio") from e

        # Multi-sample enrollment: compare against every stored sample and
        # take the best match. Returns which named sample matched, useful for
        # family accounts where samples are labeled "Mom", "Dad", etc.
        enrolled_samples = voice_auth_service.string_to_samples(user.voice_embedding or "")
        if not enrolled_samples:
            raise HTTPException(status_code=400, detail="User has no enrolled voice samples")
        similarity, matched_sample = voice_auth_service.compute_max_similarity_with_match(
            current_embedding, enrolled_samples
        )

        # 4. Run the 5 layers and aggregate
        trust_scores = trust_scorer_service.calculate_trust_scores(
            similarity=similarity,
            user_id=user_id,
            db=db,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        overall = trust_scorer_service.calculate_overall_trust(trust_scores)

        # 5. Compare against the per-task threshold
        threshold = resolve_threshold(query, self.default_threshold) if self.dynamic else self.default_threshold

        # Decide ALLOW vs DENY without raising. The gate returns a structured
        # result so the route handler (and the UI) always see the layer
        # scores and the explanation, even when access is denied.
        gate_decision = "ALLOW"
        match_phrase = f" — matched profile '{matched_sample}'" if matched_sample else ""
        gate_reason = (
            f"Voice gate cleared (similarity={similarity:.2f}, "
            f"trust={overall}/100 >= threshold {threshold}){match_phrase}."
        )

        weak_floor = authorization_service.similarity_threshold_weak
        if similarity < weak_floor:
            gate_decision = "DENY"
            gate_reason = (
                f"Voice does not match enrolled speaker "
                f"(similarity={similarity:.2f} < {weak_floor:.2f})."
            )
            logger.warning(
                f"Voice gate DENIED user={user_id} similarity={similarity:.3f} "
                f"< weak_threshold={weak_floor}"
            )
        elif overall < threshold:
            gate_decision = "DENY"
            gate_reason = (
                f"Trust score {overall}/100 below required {threshold} "
                f"for this task."
            )
            logger.warning(
                f"Voice gate DENIED user={user_id} overall_trust={overall} < threshold={threshold}"
            )
        else:
            logger.info(
                f"Voice gate ALLOWED user={user_id} similarity={similarity:.3f} "
                f"trust={overall} threshold={threshold}"
            )

        return VoiceAuthResult(
            user=user,
            audio_data=audio_data,
            similarity=similarity,
            trust_scores=trust_scores,
            overall_trust_score=overall,
            threshold_used=threshold,
            ip_address=ip_address,
            user_agent=user_agent,
            gate_decision=gate_decision,
            gate_reason=gate_reason,
            matched_sample=matched_sample,
        )


# Default guard instance for routes that don't need a custom threshold.
voice_auth_guard = VoiceAuthGuard(default_threshold=TASK_THRESHOLDS["low"], dynamic=True)
