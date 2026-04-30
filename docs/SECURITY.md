
### `docs/SECURITY.md`

```markdown
# Security Guidelines

## Overview

This document outlines security measures, best practices, and threat mitigation strategies for the Voice Authentication & Product Ordering System.

---

## Voice Authentication Security

### 1. SpeechBrain ECAPA-TDNN Model

**Strengths:**
- State-of-the-art speaker verification
- Robust to noise and channel variations
- 192-dimensional embeddings provide high discriminability

**Security Measures:**
- Similarity threshold at 0.75 for strong match
- Automatic rejection below 0.50 similarity
- Continuous authentication logging

### 2. Voice Spoofing Protection

**Current Measures:**
- Cosine similarity threshold prevents simple replay attacks
- Voice consistency checking across sessions

**Recommended Enhancements:**
```python
# Implement liveness detection
def detect_liveness(audio_features):
    # Check for natural speech variations
    # Detect synthetic/TTS voices
    # Analyze background noise patterns
    pass

# Anti-replay attack
def check_replay_attack(embedding, timestamp):
    # Verify embedding novelty
    # Check temporal patterns
    pass
	
	3. Embedding Storage
Current Implementation:

Python

# Embeddings stored as comma-separated strings
voice_embedding = "0.123,0.456,0.789,..."
Security Considerations:

Embeddings are NOT reversible to original audio
Consider encryption for highly sensitive deployments:
Python

from cryptography.fernet import Fernet

def encrypt_embedding(embedding, key):
    cipher = Fernet(key)
    embedding_str = embedding_to_string(embedding)
    encrypted = cipher.encrypt(embedding_str.encode())
    return encrypted

def decrypt_embedding(encrypted_embedding, key):
    cipher = Fernet(key)
    decrypted = cipher.decrypt(encrypted_embedding)
    return string_to_embedding(decrypted.decode())
Authentication & Authorization
1. Password Security
Current:

Python

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
Recommendations:

Enforce strong passwords (min 12 chars, mixed case, numbers, symbols)
Implement password complexity checks
Add password history (prevent reuse)
Python

import re

def validate_password_strength(password):
    if len(password) < 12:
        return False, "Password must be at least 12 characters"
    
    if not re.search(r"[A-Z]", password):
        return False, "Must contain uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Must contain lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Must contain number"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Must contain special character"
    
    return True, "Strong password"
2. Session Management
Implement JWT Tokens:

Python

from jose import JWTError, jwt
from datetime import datetime, timedelta

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
3. Multi-Factor Authentication (MFA)
Recommended Implementation:

Python

import pyotp

class MFAService:
    def generate_secret(self, user_id):
        secret = pyotp.random_base32()
        # Store secret in database
        return secret
    
    def verify_otp(self, user_id, otp_code):
        secret = get_user_mfa_secret(user_id)
        totp = pyotp.TOTP(secret)
        return totp.verify(otp_code)
API Security
1. Rate Limiting
Implement with slowapi:

Python

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/orders/process")
@limiter.limit("5/minute")  # 5 requests per minute
async def process_order(request: Request, ...):
    pass
2. Input Validation
Pydantic Schemas:

Python

from pydantic import BaseModel, validator, Field

class OrderRequest(BaseModel):
    user_id: int = Field(gt=0)
    query: str = Field(min_length=1, max_length=500)
    
    @validator('query')
    def sanitize_query(cls, v):
        # Remove SQL injection attempts
        dangerous_chars = [';', '--', '/*', '*/']
        for char in dangerous_chars:
            if char in v:
                raise ValueError('Invalid characters in query')
        return v
3. CORS Configuration
Production Settings:

Python

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],  # Never use "*" in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)
4. HTTPS Enforcement
Nginx Configuration:

nginx

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
Database Security
1. SQL Injection Prevention
Use ORM (SQLAlchemy):

Python

# SAFE - parameterized query
user = db.query(User).filter(User.id == user_id).first()

# UNSAFE - never do this
# query = f"SELECT * FROM users WHERE id = {user_id}"
2. Database Encryption
At-Rest Encryption:

SQL

-- PostgreSQL: Enable pgcrypto extension
CREATE EXTENSION pgcrypto;

-- Encrypt sensitive columns
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR,
    encrypted_data BYTEA
);

INSERT INTO users (email, encrypted_data) 
VALUES ('user@example.com', pgp_sym_encrypt('sensitive', 'encryption-key'));
3. Access Control
Principle of Least Privilege:

SQL

-- Create read-only user for analytics
CREATE USER analytics_user WITH PASSWORD 'secure_password';
GRANT SELECT ON orders, auth_logs TO analytics_user;

-- Revoke unnecessary permissions
REVOKE CREATE, DROP ON DATABASE voice_auth_db FROM PUBLIC;
4. Backup & Recovery
Bash

# Automated daily backups
0 2 * * * pg_dump -U voice_auth_user voice_auth_db > /backups/db_$(date +\%Y\%m\%d).sql

# Encrypt backups
gpg --encrypt /backups/db_20240115.sql
Frontend Security
1. XSS Prevention
React Automatic Escaping:

TypeScript

// React automatically escapes values
<div>{userInput}</div>  // Safe

// Dangerous - avoid dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{__html: userInput}} />
2. Secure Audio Handling
Validate Audio Files:

TypeScript

const validateAudioFile = (file: File): boolean => {
    const allowedTypes = ['audio/wav', 'audio/mpeg', 'audio/webm'];
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    if (!allowedTypes.includes(file.type)) {
        alert('Invalid file type');
        return false;
    }
    
    if (file.size > maxSize) {
        alert('File too large');
        return false;
    }
    
    return true;
};
3. Secure Storage
Never store sensitive data in localStorage:

TypeScript

// BAD
localStorage.setItem('password', password);

// GOOD - use httpOnly cookies for tokens
// Set by backend, inaccessible to JavaScript
Threat Model
Threat 1: Voice Impersonation
Attack Vector: Attacker uses recorded voice or deepfake

Mitigation:

Similarity threshold (< 0.50 = reject)
Liveness detection
Multi-factor authentication
Transaction limits
Threat 2: Replay Attack
Attack Vector: Attacker replays recorded voice authentication

Mitigation:

Challenge-response system:
Python

def generate_challenge():
    return f"Please say the following: {random_words()}"
Timestamp verification
Session binding
Threat 3: Database Breach
Attack Vector: Attacker gains access to database

Mitigation:

Encrypted embeddings
Hashed passwords (bcrypt)
No raw audio storage
Database access logs
Regular security audits
Threat 4: Man-in-the-Middle (MITM)
Attack Vector: Attacker intercepts API requests

Mitigation:

HTTPS/TLS encryption
Certificate pinning (mobile apps)
HSTS headers
Threat 5: Denial of Service (DoS)
Attack Vector: Flood API with requests

Mitigation:

Rate limiting
IP blocking
CAPTCHA for repeated failures
DDoS protection (Cloudflare)
Security Checklist
Pre-Production
 Change default SECRET_KEY
 Use strong database password
 Enable HTTPS/SSL
 Configure CORS properly
 Implement rate limiting
 Add input validation
 Enable database backups
 Set up monitoring/alerting
 Conduct security audit
 Penetration testing
Production
 Regular security updates
 Monitor auth logs for anomalies
 Rotate secrets periodically
 Backup database daily
 Review access logs
 Update dependencies
 Security patch management
Incident Response
1. Suspected Breach
Python

# Immediately revoke all sessions
def revoke_all_sessions(user_id):
    db.query(Session).filter(Session.user_id == user_id).delete()
    
# Force password reset
def force_password_reset(user_id):
    user = db.query(User).filter(User.id == user_id).first()
    user.password_reset_required = True
    db.commit()
    
# Notify user
send_security_alert(user.email, "Suspicious activity detected")
2. Logging & Monitoring
Python

import logging

logger = logging.getLogger(__name__)

# Log all authentication attempts
logger.info(f"Auth attempt: user={user_id}, similarity={similarity}, decision={decision}")

# Alert on suspicious patterns
if failed_attempts > 5:
    logger.warning(f"Multiple failed auth attempts for user {user_id}")
    send_alert_to_admin()
Compliance
GDPR
User consent for voice data
Right to deletion
Data portability
Privacy policy
PCI DSS (if handling payments)
Secure payment gateway
No card data storage
Tokenization
Contact
For security concerns, contact: security@yourdomain.com

Responsible Disclosure: Report vulnerabilities privately before public disclosure.