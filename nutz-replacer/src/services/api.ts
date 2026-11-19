import { CloudStatus, TryonResult, GrokAnalysis, UserProfile, AuthResponse, ServerTryonHistoryItem } from '../types';

// In development, Vite proxies /api and /health to http://127.0.0.1:8000
const API_BASE = '';

/**
 * Authentication Token Management
 */
export function getAuthToken(): string | null {
  try {
    return localStorage.getItem('nutz_token');
  } catch {
    return null;
  }
}

export function setAuthToken(token: string): void {
  try {
    localStorage.setItem('nutz_token', token);
  } catch {}
}

export function clearAuthToken(): void {
  try {
    localStorage.removeItem('nutz_token');
    localStorage.removeItem('nutz_user');
  } catch {}
}

export function getAuthHeaders(): Record<string, string> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Accept': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Registers a new user account with production Argon2id backend.
 */
export async function registerUser(params: {
  full_name: string;
  email: string;
  password: string;
  phone?: string;
}): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
    throw new Error(err.detail || 'Registration failed');
  }
  const data: AuthResponse = await res.json();
  if (data.token || data.access_token) {
    setAuthToken(data.token || data.access_token);
  }
  return data;
}

/**
 * Authenticates user and stores JWT token in localStorage.
 */
export async function loginUser(params: {
  email: string;
  password: string;
}): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Invalid credentials' }));
    throw new Error(err.detail || 'Invalid email or password');
  }
  const data: AuthResponse = await res.json();
  if (data.token || data.access_token) {
    setAuthToken(data.token || data.access_token);
  }
  return data;
}

/**
 * Securely terminates the session on the backend and clears localStorage.
 * Handles logout even if access token is already expired.
 */
export async function logoutUser(): Promise<void> {
  try {
    await fetch(`${API_BASE}/api/v1/auth/logout`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
  } catch (err) {
    console.warn('[Nutz Replacer API] Logout backend notification:', err);
  } finally {
    clearAuthToken();
  }
}

/**
 * Requests password reset instructions.
 */
export async function forgotPassword(email: string): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/api/v1/auth/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify({ email }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || 'Failed to request password reset instructions.');
  }
  return await res.json();
}

/**
 * Resets user password using single-use secret token.
 */
export async function resetPassword(token: string, new_password: string): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/api/v1/auth/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify({ token, new_password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Reset failed' }));
    throw new Error(err.detail || 'Password reset failed. The link may have expired or already been used.');
  }
  return await res.json();
}

/**
 * Verifies email address using token from verification email.
 */
export async function verifyEmail(token: string): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/api/v1/auth/verify-email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify({ token }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Verification failed' }));
    throw new Error(err.detail || 'Email verification failed or link has expired.');
  }
  return await res.json();
}

/**
 * Resends verification email to specified address.
 */
export async function resendVerification(email: string): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/api/v1/auth/resend-verification`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify({ email }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Resend failed' }));
    throw new Error(err.detail || 'Failed to resend verification email.');
  }
  return await res.json();
}

/**
 * Retrieves profile of currently authenticated user.
 */
export async function getCurrentUser(): Promise<UserProfile | null> {
  const token = getAuthToken();
  if (!token) return null;
  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      if (res.status === 401) {
        clearAuthToken();
      }
      return null;
    }
    const data = await res.json();
    return data.user as UserProfile;
  } catch {
    return null;
  }
}

/**
 * Fetches tryon history recorded in PostgreSQL for the active user.
 */
export async function fetchServerTryonHistory(): Promise<ServerTryonHistoryItem[]> {
  const token = getAuthToken();
  if (!token) return [];
  try {
    const res = await fetch(`${API_BASE}/api/v1/tryon/history`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

/**
 * Sanitizes and maps server error messages to user-friendly messages,
 * ensuring technical stack traces / quota errors always guide the user to contact admin.
 */
export function cleanErrorMessage(status: number, rawMessage: string): string {
  if (status === 429 || /quota|insufficient_quota|429/i.test(rawMessage)) {
    return 'Generation quota reached. Please contact admin.';
  }
  if (/contact admin/i.test(rawMessage)) {
    return rawMessage;
  }
  if (rawMessage.includes('{') || rawMessage.includes('inference error') || rawMessage.includes('Cloud image edit')) {
    return 'Service temporarily unavailable. Please contact admin.';
  }
  return rawMessage || 'Generation failed. Please contact admin.';
}

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

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 180000);

  try {
    const response = await fetch(`${API_BASE}/api/v1/flux-tryon`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorDetail = `Gateway returned HTTP ${response.status}`;
      try {
        const errJson = await response.json();
        errorDetail = errJson.detail || errorDetail;
      } catch (_) {
        const rawText = await response.text().catch(() => '');
        if (rawText) errorDetail = rawText.slice(0, 300);
      }
      throw new Error(cleanErrorMessage(response.status, errorDetail));
    }

    const data = await response.json();
    if (data.status !== 'success') {
      const msg = data.message || 'Generation failed on FLUX-DEV-012 server';
      throw new Error(cleanErrorMessage(response.status, msg));
    }

    return data as TryonResult;
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new Error('Generation request timed out after 180 seconds. The model server may be experiencing high load.');
    }
    if (err instanceof TypeError && err.message.includes('fetch')) {
      throw new Error('Cannot connect to the Try-On Gateway at http://localhost:8000. Please ensure the backend server is running.');
    }
    throw err;
  }
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

  // Network timeout controller (180s for diffusion models)
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 180000);

  try {
    const response = await fetch(`${API_BASE}/api/v1/intelligent-tryon`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorDetail = `Gateway returned HTTP ${response.status}`;
      try {
        const errJson = await response.json();
        errorDetail = errJson.detail || errJson.message || errorDetail;
      } catch (_) {
        const rawText = await response.text().catch(() => '');
        if (rawText) errorDetail = rawText.slice(0, 300);
      }
      throw new Error(cleanErrorMessage(response.status, errorDetail));
    }

    const data = await response.json();
    if (data.status !== 'success') {
      const msg = data.message || data.detail || 'Virtual try-on generation failed on server.';
      throw new Error(cleanErrorMessage(response.status, msg));
    }

    return data as TryonResult;
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new Error('Generation request timed out after 180 seconds. The model server may be experiencing high load.');
    }
    if (err instanceof TypeError && err.message.includes('fetch')) {
      throw new Error('Cannot connect to the Try-On Gateway at http://localhost:8000. Please ensure the backend server is running.');
    }
    throw err;
  }
}
