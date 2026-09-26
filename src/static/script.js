const resultadoEl = document.getElementById("resultado");
const restaBloque = document.getElementById("resta-bloque");

document.getElementById("btn-sumar").addEventListener("click", () => {
  const a = Number(document.getElementById("a").value);
  const b = Number(document.getElementById("b").value);
  resultadoEl.textContent = `Resultado: ${a + b}`;
});

async function pedirResta(a, b) {
  const resp = await fetch(`/api/resta?a=${a}&b=${b}`);
  if (resp.status === 404) {
    // Flag apagado: se comporta como si la función no existiera.
    restaBloque.hidden = true;
    return null;
  }
  if (!resp.ok) {
    throw new Error("Error consultando /api/resta");
  }
  const data = await resp.json();
  return data.result;
}

document.getElementById("btn-restar").addEventListener("click", async () => {
  const c = Number(document.getElementById("c").value);
  const d = Number(document.getElementById("d").value);
  const resultado = await pedirResta(c, d);
  if (resultado !== null) {
    resultadoEl.textContent = `Resultado: ${resultado}`;
  }
});

// Al cargar, probamos silenciosamente si el flag está encendido para
// decidir si mostramos el bloque de resta (rollout interno).
window.addEventListener("DOMContentLoaded", async () => {
  try {
    const resp = await fetch("/api/resta?a=0&b=0");
    restaBloque.hidden = resp.status === 404;
  } catch {
    restaBloque.hidden = true;
  }
});
