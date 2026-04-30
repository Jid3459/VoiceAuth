# API Documentation

## Base URL
http://localhost:8000

text


## Authentication Endpoints

### 1. Register User
**POST** `/auth/register`

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
Response:

JSON

{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "is_voice_enrolled": false,
  "created_at": "2024-01-15T10:30:00"
}
2. Enroll Voice
POST /auth/enroll-voice/{user_id}

Form Data:

audio: Audio file (WAV format recommended)
Response:

JSON

{
  "message": "Voice enrolled successfully",
  "user_id": 1,
  "embedding_dimension": 192
}
3. Verify Voice
POST /auth/verify-voice/{user_id}

Form Data:

audio: Audio file
Response:

JSON

{
  "similarity": 0.87,
  "status": "STRONG_MATCH",
  "message": "Voice verified - strong match"
}
Status Values:

STRONG_MATCH: similarity ≥ 0.75
UNCERTAIN: 0.50 ≤ similarity < 0.75
NO_MATCH: similarity < 0.50
4. Get User
GET /auth/users/{user_id}

Response:

JSON

{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "is_voice_enrolled": true,
  "created_at": "2024-01-15T10:30:00"
}
Order Endpoints
5. Process Order
POST /orders/process

Form Data:

user_id: integer
query: string (e.g., "Buy iPhone 13")
audio: Audio file for voice authentication
Response:

JSON

{
  "is_product_query": true,
  "search_query": "Iphone 13 Price",
  "product": "Iphone 13",
  "budget_inr": null,
  "speechbrain_similarity": 0.87,
  "trust_scores": {
    "voice_biometrics": 85,
    "speech_consistency": 78,
    "behavioral_pattern": 82,
    "device_integrity": 88,
    "contextual_anomaly": 90
  },
  "overall_trust_score": 84,
  "amount_inr": 59900,
  "decision": "ALLOW",
  "reason": "Amount ₹59900.00 approved with trust score 84/100."
}
6. Get Order History
GET /orders/history/{user_id}

Response:

JSON

[
  {
    "id": 1,
    "product_name": "iPhone 13",
    "amount_inr": 59900,
    "search_query": "iPhone 13 price",
    "budget_inr": null,
    "speechbrain_similarity": 0.87,
    "overall_trust_score": 84,
    "trust_scores": {...},
    "decision": "ALLOW",
    "decision_reason": "...",
    "created_at": "2024-01-15T11:45:00"
  }
]
7. Get Auth Logs
GET /orders/auth-logs/{user_id}?limit=20

Query Parameters:

limit: Number of logs to retrieve (default: 20)
Response:

JSON

[
  {
    "id": 1,
    "speechbrain_similarity": 0.87,
    "trust_scores": {...},
    "overall_trust_score": 84,
    "action_attempted": "Buy iPhone 13",
    "decision": "ALLOW",
    "created_at": "2024-01-15T11:45:00"
  }
]
Status Codes
200: Success
400: Bad Request
404: Not Found
422: Validation Error
500: Internal Server Error
Authorization Rules
Amount-Based Thresholds
Amount Range	Trust Score Required	Notes
< ₹500	None (Auto-approve)	Always allowed
₹500 - ₹2,000	≥ 50	Low-risk transactions
₹2,000 - ₹10,000	≥ 70	Medium-risk transactions
> ₹10,000	≥ 85	High-risk transactions
Critical Override
If speechbrain_similarity < 0.50, transaction is DENIED regardless of amount (except < ₹500).

Error Responses
JSON

{
  "detail": "Error message description"
}
Rate Limiting
Not implemented in current version. Consider adding in production.

