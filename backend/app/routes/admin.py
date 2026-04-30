from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json

from ..database import get_db
from ..models import User, SystemSettings, AuditLog
from ..schemas import (
    SystemSettingsResponse, 
    SystemSettingsUpdate, 
    AuditLogResponse,
    UserResponse
)
from ..logger import get_logger
from ..services.authorization import authorization_service
from ..services.trust_scorer import trust_scorer_service

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

def verify_admin(user_id: int, db: Session) -> User:
    """Verify user is admin/superuser"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Admin access attempt with invalid user_id: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    if not (user.is_admin or user.is_superuser):
        logger.warning(f"Unauthorized admin access attempt by user: {user.username} (ID: {user_id})")
        raise HTTPException(status_code=403, detail="Admin access required")
    
    logger.info(f"Admin access granted to user: {user.username} (ID: {user_id})")
    return user

def get_or_create_settings(db: Session) -> SystemSettings:
    """Get existing settings or create default"""
    settings = db.query(SystemSettings).first()
    if not settings:
        logger.info("Creating default system settings")
        settings = SystemSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.get("/settings", response_model=SystemSettingsResponse)
def get_settings(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get current system settings (Admin only)"""
    verify_admin(user_id, db)
    settings = get_or_create_settings(db)
    logger.info(f"Settings retrieved by admin user_id: {user_id}")
    return settings

@router.put("/settings", response_model=SystemSettingsResponse)
def update_settings(
    user_id: int,
    updates: SystemSettingsUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update system settings (Admin only)"""
    admin = verify_admin(user_id, db)
    settings = get_or_create_settings(db)
    
    # Store old values for audit
    old_values = {
        "similarity_threshold_strong": settings.similarity_threshold_strong,
        "similarity_threshold_weak": settings.similarity_threshold_weak,
        "amount_threshold_low": settings.amount_threshold_low,
        "amount_threshold_medium": settings.amount_threshold_medium,
        "amount_threshold_high": settings.amount_threshold_high,
        "trust_score_low": settings.trust_score_low,
        "trust_score_medium": settings.trust_score_medium,
        "trust_score_high": settings.trust_score_high,
        "log_level": settings.log_level,
        "enable_debug": settings.enable_debug,
    }
    
    # Update settings
    update_data = updates.dict(exclude_unset=True)
    new_values = {}
    
    for key, value in update_data.items():
        if hasattr(settings, key):
            old_val = getattr(settings, key)
            setattr(settings, key, value)
            new_values[key] = value
            logger.info(f"Setting '{key}' changed from {old_val} to {value} by {admin.username}")
    
    settings.updated_at = datetime.utcnow()
    settings.updated_by = user_id
    
    db.commit()
    db.refresh(settings)
    
    # Create audit log
    audit_log = AuditLog(
        admin_id=user_id,
        action="UPDATE_SETTINGS",
        target="SystemSettings",
        old_value=json.dumps(old_values),
        new_value=json.dumps(new_values),
        ip_address=request.client.host if request.client else "unknown"
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"System settings updated by {admin.username} (ID: {user_id})")
    
    # Update authorization service with new thresholds
    authorization_service.update_thresholds(
        amount_threshold_low=settings.amount_threshold_low,
        amount_threshold_medium=settings.amount_threshold_medium,
        amount_threshold_high=settings.amount_threshold_high,
        trust_score_low=settings.trust_score_low,
        trust_score_medium=settings.trust_score_medium,
        trust_score_high=settings.trust_score_high,
        similarity_threshold_weak=settings.similarity_threshold_weak,
        similarity_threshold_strong=settings.similarity_threshold_strong,
    )
    
    # Update trust scorer weights
    trust_scorer_service.update_weights(
        voice_biometrics=settings.weight_voice_biometrics,
        speech_consistency=settings.weight_speech_consistency,
        behavioral_pattern=settings.weight_behavioral_pattern,
        device_integrity=settings.weight_device_integrity,
        contextual_anomaly=settings.weight_contextual_anomaly
    )
    
    # Update logging settings
    from ..logger import app_logger
    app_logger.update_settings(
        log_level=settings.log_level,
        log_to_console=settings.log_to_console,
        log_to_file=settings.log_to_file,
        enable_debug=settings.enable_debug
    )
    
    return settings

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    user_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get audit logs (Admin only)"""
    verify_admin(user_id, db)
    
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    logger.info(f"Audit logs retrieved by user_id: {user_id}, count: {len(logs)}")
    return logs

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get all users (Admin only)"""
    verify_admin(user_id, db)
    
    users = db.query(User).all()
    logger.info(f"User list retrieved by admin user_id: {user_id}, total users: {len(users)}")
    return users

@router.put("/users/{target_user_id}/admin-status")
def update_admin_status(
    user_id: int,
    target_user_id: int,
    is_admin: bool,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update user admin status (Superuser only)"""
    admin = verify_admin(user_id, db)
    
    # Only superusers can modify admin status
    if not admin.is_superuser:
        logger.warning(f"Non-superuser admin access denied for user_id: {user_id}")
        raise HTTPException(status_code=403, detail="Superuser access required")
    
    target_user = db.query(User).filter(User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")
    
    old_status = target_user.is_admin
    target_user.is_admin = is_admin
    db.commit()
    
    # Create audit log
    audit_log = AuditLog(
        admin_id=user_id,
        action="UPDATE_ADMIN_STATUS",
        target=f"User: {target_user.username}",
        old_value=json.dumps({"is_admin": old_status}),
        new_value=json.dumps({"is_admin": is_admin}),
        ip_address=request.client.host if request.client else "unknown"
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"Admin status updated for user {target_user.username} by {admin.username}")
    
    return {
        "message": f"Admin status updated for {target_user.username}",
        "is_admin": is_admin
    }

@router.get("/logs")
def get_app_logs(
    user_id: int,
    lines: int = 100,
    db: Session = Depends(get_db)
):
    """Get application logs (Admin only)"""
    verify_admin(user_id, db)
    
    from ..logger import app_logger
    logs = app_logger.get_recent_logs(lines)
    
    logger.info(f"Application logs retrieved by user_id: {user_id}, lines: {lines}")
    
    return {
        "logs": logs,
        "total_lines": len(logs)
    }

@router.post("/logs/clear")
def clear_app_logs(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Clear application logs (Superuser only)"""
    admin = verify_admin(user_id, db)
    
    if not admin.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser access required")
    
    from ..logger import app_logger
    app_logger.clear_logs()
    
    # Create audit log
    audit_log = AuditLog(
        admin_id=user_id,
        action="CLEAR_LOGS",
        target="Application Logs",
        old_value=None,
        new_value=None,
        ip_address=request.client.host if request.client else "unknown"
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"Application logs cleared by {admin.username}")
    
    return {"message": "Logs cleared successfully"}

@router.get("/stats")
def get_system_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get system statistics (Admin only)"""
    verify_admin(user_id, db)
    
    from ..models import Order, AuthLog
    
    total_users = db.query(User).count()
    total_orders = db.query(Order).count()
    total_auth_logs = db.query(AuthLog).count()
    
    approved_orders = db.query(Order).filter(Order.decision == "ALLOW").count()
    denied_orders = db.query(Order).filter(Order.decision == "DENY").count()
    
    enrolled_users = db.query(User).filter(User.is_voice_enrolled == True).count()
    
    logger.info(f"System statistics retrieved by user_id: {user_id}")
    
    return {
        "total_users": total_users,
        "enrolled_users": enrolled_users,
        "total_orders": total_orders,
        "approved_orders": approved_orders,
        "denied_orders": denied_orders,
        "total_auth_logs": total_auth_logs,
        "approval_rate": round(approved_orders / total_orders * 100, 2) if total_orders > 0 else 0
    }