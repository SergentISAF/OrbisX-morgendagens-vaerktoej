/**
 * Simpel auth-hjælper: gemmer token + tenant-info i localStorage.
 * Bruges af alle authed sider/komponenter.
 */

export type AuthState = {
  token: string;
  user_id: number;
  tenant_id: number;
  email: string;
  tenant_name: string;
};

const KEY = "orbisx_auth";

export function getAuth(): AuthState | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthState;
  } catch {
    return null;
  }
}

export function setAuth(a: AuthState): void {
  localStorage.setItem(KEY, JSON.stringify(a));
}

export function clearAuth(): void {
  localStorage.removeItem(KEY);
}

export function authHeaders(): Record<string, string> {
  const a = getAuth();
  return a ? { Authorization: `Bearer ${a.token}` } : {};
}

export const API_URL = import.meta.env.PUBLIC_API_URL ?? "http://localhost:8000";
