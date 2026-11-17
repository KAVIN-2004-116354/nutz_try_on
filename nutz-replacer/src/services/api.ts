import { CloudStatus, TryonResult, GrokAnalysis } from '../types';

// In development, Vite proxies /api and /health to http://127.0.0.1:8000
const API_BASE = '';

/**
 * Checks the status of the remote FLUX-DEV-012 model on Nutz Railway Cloud.
 */
export async function getCloudStatus(): Promise<CloudStatus> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/cloud-status`, {
      headers: { 'Accept': 'application/json' },
    });
    if (!res.ok) {
      throw new Error(`Cloud status returned HTTP ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.warn('[Nutz Replacer API] Could not retrieve cloud status:', err);
    return {
      status: 'offline',
      model: 'FLUX-DEV-012',
      provider: 'Nutz Railway Cloud',
      has_key: false,
    };
  }
}

/**
 * Checks overall gateway health.
 */
export async function getGatewayHealth(): Promise<{ status: string; cloud_flux: string; cloud_flux_ready: boolean }> {
  try {
    const res = await fetch(`${API_BASE}/health`, {
      headers: { 'Accept': 'application/json' },
    });
    if (!res.ok) throw new Error(`Health check failed: HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      status: 'unreachable',
      cloud_flux: 'offline',
      cloud_flux_ready: false,
    };
  }
}

export interface GenerateTryonParams {
  personImage: File | string;
  garmentImage: File | string;
  garmentName?: string;
  customPrompt?: string;
  domain?: 'indian_ethnic' | 'western';
  category?: string;
}

/**
 * Executes Try-On exclusively via FLUX-DEV-012 Cloud Model.
 * Does NOT invoke or fall back to any other diffusion or face swap model.
 */
export async function executeFluxTryon(params: GenerateTryonParams): Promise<TryonResult> {
  const formData = new FormData();

  // 1. Person Image (Source of Truth)
  if (params.personImage instanceof File) {
    formData.append('person_image', params.personImage, params.personImage.name);
  } else if (typeof params.personImage === 'string' && params.personImage.startsWith('data:')) {
    // Base64 data URI to Blob
    const res = await fetch(params.personImage);
    const blob = await res.blob();
    formData.append('person_image', blob, 'person.png');
  } else if (typeof params.personImage === 'string') {
    // Path or URL
    const res = await fetch(params.personImage);
    const blob = await res.blob();
    formData.append('person_image', blob, 'person.jpg');
  } else {
    throw new Error('A valid person image is required as the source of truth.');
  }

  // 2. Garment Image (Clothing Reference Only)
  if (params.garmentImage instanceof File) {
    formData.append('garment_image', params.garmentImage, params.garmentImage.name);
  } else if (typeof params.garmentImage === 'string' && params.garmentImage.startsWith('data:')) {
    const res = await fetch(params.garmentImage);
    const blob = await res.blob();
    formData.append('garment_image', blob, 'garment.png');
  } else if (typeof params.garmentImage === 'string') {
    const res = await fetch(params.garmentImage);
    const blob = await res.blob();
    formData.append('garment_image', blob, 'garment.jpg');
  } else {
    throw new Error('A valid garment reference image is required.');
  }

  // 3. Engine & Parameters - Strictly FLUX-DEV-012
  formData.append('engine', 'flux');
  formData.append('domain', params.domain || 'indian_ethnic');
  if (params.category) {
    formData.append('category', params.category);
  }

  // 4. Optional Custom Styling Instruction
  const promptText = params.customPrompt?.trim();
  if (promptText) {
    formData.append('prompt', promptText);
  }
  if (params.garmentName) {
    formData.append('garment_desc', params.garmentName);
  }

  // Submit to the dedicated /api/v1/flux-tryon endpoint (or /api/v1/try-on)
  const response = await fetch(`${API_BASE}/api/v1/flux-tryon`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorDetail = `Gateway returned HTTP ${response.status}`;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errorDetail;
    } catch (_) {
      const rawText = await response.text().catch(() => '');
      if (rawText) errorDetail = rawText.slice(0, 200);
    }
    throw new Error(errorDetail);
  }

  const data = await response.json();
  if (data.status !== 'success') {
    throw new Error(data.message || 'Generation failed on FLUX-DEV-012 server');
  }

  return data as TryonResult;
}

/**
 * Executes Instant Try-On locally via CatVTON GPU Engine (1.5s - 2.5s).
 * Directly warps and clones the exact garment fabric, patterns, and motifs onto the person.
 */
export async function executeFastTryon(params: {
  personImage: File | string;
  garmentImage: File | string;
  category?: string;
  domain?: 'indian_ethnic' | 'western';
}): Promise<TryonResult> {
  const formData = new FormData();

  if (params.personImage instanceof File) {
    formData.append('person_image', params.personImage, params.personImage.name);
  } else if (typeof params.personImage === 'string' && params.personImage.startsWith('data:')) {
    const res = await fetch(params.personImage);
    const blob = await res.blob();
    formData.append('person_image', blob, 'person.png');
  } else if (typeof params.personImage === 'string') {
    const res = await fetch(params.personImage);
    const blob = await res.blob();
    formData.append('person_image', blob, 'person.jpg');
  } else {
    throw new Error('A valid person image is required.');
  }

  if (params.garmentImage instanceof File) {
    formData.append('garment_image', params.garmentImage, params.garmentImage.name);
  } else if (typeof params.garmentImage === 'string' && params.garmentImage.startsWith('data:')) {
    const res = await fetch(params.garmentImage);
    const blob = await res.blob();
    formData.append('garment_image', blob, 'garment.png');
  } else if (typeof params.garmentImage === 'string') {
    const res = await fetch(params.garmentImage);
    const blob = await res.blob();
    formData.append('garment_image', blob, 'garment.jpg');
  } else {
    throw new Error('A valid garment image is required.');
  }

  formData.append('engine', 'catvton');
  formData.append('domain', params.domain || 'western');
  if (params.category) formData.append('category', params.category);

  const response = await fetch(`${API_BASE}/api/v1/try-on`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorDetail = `Gateway returned HTTP ${response.status}`;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errorDetail;
    } catch (_) {
      const rawText = await response.text().catch(() => '');
      if (rawText) errorDetail = rawText.slice(0, 200);
    }
    throw new Error(errorDetail);
  }

  const data = await response.json();
  if (data.status !== 'success') {
    throw new Error(data.message || 'Fast Try-On failed');
  }

  return {
    ...data,
    model_used: 'CatVTON LoRA GPU (Instant 1.5s)',
    provider: 'Local NVIDIA RTX 5050 GPU',
  } as TryonResult;
}

/**
 * Analyzes garment with Grok Vision API.
 */
export async function analyzeGarment(
  garmentImage: File | string,
  personImage?: File | string
): Promise<GrokAnalysis> {
  const formData = new FormData();
  if (garmentImage instanceof File) {
    formData.append('garment_image', garmentImage, garmentImage.name);
  } else if (typeof garmentImage === 'string' && garmentImage.startsWith('data:')) {
    const res = await fetch(garmentImage);
    const blob = await res.blob();
    formData.append('garment_image', blob, 'garment.png');
  } else if (typeof garmentImage === 'string') {
    const res = await fetch(garmentImage);
    const blob = await res.blob();
    formData.append('garment_image', blob, 'garment.jpg');
  }

  if (personImage) {
    if (personImage instanceof File) {
      formData.append('person_image', personImage, personImage.name);
    } else if (typeof personImage === 'string' && personImage.startsWith('data:')) {
      const res = await fetch(personImage);
      const blob = await res.blob();
      formData.append('person_image', blob, 'person.png');
    } else if (typeof personImage === 'string') {
      const res = await fetch(personImage);
      const blob = await res.blob();
      formData.append('person_image', blob, 'person.jpg');
    }
  }

  const response = await fetch(`${API_BASE}/api/v1/analyze-garment`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Garment analysis failed: HTTP ${response.status}`);
  }

  const data = await response.json();
  return data.analysis as GrokAnalysis;
}

/**
 * Executes Intelligent AI Virtual Try-On:
 * 1. Grok Vision Multimodal Analysis
 * 2. MediaPipe Landmark-Guided Segmentation Mask & Protection
 * 3. FLUX-DEV-012 Cloud Inpainting
 */
export async function executeIntelligentTryon(params: {
  personImage: File | string;
  garmentImage?: File | string | null;
  prompt?: string;
  category?: string;
  mode?: 'pure_flux' | 'grok_flux' | 'auto';
  seed?: number;
}): Promise<TryonResult> {
  const formData = new FormData();

  if (params.personImage instanceof File) {
    formData.append('person_image', params.personImage, params.personImage.name);
  } else if (typeof params.personImage === 'string' && params.personImage.startsWith('data:')) {
    const res = await fetch(params.personImage);
    const blob = await res.blob();
    formData.append('person_image', blob, 'person.png');
  } else if (typeof params.personImage === 'string') {
    const res = await fetch(params.personImage);
    const blob = await res.blob();
    formData.append('person_image', blob, 'person.jpg');
  } else {
    throw new Error('A valid person image is required.');
  }

  if (params.garmentImage instanceof File) {
    formData.append('garment_image', params.garmentImage, params.garmentImage.name);
  } else if (typeof params.garmentImage === 'string' && params.garmentImage.startsWith('data:')) {
    const res = await fetch(params.garmentImage);
    const blob = await res.blob();
    formData.append('garment_image', blob, 'garment.png');
  } else if (typeof params.garmentImage === 'string') {
    const res = await fetch(params.garmentImage);
    const blob = await res.blob();
    formData.append('garment_image', blob, 'garment.jpg');
  }

  if (params.prompt) {
    formData.append('prompt', params.prompt);
    formData.append('custom_prompt', params.prompt);
  }

  if (params.mode) {
    formData.append('mode', params.mode);
  }

  if (params.category) {
    formData.append('category', params.category);
  }

  if (params.seed) {
    formData.append('seed', params.seed.toString());
  }

  const response = await fetch(`${API_BASE}/api/v1/intelligent-tryon`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorDetail = `Gateway returned HTTP ${response.status}`;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errorDetail;
    } catch (_) {
      const rawText = await response.text().catch(() => '');
      if (rawText) errorDetail = rawText.slice(0, 200);
    }
    throw new Error(errorDetail);
  }

  const data = await response.json();
  if (data.status !== 'success') {
    throw new Error(data.message || 'Intelligent Try-On failed');
  }

  return data as TryonResult;
}
