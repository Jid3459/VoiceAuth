from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Order, AuthLog
from ..schemas import OrderResponse, TrustScores
from ..services.product_analyzer import product_analyzer_service
from ..services.authorization import authorization_service
from ..middleware.voice_authenticator import VoiceAuthResult, voice_auth_guard

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/process", response_model=OrderResponse)
async def process_order(
    query: str = Form(...),
    auth: VoiceAuthResult = Depends(voice_auth_guard),
    db: Session = Depends(get_db),
):
    """
    Voice-authenticated task endpoint.

    The voice gate (`voice_auth_guard`) has already:
      * verified the user is enrolled,
      * extracted the embedding and computed similarity,
      * computed all 5 trust-score layers and the overall score,
      * rejected the request (HTTP 401) if it failed the per-task threshold.

    This handler only runs when the speaker has cleared the gate. Its job is to
    interpret the task (product query?), apply the amount-aware authorization
    rule on top of the gate, and persist the audit log + order.
    """
    # === Product detection ===
    is_product_query = product_analyzer_service.is_product_query(query)
    product_name = search_query = budget_inr = amount_inr = None
    if is_product_query:
        product_name, search_query, budget_inr = product_analyzer_service.extract_product_info(query)
        amount_inr = product_analyzer_service.get_product_price(product_name)

    # === Decision: gate result first, then amount-aware authorization ===
    if auth.gate_decision == "DENY":
        decision = "DENY"
        reason = auth.gate_reason
    elif is_product_query and amount_inr:
        decision, reason = authorization_service.authorize_transaction(
            amount=amount_inr,
            trust_score=auth.overall_trust_score,
            similarity=auth.similarity,
        )
    else:
        decision = "ALLOW"
        reason = auth.gate_reason or "Voice gate cleared - non-product query, no transaction."

    # === Audit log ===
    db.add(AuthLog(
        user_id=auth.user.id,
        speechbrain_similarity=auth.similarity,
        trust_scores=auth.trust_scores,
        overall_trust_score=auth.overall_trust_score,
        action_attempted=query,
        decision=decision,
        ip_address=auth.ip_address,
        user_agent=auth.user_agent,
    ))

    # === Persist order if applicable ===
    if is_product_query:
        db.add(Order(
            user_id=auth.user.id,
            product_name=product_name or "Unknown",
            amount_inr=amount_inr or 0,
            search_query=search_query,
            budget_inr=budget_inr,
            speechbrain_similarity=auth.similarity,
            overall_trust_score=auth.overall_trust_score,
            trust_scores=auth.trust_scores,
            decision=decision,
            decision_reason=reason,
        ))

    db.commit()

    return OrderResponse(
        is_product_query=is_product_query,
        search_query=search_query,
        product=product_name,
        budget_inr=budget_inr,
        speechbrain_similarity=round(auth.similarity, 2),
        trust_scores=TrustScores(**auth.trust_scores),
        overall_trust_score=auth.overall_trust_score,
        amount_inr=amount_inr,
        decision=decision,
        reason=reason,
    )


@router.get("/history/{user_id}")
def get_order_history(user_id: int, db: Session = Depends(get_db)):
    """Get user's order history"""
    return (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )


@router.get("/auth-logs/{user_id}")
def get_auth_logs(user_id: int, limit: int = 20, db: Session = Depends(get_db)):
    """Get authentication logs for user"""
    return (
        db.query(AuthLog)
        .filter(AuthLog.user_id == user_id)
        .order_by(AuthLog.created_at.desc())
        .limit(limit)
        .all()
    )
