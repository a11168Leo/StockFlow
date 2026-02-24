const ACCESS_TOKEN_KEY = "stockflow_access_token";
const REFRESH_TOKEN_KEY = "stockflow_refresh_token";

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
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function saveTokens(accessToken, refreshToken) {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
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
