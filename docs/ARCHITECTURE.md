
### `docs/ARCHITECTURE.md`

```markdown
# System Architecture

## Overview

The Voice Authentication & Product Ordering System is a full-stack application that uses biometric voice authentication powered by SpeechBrain's ECAPA-TDNN model to secure product ordering transactions.

---

## High-Level Architecture
┌─────────────┐ ┌─────────────┐ ┌──────────────┐
│ Browser │ HTTPS │ FastAPI │ SQL │ PostgreSQL │
│ (React + │ ◄──────► │ Backend │ ◄──────► │ Database │
│ TypeScript) │ │ (Python) │ │ │
└─────────────┘ └─────────────┘ └──────────────┘
│ │
│ │
▼ ▼
Microphone SpeechBrain ECAPA-TDNN
(Voice Input) (Voice Embeddings)

text


---

## Backend Architecture

### Layer Structure
app/
├── main.py # FastAPI application entry
├── config.py # Configuration management
├── database.py # Database connection
├── models.py # SQLAlchemy ORM models
├── schemas.py # Pydantic schemas
├── routes/ # API endpoints
│ ├── auth.py # Authentication routes
│ └── orders.py # Order processing routes
└── services/ # Business logic
├── voice_auth.py # SpeechBrain integration
├── trust_scorer.py # 5-layer trust scoring
├── product_analyzer.py # Product query analysis
└── authorization.py # Transaction authorization

text


### Core Components

#### 1. Voice Authentication Service
- **Model**: SpeechBrain ECAPA-TDNN (192-dimensional embeddings)
- **Function**: Extract and compare voice embeddings
- **Similarity Metric**: Cosine similarity
- **Thresholds**:
  - Strong match: ≥ 0.75
  - Uncertain: 0.50 - 0.75
  - No match: < 0.50

#### 2. Trust Scorer Service
**5-Layer Scoring System:**

| Layer | Weight | Description |
|-------|--------|-------------|
| Voice Biometrics | 40% | Based on SpeechBrain similarity |
| Speech Consistency | 20% | Historical voice pattern matching |
| Behavioral Pattern | 15% | User ordering behavior analysis |
| Device Integrity | 15% | Device/IP consistency check |
| Contextual Anomaly | 10% | Time, frequency, context analysis |

**Formula:**
Overall Trust = (VB × 0.40) + (SC × 0.20) + (BP × 0.15) + (DI × 0.15) + (CA × 0.10)

text


#### 3. Product Analyzer Service
- Detects product-related queries
- Extracts product name and budget
- Retrieves pricing from database
- Generates search queries

#### 4. Authorization Service
**Amount-Based Rules:**

```python
if similarity < 0.50 and amount >= 500:
    return DENY

if amount < 500:
    return ALLOW

if 500 <= amount < 2000:
    return ALLOW if trust >= 50 else DENY

if 2000 <= amount < 10000:
    return ALLOW if trust >= 70 else DENY

if amount >= 10000:
    return ALLOW if trust >= 85 else DENY
Frontend Architecture
Component Hierarchy
text

App
├── VoiceEnrollment
│   └── VoiceRecorder
├── OrderForm
│   ├── VoiceRecorder
│   └── TrustScoreDisplay
├── OrderHistory
└── AuthLogs
Key Components
1. VoiceRecorder
Uses MediaRecorder API
Captures audio from microphone
Returns Blob for upload
2. TrustScoreDisplay
Visualizes 5-layer trust scores
Shows similarity percentage
Color-coded indicators
3. OrderForm
Product query input
Voice recording
Real-time decision display
Data Flow
Voice Enrollment Flow
text

1. User clicks "Start Recording"
2. Browser requests microphone access
3. User speaks for 5-10 seconds
4. Audio captured as Blob
5. Sent to /auth/enroll-voice/{user_id}
6. Backend extracts embedding (SpeechBrain)
7. Embedding stored in database
8. Confirmation returned to frontend
Order Processing Flow
text

1. User enters product query
2. User records voice authentication
3. Audio + query sent to /orders/process
4. Backend performs:
   a. Voice authentication (similarity calculation)
   b. Trust scoring (5 layers)
   c. Product analysis
   d. Authorization decision
5. Response with decision + trust scores
6. Frontend displays results
7. Transaction logged in database
Database Schema
Users Table
SQL

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    voice_embedding TEXT,
    is_voice_enrolled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
Orders Table
SQL

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_name VARCHAR NOT NULL,
    amount_inr FLOAT NOT NULL,
    search_query VARCHAR,
    budget_inr FLOAT,
    speechbrain_similarity FLOAT,
    overall_trust_score FLOAT,
    trust_scores JSON,
    decision VARCHAR,
    decision_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
Auth Logs Table
SQL

CREATE TABLE auth_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    speechbrain_similarity FLOAT,
    trust_scores JSON,
    overall_trust_score FLOAT,
    action_attempted VARCHAR,
    decision VARCHAR,
    ip_address VARCHAR,
    user_agent VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
Security Architecture
1. Voice Biometric Security
Embeddings stored as comma-separated strings
Never store raw audio
Similarity threshold prevents imposter access
2. Password Security
Bcrypt hashing
Salted passwords
Minimum strength requirements (implement in production)
3. API Security
CORS protection
Rate limiting (to be implemented)
Input validation via Pydantic
4. Session Security
JWT tokens (to be implemented for auth)
Device fingerprinting
IP tracking
Performance Considerations
Backend
SpeechBrain Model: Loaded once at startup (singleton pattern)
Database: Connection pooling via SQLAlchemy
Async: FastAPI async support for I/O operations
Frontend
Code Splitting: Vite lazy loading
State Management: React hooks
Caching: Browser cache for static assets
Scalability
Horizontal Scaling
Stateless API design
Database connection pooling
Load balancer compatible
Vertical Scaling
GPU support for SpeechBrain (optional)
Increase worker processes
Database optimization
Monitoring & Logging
Backend Logging
Python

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
Metrics to Track
Authentication success/failure rate
Average similarity scores
Response times
Trust score distributions
Future Enhancements
Multi-factor Authentication: Combine voice + password + OTP
Continuous Authentication: Monitor voice throughout session
Anti-spoofing: Detect synthetic/replayed audio
Real-time Processing: WebSocket for live voice streaming
Mobile Support: React Native app
Analytics Dashboard: Admin panel for monitoring
Technology Stack
Backend
Framework: FastAPI 0.104+
ORM: SQLAlchemy 2.0+
Database: PostgreSQL 14+
Voice AI: SpeechBrain 0.5+
ML Framework: PyTorch 2.1+
Frontend
Library: React 18
Language: TypeScript 5
Build Tool: Vite 5
HTTP Client: Axios 1.6+
Infrastructure
Web Server: Uvicorn (ASGI)
Reverse Proxy: Nginx (production)
Process Manager: Gunicorn (production)