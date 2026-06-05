const $ = (sel) => document.querySelector(sel);

async function getEstado() {
  const r = await fetch("/api/estado");
  return r.json();
}
async function seleccionar(indice) {
  const r = await fetch("/api/seleccionar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ indice }),
  });
  return r.json();
}
async function reiniciar() {
  const r = await fetch("/api/reiniciar", { method: "POST" });
  return r.json();
}

function renderMenu(estado) {
  $("#titulo").textContent = estado.titulo;
  $("#migas").textContent = estado.es_submenu ? "‹ submenú" : "";
  const cont = $("#opciones");
  cont.innerHTML = "";
  for (const opt of estado.opciones) {
    const b = document.createElement("button");
    b.className = "opcion";
    b.textContent = opt.label;
    b.onclick = () => onSeleccion(opt.indice);
    cont.appendChild(b);
  }
}

function renderInspector(tripletas) {
  const cont = $("#inspector");
  cont.innerHTML = "";
  let sujetoActual = null;
  for (const t of tripletas) {
    if (t.sujeto !== sujetoActual) {
      sujetoActual = t.sujeto;
      const h = document.createElement("div");
      h.className = "trip-sujeto";
      h.textContent = t.sujeto_label || t.sujeto;
      cont.appendChild(h);
    }
    const row = document.createElement("div");
    row.className = "trip-row";
    row.textContent = `${t.rol} → ${t.valor_label || t.valor}`;
    cont.appendChild(row);
  }
}

function aplicar(data) {
  renderMenu(data.estado);
  renderInspector(data.tripletas);
}

async function onSeleccion(indice) {
  const data = await seleccionar(indice);
  const ef = data.efecto || {};
  if (ef.tipo === "texto") {
    const s = $("#salida");
    s.textContent = ef.contenido;
    s.classList.remove("oculto");
    aplicar(data);
  } else if (ef.tipo === "navegado") {
    $("#salida").classList.add("oculto");
    aplicar(data);
  } else if (ef.tipo === "salir") {
    $("#overlay").classList.remove("oculto");
  } else {
    aplicar(data);
  }
}

$("#btn-reiniciar").onclick = async () => {
  const data = await reiniciar();
  $("#overlay").classList.add("oculto");
  $("#salida").classList.add("oculto");
  aplicar(data);
};

(async () => aplicar(await getEstado()))();
