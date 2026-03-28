// ── Auth ────────────────────────────────────────────────────────────────────
export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'operator' | 'viewer';
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// ── Inspections ──────────────────────────────────────────────────────────────
export interface BoundingBox {
  x: number;
  y: number;
  w: number;
  h: number;
  label: string;
  confidence: number;
}

/** Matches backend InspectionRead schema */
export interface Inspection {
  inspection_id: string;
  image_id: string;
  camera_id: string;
  product_id: string | null;
  is_defective: boolean;
  defect_score: number;
  anomaly_score: number;
  classification_label: string | null;
  bounding_boxes: BoundingBox[];
  processing_time_ms: number;
  model_version: string | null;
  inspected_at: string;
}

/** Matches backend InspectionList schema */
export interface InspectionList {
  items: Inspection[];
  total: number;
  page: number;
  page_size: number;
}

// ── Analytics ────────────────────────────────────────────────────────────────
/** Matches backend DefectRatePoint schema */
export interface DefectRate {
  period: string;
  total: number;
  defects: number;
  defect_rate_pct: number | null;
}

export interface ModelPerformance {
  model_name?: string;
  version?: string;
  accuracy?: number;
  f1_score?: number;
  avg_latency_ms?: number;
  [key: string]: unknown;
}

// ── Models ───────────────────────────────────────────────────────────────────
export interface ModelVersion {
  name: string;
  version: string;
  stage: 'staging' | 'production' | 'archived';
  created_at: string;
  metrics?: Record<string, number>;
}

// ── WebSocket live feed ──────────────────────────────────────────────────────
/** Matches WebSocket /ws/live-feed payload from backend */
export interface LiveFeedEvent {
  image_id: string;
  inspection_id: string;
  defect_detected: boolean;
  defect_type: string | null;
  confidence: number;
  anomaly_score: number;
  timestamp: number; // milliseconds epoch
}
