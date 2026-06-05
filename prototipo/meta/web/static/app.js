const $ = (sel) => document.querySelector(sel);

function mostrarSalida(t) { const s = $("#salida"); s.textContent = t; s.classList.remove("oculto"); }
function mostrarError() { mostrarSalida("Error de comunicación con el servidor."); }

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
  try {
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
    } else if (ef.tipo === "formulario") {
      abrirVentanaForm(ef); aplicar(data);
    } else if (ef.tipo === "grilla") {
      abrirVentanaGrilla(ef); aplicar(data);
    } else {
      aplicar(data);
    }
  } catch (e) {
    mostrarError();
  }
}

$("#btn-reiniciar").onclick = async () => {
  const data = await reiniciar();
  $("#overlay").classList.add("oculto");
  $("#salida").classList.add("oculto");
  aplicar(data);
};

function cerrarVentana() { $("#ventana").classList.add("oculto"); }

function abrirVentanaForm(ef) {
  $(".ventana-titulo").textContent = ef.titulo || "Registro";
  const cuerpo = $(".ventana-cuerpo");
  cuerpo.innerHTML = "";
  for (const c of ef.campos) {
    const fila = document.createElement("div");
    fila.className = "campo";
    const lab = document.createElement("label");
    lab.textContent = c.etiqueta;
    let input;
    if (c.tipo === "referencia") {
      input = document.createElement("select");
      for (const o of (c.opciones || [])) {
        const opt = document.createElement("option");
        opt.value = o.id;
        opt.textContent = o.label;
        if (String(ef.valores[c.rol]) === String(o.id)) opt.selected = true;
        input.appendChild(opt);
      }
    } else {
      input = document.createElement("input");
      input.type = c.tipo === "numero" ? "number" : c.tipo === "fecha" ? "date" : "text";
      if (ef.valores[c.rol] != null) input.value = ef.valores[c.rol];
    }
    input.dataset.rol = c.rol;
    fila.appendChild(lab);
    fila.appendChild(input);
    cuerpo.appendChild(fila);
  }
  const pie = $(".ventana-pie");
  pie.innerHTML = "";
  const bGuardar = document.createElement("button");
  bGuardar.textContent = "Guardar";
  bGuardar.onclick = async () => {
    const valores = {};
    cuerpo.querySelectorAll("[data-rol]").forEach(el => { valores[el.dataset.rol] = el.value; });
    try {
      await fetch("/api/guardar", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ entidad: ef.entidad, valores, registro_id: ef.registro_id }),
      });
      cerrarVentana();
      mostrarSalida("Guardado.");
    } catch (e) { mostrarError(); }
  };
  const bCerrar = document.createElement("button");
  bCerrar.textContent = "Cerrar";
  bCerrar.className = "secundario";
  bCerrar.onclick = cerrarVentana;
  pie.appendChild(bGuardar);
  pie.appendChild(bCerrar);
  $("#ventana").classList.remove("oculto");
}

function abrirVentanaGrilla(ef) {
  $(".ventana-titulo").textContent = ef.titulo || "Consulta";
  const cuerpo = $(".ventana-cuerpo");
  cuerpo.innerHTML = "";
  const tabla = document.createElement("table");
  tabla.className = "grilla";
  const cab = document.createElement("tr");
  for (const col of ef.columnas) {
    const th = document.createElement("th");
    th.textContent = col.etiqueta;
    cab.appendChild(th);
  }
  tabla.appendChild(cab);
  for (const f of ef.filas) {
    const tr = document.createElement("tr");
    tr.className = "fila-click";
    for (const col of ef.columnas) {
      const td = document.createElement("td");
      td.textContent = f.valores[col.rol] || "";
      tr.appendChild(td);
    }
    tr.onclick = async () => {
      try {
        const r = await fetch("/api/abrir_formulario", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ entidad: ef.entidad, registro_id: f.id }),
        });
        const d = await r.json();
        abrirVentanaForm(d.efecto);
      } catch (e) { mostrarError(); }
    };
    tabla.appendChild(tr);
  }
  cuerpo.appendChild(tabla);
  const pie = $(".ventana-pie");
  pie.innerHTML = "";
  const bCerrar = document.createElement("button");
  bCerrar.textContent = "Cerrar";
  bCerrar.className = "secundario";
  bCerrar.onclick = cerrarVentana;
  pie.appendChild(bCerrar);
  $("#ventana").classList.remove("oculto");
}

async function cargar() {
  try {
    aplicar(await getEstado());
  } catch (e) {
    const s = document.querySelector("#salida");
    s.textContent = "No se pudo conectar con el servidor.";
    s.classList.remove("oculto");
  }
}
cargar();
