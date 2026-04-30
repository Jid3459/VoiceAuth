from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_voice_enrolled: bool
    is_admin: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    user: UserResponse
    message: str

class VoiceEnrollRequest(BaseModel):
    user_id: int

class TrustScores(BaseModel):
    voice_biometrics: int
    speech_consistency: int
    behavioral_pattern: int
    device_integrity: int
    contextual_anomaly: int

class OrderRequest(BaseModel):
    user_id: int
    query: str

class OrderResponse(BaseModel):
    is_product_query: bool
    search_query: Optional[str]
    product: Optional[str]
    budget_inr: Optional[float]
    
    speechbrain_similarity: float
    
    trust_scores: TrustScores
    overall_trust_score: int
    
    amount_inr: Optional[float]
    
    decision: str
    reason: str

# Admin Schemas
class SystemSettingsResponse(BaseModel):
    id: int
    similarity_threshold_strong: float
    similarity_threshold_weak: float
    amount_threshold_low: float
    amount_threshold_medium: float
    amount_threshold_high: float
    trust_score_low: int
    trust_score_medium: int
    trust_score_high: int
    weight_voice_biometrics: float
    weight_speech_consistency: float
    weight_behavioral_pattern: float
    weight_device_integrity: float
    weight_contextual_anomaly: float
    log_level: str
    enable_debug: bool
    log_to_file: bool
    log_to_console: bool
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SystemSettingsUpdate(BaseModel):
    similarity_threshold_strong: Optional[float] = None
    similarity_threshold_weak: Optional[float] = None
    amount_threshold_low: Optional[float] = None
    amount_threshold_medium: Optional[float] = None
    amount_threshold_high: Optional[float] = None
    trust_score_low: Optional[int] = None
    trust_score_medium: Optional[int] = None
    trust_score_high: Optional[int] = None
    weight_voice_biometrics: Optional[float] = None
    weight_speech_consistency: Optional[float] = None
    weight_behavioral_pattern: Optional[float] = None
    weight_device_integrity: Optional[float] = None
    weight_contextual_anomaly: Optional[float] = None
    log_level: Optional[str] = None
    enable_debug: Optional[bool] = None
    log_to_file: Optional[bool] = None
    log_to_console: Optional[bool] = None

class AuditLogResponse(BaseModel):
    id: int
    admin_id: int
    action: str
    target: str
    old_value: Optional[str]
    new_value: Optional[str]
    ip_address: str
    created_at: datetime
    
    class Config:
        from_attributes = True