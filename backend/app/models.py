from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    voice_embedding = Column(Text, nullable=True)
    is_voice_enrolled = Column(Boolean, default=False)
    
    # Admin fields
    is_admin = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    orders = relationship("Order", back_populates="user")
    auth_logs = relationship("AuthLog", back_populates="user")

class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Voice Authentication Thresholds
    similarity_threshold_strong = Column(Float, default=0.75)
    similarity_threshold_weak = Column(Float, default=0.50)
    
    # Authorization Thresholds
    amount_threshold_low = Column(Float, default=500.0)
    amount_threshold_medium = Column(Float, default=2000.0)
    amount_threshold_high = Column(Float, default=10000.0)
    
    # Trust Score Requirements
    trust_score_low = Column(Integer, default=50)
    trust_score_medium = Column(Integer, default=70)
    trust_score_high = Column(Integer, default=85)
    
    # Trust Score Weights (percentages)
    weight_voice_biometrics = Column(Float, default=0.40)
    weight_speech_consistency = Column(Float, default=0.20)
    weight_behavioral_pattern = Column(Float, default=0.15)
    weight_device_integrity = Column(Float, default=0.15)
    weight_contextual_anomaly = Column(Float, default=0.10)
    
    # Logging Settings
    log_level = Column(String, default="INFO")
    enable_debug = Column(Boolean, default=False)
    log_to_file = Column(Boolean, default=True)
    log_to_console = Column(Boolean, default=True)
    
    # Last updated
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_name = Column(String, nullable=False)
    amount_inr = Column(Float, nullable=False)
    search_query = Column(String)
    budget_inr = Column(Float, nullable=True)
    
    speechbrain_similarity = Column(Float)
    overall_trust_score = Column(Float)
    trust_scores = Column(JSON)
    
    decision = Column(String)
    decision_reason = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")

class AuthLog(Base):
    __tablename__ = "auth_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    speechbrain_similarity = Column(Float)
    trust_scores = Column(JSON)
    overall_trust_score = Column(Float)
    
    action_attempted = Column(String)
    decision = Column(String)
    ip_address = Column(String)
    user_agent = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="auth_logs")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)  # e.g., "UPDATE_THRESHOLD", "CREATE_USER"
    target = Column(String)  # What was changed
    old_value = Column(Text)  # Previous value (JSON string)
    new_value = Column(Text)  # New value (JSON string)
    ip_address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)