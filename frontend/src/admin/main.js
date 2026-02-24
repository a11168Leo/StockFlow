import "../styles/admin.css";
import { ensureRoleSession, getAccessToken, logout } from "../shared/auth";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const STORAGE_KEY = "stockflow_admin_layout_v1";
const MIN_SIZE = 20;

const session = ensureRoleSession(["admin"]);
if (!session) {
  throw new Error("Sessao invalida");
}

document.getElementById("user-id").textContent = session.userId;

const canvas = document.getElementById("warehouse-canvas");
const ctx = canvas.getContext("2d");
const listEl = document.getElementById("sections-list");
const statusEl = document.getElementById("status-message");
const sectionNameEl = document.getElementById("section-name");
const sectionShelfEl = document.getElementById("section-shelf");
const sectionTypeEl = document.getElementById("section-type");
const sectionColorEl = document.getElementById("section-color");

const modeDrawBtn = document.getElementById("mode-draw");
const modeSelectBtn = document.getElementById("mode-select");
const clearBtn = document.getElementById("clear-layout");
const syncBtn = document.getElementById("sync-api");
const logoutBtn = document.getElementById("logout-btn");

const state = {
  mode: "draw",
  sections: [],
  selectedId: null,
  draft: null,
};

function setStatus(text, isError = false) {
  statusEl.textContent = text;
  statusEl.style.color = isError ? "#b30021" : "#4f4f4f";
}

function uid() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function saveLayout() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.sections));
}

function loadLayout() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    state.sections = raw ? JSON.parse(raw) : [];
  } catch {
    state.sections = [];
  }
}

function setMode(mode) {
  state.mode = mode;
  modeDrawBtn.classList.toggle("active", mode === "draw");
  modeSelectBtn.classList.toggle("active", mode === "select");
}

function clearCanvas() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function drawGrid() {
  const size = 40;
  ctx.save();
  ctx.strokeStyle = "rgba(40, 62, 136, 0.10)";
  ctx.lineWidth = 1;

  for (let x = 0; x <= canvas.width; x += size) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();
  }

  for (let y = 0; y <= canvas.height; y += size) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
    ctx.stroke();
  }
  ctx.restore();
}

function drawSection(section, highlighted = false) {
  ctx.save();
  ctx.fillStyle = `${section.color}55`;
  ctx.strokeStyle = highlighted ? "#0f2cff" : section.color;
  ctx.lineWidth = highlighted ? 3 : 2;

  ctx.fillRect(section.x, section.y, section.w, section.h);
  ctx.strokeRect(section.x, section.y, section.w, section.h);

  ctx.fillStyle = "#101010";
  ctx.font = "bold 14px Segoe UI";
  ctx.fillText(section.name, section.x + 8, section.y + 18);

  ctx.font = "12px Segoe UI";
  ctx.fillText(`Prateleira: ${section.shelf || "-"}`, section.x + 8, section.y + 34);
  ctx.fillText(`Tipo: ${section.type}`, section.x + 8, section.y + 50);

  ctx.restore();
}

function drawDraft() {
  if (!state.draft) {
    return;
  }

  const { x, y, w, h } = normalizeRect(state.draft);
  ctx.save();
  ctx.fillStyle = "rgba(15, 44, 255, 0.12)";
  ctx.strokeStyle = "#0f2cff";
  ctx.setLineDash([8, 6]);
  ctx.lineWidth = 2;
  ctx.fillRect(x, y, w, h);
  ctx.strokeRect(x, y, w, h);
  ctx.restore();
}

function renderCanvas() {
  clearCanvas();
  drawGrid();

  for (const section of state.sections) {
    drawSection(section, section.id === state.selectedId);
  }

  drawDraft();
}

function renderList() {
  listEl.innerHTML = "";

  for (const section of state.sections) {
    const item = document.createElement("li");
    item.classList.toggle("active", section.id === state.selectedId);

    const meta = document.createElement("div");
    meta.className = "section-meta";

    const name = document.createElement("span");
    name.className = "section-name";
    name.textContent = section.name;

    const detail = document.createElement("span");
    detail.className = "section-detail";
    detail.textContent = `${section.type} | Prateleira ${section.shelf || "-"}`;

    const swatch = document.createElement("span");
    swatch.className = "swatch";
    swatch.style.background = section.color;

    meta.appendChild(name);
    meta.appendChild(detail);
    item.appendChild(meta);
    item.appendChild(swatch);

    item.addEventListener("click", () => {
      state.selectedId = section.id;
      renderList();
      renderCanvas();
    });

    listEl.appendChild(item);
  }
}

function normalizeRect(rect) {
  const x = Math.min(rect.startX, rect.endX);
  const y = Math.min(rect.startY, rect.endY);
  const w = Math.abs(rect.endX - rect.startX);
  const h = Math.abs(rect.endY - rect.startY);
  return { x, y, w, h };
}

function getPointer(event) {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  return {
    x: (event.clientX - rect.left) * scaleX,
    y: (event.clientY - rect.top) * scaleY,
  };
}

function hitTest(x, y) {
  for (let index = state.sections.length - 1; index >= 0; index -= 1) {
    const section = state.sections[index];
    if (x >= section.x && x <= section.x + section.w && y >= section.y && y <= section.y + section.h) {
      return section;
    }
  }
  return null;
}

function addSectionFromDraft() {
  const draftRect = normalizeRect(state.draft);
  if (draftRect.w < MIN_SIZE || draftRect.h < MIN_SIZE) {
    setStatus("Area muito pequena. Arraste uma area maior.", true);
    return;
  }

  const name = sectionNameEl.value.trim() || `Secao ${state.sections.length + 1}`;
  const shelf = sectionShelfEl.value.trim();
  const type = sectionTypeEl.value;
  const color = sectionColorEl.value;

  const section = {
    id: uid(),
    name,
    shelf,
    type,
    color,
    x: Math.round(draftRect.x),
    y: Math.round(draftRect.y),
    w: Math.round(draftRect.w),
    h: Math.round(draftRect.h),
  };

  state.sections.push(section);
  state.selectedId = section.id;
  saveLayout();
  renderList();
  renderCanvas();
  setStatus(`Secao '${name}' criada.`);
}

canvas.addEventListener("mousedown", (event) => {
  const pointer = getPointer(event);
  const hit = hitTest(pointer.x, pointer.y);

  if (state.mode === "select") {
    state.selectedId = hit ? hit.id : null;
    renderList();
    renderCanvas();
    return;
  }

  if (hit) {
    state.selectedId = hit.id;
    renderList();
    renderCanvas();
    return;
  }

  state.draft = {
    startX: pointer.x,
    startY: pointer.y,
    endX: pointer.x,
    endY: pointer.y,
  };
});

canvas.addEventListener("mousemove", (event) => {
  if (!state.draft) {
    return;
  }

  const pointer = getPointer(event);
  state.draft.endX = pointer.x;
  state.draft.endY = pointer.y;
  renderCanvas();
});

canvas.addEventListener("mouseup", () => {
  if (!state.draft) {
    return;
  }

  addSectionFromDraft();
  state.draft = null;
  renderCanvas();
});

canvas.addEventListener("mouseleave", () => {
  if (!state.draft) {
    return;
  }

  state.draft = null;
  renderCanvas();
});

modeDrawBtn.addEventListener("click", () => setMode("draw"));
modeSelectBtn.addEventListener("click", () => setMode("select"));
logoutBtn.addEventListener("click", logout);

clearBtn.addEventListener("click", () => {
  state.sections = [];
  state.selectedId = null;
  saveLayout();
  renderList();
  renderCanvas();
  setStatus("Planta limpa.");
});

syncBtn.addEventListener("click", async () => {
  if (state.sections.length === 0) {
    setStatus("Nada para sincronizar.", true);
    return;
  }

  const token = getAccessToken();
  if (!token) {
    setStatus("Sem token de autenticacao.", true);
    return;
  }

  let successCount = 0;
  let failCount = 0;

  for (const section of state.sections) {
    const payload = {
      nome: section.name,
      pos_x: section.x,
      pos_y: section.y,
      largura: section.w,
      altura: section.h,
      cor_padrao: section.color,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/secoes/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        successCount += 1;
      } else {
        failCount += 1;
      }
    } catch {
      failCount += 1;
    }
  }

  setStatus(`Sincronizacao finalizada. Sucesso: ${successCount}, Falhas: ${failCount}.`, failCount > 0);
});

loadLayout();
setMode("draw");
renderList();
renderCanvas();
setStatus("Pronto para desenhar a planta.");
