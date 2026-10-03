const resultadoEl = document.getElementById("resultado");
const flagBloque = document.getElementById("flag-bloque");
const multiplicarBloque = document.getElementById("multiplicar-bloque");
const dividirBloque = document.getElementById("dividir-bloque");
const potenciaBloque = document.getElementById("potencia-bloque");
const raizBloque = document.getElementById("raiz-bloque");
const historialEl = document.getElementById("historial");

function getUserId() {
  let userId = localStorage.getItem("tbd_user_id");
  if (!userId) {
    userId = "user_" + Math.random().toString(36).substring(2, 10);
    localStorage.setItem("tbd_user_id", userId);
  }
  return userId;
}

function mostrarResultado(valor) {
  resultadoEl.textContent = `Resultado: ${valor}`;
}

function mostrarError(data) {
  if (data.error === "division_por_cero") {
    resultadoEl.textContent = "No se puede dividir por cero.";
  } else if (data.error === "numero_negativo") {
    resultadoEl.textContent = "No se puede calcular la raíz de un número negativo.";
  } else {
    resultadoEl.textContent = "Ocurrió un error.";
  }
}

async function pedirOperacion(endpoint, a, b, bloqueAOcultar) {
  const userId = getUserId();
  const resp = await fetch(`/api/${endpoint}?a=${a}&b=${b}&user_id=${userId}`);
  const data = await resp.json();

  if (resp.status === 404) {
    // Flag apagado: se comporta como si la función no existiera.
    if (bloqueAOcultar) bloqueAOcultar.hidden = true;
    return null;
  }
  if (!resp.ok) {
    mostrarError(data);
    return null;
  }
  return data.result;
}

async function refrescarHistorial() {
  try {
    const resp = await fetch("/api/historial");
    if (!resp.ok) return;
    const { historial } = await resp.json();
    historialEl.innerHTML = "";
    for (const item of historial) {
      const li = document.createElement("li");
      const simbolo = {
        sum: "+",
        resta: "-",
        multiplicar: "×",
        multiplicacion: "×",
        dividir: "÷",
        division: "÷",
        potencia: "^",
        raiz_cuadrada: "√",
      }[item.operacion] ?? item.operacion;
      const texto = item.operacion === "raiz_cuadrada"
        ? `√${item.a} = ${item.resultado}`
        : `${item.a} ${simbolo} ${item.b} = ${item.resultado}`;
      li.textContent = texto;
      historialEl.appendChild(li);
    }
  } catch {
    // Si falla, dejamos el historial como estaba; no es crítico para el resto de la UI.
  }
}

document.getElementById("btn-sumar").addEventListener("click", async () => {
  const a = Number(document.getElementById("a").value);
  const b = Number(document.getElementById("b").value);
  const resultado = await pedirOperacion("sumar", a, b, null);
  if (resultado !== null) mostrarResultado(resultado);
  await refrescarHistorial();
});

document.getElementById("btn-restar").addEventListener("click", async () => {
  const c = Number(document.getElementById("c").value);
  const d = Number(document.getElementById("d").value);
  const resultado = await pedirOperacion("resta", c, d, flagBloque);
  if (resultado !== null) mostrarResultado(resultado);
  await refrescarHistorial();
});

document.getElementById("btn-multiplicar").addEventListener("click", async () => {
  const e = Number(document.getElementById("e").value);
  const f = Number(document.getElementById("f").value);
  const resultado = await pedirOperacion("multiplicar", e, f, multiplicarBloque);
  if (resultado !== null) mostrarResultado(resultado);
  await refrescarHistorial();
});

document.getElementById("btn-dividir").addEventListener("click", async () => {
  const g = Number(document.getElementById("g").value);
  const h = Number(document.getElementById("h").value);
  const resultado = await pedirOperacion("dividir", g, h, dividirBloque);
  if (resultado !== null) mostrarResultado(resultado);
  await refrescarHistorial();
});

document.getElementById("btn-potencia").addEventListener("click", async () => {
  const i = Number(document.getElementById("i").value);
  const j = Number(document.getElementById("j").value);
  const resultado = await pedirOperacion("potencia", i, j, potenciaBloque);
  if (resultado !== null) mostrarResultado(resultado);
  await refrescarHistorial();
});

document.getElementById("btn-raiz").addEventListener("click", async () => {
  const k = Number(document.getElementById("k").value);
  const resultado = await pedirOperacion("raiz", k, 0, raizBloque);
  if (resultado !== null) mostrarResultado(resultado);
  await refrescarHistorial();
});

// Al cargar, probamos silenciosamente si cada flag está encendido para
// decidir qué bloques mostrar (rollout independiente por operación).
window.addEventListener("DOMContentLoaded", async () => {
  const userId = getUserId();

  try {
    const resp = await fetch(`/api/resta?a=0&b=0&user_id=${userId}`);
    if (flagBloque) flagBloque.hidden = resp.status === 404;
  } catch {
    if (flagBloque) flagBloque.hidden = true;
  }

  try {
    const resp = await fetch(`/api/multiplicar?a=0&b=0&user_id=${userId}`);
    if (multiplicarBloque) multiplicarBloque.hidden = resp.status === 404;
  } catch {
    if (multiplicarBloque) multiplicarBloque.hidden = true;
  }

  try {
    const resp = await fetch(`/api/dividir?a=0&b=1&user_id=${userId}`);
    if (dividirBloque) dividirBloque.hidden = resp.status === 404;
  } catch {
    if (dividirBloque) dividirBloque.hidden = true;
  }

  try {
    const resp = await fetch(`/api/potencia?a=0&b=0&user_id=${userId}`);
    if (potenciaBloque) potenciaBloque.hidden = resp.status === 404;
  } catch {
    if (potenciaBloque) potenciaBloque.hidden = true;
  }

  try {
    const resp = await fetch(`/api/raiz?a=0&b=0&user_id=${userId}`);
    if (raizBloque) raizBloque.hidden = resp.status === 404;
  } catch {
    if (raizBloque) raizBloque.hidden = true;
  }

  await refrescarHistorial();
});