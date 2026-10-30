const API_URL = process.env.EXPO_PUBLIC_API_URL?.replace(/\/$/, '') || 'http://127.0.0.1:8000';

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function api<T>(path: string, options: RequestInit = {}, token?: string | null): Promise<T> {
  const headers: Record<string, string> = {'Content-Type': 'application/json'};
  Object.assign(headers, (options.headers || {}) as Record<string, string>);
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${API_URL}${path}`, {...options, headers});
  const payload = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(payload.detail || `Request failed (${res.status})`, res.status);
  return payload as T;
}

export const todayISO = () => new Date().toISOString().slice(0, 10);
