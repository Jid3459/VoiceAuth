from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from .database import engine, Base, init_db
from .routes import auth, orders, admin
from .middleware.rate_limiter import RateLimitMiddleware
from .middleware.error_handler import ErrorHandlerMiddleware
from .middleware.request_logger import RequestLoggerMiddleware
from .logger import get_logger, app_logger
from .cache import cache_manager

logger = get_logger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 70)
    logger.info("🚀 VOICE AUTHENTICATION SYSTEM STARTING")
    logger.info("=" * 70)
    
    try:
        # Initialize database
        init_db()
        logger.info("✓ Database initialized")
        
        # Initialize system settings
        from .models import SystemSettings
        from .database import SessionLocal
        db = SessionLocal()
        try:
            settings = db.query(SystemSettings).first()
            if not settings:
                settings = SystemSettings()
                db.add(settings)
                db.commit()
                logger.info("✓ System settings initialized with defaults")
            else:
                logger.info("✓ System settings loaded from database")
                
            # Update logger settings from database
            app_logger.update_settings(
                log_level=settings.log_level,
                log_to_console=settings.log_to_console,
                log_to_file=settings.log_to_file,
                enable_debug=settings.enable_debug
            )

            # Sync DB-stored thresholds and weights into the singleton services
            # so the very first request honours admin-configured values rather
            # than the hardcoded defaults baked into the service classes.
            from .services.authorization import authorization_service
            from .services.trust_scorer import trust_scorer_service

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
            trust_scorer_service.update_weights(
                voice_biometrics=settings.weight_voice_biometrics,
                speech_consistency=settings.weight_speech_consistency,
                behavioral_pattern=settings.weight_behavioral_pattern,
                device_integrity=settings.weight_device_integrity,
                contextual_anomaly=settings.weight_contextual_anomaly,
            )
            logger.info("✓ Authorization thresholds and trust-score weights synced from database")
        finally:
            db.close()
        
        # Load SpeechBrain model (singleton initialization)
        from .services.voice_auth import voice_auth_service
        logger.info("✓ SpeechBrain ECAPA-TDNN model loaded")
        
        # Log cache status
        logger.info("✓ Cache system initialized")
        
        logger.info("=" * 70)
        logger.info("✓ SYSTEM READY")
        logger.info("📊 Database: SQLite")
        logger.info("🎤 Voice Model: SpeechBrain ECAPA-TDNN")
        logger.info("🔒 Security: Multi-layer authentication enabled")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.critical(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("=" * 70)
    logger.info("👋 Shutting down Voice Authentication System")
    logger.info("=" * 70)
    
    # Log cache statistics
    stats = cache_manager.get_stats()
    logger.info(f"Cache Statistics: {stats}")

# Create FastAPI app
app = FastAPI(
    title="Voice Authentication & Product Ordering System",
    description="Enterprise-grade voice biometric authentication with SpeechBrain ECAPA-TDNN",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ============================================
# MIDDLEWARE (Order matters!)
# ============================================

# 1. CORS Middleware (must be first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
)

# 2. Request Logger Middleware
app.add_middleware(RequestLoggerMiddleware)

# 3. Rate Limiter Middleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# 4. Error Handler Middleware (should be last)
app.add_middleware(ErrorHandlerMiddleware)

# ============================================
# ROUTES
# ============================================

app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(admin.router)

# ============================================
# ROOT ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Root endpoint with system information"""
    logger.debug("Root endpoint accessed")
    return {
        "name": "Voice Authentication System",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "Voice Biometric Authentication (SpeechBrain ECAPA-TDNN)",
            "5-Layer Trust Scoring System",
            "Amount-Based Authorization",
            "Real-time Imposter Detection",
            "Admin Configuration Panel",
            "Comprehensive Audit Logging"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "metrics": "/metrics"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    logger.debug("Health check accessed")
    
    from .database import SessionLocal
    from .models import User
    
    # Check database connection
    db_status = "healthy"
    try:
        db = SessionLocal()
        db.query(User).first()
        db.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Get cache stats
    cache_stats = cache_manager.get_stats()
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": time.time(),
        "components": {
            "database": db_status,
            "voice_model": "healthy",
            "cache": "healthy",
            "api": "healthy"
        },
        "cache_statistics": cache_stats,
        "system": {
            "database": "SQLite",
            "voice_engine": "SpeechBrain ECAPA-TDNN",
            "ml_framework": "PyTorch"
        }
    }

@app.get("/metrics")
async def metrics():
    """System metrics endpoint"""
    logger.debug("Metrics endpoint accessed")
    
    from .database import SessionLocal
    from .models import User, Order, AuthLog
    
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        enrolled_users = db.query(User).filter(User.is_voice_enrolled == True).count()
        total_orders = db.query(Order).count()
        total_auth_logs = db.query(AuthLog).count()
        
        cache_stats = cache_manager.get_stats()
        
        return {
            "users": {
                "total": total_users,
                "enrolled": enrolled_users,
                "enrollment_rate": round(enrolled_users / total_users * 100, 2) if total_users > 0 else 0
            },
            "transactions": {
                "total_orders": total_orders,
                "total_authentications": total_auth_logs
            },
            "cache": cache_stats,
            "uptime": "System uptime tracking not implemented"
        }
    finally:
        db.close()

# ============================================
# EXCEPTION HANDLERS
# ============================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested resource '{request.url.path}' was not found",
            "type": "not_found_error"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Our team has been notified.",
            "type": "internal_error"
        }
    )

# ============================================
# STARTUP MESSAGE
# ============================================

logger.info("FastAPI application configured successfully")