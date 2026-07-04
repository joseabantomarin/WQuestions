# Landing de entrada estilo Gamma — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Skill de diseño:** al construir el CSS y el marcado (Tareas 1–5) usa la skill `frontend-design` para el pulido visual (espaciados, sombras, hover, ritmo tipográfico) DENTRO de los tokens y clases que fija este plan. No inventes clases nuevas ni cambies la paleta.

**Goal:** Crear una landing de entrada (estilo del sitio Gamma, adaptada a la voz del libro) como nuevo `index.html` raíz de GitHub Pages, moviendo el índice actual a `indice.html`.

**Architecture:** Sitio estático servido desde `libro/manuscrito2/`. La landing es un único `index.html` + una hoja autónoma `assets/landing.css` que reutiliza los tokens del libro (colores de eje, acento, tema claro/oscuro) y `assets/interacciones.js` (toggle de tema y animaciones `.revelar`). El índice del libro se renombra a `indice.html` sin más cambios.

**Tech Stack:** HTML5 + CSS (custom properties, flexbox/grid) + el JS existente `interacciones.js`. Sin dependencias externas, sin build.

## Global Constraints

- **Directorio servido:** `libro/manuscrito2/` (GitHub Pages, `static.yml` ya publica todo el dir). Todas las rutas son relativas dentro de ese dir.
- **Sin dependencias externas:** todo CSS/JS local. Nada de CDNs, fuentes remotas ni fetch (compatible con Pages y CSP).
- **Reusar tokens del libro, no editar `estilo.css`:** `--eje-q #b23a48`, `--eje-o #2161a8`, `--eje-l #3a7d44`, `--eje-t #6d4c91`, `--eje-n #c47f17`, `--eje-k #0f8a7e`, `--eje-m #a8327d`; acento `--acento #1f6f8b`; tinta `--tinta #23201a`.
- **Tema:** atributo `data-tema="oscuro"` en `<html>`; toggle vía botón `data-accion="tema"` (lo maneja `interacciones.js`, persiste en `localStorage['wq-tema']`). La landing debe soportar claro (defecto) y oscuro.
- **Voz del copy:** español neutro, tuteo neutro (quieres/puedes, NO querés/podés). Sin muletillas de IA. Sin auto-declarar «rigor/honestidad». El copy exacto de cada sección está en las tareas — úsalo tal cual salvo la pasada de tono final (Tarea 6).
- **No editar los 34 capítulos** ni `indice.html` (salvo el renombrado).
- **H1 del héroe:** «Las preguntas como coordenadas».

---

## File Structure

- `libro/manuscrito2/indice.html` — el índice del libro (renombrado desde `index.html`, sin cambios de contenido).
- `libro/manuscrito2/index.html` — NUEVA landing (este plan la construye por secciones).
- `libro/manuscrito2/assets/landing.css` — NUEVA hoja autónoma con el sistema de diseño de la landing.
- `libro/manuscrito2/assets/img/portada.png` — copia de `libro/portada.png` para el visual del héroe.
- `libro/manuscrito2/assets/interacciones.js` — SIN cambios; se reutiliza.

### Vocabulario de clases (contrato entre tareas)

Definido en la Tarea 1 (`landing.css`), consumido por las Tareas 2–5:

- Contenedor: `.env` (máx-ancho centrado). Sección: `.seccion`, con `.seccion__cab` (super + h2 + intro).
- Etiqueta pequeña: `.super`. Título de sección: `.seccion__tit`. Intro: `.seccion__intro`.
- Botones: `.btn`, modificadores `.btn--solido` (acento relleno) y `.btn--borde` (contorno). Fila: `.cta-fila`.
- Rejillas: `.rejilla` (base, auto-fit) y variantes por conteo con `--min` (ancho mínimo de columna).
- Tarjeta genérica: `.tarjeta` (`.tarjeta__num`, `.tarjeta__tit`, `.tarjeta__txt`).
- Tarjeta de eje (coloreada): `.eje-card` con `style="--c: var(--eje-X)"`; usa `--c` para número, borde e icono.
- Tarjeta de caso (enlace): `a.caso` (`.caso__tit`, `.caso__txt`).
- Lista de beneficios: `.beneficios` (`li` con viñeta ✓).
- Franja de ejes del héroe: `.franja-ejes` + `.pill` + `.pt` (reutiliza el patrón del índice actual).
- Autor: `.autor-bloque`. CTA final: `.cta-final`. Pie: `.pie`.

---

### Task 1: Andamiaje + sistema de diseño + héroe

Renombra el índice, copia la imagen, crea `landing.css` (tokens + layout + componentes + tema) y un `index.html` con head, header, héroe y pie. Deja una página válida y navegable.

**Files:**
- Rename: `libro/manuscrito2/index.html` → `libro/manuscrito2/indice.html`
- Create: `libro/manuscrito2/index.html`
- Create: `libro/manuscrito2/assets/landing.css`
- Create (copy): `libro/manuscrito2/assets/img/portada.png`

**Interfaces:**
- Produces: el vocabulario de clases de arriba; el head con `<link rel="stylesheet" href="assets/landing.css">` y `<script src="assets/interacciones.js">`; el header con botón `data-accion="tema"`; los contenedores `<main>` donde las Tareas 2–5 insertan `<section class="seccion">`.

- [ ] **Step 1: Renombrar el índice y copiar la portada**

```bash
cd libro/manuscrito2
git mv index.html indice.html
mkdir -p assets/img
cp ../portada.png assets/img/portada.png
```

- [ ] **Step 2: Verificar que el índice se movió y la portada existe**

```bash
cd libro/manuscrito2
test -f indice.html && test ! -f index.html && test -f assets/img/portada.png && echo OK
```
Expected: `OK`

- [ ] **Step 3: Crear `assets/landing.css` (sistema de diseño)**

Reutiliza los tokens del libro y define el look Gamma. Código base (frontend-design puede refinar valores de sombra/espaciado dentro de estas reglas):

```css
/* ===== WQuestions — landing.css =====
   Look "Gamma" (tema claro por defecto) sobre los tokens del libro. */
:root{
  /* Ejes del libro (copiados; NO dependemos de estilo.css) */
  --eje-q:#b23a48; --eje-o:#2161a8; --eje-l:#3a7d44; --eje-t:#6d4c91;
  --eje-n:#c47f17; --eje-k:#0f8a7e; --eje-m:#a8327d;
  --eje-q-suave:#f6e3e3; --eje-o-suave:#e2ebf6; --eje-l-suave:#e2efe4;
  --eje-t-suave:#ebe5f3; --eje-n-suave:#f6ecd8; --eje-k-suave:#d9f0ed; --eje-m-suave:#f6e2ef;
  /* Base clara */
  --tinta:#23201a; --tinta-suave:#5f574a; --tinta-tenue:#8a8170;
  --acento:#1f6f8b; --acento-hov:#155063;
  --fondo:#ffffff; --fondo-2:#f6f4ef; --linea:#e7e2d8;
  --radio:14px; --sombra:0 1px 2px rgba(0,0,0,.04), 0 8px 24px rgba(0,0,0,.06);
  --sans:Arial,"Helvetica Neue",Helvetica,"Liberation Sans",sans-serif;
  --display:Arial,"Helvetica Neue",Helvetica,sans-serif;
  --env:72rem;
}
html[data-tema="oscuro"]{
  --tinta:#ece3d1; --tinta-suave:#b7ac96; --tinta-tenue:#8a8170;
  --acento:#6fb6cf; --acento-hov:#95cee2;
  --fondo:#1a1814; --fondo-2:#221f19; --linea:#33302a;
  --sombra:0 1px 2px rgba(0,0,0,.3), 0 8px 24px rgba(0,0,0,.35);
  --eje-q-suave:#3a262a; --eje-o-suave:#23303f; --eje-l-suave:#243524;
  --eje-t-suave:#2e2740; --eje-n-suave:#3a3018; --eje-k-suave:#163230; --eje-m-suave:#3a2333;
}
*{box-sizing:border-box}
body{margin:0;background:var(--fondo);color:var(--tinta);font-family:var(--sans);
  line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:var(--acento);text-decoration:none}
a:hover{color:var(--acento-hov)}
img{max-width:100%;height:auto}
.env{max-width:var(--env);margin-inline:auto;padding-inline:clamp(1rem,4vw,2rem)}

/* Header */
.cabecera{position:sticky;top:0;z-index:20;display:flex;align-items:center;
  justify-content:space-between;gap:1rem;padding:.7rem clamp(1rem,4vw,2rem);
  background:color-mix(in srgb,var(--fondo) 88%,transparent);backdrop-filter:blur(8px);
  border-bottom:1px solid var(--linea)}
.marca{display:flex;align-items:center;gap:.55rem;font-weight:700;color:var(--tinta);
  letter-spacing:.14em;text-transform:uppercase;font-size:.82rem}
.marca .glifo{display:inline-grid;grid-template-columns:repeat(3,4px);gap:2px}
.marca .glifo i{width:4px;height:4px;border-radius:1px;display:block}
.marca .glifo i:nth-child(1){background:var(--eje-q)} .marca .glifo i:nth-child(2){background:var(--eje-o)}
.marca .glifo i:nth-child(3){background:var(--eje-l)} .marca .glifo i:nth-child(4){background:var(--eje-t)}
.marca .glifo i:nth-child(5){background:var(--eje-n)} .marca .glifo i:nth-child(6){background:var(--eje-k)}
.acciones{display:flex;gap:.5rem;align-items:center}

/* Botones */
.btn{display:inline-flex;align-items:center;gap:.4rem;font-family:var(--sans);
  font-size:.9rem;font-weight:600;padding:.6rem 1.1rem;border-radius:999px;
  border:1px solid transparent;cursor:pointer;transition:all .18s;white-space:nowrap}
.btn--solido{background:var(--acento);color:#fff;border-color:var(--acento)}
.btn--solido:hover{background:var(--acento-hov);color:#fff}
.btn--borde{background:transparent;color:var(--tinta);border-color:var(--linea)}
.btn--borde:hover{border-color:var(--tinta-tenue);color:var(--tinta)}
.btn-cromo{font-size:.78rem;font-weight:500;color:var(--tinta-suave);background:transparent;
  border:1px solid var(--linea);border-radius:999px;padding:.4rem .8rem;cursor:pointer}
.btn-cromo:hover{color:var(--tinta);border-color:var(--tinta-tenue)}
.cta-fila{display:flex;flex-wrap:wrap;gap:.7rem;margin-top:1.6rem}

/* Secciones */
.seccion{padding:clamp(3rem,7vw,5.5rem) 0;border-top:1px solid var(--linea)}
.seccion--tenue{background:var(--fondo-2)}
.seccion__cab{max-width:46rem;margin-bottom:2.2rem}
.super{font-family:var(--sans);font-weight:700;font-size:.72rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--acento);margin:0 0 .5rem}
.seccion__tit{font-family:var(--display);font-weight:700;font-size:clamp(1.6rem,4vw,2.4rem);
  line-height:1.15;letter-spacing:-.02em;margin:0 0 .6rem;color:var(--tinta)}
.seccion__intro{font-size:1.08rem;color:var(--tinta-suave);margin:0}

/* Rejillas y tarjetas */
.rejilla{display:grid;gap:1.1rem;grid-template-columns:repeat(auto-fit,minmax(var(--min,16rem),1fr))}
.tarjeta{background:var(--fondo);border:1px solid var(--linea);border-radius:var(--radio);
  padding:1.4rem;box-shadow:var(--sombra)}
.tarjeta__num{font-family:var(--display);font-weight:800;font-size:1.5rem;color:var(--acento)}
.tarjeta__tit{font-weight:700;font-size:1.05rem;margin:.5rem 0 .35rem;color:var(--tinta)}
.tarjeta__txt{margin:0;color:var(--tinta-suave);font-size:.98rem}

/* Tarjeta de eje (coloreada por --c) */
.eje-card{background:var(--fondo);border:1px solid var(--linea);border-left:4px solid var(--c);
  border-radius:var(--radio);padding:1.3rem;box-shadow:var(--sombra)}
.eje-card__num{font-family:var(--display);font-weight:800;font-size:1.7rem;color:var(--c);line-height:1}
.eje-card__q{font-weight:700;font-size:1.08rem;margin:.4rem 0 .3rem;color:var(--tinta)}
.eje-card__txt{margin:0;color:var(--tinta-suave);font-size:.96rem}

/* Tarjeta de caso (enlace) */
.caso{display:block;background:var(--fondo);border:1px solid var(--linea);border-radius:var(--radio);
  padding:1.2rem;box-shadow:var(--sombra);color:var(--tinta);transition:transform .18s,border-color .18s}
.caso:hover{transform:translateY(-2px);border-color:var(--acento);color:var(--tinta)}
.caso__tit{font-weight:700;font-size:1.02rem;margin:0 0 .3rem}
.caso__txt{margin:0;color:var(--tinta-suave);font-size:.94rem}

/* Beneficios */
.beneficios{list-style:none;padding:0;margin:1.2rem 0 0;display:grid;gap:.5rem}
.beneficios li{padding-left:1.6rem;position:relative;color:var(--tinta-suave)}
.beneficios li::before{content:"✓";position:absolute;left:0;color:var(--eje-k);font-weight:700}

/* Héroe */
.landing-heroe{padding:clamp(3rem,8vw,6rem) 0 clamp(2rem,5vw,3.5rem)}
.landing-heroe h1{font-family:var(--display);font-weight:800;letter-spacing:-.03em;
  font-size:clamp(2.4rem,7vw,4.2rem);line-height:1.02;margin:.4rem 0 0}
.landing-heroe h1 em{font-style:normal;color:var(--acento)}
.bajada{font-size:clamp(1.1rem,2.4vw,1.35rem);color:var(--tinta-suave);max-width:44ch;margin:1.3rem 0 0}
.franja-ejes{display:flex;flex-wrap:wrap;gap:.5rem;margin:1.8rem 0 0}
.pill{display:inline-flex;align-items:center;gap:.4rem;font-size:.82rem;font-weight:600;
  padding:.35rem .7rem;border-radius:999px;border:1px solid var(--linea);background:var(--fondo-2)}
.pill .pt{width:9px;height:9px;border-radius:50%;display:inline-block}

/* Autor / CTA final / pie */
.autor-bloque{display:grid;gap:1.2rem;align-items:center;grid-template-columns:1fr}
.cta-final{text-align:center;padding:clamp(3.5rem,8vw,6rem) 0}
.cta-final h2{font-family:var(--display);font-weight:800;font-size:clamp(1.8rem,5vw,3rem);
  letter-spacing:-.02em;margin:0 auto;max-width:20ch}
.cta-final .cta-fila{justify-content:center}
.pie{border-top:1px solid var(--linea);padding:2.2rem 0;color:var(--tinta-tenue);font-size:.9rem}
.pie a{color:var(--tinta-suave)}
.pie .env{display:flex;flex-wrap:wrap;gap:1rem;justify-content:space-between}

/* Revelar (con interacciones.js) */
.revelar{opacity:0;transform:translateY(14px);transition:opacity .6s,transform .6s}
html:not(.js) .revelar{opacity:1;transform:none}
.revelar.visible{opacity:1;transform:none}

@media (max-width:34rem){ .cabecera .marca span.txt{display:none} }
```

- [ ] **Step 4: Crear `index.html` con head, header, héroe y pie**

```html
<!DOCTYPE html>
<html lang="es" data-tema="claro">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WQuestions — Las preguntas como coordenadas</title>
  <meta name="description" content="Siete preguntas bastan para organizar la información de cualquier dominio. Una arquitectura universal para la era de la inteligencia artificial.">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="WQuestions">
  <meta property="og:locale" content="es_ES">
  <meta property="og:title" content="WQuestions — Las preguntas como coordenadas">
  <meta property="og:description" content="Siete preguntas bastan para organizar la información de cualquier dominio. Una arquitectura universal para la era de la inteligencia artificial.">
  <meta property="og:url" content="https://joseabantomarin.github.io/WQuestions/">
  <meta property="og:image" content="https://joseabantomarin.github.io/WQuestions/assets/og-cover.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="stylesheet" href="assets/landing.css">
  <script>
    document.documentElement.classList.add('js');
    try{var t=localStorage.getItem('wq-tema');if(t)document.documentElement.dataset.tema=t;}catch(e){}
  </script>
</head>
<body>
  <div class="barra-progreso" aria-hidden="true"></div>
  <header class="cabecera">
    <a class="marca" href="index.html">
      <span class="glifo"><i></i><i></i><i></i><i></i><i></i><i></i></span>
      <span class="txt">WQuestions</span>
    </a>
    <div class="acciones">
      <button class="btn-cromo" data-accion="tema" aria-label="Cambiar tema">◐ Tema</button>
      <a class="btn btn--solido" href="indice.html">Leer el libro</a>
    </div>
  </header>

  <main>
    <section class="landing-heroe">
      <div class="env">
        <p class="super revelar">Arquitectura universal de la información</p>
        <h1 class="revelar">Las preguntas como <em>coordenadas</em></h1>
        <p class="bajada revelar">Quién, qué, dónde, cuándo, cuánto, cuál y cómo. Siete preguntas
          bastan para organizar la información de cualquier dominio —y para que la inteligencia
          artificial trabaje con nuestros datos sin perder rigor.</p>
        <div class="franja-ejes revelar" aria-label="Los siete ejes">
          <span class="pill"><span class="pt" style="background:var(--eje-q)"></span>Q · quién</span>
          <span class="pill"><span class="pt" style="background:var(--eje-o)"></span>O · qué</span>
          <span class="pill"><span class="pt" style="background:var(--eje-l)"></span>L · dónde</span>
          <span class="pill"><span class="pt" style="background:var(--eje-t)"></span>T · cuándo</span>
          <span class="pill"><span class="pt" style="background:var(--eje-n)"></span>N · cuánto</span>
          <span class="pill"><span class="pt" style="background:var(--eje-k)"></span>K · cuál</span>
          <span class="pill"><span class="pt" style="background:var(--eje-m)"></span>M · cómo</span>
        </div>
        <div class="cta-fila revelar">
          <a class="btn btn--solido" href="indice.html">Leer el libro</a>
          <a class="btn btn--borde" href="33-anexo-prototipo.html">Ver el prototipo (Python)</a>
        </div>
      </div>
    </section>

    <!-- Las Tareas 2–5 insertan aquí sus <section class="seccion"> -->

  </main>

  <footer class="pie">
    <div class="env">
      <span>© José Abanto Marín · WQuestions</span>
      <span>
        <a href="indice.html">Índice</a> ·
        <a href="WQuestions.pdf">PDF</a> ·
        <a href="33-anexo-prototipo.html">Prototipo</a>
      </span>
    </div>
  </footer>

  <script src="assets/interacciones.js"></script>
</body>
</html>
```

- [ ] **Step 5: Verificar estructura, enlaces del andamiaje y validez**

```bash
cd libro/manuscrito2
# los destinos enlazados existen
for f in indice.html 33-anexo-prototipo.html WQuestions.pdf assets/landing.css assets/interacciones.js assets/img/portada.png; do test -e "$f" && echo "ok $f" || echo "FALTA $f"; done
# HTML bien formado (usa python stdlib, sin deps)
python3 - <<'PY'
from html.parser import HTMLParser
class P(HTMLParser):
    pass
P().feed(open('index.html',encoding='utf-8').read())
print("html-parse OK")
PY
```
Expected: seis líneas `ok ...` y `html-parse OK`. Ninguna `FALTA`.

- [ ] **Step 6: (Verificación visual del usuario)** Abrir `libro/manuscrito2/index.html` en el navegador: se ve el héroe con la franja de 7 ejes; el botón «◐ Tema» alterna claro/oscuro y persiste al recargar; «Leer el libro» abre el índice.

- [ ] **Step 7: Commit**

```bash
cd /Users/joseabanto/WQuestions
git add libro/manuscrito2/index.html libro/manuscrito2/indice.html libro/manuscrito2/assets/landing.css libro/manuscrito2/assets/img/portada.png
git commit -m "feat(landing): andamiaje, sistema de diseño y héroe de la landing

Renombra index.html -> indice.html (índice del libro) y crea la nueva
landing como index.html raíz, con assets/landing.css (look Gamma sobre
los tokens del libro) y reutilizando interacciones.js.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Secciones «El problema» + «La solución» + «Las 7 coordenadas»

**Files:**
- Modify: `libro/manuscrito2/index.html` (insertar 3 `<section>` en el marcador de `<main>`)

**Interfaces:**
- Consumes: clases `.seccion`, `.env`, `.seccion__cab`, `.super`, `.seccion__tit`, `.seccion__intro`, `.rejilla`, `.tarjeta`, `.eje-card` (Tarea 1).

- [ ] **Step 1: Insertar las tres secciones** (reemplaza el comentario `<!-- Las Tareas 2–5 ... -->`)

```html
    <section class="seccion" id="problema">
      <div class="env">
        <div class="seccion__cab revelar">
          <p class="super">El problema</p>
          <h2 class="seccion__tit">La torre de Babel de los datos</h2>
          <p class="seccion__intro">La información existe, pero no puede dialogar. Cada sistema
            habla su propio idioma, y traducir entre ellos cuesta tiempo, dinero y contexto.</p>
        </div>
        <div class="rejilla revelar" style="--min:15rem">
          <div class="tarjeta">
            <div class="tarjeta__num">01</div>
            <h3 class="tarjeta__tit">Sistemas aislados</h3>
            <p class="tarjeta__txt">Aplicaciones que no comparten ni el contexto ni la forma de sus datos.</p>
          </div>
          <div class="tarjeta">
            <div class="tarjeta__num">02</div>
            <h3 class="tarjeta__tit">Vocabularios incompatibles</h3>
            <p class="tarjeta__txt">Esquemas y ontologías que no se entienden entre plataformas.</p>
          </div>
          <div class="tarjeta">
            <div class="tarjeta__num">03</div>
            <h3 class="tarjeta__tit">Fragmentación</h3>
            <p class="tarjeta__txt">El conocimiento queda disperso: difícil de localizar, de relacionar y de reutilizar.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="seccion seccion--tenue" id="solucion">
      <div class="env">
        <div class="seccion__cab revelar">
          <p class="super">La solución</p>
          <h2 class="seccion__tit">Un modelo basado en siete preguntas</h2>
          <p class="seccion__intro">Cualquier hecho puede describirse respondiendo siete preguntas.
            Funcionan como coordenadas: ubican, relacionan y transmiten un dato sin ambigüedad,
            igual que la latitud y la longitud ubican un punto en el mapa.</p>
        </div>
      </div>
    </section>

    <section class="seccion" id="coordenadas">
      <div class="env">
        <div class="seccion__cab revelar">
          <p class="super">La gramática del conocimiento</p>
          <h2 class="seccion__tit">Las siete coordenadas</h2>
        </div>
        <div class="rejilla revelar" style="--min:14rem">
          <div class="eje-card" style="--c:var(--eje-q)">
            <div class="eje-card__num">Q</div>
            <h3 class="eje-card__q">¿Quién?</h3>
            <p class="eje-card__txt">El agente o sujeto: quién actúa en el hecho.</p>
          </div>
          <div class="eje-card" style="--c:var(--eje-o)">
            <div class="eje-card__num">O</div>
            <h3 class="eje-card__q">¿Qué?</h3>
            <p class="eje-card__txt">El objeto o la acción: el núcleo del dato.</p>
          </div>
          <div class="eje-card" style="--c:var(--eje-l)">
            <div class="eje-card__num">L</div>
            <h3 class="eje-card__q">¿Dónde?</h3>
            <p class="eje-card__txt">El lugar: ancla el hecho a un espacio.</p>
          </div>
          <div class="eje-card" style="--c:var(--eje-t)">
            <div class="eje-card__num">T</div>
            <h3 class="eje-card__q">¿Cuándo?</h3>
            <p class="eje-card__txt">El momento: sitúa el hecho en el tiempo.</p>
          </div>
          <div class="eje-card" style="--c:var(--eje-n)">
            <div class="eje-card__num">N</div>
            <h3 class="eje-card__q">¿Cuánto?</h3>
            <p class="eje-card__txt">La cantidad y su unidad: hace el dato medible y comparable.</p>
          </div>
          <div class="eje-card" style="--c:var(--eje-k)">
            <div class="eje-card__num">K</div>
            <h3 class="eje-card__q">¿Cuál?</h3>
            <p class="eje-card__txt">La clase o categoría: distingue entre opciones.</p>
          </div>
          <div class="eje-card" style="--c:var(--eje-m)">
            <div class="eje-card__num">M</div>
            <h3 class="eje-card__q">¿Cómo?</h3>
            <p class="eje-card__txt">El predicado que conecta: la relación y el método.</p>
          </div>
        </div>
        <p class="revelar" style="margin-top:1.4rem"><a href="02-cuatro-pilares.html">Conócelas en detalle →</a></p>
      </div>
    </section>
```

- [ ] **Step 2: Verificar** (secciones presentes, 7 tarjetas de eje, HTML válido)

```bash
cd libro/manuscrito2
grep -c 'class="eje-card"' index.html   # espera: 7
grep -q 'id="problema"' index.html && grep -q 'id="solucion"' index.html && grep -q 'id="coordenadas"' index.html && echo "secciones OK"
python3 -c "from html.parser import HTMLParser as H; H().feed(open('index.html',encoding='utf-8').read()); print('html-parse OK')"
```
Expected: `7`, `secciones OK`, `html-parse OK`.

- [ ] **Step 3: Commit**

```bash
cd /Users/joseabanto/WQuestions
git add libro/manuscrito2/index.html
git commit -m "feat(landing): secciones problema, solución y las 7 coordenadas

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Secciones «Interoperabilidad» + «IA & LLMs»

**Files:**
- Modify: `libro/manuscrito2/index.html` (insertar 2 `<section>` tras la sección `#coordenadas`)

**Interfaces:**
- Consumes: `.seccion`, `.seccion--tenue`, `.rejilla`, `.tarjeta`, `.beneficios` (Tarea 1).

- [ ] **Step 1: Insertar las dos secciones** (después de `</section>` de `#coordenadas`)

```html
    <section class="seccion seccion--tenue" id="interoperabilidad">
      <div class="env">
        <div class="seccion__cab revelar">
          <p class="super">Interoperabilidad</p>
          <h2 class="seccion__tit">Del caos a un idioma común</h2>
          <p class="seccion__intro">Si todos los sistemas estructuran sus datos con las mismas
            siete preguntas, un hospital y un banco pueden intercambiar información sin traducciones
            a medida. No hace falta un estándar propietario ni un acuerdo entre cada par de sistemas:
            las preguntas ya son comunes a todos.</p>
        </div>
        <ul class="beneficios revelar">
          <li>Sin middleware a medida entre cada par de sistemas.</li>
          <li>Sin traducciones ad hoc que se rompen con cada cambio.</li>
          <li>Sin pérdida de contexto al cruzar de una plataforma a otra.</li>
        </ul>
      </div>
    </section>

    <section class="seccion" id="ia">
      <div class="env">
        <div class="seccion__cab revelar">
          <p class="super">IA y modelos de lenguaje</p>
          <h2 class="seccion__tit">El puente con los modelos de lenguaje</h2>
          <p class="seccion__intro">Los modelos de lenguaje ya razonan con preguntas. Estructurar
            los datos así acorta la distancia entre lo que decimos y lo que la máquina procesa.</p>
        </div>
        <div class="rejilla revelar" style="--min:15rem">
          <div class="tarjeta">
            <h3 class="tarjeta__tit">Unidades de significado</h3>
            <p class="tarjeta__txt">Los modelos tratan las preguntas como unidades de sentido; el modelo las hace explícitas.</p>
          </div>
          <div class="tarjeta">
            <h3 class="tarjeta__tit">Datos que un modelo consume</h3>
            <p class="tarjeta__txt">Un hecho estructurado en siete ejes se lee sin preprocesarlo aparte.</p>
          </div>
          <div class="tarjeta">
            <h3 class="tarjeta__tit">Puente humano-máquina</h3>
            <p class="tarjeta__txt">El lexicon traduce el lenguaje del usuario a hechos, y a la inversa.</p>
          </div>
        </div>
        <p class="revelar" style="margin-top:1.4rem"><a href="26-llms.html">WQuestions y los LLM →</a></p>
      </div>
    </section>
```

- [ ] **Step 2: Verificar**

```bash
cd libro/manuscrito2
grep -q 'id="interoperabilidad"' index.html && grep -q 'id="ia"' index.html && echo "secciones OK"
grep -q '26-llms.html' index.html && echo "enlace LLM OK"
python3 -c "from html.parser import HTMLParser as H; H().feed(open('index.html',encoding='utf-8').read()); print('html-parse OK')"
```
Expected: `secciones OK`, `enlace LLM OK`, `html-parse OK`.

- [ ] **Step 3: Commit**

```bash
cd /Users/joseabanto/WQuestions
git add libro/manuscrito2/index.html
git commit -m "feat(landing): secciones interoperabilidad e IA/LLMs

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Secciones «Casos de uso» (enlazadas) + «Del concepto al código»

**Files:**
- Modify: `libro/manuscrito2/index.html` (insertar 2 `<section>` tras `#ia`)

**Interfaces:**
- Consumes: `.seccion`, `.rejilla`, `a.caso`, `.tarjeta`, `.cta-fila`, `.btn` (Tarea 1).

- [ ] **Step 1: Insertar las dos secciones**

```html
    <section class="seccion seccion--tenue" id="casos">
      <div class="env">
        <div class="seccion__cab revelar">
          <p class="super">Casos de uso</p>
          <h2 class="seccion__tit">El mismo modelo en cualquier dominio</h2>
          <p class="seccion__intro">La Parte V del libro construye sistemas reales con esta gramática.
            Cada tarjeta lleva al capítulo donde se desarrolla.</p>
        </div>
        <div class="rejilla revelar" style="--min:16rem">
          <a class="caso" href="18-clinica.html">
            <h3 class="caso__tit">Una historia clínica</h3>
            <p class="caso__txt">Consulta, historia longitudinal, hospitalización y farmacia interna.</p>
          </a>
          <a class="caso" href="19-banco.html">
            <h3 class="caso__tit">El dominio más exigente: un banco</h3>
            <p class="caso__txt">Donde la elegancia se vuelve exigencia regulatoria.</p>
          </a>
          <a class="caso" href="23-minera.html">
            <h3 class="caso__tit">Una operación minera</h3>
            <p class="caso__txt">Cadenas causales, sensores, comisionamiento y mantenimiento.</p>
          </a>
          <a class="caso" href="22-municipalidad.html">
            <h3 class="caso__tit">Una municipalidad</h3>
            <p class="caso__txt">Trámites de punta a punta y el principio «una sola vez».</p>
          </a>
          <a class="caso" href="21-universidad.html">
            <h3 class="caso__tit">Una universidad</h3>
            <p class="caso__txt">Prerrequisitos como grafo dirigido y planes de estudio.</p>
          </a>
          <a class="caso" href="16-spa.html">
            <h3 class="caso__tit">Un sistema de ventas</h3>
            <p class="caso__txt">Comercio minorista con impuestos, comprobantes y multi-divisa.</p>
          </a>
        </div>
        <p class="revelar" style="margin-top:1.4rem"><a href="indice.html">…y más en la Parte V →</a></p>
      </div>
    </section>

    <section class="seccion" id="codigo">
      <div class="env">
        <div class="seccion__cab revelar">
          <p class="super">Del concepto al código</p>
          <h2 class="seccion__tit">No se queda en la teoría</h2>
          <p class="seccion__intro">El libro incluye implementaciones en Python y un prototipo
            ejecutable que construye estos sistemas desde el primer capítulo.</p>
        </div>
        <div class="cta-fila revelar">
          <a class="btn btn--solido" href="33-anexo-prototipo.html">Ver el prototipo</a>
          <a class="btn btn--borde" href="32-anexo-codigo.html">Explorar el código</a>
        </div>
      </div>
    </section>
```

- [ ] **Step 2: Verificar que todos los capítulos enlazados existen**

```bash
cd libro/manuscrito2
for f in 18-clinica.html 19-banco.html 23-minera.html 22-municipalidad.html 21-universidad.html 16-spa.html 32-anexo-codigo.html 33-anexo-prototipo.html; do test -f "$f" && echo "ok $f" || echo "FALTA $f"; done
grep -c 'class="caso"' index.html   # espera: 6
```
Expected: ocho `ok ...` (ninguna `FALTA`) y `6`.

- [ ] **Step 3: Commit**

```bash
cd /Users/joseabanto/WQuestions
git add libro/manuscrito2/index.html
git commit -m "feat(landing): casos de uso enlazados a capítulos y sección de código

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Sección «El autor» + CTA final

**Files:**
- Modify: `libro/manuscrito2/index.html` (insertar tras `#codigo`, antes de `</main>`)
- Read (para la bio): `libro/manuscrito2/34-el-autor.html`

**Interfaces:**
- Consumes: `.seccion`, `.autor-bloque`, `.cta-final`, `.cta-fila`, `.btn` (Tarea 1).

- [ ] **Step 1: Leer la bio del autor para tomar 2–3 frases fieles**

Run: abrir `34-el-autor.html` y extraer una bio breve (2–3 frases) en la voz del libro. Si el capítulo trae una descripción, resúmela; no inventes credenciales.

- [ ] **Step 2: Insertar las dos secciones** (usa la bio del paso 1 en el `<p>` marcado)

```html
    <section class="seccion seccion--tenue" id="autor">
      <div class="env">
        <div class="autor-bloque revelar">
          <div>
            <p class="super">El autor</p>
            <h2 class="seccion__tit">José Abanto Marín</h2>
            <!-- BIO: 2–3 frases tomadas de 34-el-autor.html, voz del libro -->
            <p class="seccion__intro">José Abanto Marín integra lingüística, datos e inteligencia
              artificial en un mismo marco. Con WQuestions propone una arquitectura verificable y
              aplicable para que los sistemas dejen de hablar idiomas distintos.</p>
            <p style="margin-top:1rem"><a href="34-el-autor.html">Sobre el autor →</a></p>
          </div>
        </div>
      </div>
    </section>

    <section class="cta-final" id="empezar">
      <div class="env">
        <h2 class="revelar">Construye sistemas que hablen el mismo idioma</h2>
        <div class="cta-fila revelar">
          <a class="btn btn--solido" href="indice.html">Leer el libro</a>
          <a class="btn btn--borde" href="00-introduccion.html">Empezar por la introducción</a>
        </div>
      </div>
    </section>
```

- [ ] **Step 3: Verificar**

```bash
cd libro/manuscrito2
for f in 34-el-autor.html 00-introduccion.html indice.html; do test -f "$f" && echo "ok $f" || echo "FALTA $f"; done
grep -q 'id="autor"' index.html && grep -q 'id="empezar"' index.html && echo "secciones OK"
python3 -c "from html.parser import HTMLParser as H; H().feed(open('index.html',encoding='utf-8').read()); print('html-parse OK')"
```
Expected: tres `ok ...`, `secciones OK`, `html-parse OK`.

- [ ] **Step 4: Commit**

```bash
cd /Users/joseabanto/WQuestions
git add libro/manuscrito2/index.html
git commit -m "feat(landing): sección del autor y CTA final

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Pasada de tono + verificación integral

**Files:**
- Modify: `libro/manuscrito2/index.html` (solo copy, si la pasada de tono lo pide)

**Interfaces:**
- Consumes: la landing completa (Tareas 1–5).

- [ ] **Step 1: Pasada de tono con la skill `humanizalo`** sobre todo el copy visible de `index.html`. Objetivo: sin muletillas de IA, sin auto-declarar rigor/honestidad, español neutro (tuteo neutro). Aplica los cambios de texto que haga falta (sin tocar estructura ni clases).

- [ ] **Step 2: Verificación de enlaces — todos los `href` internos resuelven a un archivo existente**

```bash
cd libro/manuscrito2
python3 - <<'PY'
import re,os
html=open('index.html',encoding='utf-8').read()
hrefs=re.findall(r'href="([^"#]+)"',html)
faltan=[h for h in hrefs if not h.startswith(('http','mailto:')) and not os.path.exists(h.split('#')[0])]
print("Enlaces rotos:",faltan if faltan else "ninguno")
PY
```
Expected: `Enlaces rotos: ninguno`.

- [ ] **Step 3: Verificación de estructura — conteos esperados y parse final**

```bash
cd libro/manuscrito2
echo "eje-card: $(grep -c 'class="eje-card"' index.html) (esperado 7)"
echo "caso:     $(grep -c 'class=\"caso\"' index.html) (esperado 6)"
echo "secciones:$(grep -c '<section' index.html) (esperado 8: heroe + 7)"
python3 -c "from html.parser import HTMLParser as H; H().feed(open('index.html',encoding='utf-8').read()); print('html-parse OK')"
```
Expected: `eje-card: 7`, `caso: 6`, `secciones: 8`, `html-parse OK`.

- [ ] **Step 4: (Verificación visual del usuario)** Abrir `index.html`: revisar en móvil (DevTools ~375px) que no hay scroll horizontal y los grids colapsan a 1 columna; alternar tema claro/oscuro; recorrer que cada CTA y cada tarjeta de caso abre su destino; comprobar contraste legible en ambos temas.

- [ ] **Step 5: Commit**

```bash
cd /Users/joseabanto/WQuestions
git add libro/manuscrito2/index.html
git commit -m "polish(landing): pasada de tono y verificación integral

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review (autor del plan)

**Cobertura del spec:**
- Renombrado índice → `indice.html`: Tarea 1. ✅
- Nueva landing `index.html` + `landing.css` reusando tokens y tema: Tarea 1. ✅
- Reuso de `interacciones.js` (toggle + revelar): Tarea 1 (head script + `<script>`). ✅
- Copiar `portada.png` a `assets/img/`: Tarea 1. ✅
- Secciones 1–12 del spec: header/héroe/pie (T1), problema/solución/7 coordenadas (T2), interoperabilidad/IA (T3), casos/código (T4), autor/CTA (T5). ✅
- 7 tarjetas con color de eje: Tarea 2. ✅
- Casos de uso enlazados a capítulos reales: Tarea 4 (verifica existencia). ✅
- Copy en voz del libro, sin muletillas IA: copy en T2–T5 + pasada `humanizalo` en T6. ✅
- No editar capítulos ni `estilo.css`: respetado (solo se toca `index.html`, `indice.html` renombrado, `landing.css` nuevo). ✅

**Escaneo de placeholders:** la bio del autor (T5) se marca como «tomar de 34-el-autor.html» con un texto por defecto verificable; no es un TODO abierto. Sin otros placeholders.

**Consistencia de tipos/clases:** el vocabulario de clases se define en T1 y se consume idéntico en T2–T5 (`.seccion`, `.eje-card` + `--c`, `.caso`, `.tarjeta`, `.beneficios`, `.btn--solido/--borde`). Coherente.
