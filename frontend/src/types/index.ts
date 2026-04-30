export interface User {
  id: number;
  username: string;
  email: string;
  is_voice_enrolled: boolean;
  is_admin: boolean;
  is_superuser: boolean;
  created_at: string;
  last_login?: string;
}

export interface TrustScores {
  voice_biometrics: number;
  speech_consistency: number;
  behavioral_pattern: number;
  device_integrity: number;
  contextual_anomaly: number;
}

export interface OrderResponse {
  is_product_query: boolean;
  search_query: string | null;
  product: string | null;
  budget_inr: number | null;
  speechbrain_similarity: number;
  trust_scores: TrustScores;
  overall_trust_score: number;
  amount_inr: number | null;
  decision: "ALLOW" | "DENY";
  reason: string;
}

export interface AuthLog {
  id: number;
  speechbrain_similarity: number;
  trust_scores: TrustScores;
  overall_trust_score: number;
  action_attempted: string;
  decision: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  message: string;
}

// Admin Types (moved here to avoid import issues)
export interface SystemSettings {
  id: number;
  similarity_threshold_strong: number;
  similarity_threshold_weak: number;
  amount_threshold_low: number;
  amount_threshold_medium: number;
  amount_threshold_high: number;
  trust_score_low: number;
  trust_score_medium: number;
  trust_score_high: number;
  weight_voice_biometrics: number;
  weight_speech_consistency: number;
  weight_behavioral_pattern: number;
  weight_device_integrity: number;
  weight_contextual_anomaly: number;
  log_level: string;
  enable_debug: boolean;
  log_to_file: boolean;
  log_to_console: boolean;
  updated_at: string;
}

export interface SystemStats {
  total_users: number;
  enrolled_users: number;
  total_orders: number;
  approved_orders: number;
  denied_orders: number;
  total_auth_logs: number;
  approval_rate: number;
}