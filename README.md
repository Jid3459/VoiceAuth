# 🎤 Voice Authentication & Product Ordering System

Intelligent backend assistant integrated with secure voice authentication using **SpeechBrain ECAPA-TDNN** for speaker verification.

## 🚀 Features

- **Voice Biometric Authentication** using SpeechBrain ECAPA-TDNN
- **5-Layer Trust Scoring System**
- **Amount-Based Authorization** (INR ₹)
- **Real-time Imposter Detection**
- **Product Query Analysis**
- **Comprehensive Audit Logging**

## 🛠️ Tech Stack

### Backend
- Python 3.10+
- FastAPI
- SQLAlchemy
- PostgreSQL
- SpeechBrain
- PyTorch

### Frontend
- React 18
- TypeScript
- Vite
- CSS3

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Microphone access

## ⚡ Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure .env file
cp .env.example .env
# Edit .env with your database credentials

# Run server
uvicorn app.main:app --reload --port 8000


Frontend Setup
Bash

cd frontend
npm install
npm run dev
Access
Frontend: http://localhost:5173
Backend: http://localhost:8000
API Docs: http://localhost:8000/docs
📊 System Rules
Similarity Thresholds
≥ 0.75 → Strong Match (Genuine User)
0.50 - 0.75 → Uncertain/Suspicious
< 0.50 → Different Speaker (Imposter)
Authorization Rules
< ₹500 → Auto-approve
₹500 - ₹2,000 → Requires trust score ≥ 50
₹2,000 - ₹10,000 → Requires trust score ≥ 70
> ₹10,000 → Requires trust score ≥ 85
CRITICAL: If similarity < 0.50, DENY regardless (except < ₹500)

📖 Documentation
See /docs folder for detailed documentation:

API Reference
Architecture Overview
Security Guidelines
Setup Guide
🔒 Security
Voice embeddings stored securely in database
Password hashing with bcrypt
CORS protection
Session integrity checks
Comprehensive audit logging
📝 License
MIT License

👥 Contributors
Your Name - Voice Auth System

Built with ❤️ using FastAPI, React, and SpeechBrain