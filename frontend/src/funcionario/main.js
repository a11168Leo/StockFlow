import "../styles/role.css";
import { ensureRoleSession, logout } from "../shared/auth";

const session = ensureRoleSession(["funcionario"]);
if (!session) {
  throw new Error("Sessao invalida");
}

document.getElementById("role-name").textContent = "Funcionario";
document.getElementById("user-id").textContent = session.userId;

document.getElementById("logout-btn").addEventListener("click", logout);
