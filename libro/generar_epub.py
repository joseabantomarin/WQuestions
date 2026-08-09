#!/usr/bin/env python3
"""Genera el EPUB 3 del libro WQuestions desde la edición HTML canónica (manuscrito2/).

Mismo origen y mismo orden que generar_pdf_html.py: toma el contenido <main> de
cada página, lo convierte a XHTML bien formado y lo empaqueta como un capítulo
del EPUB. Reutiliza el CSS del sitio (con las tipografías incrustadas) y le
quita lo que solo tiene sentido en pantalla: el audio, el JavaScript, la barra
de progreso, el cajón del índice y los botones de copiar.

Orden: portada → index.html → 00..35 → referencias.html → anexo-reglas.html.

Uso: python3 libro/generar_epub.py
Salida: libro/manuscrito2/WQuestions.epub
"""

import os
import re
import sys
import zipfile
import subprocess
import xml.etree.ElementTree as ET

LIBRO_DIR = os.path.dirname(os.path.abspath(__file__))
M2 = os.path.join(LIBRO_DIR, "manuscrito2")
ASSETS = os.path.join(M2, "assets")
OUT_EPUB = os.path.join(M2, "WQuestions.epub")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

TITULO = "WQuestions: las preguntas como coordenadas"
AUTOR = "José Abanto Marín"
IDIOMA = "es"
# Identificador estable: no cambia entre regeneraciones, para que los lectores
# reconozcan el libro como el mismo y no lo dupliquen en la biblioteca.
UID = "urn:uuid:6f2a1c94-8b3d-4e57-9a20-wquestions0001"

MAIN_RE = re.compile(r"<main\b[^>]*>(.*?)</main>", re.DOTALL | re.IGNORECASE)
REDIRECT_RE = re.compile(r'http-equiv=["\']refresh', re.IGNORECASE)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.DOTALL | re.IGNORECASE)
PARTE_RE = re.compile(r'<p class="parte">(.*?)</p>', re.DOTALL | re.IGNORECASE)

# Elementos vacíos de HTML: en XHTML tienen que cerrarse solos. Los de SVG no
# entran aquí: Chrome ya los devuelve emparejados (<line …></line>), y forzar
# el autocierre dejaría huérfana la etiqueta de cierre.
VACIOS = ("br", "img", "hr", "meta", "link", "input", "col", "area", "source",
          "track", "wbr", "embed")


# --------------------------------------------------------------------------
# selección y orden de las páginas (idéntico al builder del PDF)
# --------------------------------------------------------------------------

def es_stub(path):
    """Los stubs de redirección comparten prefijo numérico con capítulos reales
    (28-prueba-reflexiva.html apunta al 29). No son páginas del libro."""
    with open(path, encoding="utf-8") as f:
        return bool(REDIRECT_RE.search(f.read(2048)))


def ordered_files():
    # index.html (la portada del sitio, con el resumen de capítulos) no viaja:
    # el EPUB abre con su cubierta, sigue con el índice y entra directo a la
    # introducción.
    files = []
    for i in range(0, 36):
        n = f"{i:02d}"
        files += sorted(f for f in os.listdir(M2)
                        if f.startswith(n + "-") and f.endswith(".html"))
    files += ["referencias.html", "anexo-reglas.html"]
    return [f for f in files
            if os.path.isfile(os.path.join(M2, f))
            and not es_stub(os.path.join(M2, f))]


# --------------------------------------------------------------------------
# limpieza del contenido y conversión a XHTML
# --------------------------------------------------------------------------

def render_dom(path):
    """Devuelve el HTML de la página después de ejecutar su JavaScript.

    Doce figuras del libro son gráficos que interacciones.js dibuja en SVG a
    partir de un JSON incrustado. Sin este paso llegarían vacías al EPUB, que
    no ejecuta scripts. Usamos el mismo Chrome que imprime el PDF, así que las
    dos ediciones muestran exactamente la misma figura."""
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
           "--no-default-browser-check", "--run-all-compositor-stages-before-draw",
           "--virtual-time-budget=15000", "--dump-dom", f"file://{path}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not r.stdout.strip():
        sys.stderr.write((r.stderr or "")[-800:] + "\n")
        sys.exit(f"Chrome no pudo renderizar {os.path.basename(path)}.")
    return r.stdout


def limpiar(bloque, base, sacados):
    """Quita lo que solo existe para la pantalla: audio, scripts, navegación,
    botones de copiar y la barra de progreso."""
    fuera = [
        r"<script\b.*?</script>",
        r"<audio\b.*?</audio>",
        r"<audio\b[^>]*/>",
        r'<div class="audios".*?</div>\s*',
        r'<button[^>]*class="copiar"[^>]*>.*?</button>',
        r'<nav class="nav-cap".*?</nav>',
        r'<div class="barra-progreso".*?</div>',
    ]
    for pat in fuera:
        bloque = re.sub(pat, "", bloque, flags=re.DOTALL | re.IGNORECASE)
    # las rutas de imagen bajan un nivel dentro del EPUB
    bloque = bloque.replace('src="assets/img/', 'src="img/')
    # los enlaces entre capítulos apuntan a los .xhtml del paquete
    bloque = re.sub(r'href="([0-9]{2}-[a-z0-9-]+)\.html', r'href="\1.xhtml', bloque)
    # el índice del sitio no viaja como página: el EPUB trae el suyo (nav.xhtml)
    bloque = re.sub(r'href="indice\.html[^"]*"', 'href="nav.xhtml"', bloque)
    bloque = re.sub(r'href="(index|referencias|anexo-reglas)\.html',
                    r'href="\1.xhtml', bloque)
    return partir_lineas_de_codigo(externalizar_svg(bloque, base, sacados))


# Un <svg …> puede llevar «>» dentro de un atributo (los aria-label describen
# notaciones como «M(O->O)»), así que al buscar el fin de la etiqueta hay que
# saltarse lo que va entre comillas.
SVG_RE = re.compile(r"""<svg\b((?:[^>"']|"[^"]*"|'[^']*')*)>(.*?)</svg>""",
                    re.DOTALL | re.IGNORECASE)
VAR_RE = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*?)\s*)?\)")


def _paleta():
    """Los valores del bloque :root del sitio, con las variables ya resueltas.

    Un SVG suelto no ve la hoja de estilo del libro: hay que dejarle los
    colores escritos."""
    with open(os.path.join(ASSETS, "estilo.css"), encoding="utf-8") as f:
        raiz = re.search(r":root\s*\{(.*?)\n\}", f.read(), re.S).group(1)
    tabla = {k: v.strip() for k, v in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", raiz)}
    for _ in range(4):    # una variable puede citar a otra
        tabla = {k: resolver_vars(v, tabla) for k, v in tabla.items()}
    return tabla


def resolver_vars(texto, tabla):
    def una(m):
        nombre, respaldo = m.group(1), m.group(2)
        valor = tabla.get(nombre, respaldo if respaldo is not None else "currentColor")
        # Casi siempre se sustituye dentro de un atributo entrecomillado, y las
        # familias tipográficas traen comillas dobles («Helvetica Neue») que
        # partirían el atributo en dos. CSS acepta igual las simples.
        return valor.replace('"', "'")
    return VAR_RE.sub(una, texto)


PALETA = None


def externalizar_svg(bloque, base, sacados):
    """Saca cada SVG a su propio archivo y lo deja como <img>.

    En línea, el dibujo depende de que el lector implemente SVG dentro del
    XHTML. Los que se limitan a maquetar texto —los mismos que ignoran el
    `white-space` de los bloques de código— descartan la etiqueta y sueltan
    como prosa los textos que lleva dentro: la figura desaparece y en su lugar
    quedan sus rótulos. Como imagen enlazada no hay nada que implementar; si el
    lector muestra la portada, muestra la figura.

    Dos cosas hay que llevarse al archivo, porque afuera ya no las alcanza:
    los `var(--…)` de cada fill y stroke, y la única regla del sitio que toca
    el interior de un SVG (`.svg-eje text`)."""
    global PALETA
    if PALETA is None:
        PALETA = _paleta()

    def saca(m):
        attrs, dentro = m.group(1), m.group(2)
        vb = re.search(r'viewBox="\s*([-\d.]+\s+[-\d.]+\s+[\d.]+\s+[\d.]+)\s*"', attrs)
        if not vb:
            return m.group(0)                     # sin viewBox no hay proporción que salvar
        _, _, w, h = vb.group(1).split()
        wn, hn = (x[:-2] if x.endswith(".0") else x for x in (w, h))

        etq = re.search(r'aria-label="([^"]*)"', attrs)
        alt = etq.group(1) if etq else ""
        # `.svg-eje text { font-family: var(--sans) }` pisaba los font-family
        # de dentro; se replica igual para no cambiar el dibujo.
        clase = re.search(r'class="([^"]*)"', attrs)
        estilo = ""
        if clase and "svg-eje" in clase.group(1):
            estilo = f"<style>text{{font-family:{PALETA.get('--sans','sans-serif')}}}</style>"

        nombre = f"fig-{base}-{len(sacados) + 1:02d}.svg"
        doc = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb.group(1)}" '
               f'width="{wn}" height="{hn}" preserveAspectRatio="xMidYMid meet">'
               f'{estilo}{resolver_vars(dentro, PALETA)}</svg>'
               ).replace("&nbsp;", "&#160;")
        # Un SVG suelto es un XML: si no parsea, el lector no dibuja nada y no
        # avisa. Vale más romper aquí la generación.
        try:
            ET.fromstring(doc)
        except ET.ParseError as e:
            sys.exit(f"SVG mal formado en {nombre}: {e}")
        sacados.append((nombre, doc.encode("utf-8")))

        return (f'<img src="img/{nombre}" alt="{escapar(alt)}" '
                f'width="{wn}" height="{hn}" class="figura-svg"/>')

    return SVG_RE.sub(saca, bloque)


MAX_COLS = 56          # caracteres por línea de código que caben en una página
PRE_RE = re.compile(r"(<pre\b[^>]*>)(.*?)(</pre>)", re.DOTALL | re.IGNORECASE)
TROZO_RE = re.compile(r"(<[^>]+>|&[#a-zA-Z0-9]+;|[^<&]+)")


def _visible(trozo):
    """Longitud en pantalla de un trozo: las etiquetas no ocupan, las entidades
    ocupan un carácter."""
    if trozo.startswith("<"):
        return 0
    if trozo.startswith("&"):
        return 1
    return len(trozo)


def partir_lineas_de_codigo(bloque, ancho=MAX_COLS):
    """Parte las líneas de código largas en el propio archivo.

    El CSS `white-space: pre-wrap` debería bastar, pero varios lectores
    imponen su propia hoja de estilo y vuelven a `pre`, de modo que la línea
    se corta por el borde y se pierde la mitad derecha. Partiéndolas aquí, el
    resultado ya no depende de lo que decida el lector.

    Se corta por el último espacio antes del límite, y la continuación se
    sangra dos espacios más que la línea original para que se vea que sigue.
    No se pierde ni un carácter; solo se pierde la alineación en columnas."""
    def una(m):
        apertura, cuerpo, cierre = m.group(1), m.group(2), m.group(3)
        salida = []
        for linea in cuerpo.split("\n"):
            trozos = TROZO_RE.findall(linea)
            if sum(_visible(t) for t in trozos) <= ancho:
                salida.append(linea)
                continue

            # Antes de partir, comprimir. El libro alinea el código en columnas
            # con tiradas largas de espacios, y esas tiradas se comen el ancho
            # disponible. Reduciéndolas a dos espacios, la mayoría de las
            # líneas entran enteras: se pierde la alineación, pero se gana no
            # tener que partirlas.
            apretados, primer_texto = [], True
            for t in trozos:
                if t.startswith("<") or t.startswith("&"):
                    apretados.append(t)
                    continue
                if primer_texto:                       # respeta la sangría
                    sang = len(t) - len(t.lstrip(" "))
                    t = t[:sang] + re.sub(r"   +", "  ", t[sang:])
                    primer_texto = False
                else:
                    t = re.sub(r"   +", "  ", t)
                apretados.append(t)
            if sum(_visible(t) for t in apretados) <= ancho:
                salida.append("".join(apretados))
                continue
            trozos = apretados
            texto_plano = "".join("" if t.startswith("<") else
                                  (" " if t.startswith("&") else t) for t in trozos)
            sangria = len(texto_plano) - len(texto_plano.lstrip(" "))
            cont = " " * min(sangria + 2, ancho // 3)

            actual, col = [], 0
            base = 0            # ancho ya ocupado por la sangría de continuación

            def cerrar():
                """Vuelca la línea en curso y abre una de continuación."""
                nonlocal actual, col, base
                salida.append("".join(actual).rstrip())
                actual, col, base = [cont], len(cont), len(cont)

            for t in trozos:
                if t.startswith("<"):        # las etiquetas no ocupan ancho
                    actual.append(t)
                    continue
                v = _visible(t)
                if col + v <= ancho:
                    actual.append(t)
                    col += v
                    continue

                resto = t
                while resto and col + _visible(resto) > ancho:
                    hueco = ancho - col
                    corte = resto.rfind(" ", 0, hueco + 1) if hueco > 0 else -1
                    if corte <= 0:
                        # No hay dónde cortar por espacio. Si la línea ya lleva
                        # algo, se cierra y se reintenta desde el margen; si ya
                        # está vacía, no queda más que cortar a lo bruto (y así
                        # el bucle siempre avanza).
                        if col > base:
                            cerrar()
                            continue
                        corte = max(1, ancho - col)
                    actual.append(resto[:corte])
                    cerrar()
                    resto = resto[corte:].lstrip(" ")
                if resto:
                    actual.append(resto)
                    col += _visible(resto)

            if actual:
                salida.append("".join(actual).rstrip())
        return apertura + "\n".join(salida) + cierre

    return PRE_RE.sub(una, bloque)


def a_xhtml(bloque):
    """Convierte el HTML5 del manuscrito en XHTML bien formado."""
    # entidades con nombre que XML no conoce
    bloque = bloque.replace("&nbsp;", "&#160;")
    # elementos vacíos sin cerrar
    for tag in VACIOS:
        bloque = re.sub(
            rf"<{tag}\b([^>]*?)\s*/?>",
            lambda m: f"<{tag}{m.group(1).rstrip()}/>",
            bloque, flags=re.IGNORECASE)
    # atributos sin valor: en XHTML todos necesitan uno (data-chart -> data-chart="")
    ATTR = re.compile(r"""\s*([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*(=\s*("[^"]*"|'[^']*'|[^\s/>]+))?""")

    def fija_attrs(m):
        tag, attrs, cierre = m.group(1), m.group(2), m.group(3)
        partes, pos = [], 0
        while pos < len(attrs):
            a = ATTR.match(attrs, pos)
            if not a or a.end() == pos:
                break
            nombre, valor = a.group(1), a.group(3)
            if valor is None:
                valor = f'"{nombre}"'          # atributo booleano
            elif not valor.startswith(("'", '"')):
                valor = f'"{valor}"'           # valor sin comillas
            partes.append(f'{nombre}={valor}')
            pos = a.end()
        # el resto es basura o el «/» de cierre; hay que conservarlo
        if attrs[pos:].strip().endswith("/") or cierre == "/>":
            cierre = "/>"
        return f"<{tag}{(' ' + ' '.join(partes)) if partes else ''}{cierre}"

    bloque = re.sub(r"""<([a-zA-Z][-a-zA-Z0-9]*)((?:[^<>"']|"[^"]*"|'[^']*')*)(/?>)""",
                    fija_attrs, bloque)
    return bloque


def envolver(cuerpo, titulo):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{IDIOMA}" xml:lang="{IDIOMA}">
<head>
  <meta charset="utf-8"/>
  <title>{escapar(titulo)}</title>
  <link rel="stylesheet" type="text/css" href="estilo.css"/>
</head>
<body class="libro">
{cuerpo}
</body>
</html>
"""


def escapar(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def texto_plano(html):
    t = re.sub(r"<[^>]+>", "", html)
    t = t.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", t).strip()


def titulo_de(bloque, fallback):
    m = H1_RE.search(bloque)
    return texto_plano(m.group(1)) if m else fallback


# --------------------------------------------------------------------------
# hoja de estilo
# --------------------------------------------------------------------------

EPUB_CSS = """
/* --- ajustes del build EPUB ------------------------------------------- */
/* Fuera todo lo que dependía de JavaScript o de una ventana de navegador. */
.cabecera, .barra-progreso, .drawer-indice, .velo, .nav-cap, .audios,
.copiar, .boton-tema, .marca-agua, #ir-arriba { display: none !important; }

html, body { margin: 0; padding: 0; }
body.libro { background: var(--papel); color: var(--tinta); }

/* Cuerpo un 10% más pequeño. Va en porcentaje sobre la raíz, no en píxeles:
   como todo el libro está medido en rem, baja el conjunto de forma pareja y
   sigue respetando el tamaño que el lector tenga configurado. */
html { font-size: 90%; }
/* Colchón lateral mínimo: casi todos los lectores ponen su propio
   margen, pero si alguno no lo hace el texto no queda pegado al borde. */
body.libro { padding: 0 .5rem; }

/* El lector paginará: nada puede quedar fijo ni pegado al viewport. Se quitan
   solo fixed y sticky; el position:absolute de la comilla volada y del número
   de referencia es tipografía legítima y se conserva. */
.barra-progreso, .cabecera, .drawer-indice, .velo, .tip-flotante {
  position: static !important; }
.capitulo, .contenido, main, article { max-width: none; width: auto;
  margin-left: 0; margin-right: 0; padding-left: 0; padding-right: 0; }

/* Sin JS, .revelar ya está visible; lo dejamos explícito por si acaso. */
.revelar { opacity: 1 !important; transform: none !important; }

/* --- 1. Nada flota ni sale del cauce del texto ------------------------- */
/* En la web hay una columna de notas a la derecha (--gutter: 17rem) y estos
   bloques se sacan ahí con un margen negativo. El EPUB no tiene esa columna:
   el bloque aterrizaba encima del texto. Aquí van todos en el flujo. */
.nota-margen, .figura--margen, .retrato-autor, .figura--ancha {
  float: none !important; clear: both !important;
  width: auto !important; max-width: 100% !important;
  margin-left: 0 !important; margin-right: 0 !important;
}
.nota-margen, .figura--margen {
  margin-top: 1.2rem !important; margin-bottom: 1.4rem !important;
  background: var(--papel-2); border: 1px solid var(--linea);
  border-radius: var(--radio); padding: .8rem 1rem;
}
.retrato-autor { margin: 1rem auto 1.4rem !important; width: min(230px, 60%) !important; }

/* La capitular flotada es la causa clásica de letras encimadas en un lector
   paginado. Se conserva la inicial destacada, pero dentro de la línea. */
.contenido > .entrada:first-of-type::first-letter,
p.capitular::first-letter {
  float: none !important; font-size: 1.9em !important; line-height: 1 !important;
  padding: 0 !important; vertical-align: baseline;
}

/* Comilla volada y número de referencia: fuera del posicionamiento absoluto. */
.cita-destacada::before { display: none !important; }
.ref-item { padding-left: 0 !important; }
.ref-item .ref-n { position: static !important; display: inline;
  width: auto !important; margin-right: .4rem; }

/* --- 2. Contenido ancho: que se encoja, nunca que desborde -------------- */
img, figure { max-width: 100%; height: auto; }
/* Las figuras viajan como imagen enlazada, con width/height reales para que el
   lector reserve el hueco y respete la proporción aunque aún no la haya
   descargado. Nunca más anchas que la caja de texto. */
img.figura-svg { display: block; margin: 0 auto;
                 max-width: 100%; height: auto; }
svg { max-width: 100%; height: auto; }

/* El código es el caso grave. En la web, .bloque-codigo recorta (overflow
   hidden) y el <pre> de dentro ofrece barra horizontal (overflow-x auto). Un
   lector paginado no tiene desplazamiento lateral: lo que sobra se corta o se
   mete en la página siguiente encima del texto. Aquí las líneas se parten.
   Hace falta !important y el selector completo: `.bloque-codigo pre` gana por
   especificidad a un `pre` a secas. */
.bloque-codigo { overflow: visible !important; }
.bloque-codigo pre, pre {
  overflow-x: visible !important; overflow: visible !important;
  white-space: pre-wrap !important;
  word-break: break-word !important; overflow-wrap: anywhere !important;
  font-size: .72rem !important; line-height: 1.5 !important;
}
/* Las líneas más largas del libro llegan a 113 caracteres. Con el cuerpo
   reducido caben unos 58 por línea, así que las demás se parten en dos: se
   pierde la alineación en columnas, pero no se pierde ni un carácter. */

/* Tablas y rejillas: a una sola columna, que en una página estrecha dos no
   caben sin desbordar. */
table { width: 100% !important; table-layout: fixed; word-wrap: break-word;
        font-size: .82em; }
.rejilla-2, .rejilla-3 { grid-template-columns: 1fr !important; display: block !important; }
.rejilla-2 > *, .rejilla-3 > * { margin-bottom: 1rem; }
.columnas { column-count: 1 !important; }

/* --- 3. Nada se parte por la mitad entre dos páginas -------------------- */
/* Un bloque partido en el corte deja media caja negra vacía en una página y
   el texto en la otra. Con esto el lector empuja el bloque entero a la página
   siguiente. Si el bloque es más alto que una página el lector ignora la
   regla y lo parte igual, que es justo el respaldo que queremos. */
figure, .figura, .lienzo, .bloque-codigo, .caja, .triple, .cita-destacada,
.nota-margen, table, tr, .rejilla-2, .rejilla-3 {
  break-inside: avoid; page-break-inside: avoid;
}
figcaption { break-before: avoid; page-break-before: avoid; }

/* --- 3 bis. Código en claro: nada de texto claro sobre fondo oscuro ----- */
/* En pantalla el código va en tema oscuro (fondo #221f1a, texto #ece3d1).
   Muchos lectores de EPUB imponen su propio color de texto para asegurar la
   legibilidad, pero no tocan el fondo: el resultado es texto oscuro sobre
   fondo oscuro, es decir, una caja negra vacía. La única solución que aguanta
   cualquier tema del lector es invertirlo: fondo claro y texto oscuro, como
   ya hace la edición impresa. Si el lector fuerza su color, el código sigue
   leyéndose. */
.bloque-codigo { border: 1px solid #ddd4c0 !important; box-shadow: none !important; }
.bloque-codigo pre, pre {
  background: #f4f1ea !important; background-color: #f4f1ea !important;
  color: #1f1c17 !important;
}
.bloque-codigo .barra {
  background: #e7e0d2 !important; background-color: #e7e0d2 !important;
  color: #5f574a !important; border-bottom: 1px solid #ddd4c0 !important;
}
.bloque-codigo .barra .lenguaje { color: #8a5a0b !important; }
/* Tonos oscuros del resaltado: conservan el código de color y todos superan
   la relación de contraste 4,5:1 sobre el fondo claro. */
.bloque-codigo .tk-coment, .tk-coment { color: #6b6252 !important; }
.bloque-codigo .tk-cadena, .tk-cadena { color: #8a5a0b !important; }
.bloque-codigo .tk-clave,  .tk-clave  { color: #a3384a !important; }
.bloque-codigo .tk-num,    .tk-num    { color: #1c5f80 !important; }
.bloque-codigo .tk-func,   .tk-func   { color: #20705a !important; }
.bloque-codigo .tk-puntu,  .tk-puntu  { color: #5f574a !important; }

/* El rótulo D1..D9 era texto blanco sobre color: mismo riesgo. Va en negrita
   y con el color en la letra, no en el fondo. */
.caja--decision .codigo-d, .codigo-d {
  background: none !important; background-color: transparent !important;
  color: #2161a8 !important; padding: 0 !important; font-weight: 700 !important;
}

/* --- 4. La notación de eje, en negrita y sin cuadradito ---------------- */
/* En pantalla, Q O L T N K M van en un recuadro de color. En el EPUB eso se
   ve mal y muchos lectores fuerzan sus propios colores, así que la letra va
   simplemente en negrita, dentro de la línea. */
.eje, .eje--q, .eje--o, .eje--l, .eje--t, .eje--n, .eje--k, .eje--m {
  display: inline !important; background: none !important;
  background-color: transparent !important; color: inherit !important;
  width: auto !important; height: auto !important;
  min-width: 0 !important; padding: 0 !important; margin: 0 !important;
  border: 0 !important; border-radius: 0 !important; box-shadow: none !important;
  font-family: inherit !important; font-size: inherit !important;
  font-weight: 700 !important; line-height: inherit !important;
  vertical-align: baseline !important;
}
.eje-rotulo { display: inline !important; }
pre { white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word;
      font-size: .78em; line-height: 1.45; }
table { width: 100%; table-layout: fixed; word-wrap: break-word; font-size: .85em; }
.triple { flex-wrap: wrap; }

/* Cada capítulo abre en página nueva (es un archivo aparte, pero por si el
   lector concatena). */
.capitulo { page-break-before: always; break-before: page; }
.portada-cap { page-break-after: avoid; break-after: avoid; }
h1, h2, h3 { page-break-after: avoid; break-after: avoid; }

/* Portada del EPUB */
.epub-portada { margin: 0; padding: 0; text-align: center; page-break-after: always; }
.epub-portada img { max-width: 100%; max-height: 100%; }
"""


def construir_css():
    with open(os.path.join(ASSETS, "estilo.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(ASSETS, "fonts", "fonts.css"), encoding="utf-8") as f:
        fonts = f.read()
    # el @import se sustituye por el contenido, con las rutas ya reubicadas
    fonts = re.sub(r"url\(([^)]+\.woff2)\)", r"url(fonts/\1)", fonts)
    css = css.replace('@import "fonts/fonts.css";', fonts)
    return css + "\n" + EPUB_CSS


# --------------------------------------------------------------------------
# empaquetado
# --------------------------------------------------------------------------

CONTAINER = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""


def main():
    paginas = ordered_files()
    if not paginas:
        sys.exit("No se encontró ninguna página en manuscrito2/.")

    capitulos = []   # (nombre_xhtml, titulo, parte)
    recursos = []    # (ruta_en_epub, bytes, media-type)

    print(f"  Renderizando {len(paginas)} páginas con Chrome "
          f"(para que los gráficos JS lleguen como SVG)…")
    for n, name in enumerate(paginas, 1):
        sys.stdout.write(f"\r    {n}/{len(paginas)}  {name[:40]:<42}")
        sys.stdout.flush()
        html = render_dom(os.path.join(M2, name))
        m = MAIN_RE.search(html)
        bloque = m.group(1) if m else html

        base = os.path.splitext(name)[0]
        sacados = []                    # los SVG de este capítulo, ya como archivo
        bloque = a_xhtml(limpiar(bloque, base, sacados))
        for fn, datos in sacados:
            recursos.append((f"OEBPS/img/{fn}", datos, "image/svg+xml"))

        xhtml_name = base + ".xhtml"
        titulo = titulo_de(bloque, base)
        mp = PARTE_RE.search(bloque)
        parte = texto_plano(mp.group(1)) if mp else ""

        doc = envolver(bloque, titulo)
        # verificación: si esto no parsea, el EPUB estaría roto
        try:
            ET.fromstring(doc.split("<!DOCTYPE html>", 1)[1])
        except ET.ParseError as e:
            sys.exit(f"XHTML mal formado en {name}: {e}")

        recursos.append((f"OEBPS/{xhtml_name}", doc.encode("utf-8"),
                         "application/xhtml+xml"))
        capitulos.append((xhtml_name, titulo, parte))

    # portada
    portada_src = os.path.join(ASSETS, "img", "portada.png")
    with open(portada_src, "rb") as f:
        recursos.append(("OEBPS/img/portada.png", f.read(), "image/png"))
    cubierta = envolver(
        '<div class="epub-portada"><img src="img/portada.png" '
        f'alt="{escapar(TITULO)}"/></div>', TITULO)
    recursos.append(("OEBPS/cubierta.xhtml", cubierta.encode("utf-8"),
                     "application/xhtml+xml"))

    # foto del autor
    autor_img = os.path.join(ASSETS, "img", "el-autor.jpg")
    if os.path.isfile(autor_img):
        with open(autor_img, "rb") as f:
            recursos.append(("OEBPS/img/el-autor.jpg", f.read(), "image/jpeg"))

    # css y tipografías
    recursos.append(("OEBPS/estilo.css", construir_css().encode("utf-8"),
                     "text/css"))
    fdir = os.path.join(ASSETS, "fonts")
    for fn in sorted(os.listdir(fdir)):
        if fn.endswith(".woff2"):
            with open(os.path.join(fdir, fn), "rb") as f:
                recursos.append((f"OEBPS/fonts/{fn}", f.read(), "font/woff2"))

    # índice de navegación
    # Los capítulos que declaran parte se agrupan bajo ella; los que no
    # (portada, referencias, anexos sueltos) cuelgan del primer nivel.
    grupos = []
    for xhtml_name, titulo, parte in capitulos:
        clave = parte or None
        if grupos and clave is not None and grupos[-1][0] == clave:
            grupos[-1][1].append((xhtml_name, titulo))
        else:
            grupos.append((clave, [(xhtml_name, titulo)]))

    filas = []
    for parte, items in grupos:
        if parte is None:
            for href, t in items:
                filas.append(f'      <li><a href="{href}">{escapar(t)}</a></li>')
        else:
            filas.append(f'      <li><span>{escapar(parte)}</span>')
            filas.append('        <ol>')
            for href, t in items:
                filas.append(f'          <li><a href="{href}">{escapar(t)}</a></li>')
            filas.append('        </ol>')
            filas.append('      </li>')

    nav = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{IDIOMA}" xml:lang="{IDIOMA}">
<head><meta charset="utf-8"/><title>Índice</title>
<link rel="stylesheet" type="text/css" href="estilo.css"/></head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>Índice</h1>
    <ol>
{chr(10).join(filas)}
    </ol>
  </nav>
</body>
</html>
"""
    ET.fromstring(nav.split("<!DOCTYPE html>", 1)[1])
    recursos.append(("OEBPS/nav.xhtml", nav.encode("utf-8"),
                     "application/xhtml+xml"))

    # manifiesto
    items, spine = [], ['    <itemref idref="cubierta"/>']
    items.append('    <item id="cubierta" href="cubierta.xhtml" '
                 'media-type="application/xhtml+xml"/>')
    items.append('    <item id="nav" href="nav.xhtml" '
                 'media-type="application/xhtml+xml" properties="nav"/>')
    items.append('    <item id="portada-img" href="img/portada.png" '
                 'media-type="image/png" properties="cover-image"/>')
    items.append('    <item id="css" href="estilo.css" media-type="text/css"/>')
    spine.append('    <itemref idref="nav"/>')

    for i, (xhtml_name, _, _) in enumerate(capitulos):
        iid = f"c{i:02d}"
        items.append(f'    <item id="{iid}" href="{xhtml_name}" '
                     'media-type="application/xhtml+xml"/>')
        spine.append(f'    <itemref idref="{iid}"/>')

    for ruta, _, mt in recursos:
        rel = ruta[len("OEBPS/"):]
        if rel.startswith(("fonts/", "img/")) and rel != "img/portada.png":
            fid = re.sub(r"[^a-zA-Z0-9]", "_", rel)
            items.append(f'    <item id="{fid}" href="{rel}" media-type="{mt}"/>')

    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="pub-id" xml:lang="{IDIOMA}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="pub-id">{UID}</dc:identifier>
    <dc:title>{escapar(TITULO)}</dc:title>
    <dc:creator>{escapar(AUTOR)}</dc:creator>
    <dc:language>{IDIOMA}</dc:language>
    <dc:publisher>{escapar(AUTOR)}</dc:publisher>
    <dc:description>Un modelo de información que organiza cualquier dominio sobre siete preguntas: quién, qué, dónde, cuándo, cuánto, cuál y cómo.</dc:description>
    <meta property="dcterms:modified">{FECHA}</meta>
  </metadata>
  <manifest>
{chr(10).join(items)}
  </manifest>
  <spine>
{chr(10).join(spine)}
  </spine>
</package>
"""
    ET.fromstring(opf)
    recursos.append(("OEBPS/content.opf", opf.encode("utf-8"),
                     "application/oebps-package+xml"))
    recursos.append(("META-INF/container.xml", CONTAINER.encode("utf-8"), ""))

    # el zip: mimetype primero y sin comprimir, como exige la especificación
    if os.path.exists(OUT_EPUB):
        os.remove(OUT_EPUB)
    with zipfile.ZipFile(OUT_EPUB, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip",
                   compress_type=zipfile.ZIP_STORED)
        for ruta, datos, _ in recursos:
            z.writestr(ruta, datos)

    print(f"  Capítulos: {len(capitulos)}")
    print(f"  Recursos:  {len(recursos)} archivos empaquetados")
    print(f"  ✓ {OUT_EPUB}  ({os.path.getsize(OUT_EPUB)//1024} KB)")


# La fecha de modificación que exige EPUB 3; se toma del HTML más reciente
# para que dos corridas sobre el mismo manuscrito den el mismo archivo.
def _fecha():
    import datetime
    ts = max(os.path.getmtime(os.path.join(M2, f))
             for f in os.listdir(M2) if f.endswith(".html"))
    return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ")


FECHA = _fecha()


if __name__ == "__main__":
    main()
