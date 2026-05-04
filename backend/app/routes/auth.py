from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
from passlib.context import CryptContext

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse, LoginRequest, LoginResponse
from ..services.voice_auth import voice_auth_service
from ..services.authorization import authorization_service
from ..logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    logger.info(f"Registration attempt for email: {user.email}")
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        logger.warning(f"Registration failed - Email already exists: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"User registered successfully: {user.username} (ID: {db_user.id})")
    return db_user

@router.post("/login", response_model=LoginResponse)
def login_user(login: LoginRequest, db: Session = Depends(get_db)):
    """Login user with email and password"""
    logger.info(f"Login attempt for email: {login.email}")
    
    user = db.query(User).filter(User.email == login.email).first()
    if not user:
        logger.warning(f"Login failed - User not found: {login.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not pwd_context.verify(login.password, user.hashed_password):
        logger.warning(f"Login failed - Invalid password for: {login.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    logger.info(f"User logged in successfully: {user.username} (ID: {user.id})")
    
    return LoginResponse(
        user=user,
        message="Login successful"
    )

@router.post("/enroll-voice/{user_id}")
async def enroll_voice(
    user_id: int,
    audio: UploadFile = File(...),
    sample_name: str = Form("", description="Optional label for this sample (e.g. 'Dad', 'Mom', 'Office Mic')"),
    db: Session = Depends(get_db)
):
    """Enroll user's voice by storing embedding"""
    logger.info(f"Voice enrollment attempt for user_id: {user_id}")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"Voice enrollment failed - User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            logger.error("Voice enrollment failed - Empty audio file")
            raise HTTPException(status_code=400, detail="Empty audio file received")

        logger.debug(f"Received audio: {len(audio_data)} bytes, type: {audio.content_type}")

        # Reject too-short clips at enrollment - a noisy 0.3s sample produces
        # an unstable embedding that ruins every subsequent verification.
        duration = voice_auth_service.get_audio_duration_seconds(audio_data)
        if duration < 1.5:
            logger.error(f"Voice enrollment failed - audio too short ({duration:.2f}s)")
            raise HTTPException(
                status_code=400,
                detail=f"Audio too short ({duration:.2f}s); please record at least 1.5 seconds."
            )

        new_embedding = await voice_auth_service.extract_embedding_async(audio_data)

        # Multi-sample enrollment: APPEND a new labeled sample to the user's
        # voice profile instead of replacing the old one. Verification compares
        # the live audio against every stored sample and uses the best match,
        # so additional samples can only help — and the same account can hold
        # multiple speakers (family members) under different sample names.
        import uuid
        from datetime import datetime as _dt
        existing = voice_auth_service.string_to_samples(user.voice_embedding or "")
        label = (sample_name or "").strip() or f"Sample {len(existing) + 1}"
        existing.append({
            "id": str(uuid.uuid4()),
            "name": label,
            "created_at": _dt.utcnow().isoformat() + "Z",
            "embedding": new_embedding,
        })
        user.voice_embedding = voice_auth_service.samples_to_string(existing)
        user.is_voice_enrolled = True

        db.commit()

        logger.info(
            f"Voice sample '{label}' enrolled for user {user.username} (ID: {user_id}); "
            f"total samples now {len(existing)}"
        )

        return {
            "message": "Voice sample enrolled successfully",
            "user_id": user_id,
            "sample_name": label,
            "embedding_dimension": len(new_embedding),
            "total_samples": len(existing),
        }
    
    except Exception as e:
        logger.error(f"Voice enrollment error for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice enrollment failed: {str(e)}")

@router.post("/verify-voice/{user_id}")
async def verify_voice(
    user_id: int,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Verify voice against enrolled embedding"""
    logger.info(f"Voice verification attempt for user_id: {user_id}")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"Voice verification failed - User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.is_voice_enrolled:
        logger.warning(f"Voice verification failed - Voice not enrolled for user_id: {user_id}")
        raise HTTPException(status_code=400, detail="User has not enrolled voice")
    
    try:
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file received")
        
        current_embedding = await voice_auth_service.extract_embedding_async(audio_data)
        enrolled_list = voice_auth_service.string_to_embeddings(user.voice_embedding or "")
        if not enrolled_list:
            raise HTTPException(status_code=400, detail="User has no enrolled voice samples")
        similarity = voice_auth_service.compute_max_similarity(current_embedding, enrolled_list)

        strong = authorization_service.similarity_threshold_strong
        weak = authorization_service.similarity_threshold_weak

        if similarity >= strong:
            status = "STRONG_MATCH"
            message = "Voice verified - strong match"
        elif similarity >= weak:
            status = "UNCERTAIN"
            message = "Voice verification uncertain - proceed with caution"
        else:
            status = "NO_MATCH"
            message = "Voice does not match - possible imposter"
        
        logger.info(f"Voice verification complete for user_id {user_id}: similarity={similarity:.3f}, status={status}")
        
        return {
            "similarity": float(similarity),
            "status": status,
            "message": message
        }
    
    except Exception as e:
        logger.error(f"Voice verification error for user_id {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice verification failed: {str(e)}")

@router.get("/enrollments/{user_id}")
def list_enrollments(user_id: int, db: Session = Depends(get_db)):
    """Return all voice samples on this account with metadata (no embeddings)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    samples = voice_auth_service.string_to_samples(user.voice_embedding or "")
    return {
        "user_id": user_id,
        "is_voice_enrolled": user.is_voice_enrolled,
        "total_samples": len(samples),
        "samples": [
            {"id": s["id"], "name": s["name"], "created_at": s["created_at"]}
            for s in samples
        ],
    }


@router.delete("/enrollments/{user_id}/{sample_id}")
def delete_enrollment_sample(user_id: int, sample_id: str, db: Session = Depends(get_db)):
    """Remove ONE voice sample (by id) from this account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    samples = voice_auth_service.string_to_samples(user.voice_embedding or "")
    remaining = [s for s in samples if s["id"] != sample_id]
    if len(remaining) == len(samples):
        raise HTTPException(status_code=404, detail="Voice sample not found")
    if remaining:
        user.voice_embedding = voice_auth_service.samples_to_string(remaining)
        user.is_voice_enrolled = True
    else:
        user.voice_embedding = None
        user.is_voice_enrolled = False
    db.commit()
    logger.info(
        f"Voice sample {sample_id} removed from user {user.username} (ID: {user_id}); "
        f"{len(remaining)} samples remain"
    )
    return {
        "message": "Voice sample removed",
        "user_id": user_id,
        "remaining_samples": len(remaining),
    }


@router.delete("/enrollments/{user_id}")
def clear_enrollments(user_id: int, db: Session = Depends(get_db)):
    """Remove ALL voice samples for this user; they will need to re-enroll."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.voice_embedding = None
    user.is_voice_enrolled = False
    db.commit()
    logger.info(f"All voice samples cleared for user {user.username} (ID: {user_id})")
    return {"message": "All voice samples cleared", "user_id": user_id}


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user details"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Get user failed - User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.debug(f"User details retrieved for user_id: {user_id}")
    return user