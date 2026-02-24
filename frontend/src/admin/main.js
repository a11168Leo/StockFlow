import "../styles/admin.css";
import { ensureRoleSession, fetchCurrentUser, getAccessToken, logout } from "../shared/auth";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const STORAGE_KEY = "stockflow_admin_layout_v2";
const MIN_SIZE = 20;
const RESIZE_HANDLE = 14;

const session = ensureRoleSession(["admin"]);
if (!session) {
  throw new Error("Sessao invalida");
}

document.getElementById("user-id").textContent = session.userId;
document.getElementById("navbar-user-name").textContent = "Admin";

const canvas = document.getElementById("warehouse-canvas");
const ctx = canvas.getContext("2d");
const listEl = document.getElementById("sections-list");
const productListEl = document.getElementById("assigned-products");
const statusEl = document.getElementById("status-message");

const sectionNameEl = document.getElementById("section-name");
const sectionShelfEl = document.getElementById("section-shelf");
const sectionTypeEl = document.getElementById("section-type");
const sectionColorEl = document.getElementById("section-color");

const productNameEl = document.getElementById("product-name");
const productCodeEl = document.getElementById("product-code");

const modeDrawBtn = document.getElementById("mode-draw");
const modeSelectBtn = document.getElementById("mode-select");
const addProductBtn = document.getElementById("add-product");
const deleteSectionBtn = document.getElementById("delete-section");
const clearBtn = document.getElementById("clear-layout");
const syncBtn = document.getElementById("sync-api");
const logoutBtn = document.getElementById("logout-btn");

const state = {
  mode: "draw",
  sections: [],
  selectedId: null,
  draft: null,
  interaction: null,
};

function setStatus(text, isError = false) {
  statusEl.textContent = text;
  statusEl.style.color = isError ? "#b30021" : "#4f4f4f";
}

function uid() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function getSelectedSection() {
  return state.sections.find((section) => section.id === state.selectedId) || null;
}

function saveLayout() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.sections));
}

function normalizeSection(section) {
  return {
    ...section,
    products: Array.isArray(section.products) ? section.products : [],
  };
}

function loadLayout() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    state.sections = parsed.map(normalizeSection);
  } catch {
    state.sections = [];
  }
}

function setMode(mode) {
  state.mode = mode;
  modeDrawBtn.classList.toggle("active", mode === "draw");
  modeSelectBtn.classList.toggle("active", mode === "select");
  canvas.style.cursor = mode === "draw" ? "crosshair" : "default";
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

function drawResizeHandle(section) {
  ctx.save();
  ctx.fillStyle = "#0f2cff";
  ctx.fillRect(section.x + section.w - RESIZE_HANDLE, section.y + section.h - RESIZE_HANDLE, RESIZE_HANDLE, RESIZE_HANDLE);
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
  ctx.fillText(`Produtos: ${section.products.length}`, section.x + 8, section.y + 66);

  if (highlighted && state.mode === "select") {
    drawResizeHandle(section);
  }

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
    detail.textContent = `${section.type} | Prateleira ${section.shelf || "-"} | ${section.products.length} produto(s)`;

    const swatch = document.createElement("span");
    swatch.className = "swatch";
    swatch.style.background = section.color;

    meta.appendChild(name);
    meta.appendChild(detail);
    item.appendChild(meta);
    item.appendChild(swatch);

    item.addEventListener("click", () => {
      state.selectedId = section.id;
      renderAll();
    });

    listEl.appendChild(item);
  }
}

function renderProducts() {
  const selected = getSelectedSection();
  productListEl.innerHTML = "";

  if (!selected) {
    const empty = document.createElement("li");
    empty.textContent = "Selecione uma secao para vincular produtos.";
    productListEl.appendChild(empty);
    return;
  }

  if (selected.products.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = "Nenhum produto vinculado nesta secao.";
    productListEl.appendChild(empty);
    return;
  }

  for (const product of selected.products) {
    const item = document.createElement("li");

    const meta = document.createElement("div");
    meta.className = "product-meta";

    const name = document.createElement("span");
    name.className = "product-name";
    name.textContent = product.name;

    const detail = document.createElement("span");
    detail.className = "product-detail";
    detail.textContent = product.code ? `Codigo: ${product.code}` : "Sem codigo";

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "mini-danger";
    removeBtn.textContent = "x";
    removeBtn.addEventListener("click", () => {
      selected.products = selected.products.filter((itemProduct) => itemProduct.id !== product.id);
      saveLayout();
      renderAll();
      setStatus(`Produto removido da secao '${selected.name}'.`);
    });

    meta.appendChild(name);
    meta.appendChild(detail);
    item.appendChild(meta);
    item.appendChild(removeBtn);
    productListEl.appendChild(item);
  }
}

function renderAll() {
  renderList();
  renderProducts();
  renderCanvas();
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

function clamp(value, min, max) {
  return Math.max(min, Math.min(value, max));
}

function isInResizeHandle(section, x, y) {
  return (
    x >= section.x + section.w - RESIZE_HANDLE &&
    x <= section.x + section.w &&
    y >= section.y + section.h - RESIZE_HANDLE &&
    y <= section.y + section.h
  );
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
    products: [],
  };

  state.sections.push(section);
  state.selectedId = section.id;
  saveLayout();
  renderAll();
  setStatus(`Secao '${name}' criada.`);
}

canvas.addEventListener("mousedown", (event) => {
  const pointer = getPointer(event);
  const hit = hitTest(pointer.x, pointer.y);

  if (state.mode === "select") {
    state.selectedId = hit ? hit.id : null;

    if (!hit) {
      state.interaction = null;
      renderAll();
      return;
    }

    if (isInResizeHandle(hit, pointer.x, pointer.y)) {
      state.interaction = {
        type: "resize",
        sectionId: hit.id,
        startX: pointer.x,
        startY: pointer.y,
        initialW: hit.w,
        initialH: hit.h,
      };
    } else {
      state.interaction = {
        type: "move",
        sectionId: hit.id,
        offsetX: pointer.x - hit.x,
        offsetY: pointer.y - hit.y,
      };
    }

    renderAll();
    return;
  }

  if (hit) {
    state.selectedId = hit.id;
    renderAll();
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
  const pointer = getPointer(event);

  if (state.draft) {
    state.draft.endX = pointer.x;
    state.draft.endY = pointer.y;
    renderCanvas();
    return;
  }

  if (!state.interaction) {
    return;
  }

  const section = state.sections.find((item) => item.id === state.interaction.sectionId);
  if (!section) {
    return;
  }

  if (state.interaction.type === "move") {
    section.x = clamp(pointer.x - state.interaction.offsetX, 0, canvas.width - section.w);
    section.y = clamp(pointer.y - state.interaction.offsetY, 0, canvas.height - section.h);
    renderCanvas();
    return;
  }

  if (state.interaction.type === "resize") {
    const deltaX = pointer.x - state.interaction.startX;
    const deltaY = pointer.y - state.interaction.startY;
    section.w = clamp(Math.round(state.interaction.initialW + deltaX), MIN_SIZE, canvas.width - section.x);
    section.h = clamp(Math.round(state.interaction.initialH + deltaY), MIN_SIZE, canvas.height - section.y);
    renderCanvas();
  }
});

function stopInteractions() {
  const hadDraft = Boolean(state.draft);
  const hadInteraction = Boolean(state.interaction);

  if (state.draft) {
    addSectionFromDraft();
    state.draft = null;
  }

  if (state.interaction) {
    state.interaction = null;
    saveLayout();
    renderAll();
  }

  if (hadDraft || hadInteraction) {
    renderCanvas();
  }
}

canvas.addEventListener("mouseup", stopInteractions);
canvas.addEventListener("mouseleave", stopInteractions);

modeDrawBtn.addEventListener("click", () => setMode("draw"));
modeSelectBtn.addEventListener("click", () => setMode("select"));
logoutBtn.addEventListener("click", logout);

addProductBtn.addEventListener("click", () => {
  const section = getSelectedSection();
  if (!section) {
    setStatus("Selecione uma secao antes de vincular produto.", true);
    return;
  }

  const name = productNameEl.value.trim();
  const code = productCodeEl.value.trim();

  if (!name) {
    setStatus("Informe o nome do produto.", true);
    return;
  }

  section.products.push({
    id: uid(),
    name,
    code,
  });

  productNameEl.value = "";
  productCodeEl.value = "";

  saveLayout();
  renderAll();
  setStatus(`Produto vinculado na secao '${section.name}'.`);
});

deleteSectionBtn.addEventListener("click", () => {
  const section = getSelectedSection();
  if (!section) {
    setStatus("Selecione uma secao para remover.", true);
    return;
  }

  state.sections = state.sections.filter((item) => item.id !== section.id);
  state.selectedId = null;
  saveLayout();
  renderAll();
  setStatus(`Secao '${section.name}' removida.`);
});

clearBtn.addEventListener("click", () => {
  state.sections = [];
  state.selectedId = null;
  saveLayout();
  renderAll();
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

async function loadUserName() {
  const nameEl = document.getElementById("navbar-user-name");
  try {
    const user = await fetchCurrentUser();
    nameEl.textContent = user.nome || "Admin";
  } catch {
    nameEl.textContent = "Admin";
  }
}

loadLayout();
setMode("draw");
renderAll();
setStatus("Pronto para desenhar e organizar a planta.");
loadUserName();
