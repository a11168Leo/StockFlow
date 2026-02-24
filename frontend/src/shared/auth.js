const ACCESS_TOKEN_KEY = "stockflow_access_token";
const REFRESH_TOKEN_KEY = "stockflow_refresh_token";
const STORAGE_MODE_KEY = "stockflow_storage_mode";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function decodeBase64Url(value) {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized + "=".repeat((4 - (normalized.length % 4)) % 4);
  return atob(padded);
}

export function decodeJwtPayload(token) {
  if (!token || typeof token !== "string") {
    return null;
  }

  const parts = token.split(".");
  if (parts.length !== 3) {
    return null;
  }

  try {
    const payloadJson = decodeBase64Url(parts[1]);
    return JSON.parse(payloadJson);
  } catch {
    return null;
  }
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY) || sessionStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY) || sessionStorage.getItem(REFRESH_TOKEN_KEY);
}

export function saveTokens(accessToken, refreshToken, remember = true) {
  if (remember) {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    localStorage.setItem(STORAGE_MODE_KEY, "local");
    sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(REFRESH_TOKEN_KEY);
    return;
  }

  sessionStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  sessionStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  localStorage.setItem(STORAGE_MODE_KEY, "session");
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function getRememberMode() {
  return localStorage.getItem(STORAGE_MODE_KEY) !== "session";
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(STORAGE_MODE_KEY);
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  sessionStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function getCurrentProfile() {
  const payload = decodeJwtPayload(getAccessToken());
  return payload?.perfil || null;
}

export function ensureRoleSession(allowedProfiles) {
  const token = getAccessToken();
  const payload = decodeJwtPayload(token);

  if (!token || !payload?.perfil) {
    window.location.replace("/login/");
    return null;
  }

  const role = payload.perfil;
  if (!allowedProfiles.includes(role)) {
    window.location.replace("/login/");
    return null;
  }

  return {
    role,
    userId: payload.sub,
  };
}

export function logout() {
  clearTokens();
  window.location.replace("/login/");
}

export async function fetchCurrentUser() {
  const token = getAccessToken();
  if (!token) {
    throw new Error("Sem token de autenticacao.");
  }

  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Falha ao carregar perfil.");
  }

  return data;
}
