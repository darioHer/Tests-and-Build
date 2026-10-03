const resultadoEl = document.getElementById("resultado");
const screenSubtext = document.getElementById("screen-subtext");
const flagBloque = document.getElementById("flag-bloque");
const multiplicarBloque = document.getElementById("multiplicar-bloque");
const dividirBloque = document.getElementById("dividir-bloque");
const potenciaBloque = document.getElementById("potencia-bloque");
const raizBloque = document.getElementById("raiz-bloque");
const historialEl = document.getElementById("historial");
const userDisplay = document.getElementById("user-display");
const healthBadge = document.getElementById("health-badge");
const healthText = document.getElementById("health-text");

let currentFlagMode = localStorage.getItem("tbd_flag_mode") || "all";

function getUserId() {
  let userId = localStorage.getItem("tbd_user_id");
  if (!userId) {
    userId = "user_" + Math.random().toString(36).substring(2, 8);
    localStorage.setItem("tbd_user_id", userId);
  }
  return userId;
}

function getSimQuery() {
  return currentFlagMode !== "prod" ? `&simulate_flags=${currentFlagMode}` : "";
}

function mostrarResultado(valor, operacionTexto) {
  resultadoEl.className = "";
  resultadoEl.textContent = valor;
  if (screenSubtext && operacionTexto) {
    screenSubtext.textContent = operacionTexto;
  }
}

function mostrarError(data) {
  resultadoEl.className = "error";
  if (data.error === "division_por_cero") {
    resultadoEl.textContent = "No se puede dividir por cero.";
  } else if (data.error === "numero_negativo") {
    resultadoEl.textContent = "No se puede calcular la raíz de un número negativo.";
  } else {
    resultadoEl.textContent = "Ocurrió un error.";
  }
  if (screenSubtext) {
    screenSubtext.textContent = "Error en Operación";
  }
}

async function pedirOperacion(endpoint, a, b, bloqueAOcultar) {
  const userId = getUserId();
  const sim = getSimQuery();
  try {
    const resp = await fetch(`/api/${endpoint}?a=${a}&b=${b}&user_id=${userId}${sim}`);
    const data = await resp.json();

    if (resp.status === 404) {
      if (bloqueAOcultar) bloqueAOcultar.hidden = true;
      return null;
    }
    if (!resp.ok) {
      mostrarError(data);
      return null;
    }
    return data.result;
  } catch (err) {
    mostrarError({ error: "network_error" });
    return null;
  }
}

async function refrescarHistorial() {
  try {
    const resp = await fetch("/api/historial");
    if (!resp.ok) return;
    const { historial } = await resp.json();
    historialEl.innerHTML = "";

    if (!historial || historial.length === 0) {
      historialEl.innerHTML = '<li class="history-empty">No hay operaciones registradas aún.</li>';
      return;
    }

    const badgeMap = {
      sum: { symbol: "+", cls: "badge-sum" },
      resta: { symbol: "-", cls: "badge-resta" },
      multiplicar: { symbol: "×", cls: "badge-mult" },
      multiplicacion: { symbol: "×", cls: "badge-mult" },
      dividir: { symbol: "÷", cls: "badge-div" },
      division: { symbol: "÷", cls: "badge-div" },
      potencia: { symbol: "^", cls: "badge-pot" },
      raiz_cuadrada: { symbol: "√", cls: "badge-raiz" },
    };

    // Mostrar de más reciente a más antiguo
    for (const item of [...historial].reverse()) {
      const li = document.createElement("li");
      li.className = "history-item";

      const info = badgeMap[item.operacion] || { symbol: "•", cls: "badge-sum" };
      const expr = item.operacion === "raiz_cuadrada"
        ? `√(${item.a})`
        : `${item.a} ${info.symbol} ${item.b}`;

      li.innerHTML = `
        <div style="display: flex; align-items: center;">
          <span class="history-badge ${info.cls}">${info.symbol}</span>
          <span class="history-expr">${expr}</span>
        </div>
        <span class="history-val">= ${item.resultado}</span>
      `;
      historialEl.appendChild(li);
    }
  } catch {
    // Falla silenciosa sin afectar la consola
  }
}

// Actualizar chips de telemetría de flags en vivo
function actualizarChip(idChip, activo, etiqueta = "100% GA") {
  const chip = document.getElementById(idChip);
  if (!chip) return;
  const statusEl = chip.querySelector(".flag-chip-status");
  if (!statusEl) return;

  if (activo) {
    statusEl.className = "flag-chip-status " + (etiqueta.includes("10%") ? "status-canary" : "status-on");
    statusEl.textContent = `● ${etiqueta}`;
  } else {
    statusEl.className = "flag-chip-status status-off";
    statusEl.textContent = "○ Desactivado (404)";
  }
}

// Chequeo de Salud del Backend
async function verificarHealth() {
  try {
    const resp = await fetch("/health");
    if (resp.ok) {
      if (healthBadge) healthBadge.className = "badge badge-online";
      if (healthText) healthText.textContent = "API Online (Render Ready)";
    } else {
      if (healthBadge) healthBadge.className = "badge";
      if (healthText) healthText.textContent = "API Degradada";
    }
  } catch {
    if (healthBadge) healthBadge.className = "badge";
    if (healthText) healthText.textContent = "API Desconectada";
  }
}

// Botones de Operación
document.getElementById("btn-sumar").addEventListener("click", async () => {
  const a = Number(document.getElementById("a").value);
  const b = Number(document.getElementById("b").value);
  const resultado = await pedirOperacion("sumar", a, b, null);
  if (resultado !== null) mostrarResultado(resultado, `${a} + ${b}`);
  await refrescarHistorial();
});

document.getElementById("btn-restar").addEventListener("click", async () => {
  const c = Number(document.getElementById("c").value);
  const d = Number(document.getElementById("d").value);
  const resultado = await pedirOperacion("resta", c, d, flagBloque);
  if (resultado !== null) mostrarResultado(resultado, `${c} - ${d}`);
  await refrescarHistorial();
});

document.getElementById("btn-multiplicar").addEventListener("click", async () => {
  const e = Number(document.getElementById("e").value);
  const f = Number(document.getElementById("f").value);
  const resultado = await pedirOperacion("multiplicar", e, f, multiplicarBloque);
  if (resultado !== null) mostrarResultado(resultado, `${e} × ${f}`);
  await refrescarHistorial();
});

document.getElementById("btn-dividir").addEventListener("click", async () => {
  const g = Number(document.getElementById("g").value);
  const h = Number(document.getElementById("h").value);
  const resultado = await pedirOperacion("dividir", g, h, dividirBloque);
  if (resultado !== null) mostrarResultado(resultado, `${g} ÷ ${h}`);
  await refrescarHistorial();
});

document.getElementById("btn-potencia").addEventListener("click", async () => {
  const i = Number(document.getElementById("i").value);
  const j = Number(document.getElementById("j").value);
  const resultado = await pedirOperacion("potencia", i, j, potenciaBloque);
  if (resultado !== null) mostrarResultado(resultado, `${i} ^ ${j}`);
  await refrescarHistorial();
});

document.getElementById("btn-raiz").addEventListener("click", async () => {
  const k = Number(document.getElementById("k").value);
  const resultado = await pedirOperacion("raiz", k, 0, raizBloque);
  if (resultado !== null) mostrarResultado(resultado, `√(${k})`);
  await refrescarHistorial();
});

const refreshBtn = document.getElementById("btn-refresh-historial");
if (refreshBtn) {
  refreshBtn.addEventListener("click", refrescarHistorial);
}

// Actualización de UI según el modo de simulación
async function actualizarEstadoFlags() {
  const userId = getUserId();
  const sim = getSimQuery();

  // Actualizar estilos de los botones de modo
  const modeButtons = {
    all: document.getElementById("mode-all"),
    canary: document.getElementById("mode-canary"),
    off: document.getElementById("mode-off"),
    prod: document.getElementById("mode-prod"),
  };

  for (const [key, btn] of Object.entries(modeButtons)) {
    if (btn) {
      if (key === currentFlagMode) {
        btn.style.opacity = "1";
        btn.style.boxShadow = "0 0 10px rgba(56, 189, 248, 0.4)";
      } else {
        btn.style.opacity = "0.6";
        btn.style.boxShadow = "none";
      }
    }
  }

  // Comprobar flags en backend
  try {
    const resp = await fetch(`/api/resta?a=0&b=0&user_id=${userId}${sim}`);
    const activo = resp.status !== 404;
    if (flagBloque) flagBloque.hidden = !activo;
    actualizarChip("chip-resta", activo, "100% GA");
  } catch {
    if (flagBloque) flagBloque.hidden = true;
    actualizarChip("chip-resta", false);
  }

  try {
    const resp = await fetch(`/api/multiplicar?a=0&b=0&user_id=${userId}${sim}`);
    const activo = resp.status !== 404;
    if (multiplicarBloque) multiplicarBloque.hidden = !activo;
    actualizarChip("chip-mult", activo, "10% Canary");
  } catch {
    if (multiplicarBloque) multiplicarBloque.hidden = true;
    actualizarChip("chip-mult", false);
  }

  try {
    const resp = await fetch(`/api/dividir?a=0&b=1&user_id=${userId}${sim}`);
    const activo = resp.status !== 404;
    if (dividirBloque) dividirBloque.hidden = !activo;
    actualizarChip("chip-div", activo, "100% GA");
  } catch {
    if (dividirBloque) dividirBloque.hidden = true;
    actualizarChip("chip-div", false);
  }

  try {
    const resp = await fetch(`/api/potencia?a=0&b=0&user_id=${userId}${sim}`);
    const activo = resp.status !== 404;
    if (potenciaBloque) potenciaBloque.hidden = !activo;
    actualizarChip("chip-pot", activo, "100% GA");
  } catch {
    if (potenciaBloque) potenciaBloque.hidden = true;
    actualizarChip("chip-pot", false);
  }

  try {
    const resp = await fetch(`/api/raiz?a=0&b=0&user_id=${userId}${sim}`);
    const activo = resp.status !== 404;
    if (raizBloque) raizBloque.hidden = !activo;
    actualizarChip("chip-raiz", activo, "100% GA");
  } catch {
    if (raizBloque) raizBloque.hidden = true;
    actualizarChip("chip-raiz", false);
  }
}

function cambiarModoFlags(nuevoModo) {
  currentFlagMode = nuevoModo;
  localStorage.setItem("tbd_flag_mode", nuevoModo);
  actualizarEstadoFlags();
}

// Inicialización de la aplicación
window.addEventListener("DOMContentLoaded", async () => {
  const userId = getUserId();
  if (userDisplay) {
    userDisplay.textContent = userId;
  }

  // Vincular botones de modo de flags
  const btnAll = document.getElementById("mode-all");
  const btnCanary = document.getElementById("mode-canary");
  const btnOff = document.getElementById("mode-off");
  const btnProd = document.getElementById("mode-prod");

  if (btnAll) btnAll.addEventListener("click", () => cambiarModoFlags("all"));
  if (btnCanary) btnCanary.addEventListener("click", () => cambiarModoFlags("canary"));
  if (btnOff) btnOff.addEventListener("click", () => cambiarModoFlags("off"));
  if (btnProd) btnProd.addEventListener("click", () => cambiarModoFlags("prod"));

  // Verificación de estado de salud
  await verificarHealth();

  // Comprobar flags en backend
  await actualizarEstadoFlags();

  await refrescarHistorial();
});