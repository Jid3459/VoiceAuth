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