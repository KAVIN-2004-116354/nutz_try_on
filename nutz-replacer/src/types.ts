export type GenerationStatus = 'ready' | 'uploading' | 'processing' | 'completed' | 'failed';

export interface GarmentAnalysis {
  category: 'upper_body' | 'lower_body' | 'full_body' | 'complex_ethnic';
  garment_type: string;
  primary_color: string;
  secondary_color: string;
  fabric: string;
  pattern: string;
  sleeves: string;
  collar: string;
  construction_details: string[];
  layering: boolean;
  confidence: number;
}

export interface PersonAnalysis {
  pose: string;
  visible_body_regions: string[];
  existing_clothing: string[];
  background: string;
}

export interface ReplacementPlan {
  target_regions: string[];
  protected_regions: string[];
  requires_manual_review: boolean;
}

export interface GrokAnalysis {
  garment_analysis: GarmentAnalysis;
  person_analysis: PersonAnalysis;
  replacement_plan: ReplacementPlan;
  generation_prompt: string;
  engine?: string;
}

export interface MaskMetrics {
  total_pixels: number;
  replacement_pixels: number;
  coverage_percentage: number;
  protected_integrity: number;
  quality_score: number;
}

export interface ImageInputState {
  file: File | null;
  previewUrl: string | null;
  name: string;
  isCustom: boolean;
  aspectRatio?: string;
  resolution?: string;
}

export interface TryonResult {
  status: 'success' | 'error';
  mode?: string;
  engine?: string;
  model_used: string;
  provider?: string;
  domain?: string;
  used_weights?: string;
  selected_lora?: string;
  latency_seconds: number;
  inference_time_ms: number;
  output_image?: string;
  result_url: string;
  image_data?: string;
  mask_url?: string;
  overlay_url?: string;
  mask_data?: string;
  overlay_data?: string;
  grok_analysis?: GrokAnalysis;
  mask_metrics?: MaskMetrics;
  width?: number;
  height?: number;
  file_size_bytes?: number;
}

export interface CloudStatus {
  status: 'online' | 'offline';
  model: string;
  provider: string;
  has_key: boolean;
}

export interface HistoryItem {
  id: string;
  timestamp: string;
  personThumb: string;
  garmentThumb: string;
  resultUrl: string;
  maskUrl?: string;
  overlayUrl?: string;
  personName: string;
  garmentName: string;
  category?: string;
  model: string;
  latencySec: number;
  width: number;
  height: number;
  fileSizeStr: string;
  status: 'completed' | 'failed';
}

export interface SamplePreset {
  id: string;
  name: string;
  category: string;
  gender: 'men' | 'women';
  imageUrl: string;
  promptHint?: string;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  full_name: string;
  phone?: string | null;
  role: 'admin' | 'client' | 'user' | string;
  is_active: boolean;
  email_verified: boolean;
  created_at?: string;
  last_login?: string | null;
}

export interface AuthResponse {
  access_token: string;
  token: string;
  token_type: string;
  user: UserProfile;
}

export interface ServerTryonHistoryItem {
  id: string;
  user_id: string;
  client_id?: string | null;
  garment_category?: string | null;
  input_image_reference?: string | null;
  output_image_reference?: string | null;
  generation_status: string;
  created_at: string;
}
