const resultadoEl = document.getElementById("resultado");
const flagBloque = document.getElementById("flag-bloque");
const historialEl = document.getElementById("historial");

function mostrarResultado(valor) {
  resultadoEl.textContent = `Resultado: ${valor}`;
}

function mostrarError(data) {
  if (data.error === "division_por_cero") {
    resultadoEl.textContent = "No se puede dividir por cero.";
  } else {
    resultadoEl.textContent = "Ocurrió un error.";
  }
}

async function pedirOperacion(endpoint, a, b) {
  const resp = await fetch(`/api/${endpoint}?a=${a}&b=${b}`);
  const data = await resp.json();

  if (resp.status === 404) {
    // Flag apagado: se comporta como si la función no existiera.
    flagBloque.hidden = true;
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
      const simbolo = { sum: "+", resta: "-", multiplicar: "×", dividir: "÷" }[item.operacion] ?? item.operacion;
      li.textContent = `${item.a} ${simbolo} ${item.b} = ${item.resultado}`;
      historialEl.appendChild(li);
    }
  } catch {
    // Si falla, dejamos el historial como estaba; no es crítico para el resto de la UI.
  }
}

document.getElementById("btn-sumar").addEventListener("click", async () => {
  const a = Number(document.getElementById("a").value);
  const b = Number(document.getElementById("b").value);
  const resultado = await pedirOperacion("sumar", a, b);
  if (resultado !== null) mostrarResultado(resultado);
  await refrescarHistorial();
});

document.getElementById("btn-restar").addEventListener("click", async () => {
  const c = Number(document.getElementById("c").value);
  const d = Number(document.getElementById("d").value);
  const resultado = await pedirOperacion("resta", c, d);
  if (resultado !== null) mostrarResultado(resultado);
  await refrescarHistorial();
});

document.getElementById("btn-multiplicar").addEventListener("click", async () => {
  const e = Number(document.getElementById("e").value);
  const f = Number(document.getElementById("f").value);
  const resultado = await pedirOperacion("multiplicar", e, f);
  if (resultado !== null) mostrarResultado(resultado);
  await refrescarHistorial();
});

document.getElementById("btn-dividir").addEventListener("click", async () => {
  const g = Number(document.getElementById("g").value);
  const h = Number(document.getElementById("h").value);
  const resultado = await pedirOperacion("dividir", g, h);
  if (resultado !== null) mostrarResultado(resultado);
  await refrescarHistorial();
});

// Al cargar, probamos silenciosamente si el flag está encendido para
// decidir si mostramos multiplicar/restar/dividir (rollout al 100%).
window.addEventListener("DOMContentLoaded", async () => {
  try {
    const resp = await fetch("/api/resta?a=0&b=0");
    flagBloque.hidden = resp.status === 404;
  } catch {
    flagBloque.hidden = true;
  }
  await refrescarHistorial();
});