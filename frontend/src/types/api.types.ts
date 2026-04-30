/**
 * API Request/Response Types
 */

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  user_id: number;
}

export interface VoiceEnrollRequest {
  user_id: number;
  audio: Blob;
}

export interface VoiceVerifyRequest {
  user_id: number;
  audio: Blob;
}

export interface VoiceVerifyResponse {
  similarity: number;
  status: 'STRONG_MATCH' | 'UNCERTAIN' | 'NO_MATCH';
  message: string;
}

export interface ProcessOrderRequest {
  user_id: number;
  query: string;
  audio: Blob;
}

export interface OrderHistoryItem {
  id: number;
  product_name: string;
  amount_inr: number;
  search_query: string;
  budget_inr: number | null;
  speechbrain_similarity: number;
  overall_trust_score: number;
  trust_scores: {
    voice_biometrics: number;
    speech_consistency: number;
    behavioral_pattern: number;
    device_integrity: number;
    contextual_anomaly: number;
  };
  decision: string;
  decision_reason: string;
  created_at: string;
}

export interface ApiError {
  detail: string;
}

export interface HealthCheckResponse {
  status: string;
}

export interface EnrollmentResponse {
  message: string;
  user_id: number;
  embedding_dimension: number;
}