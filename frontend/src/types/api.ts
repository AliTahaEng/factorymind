export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'operator' | 'viewer';
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface Defect {
  type: string;
  confidence: number;
  bbox?: [number, number, number, number];
}

export interface Inspection {
  id: string;
  camera_id: string;
  timestamp: string;
  defect_probability: number;
  has_defect: boolean;
  defects: Defect[];
  model_version: string;
  processing_time_ms: number;
  image_url?: string;
}

export interface InspectionList {
  items: Inspection[];
  total: number;
  page: number;
  size: number;
}

export interface DefectRate {
  date: string;
  defect_rate: number;
  total_count: number;
  defect_count: number;
}

export interface ModelPerformance {
  model_name: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  avg_latency_ms: number;
  total_inferences: number;
}

export interface ModelVersion {
  name: string;
  version: string;
  stage: 'staging' | 'production' | 'archived';
  created_at: string;
  metrics?: Record<string, number>;
}

export interface LiveFeedEvent {
  inspection_id: string;
  camera_id: string;
  defect_probability: number;
  has_defect: boolean;
  defects: Defect[];
  timestamp: string;
}
