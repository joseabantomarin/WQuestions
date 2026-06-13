/* =========================================================================
   WQuestions — interacciones.js
   Sin dependencias. Progreso de lectura, índice lateral, copiar código,
   resaltado de sintaxis y mini-charts SVG con tooltips.
   ========================================================================= */
(function () {
  "use strict";
  const $  = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const esc = (t) => t.replace(/[&<>]/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[m]));

  /* --------------------------------------------------------------------- */
  /* 1. Barra de progreso de lectura + cabecera fija                       */
  /* --------------------------------------------------------------------- */
  function progreso() {
    const barra = $(".barra-progreso");
    const cab = $(".cabecera");
    const f = () => {
      const h = document.documentElement;
      const max = h.scrollHeight - h.clientHeight;
      const p = max > 0 ? h.scrollTop / max : 0;
      if (barra) barra.style.setProperty("--avance", p.toFixed(4));
      if (cab) cab.dataset.fija = h.scrollTop > 8 ? "si" : "no";
    };
    document.addEventListener("scroll", f, { passive: true });
    f();
  }

  /* --------------------------------------------------------------------- */
  /* 2. Índice lateral: secciones del capítulo + scrollspy                 */
  /* --------------------------------------------------------------------- */
  function indiceLateral() {
    const drawer = $(".drawer-indice");
    const velo = $(".velo");
    const btn = $("[data-accion='indice']");
    if (!drawer || !btn) return;

    const lista = $(".lista-secciones", drawer);
    const secciones = $$(".contenido h2");
    if (lista && secciones.length) {
      secciones.forEach((h, i) => {
        if (!h.id) h.id = "sec-" + i;
        const a = document.createElement("a");
        a.href = "#" + h.id;
        a.textContent = h.textContent.replace(/^\s*[—·]\s*/, "");
        a.dataset.ref = h.id;
        lista.appendChild(a);
      });
    }

    const abrir = (v) => {
      drawer.dataset.abierto = v ? "si" : "no";
      velo.dataset.abierto = v ? "si" : "no";
      btn.setAttribute("aria-expanded", v ? "true" : "false");
    };
    btn.addEventListener("click", () => abrir(drawer.dataset.abierto !== "si"));
    velo.addEventListener("click", () => abrir(false));
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") abrir(false); });
    $$("a", lista || drawer).forEach((a) => a.addEventListener("click", () => abrir(false)));

    if (secciones.length && "IntersectionObserver" in window) {
      const enlaces = new Map($$("a[data-ref]", drawer).map((a) => [a.dataset.ref, a]));
      const io = new IntersectionObserver((ents) => {
        ents.forEach((e) => {
          if (e.isIntersecting) {
            enlaces.forEach((a) => a.classList.remove("activo"));
            const a = enlaces.get(e.target.id);
            if (a) a.classList.add("activo");
          }
        });
      }, { rootMargin: "-20% 0px -70% 0px" });
      secciones.forEach((h) => io.observe(h));
    }
  }

  /* --------------------------------------------------------------------- */
  /* 3. Modo claro/oscuro (persistente)                                    */
  /* --------------------------------------------------------------------- */
  function tema() {
    const btn = $("[data-accion='tema']");
    const guardado = localStorage.getItem("wq-tema");
    if (guardado) document.documentElement.dataset.tema = guardado;
    if (!btn) return;
    btn.addEventListener("click", () => {
      const o = document.documentElement.dataset.tema === "oscuro";
      document.documentElement.dataset.tema = o ? "claro" : "oscuro";
      localStorage.setItem("wq-tema", o ? "claro" : "oscuro");
    });
  }

  /* --------------------------------------------------------------------- */
  /* 4. Resaltado de sintaxis (escáner de tokens con regex sticky)         */
  /* --------------------------------------------------------------------- */
  const REGLAS = {
    triple: [
      ["tk-coment", /(?:#|\/\/|→).*?(?=\n|$)/y],
      ["tk-cadena", /"[^"]*"|'[^']*'/y],
      ["tk-num", /\b\d[\d_]*(?:\.\d+)?(?:-\d\d-\d\d(?:T[\d:.\-+]+)?)?\b/y],
      ["tk-q", /\bQ\b/y], ["tk-o", /\bO\b/y], ["tk-l", /\bL\b/y],
      ["tk-t", /\bT\b/y], ["tk-n", /\bN\b/y], ["tk-k", /\bK\b/y], ["tk-m", /\b[MP]\b/y],
      ["tk-puntu", /[∈(){}\[\],→]/y],
    ],
    json: [
      ["tk-coment", /\/\/.*?(?=\n|$)/y],
      ["tk-func", /"(?:[^"\\]|\\.)*"(?=\s*:)/y],
      ["tk-cadena", /"(?:[^"\\]|\\.)*"/y],
      ["tk-clave", /\b(?:true|false|null)\b/y],
      ["tk-num", /-?\b\d[\d_]*(?:\.\d+)?(?:[eE][+-]?\d+)?\b/y],
      ["tk-puntu", /[{}\[\]:,]/y],
    ],
    sql: [
      ["tk-coment", /--.*?(?=\n|$)/y],
      ["tk-cadena", /'(?:[^'\\]|\\.)*'/y],
      ["tk-clave", /\b(?:SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|AND|OR|NOT|IN|BETWEEN|GROUP|BY|ORDER|HAVING|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|AS|LIMIT|DISTINCT|COUNT|SUM|AVG|MIN|MAX|NULL|LIKE|UNION)\b/yi],
      ["tk-num", /\b\d[\d_]*(?:\.\d+)?\b/y],
      ["tk-puntu", /[(){}\[\],;.*=<>]/y],
    ],
    python: [
      ["tk-coment", /#.*?(?=\n|$)/y],
      ["tk-cadena", /[frbFRB]?(?:"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/y],
      ["tk-func", /@[A-Za-z_][\w.]*/y],
      ["tk-clave", /\b(?:def|class|return|if|elif|else|for|while|in|not|and|or|is|None|True|False|import|from|as|with|try|except|finally|raise|yield|lambda|pass|break|continue|global|assert|self)\b/y],
      ["tk-num", /\b\d[\d_]*(?:\.\d+)?\b/y],
      ["tk-func", /\b[A-Za-z_]\w*(?=\s*\()/y],
      ["tk-puntu", /[(){}\[\]:,.=+\-*/<>]/y],
    ],
  };

  function resaltar(codigo, lang) {
    const reglas = REGLAS[lang];
    if (!reglas) return esc(codigo);
    let out = "", i = 0, n = codigo.length;
    while (i < n) {
      let hit = null;
      for (const [cls, re] of reglas) {
        re.lastIndex = i;
        const m = re.exec(codigo);
        if (m && m.index === i && m[0].length) { hit = [cls, m[0]]; break; }
      }
      if (hit) { out += '<span class="' + hit[0] + '">' + esc(hit[1]) + "</span>"; i += hit[1].length; }
      else { out += esc(codigo[i]); i++; }
    }
    return out;
  }

  function codigos() {
    $$("pre code[data-lang]").forEach((code) => {
      const lang = code.dataset.lang;
      code.innerHTML = resaltar(code.textContent, lang);
    });
    // botón copiar
    $$(".bloque-codigo").forEach((b) => {
      const btn = $(".copiar", b);
      if (!btn) return;
      btn.addEventListener("click", () => {
        const t = $("pre code", b).textContent;
        navigator.clipboard.writeText(t).then(() => {
          const o = btn.innerHTML; btn.textContent = "copiado ✓";
          setTimeout(() => (btn.innerHTML = o), 1400);
        });
      });
    });
  }

  /* --------------------------------------------------------------------- */
  /* 5. Mini-charts SVG (barras, líneas, dispersión) con tooltip           */
  /* --------------------------------------------------------------------- */
  let TIP;
  function tip() { if (!TIP) { TIP = document.createElement("div"); TIP.className = "tip-flotante"; document.body.appendChild(TIP); } return TIP; }
  function mostrarTip(html, x, y) { const t = tip(); t.innerHTML = html; t.dataset.visible = "si"; t.style.left = x + 12 + "px"; t.style.top = y + 12 + "px"; }
  function ocultarTip() { if (TIP) TIP.dataset.visible = "no"; }

  const NS = "http://www.w3.org/2000/svg";
  const cssVar = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const PAL = () => [cssVar("--eje-o"), cssVar("--eje-n"), cssVar("--eje-k"), cssVar("--eje-q"), cssVar("--eje-t"), cssVar("--eje-l"), cssVar("--eje-m")];

  function svgEl(tag, attrs) { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); return e; }

  function chart(cont, spec) {
    const W = 640, H = spec.alto || 320, m = { t: 16, r: 18, b: 46, l: 46 };
    const iw = W - m.l - m.r, ih = H - m.t - m.b;
    const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}`, class: "chart", role: "img", width: "100%" });
    const datos = spec.datos || [];
    const pal = PAL();
    const colTxt = cssVar("--tinta-tenue"), colLinea = cssVar("--linea");

    const ejeColor = spec.eje ? cssVar("--eje-" + spec.eje) : pal[0];

    if (spec.tipo === "barras") {
      const maxV = spec.max || Math.max(...datos.map((d) => d.v)) * 1.1;
      // grid + eje Y
      const ticks = 4;
      for (let t = 0; t <= ticks; t++) {
        const y = m.t + ih - (ih * t) / ticks;
        svg.appendChild(svgEl("line", { x1: m.l, y1: y, x2: m.l + iw, y2: y, stroke: colLinea, "stroke-width": 1 }));
        const lab = svgEl("text", { x: m.l - 8, y: y + 4, "text-anchor": "end", fill: colTxt, "font-size": 11 });
        lab.textContent = Math.round((maxV * t) / ticks);
        svg.appendChild(lab);
      }
      const bw = iw / datos.length;
      datos.forEach((d, i) => {
        const bh = (d.v / maxV) * ih;
        const x = m.l + i * bw + bw * 0.18, y = m.t + ih - bh, w = bw * 0.64;
        const col = d.color ? cssVar("--eje-" + d.color) || d.color : ejeColor;
        const r = svgEl("rect", { x, y, width: w, height: bh, rx: 3, fill: col, opacity: .88 });
        r.style.transition = "opacity .2s";
        r.addEventListener("mousemove", (e) => { r.setAttribute("opacity", 1); mostrarTip(`<b>${d.l}</b><br>${d.v}${spec.unidad || ""}`, e.clientX, e.clientY); });
        r.addEventListener("mouseleave", () => { r.setAttribute("opacity", .88); ocultarTip(); });
        svg.appendChild(r);
        const lab = svgEl("text", { x: m.l + i * bw + bw / 2, y: H - m.b + 18, "text-anchor": "middle", fill: colTxt, "font-size": 11 });
        lab.textContent = d.l;
        svg.appendChild(lab);
      });
    }

    if (spec.tipo === "lineas") {
      const series = spec.series || [{ datos, color: spec.eje || "o" }];
      const xs = series[0].datos.map((d) => d.x);
      const allV = series.flatMap((s) => s.datos.map((d) => d.y));
      const maxV = spec.max || Math.max(...allV) * 1.1, minV = spec.min || 0;
      const X = (i) => m.l + (iw * i) / (xs.length - 1);
      const Y = (v) => m.t + ih - (ih * (v - minV)) / (maxV - minV);
      for (let t = 0; t <= 4; t++) {
        const y = m.t + ih - (ih * t) / 4;
        svg.appendChild(svgEl("line", { x1: m.l, y1: y, x2: m.l + iw, y2: y, stroke: colLinea }));
        const lab = svgEl("text", { x: m.l - 8, y: y + 4, "text-anchor": "end", fill: colTxt, "font-size": 11 });
        lab.textContent = Math.round(minV + ((maxV - minV) * t) / 4); svg.appendChild(lab);
      }
      xs.forEach((xv, i) => { if (i % Math.ceil(xs.length / 8) === 0) { const lab = svgEl("text", { x: X(i), y: H - m.b + 18, "text-anchor": "middle", fill: colTxt, "font-size": 11 }); lab.textContent = xv; svg.appendChild(lab); } });
      series.forEach((s, si) => {
        const col = cssVar("--eje-" + (s.color || "o")) || pal[si];
        const dd = s.datos.map((d, i) => (i ? "L" : "M") + X(i) + " " + Y(d.y)).join(" ");
        svg.appendChild(svgEl("path", { d: dd, fill: "none", stroke: col, "stroke-width": 2.4, "stroke-linejoin": "round" }));
        s.datos.forEach((d, i) => {
          const c = svgEl("circle", { cx: X(i), cy: Y(d.y), r: 3.5, fill: col });
          c.addEventListener("mousemove", (e) => mostrarTip(`<b>${d.x}</b><br>${s.nombre ? s.nombre + ": " : ""}${d.y}${spec.unidad || ""}`, e.clientX, e.clientY));
          c.addEventListener("mouseleave", ocultarTip);
          svg.appendChild(c);
        });
      });
    }

    if (spec.tipo === "dispersion") {
      const maxX = Math.max(...datos.map((d) => d.x)) * 1.1, maxY = Math.max(...datos.map((d) => d.y)) * 1.1;
      const X = (v) => m.l + (iw * v) / maxX, Y = (v) => m.t + ih - (ih * v) / maxY;
      for (let t = 0; t <= 4; t++) { const y = m.t + ih - (ih * t) / 4; svg.appendChild(svgEl("line", { x1: m.l, y1: y, x2: m.l + iw, y2: y, stroke: colLinea })); }
      datos.forEach((d) => {
        const col = d.color ? cssVar("--eje-" + d.color) || d.color : ejeColor;
        const c = svgEl("circle", { cx: X(d.x), cy: Y(d.y), r: d.r || 6, fill: col, opacity: .7 });
        c.addEventListener("mousemove", (e) => mostrarTip(`<b>${d.l || ""}</b><br>${d.x}, ${d.y}`, e.clientX, e.clientY));
        c.addEventListener("mouseleave", ocultarTip);
        svg.appendChild(c);
      });
    }

    // ejes base
    svg.appendChild(svgEl("line", { x1: m.l, y1: m.t + ih, x2: m.l + iw, y2: m.t + ih, stroke: colTxt, "stroke-width": 1.2 }));
    cont.innerHTML = ""; cont.appendChild(svg);
  }

  function charts() {
    $$("[data-chart]").forEach((el) => {
      const raw = $("script[type='application/json']", el);
      if (!raw) return;
      try { chart(el, JSON.parse(raw.textContent)); } catch (e) { console.warn("chart inválido", e); }
    });
  }
  window.WQchart = chart;

  /* --------------------------------------------------------------------- */
  /* 6. Revelar al hacer scroll                                            */
  /* --------------------------------------------------------------------- */
  function revelar() {
    const els = $$(".revelar");
    if (!("IntersectionObserver" in window)) { els.forEach((e) => e.classList.add("visible")); return; }
    const io = new IntersectionObserver((ents) => {
      ents.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("visible"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    els.forEach((e) => io.observe(e));
  }

  /* --------------------------------------------------------------------- */
  document.addEventListener("DOMContentLoaded", function () {
    progreso(); indiceLateral(); tema(); codigos(); charts(); revelar();
  });
})();
