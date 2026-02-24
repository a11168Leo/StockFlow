import "../styles/role.css";
import { ensureRoleSession, fetchCurrentUser, logout } from "../shared/auth";

const session = ensureRoleSession(["lider", "gerente"]);
if (!session) {
  throw new Error("Sessao invalida");
}

document.getElementById("role-name").textContent = "Gerente";
document.getElementById("user-id").textContent = session.userId;

document.getElementById("logout-btn").addEventListener("click", logout);

const offcanvas = document.getElementById("offcanvas");
const overlay = document.getElementById("offcanvas-overlay");

function openMenu() {
  offcanvas.classList.add("open");
  offcanvas.setAttribute("aria-hidden", "false");
  overlay.hidden = false;
}

function closeMenu() {
  offcanvas.classList.remove("open");
  offcanvas.setAttribute("aria-hidden", "true");
  overlay.hidden = true;
}

document.getElementById("menu-toggle").addEventListener("click", openMenu);
document.getElementById("menu-close").addEventListener("click", closeMenu);
overlay.addEventListener("click", closeMenu);

async function loadUserName() {
  const nameEl = document.getElementById("user-name");
  try {
    const user = await fetchCurrentUser();
    nameEl.textContent = user.nome || "Utilizador";
  } catch {
    nameEl.textContent = "Utilizador";
  }
}

loadUserName();
