import "../styles/login.css";
import { getCurrentProfile, getRememberMode, saveTokens } from "../shared/auth";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const RAIN_MODE = (import.meta.env.VITE_RAIN_MODE || "mixed").toLowerCase();
const ICON_FILES = (
  import.meta.env.VITE_ICON_FILES ||
  "shopping-cart-01-svgrepo-com.svg,shopping-cart-round-1137-svgrepo-com.svg,delivery-truck.svg,inventory-box.svg,warehouse.svg,barcode.svg,business-bag-that-can-be-used-for-svgrepo-com.svg,business-suitcase-svgrepo-com.svg"
)
  .split(",")
  .map((item) => item.trim())
  .filter(Boolean);

const form = document.getElementById("login-form");
const message = document.getElementById("message");
const submitBtn = document.getElementById("submit-btn");
const rememberMeEl = document.getElementById("remember-me");
const forgotBtn = document.getElementById("forgot-password-btn");
const forgotDialog = document.getElementById("forgot-password-dialog");
const forgotForm = document.getElementById("forgot-password-form");
const forgotEmailEl = document.getElementById("forgot-email");
const forgotMessageEl = document.getElementById("forgot-message");
const forgotSubmitBtn = document.getElementById("forgot-submit-btn");
const forgotCloseBtn = document.getElementById("forgot-close-btn");
const passwordEl = document.getElementById("senha");
const togglePasswordBtn = document.getElementById("toggle-password");
const starfield = document.getElementById("starfield");

function createStaticStars() {
  if (!starfield) {
    return;
  }

  const starsCount = Math.min(120, Math.floor(window.innerWidth / 11));
  for (let index = 0; index < starsCount; index += 1) {
    const star = document.createElement("span");
    const isNear = Math.random() > 0.62;
    star.className = `star ${isNear ? "near" : "far"}`;
    const size = isNear ? Math.random() * 1.9 + 0.8 : Math.random() * 1.4 + 0.4;
    star.style.width = `${size}px`;
    star.style.height = `${size}px`;
    star.style.left = `${Math.random() * 100}%`;
    star.style.top = `${Math.random() * 100}%`;
    star.style.setProperty("--twinkle-duration", `${2.6 + Math.random() * 5.2}s`);
    star.style.animationDelay = `${Math.random() * 4}s`;
    starfield.appendChild(star);
  }
}

function spawnRainIcon() {
  if (!starfield || ICON_FILES.length === 0) {
    return;
  }

  const icon = document.createElement("img");
  icon.className = "rain-icon";
  const iconFile = ICON_FILES[Math.floor(Math.random() * ICON_FILES.length)];
  const size = Math.random() * 24 + 16;

  icon.src = `/icons/${iconFile}`;
  icon.alt = "";
  icon.loading = "lazy";
  icon.style.left = `${Math.random() * 100}%`;
  icon.style.top = `${-50 - Math.random() * 80}px`;
  icon.style.width = `${size}px`;
  icon.style.height = `${size}px`;
  icon.style.opacity = `${0.34 + Math.random() * 0.36}`;
  icon.style.setProperty("--icon-duration", `${6.5 + Math.random() * 6.5}s`);
  icon.style.setProperty("--icon-drift", `${-55 + Math.random() * 110}px`);
  icon.style.setProperty("--icon-rotate", `${80 + Math.random() * 170}deg`);
  icon.style.animationDelay = `${Math.random() * 0.5}s`;

  icon.onerror = () => icon.remove();
  starfield.appendChild(icon);

  window.setTimeout(() => icon.remove(), 12000);
}

function scheduleSpawner(spawnFn, minMs, maxMs) {
  const tick = () => {
    spawnFn();
    const delay = minMs + Math.random() * (maxMs - minMs);
    window.setTimeout(tick, delay);
  };
  tick();
}

function initSkyEffects() {
  createStaticStars();

  if (RAIN_MODE === "icons" || RAIN_MODE === "mixed" || RAIN_MODE === "stars") {
    scheduleSpawner(spawnRainIcon, 700, 1700);
  }
}

function resolveHomeByProfile(profile) {
  if (profile === "admin") {
    return "/admin/";
  }
  if (profile === "lider" || profile === "gerente") {
    return "/gerente/";
  }
  if (profile === "funcionario") {
    return "/funcionario/";
  }
  return null;
}

function setMessage(text, type = "") {
  message.textContent = text;
  message.className = `message ${type}`.trim();
}

async function login(email, senha) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, senha }),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Falha ao autenticar.");
  }
  return data;
}

async function requestPasswordReset(email) {
  const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email }),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Falha ao solicitar redefinicao.");
  }
  return data;
}

const profile = getCurrentProfile();
const existingRoute = resolveHomeByProfile(profile);
if (existingRoute) {
  window.location.replace(existingRoute);
}
rememberMeEl.checked = getRememberMode();

initSkyEffects();

togglePasswordBtn.addEventListener("click", () => {
  const isHidden = passwordEl.type === "password";
  passwordEl.type = isHidden ? "text" : "password";
  togglePasswordBtn.setAttribute("aria-label", isHidden ? "Ocultar senha" : "Mostrar senha");
  togglePasswordBtn.textContent = isHidden ? "🙈" : "👁";
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const email = String(formData.get("email") || "").trim();
  const senha = String(formData.get("senha") || "").trim();
  const rememberMe = Boolean(formData.get("remember_me"));

  setMessage("");
  submitBtn.disabled = true;
  submitBtn.textContent = "Entrando...";

  try {
    const tokens = await login(email, senha);
    saveTokens(tokens.access_token, tokens.refresh_token, rememberMe);

    const userProfile = getCurrentProfile();
    const route = resolveHomeByProfile(userProfile);
    if (!route) {
      throw new Error("Perfil sem area configurada no frontend.");
    }

    setMessage("Login realizado com sucesso.", "success");
    window.location.replace(route);
  } catch (error) {
    setMessage(error.message, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Entrar";
  }
});

function setForgotMessage(text, type = "") {
  forgotMessageEl.textContent = text;
  forgotMessageEl.className = `message ${type}`.trim();
}

forgotBtn.addEventListener("click", () => {
  setForgotMessage("");
  forgotEmailEl.value = document.getElementById("email").value || "";
  forgotDialog.showModal();
});

forgotCloseBtn.addEventListener("click", () => {
  forgotDialog.close();
});

forgotForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const email = forgotEmailEl.value.trim();
  if (!email) {
    setForgotMessage("Informe um email valido.", "error");
    return;
  }

  forgotSubmitBtn.disabled = true;
  forgotSubmitBtn.textContent = "Enviando...";
  setForgotMessage("");

  try {
    const result = await requestPasswordReset(email);
    setForgotMessage(result.detail || "Solicitacao enviada.", "success");
  } catch (error) {
    setForgotMessage(error.message, "error");
  } finally {
    forgotSubmitBtn.disabled = false;
    forgotSubmitBtn.textContent = "Enviar email";
  }
});
