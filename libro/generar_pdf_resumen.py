#!/usr/bin/env python3
"""Genera la edición RESUMEN del libro WQuestions desde manuscrito2/.

Misma fuente y mismo pipeline que generar_pdf_html.py, con tres podas:

  1. Se eliminan todos los bloques de código (.bloque-codigo: tripletas, Python,
     SQL, JSON). La prosa queda intacta aunque los mencione — es deliberado.
  2. Se eliminan los gráficos: las <figure> con sus diagramas SVG y sus pies, y
     los diagramas de tripleta en línea (.triple).
  3. Se omiten los dos anexos de código: 33-anexo-codigo y 34-anexo-prototipo.

Queda el libro en prosa: los 33 capítulos restantes —incluidos los casos de
dominio (spa, taxi, clínica, banco, ERP, universidad, municipalidad, minera,
yaku)—, las cajas, las tablas, las notas al margen y el anexo de reglas.

Uso: python3 libro/generar_pdf_resumen.py
Salida: libro/manuscrito2/WQuestions-resumen.pdf
"""

import os
import re
import base64
import subprocess
import sys
import zlib

LIBRO_DIR = os.path.dirname(os.path.abspath(__file__))
M2 = os.path.join(LIBRO_DIR, "manuscrito2")
OUT_PDF = os.path.join(M2, "WQuestions-resumen.pdf")
TMP_HTML = os.path.join(M2, ".pdf_resumen_build.html")  # en M2 para que assets resuelvan
PORTADA = os.path.join(LIBRO_DIR, "portada.png")
CSS_FILE = os.path.join(M2, "assets", "estilo.css")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Los anexos que sólo existen para mostrar código no tienen lugar en el resumen.
EXCLUIR = {"33-anexo-codigo.html", "34-anexo-prototipo.html"}

# PDF completo del que se copia el tamaño de letra (ver `zoom_de_la_edicion_completa`).
PDF_COMPLETO = os.path.join(M2, "WQuestions.pdf")
# Factor con el que Chrome escribe una página que NO desborda; si el documento
# es más ancho que el papel, Chrome encoge todo y este número baja.
ESCALA_SIN_ENCOGER = 3.125
CTM_RE = re.compile(rb"([\d.]+) 0 0 ([\d.]+) [\d.-]+ [\d.-]+ cm")

MAIN_RE = re.compile(r"<main\b[^>]*>(.*?)</main>", re.DOTALL | re.IGNORECASE)
AUDIO_RE = re.compile(r"<audio\b.*?</audio>|<audio\b[^>]*/>", re.DOTALL | re.IGNORECASE)
REDIRECT_RE = re.compile(r'http-equiv=["\']refresh', re.IGNORECASE)
FIGURA_RE = re.compile(r"<figure\b.*?</figure>", re.DOTALL | re.IGNORECASE)
DIV_RE = re.compile(r"<(/?)div\b", re.IGNORECASE)
TEXTO_RE = re.compile(r"<[^>]+>")


def es_stub(path):
    """Los stubs de redirección comparten prefijo numérico con capítulos reales
    (28-prueba-reflexiva.html apunta al 29). No son páginas del libro."""
    with open(path, encoding="utf-8") as f:
        return bool(REDIRECT_RE.search(f.read(2048)))


def ordered_files():
    files = ["index.html"]
    for i in range(0, 36):
        n = f"{i:02d}"
        files += sorted(f for f in os.listdir(M2)
                        if f.startswith(n + "-") and f.endswith(".html"))
    files += ["referencias.html", "anexo-reglas.html"]
    return [f for f in files
            if f not in EXCLUIR
            and os.path.isfile(os.path.join(M2, f))
            and not es_stub(os.path.join(M2, f))]


def fin_del_div(html, inicio):
    """Devuelve el índice justo después del </div> que cierra el <div> abierto
    en `inicio`, contando anidamiento."""
    profundidad = 0
    pos = inicio
    while True:
        m = DIV_RE.search(html, pos)
        if not m:
            return len(html)
        if m.group(1):
            profundidad -= 1
            if profundidad == 0:
                cierre = html.find(">", m.end())
                return len(html) if cierre < 0 else cierre + 1
        else:
            profundidad += 1
        pos = m.end()


def quitar_divs(html, marcador, minimo_texto=0):
    """Elimina cada <div> cuyo atributo class empiece por `marcador`.

    Con minimo_texto > 0 sólo se elimina si al div le queda menos texto visible
    que ese umbral — así se podan los contenedores que quedaron vacíos tras
    sacarles el código, sin tocar los que aún dicen algo."""
    out = []
    i = 0
    while True:
        j = html.find(marcador, i)
        if j < 0:
            out.append(html[i:])
            return "".join(out)
        fin = fin_del_div(html, j)
        bloque = html[j:fin]
        out.append(html[i:j])
        if minimo_texto and len(texto_visible(bloque)) >= minimo_texto:
            out.append(bloque)          # conserva: todavía tiene contenido
        i = fin


def zoom_de_la_edicion_completa():
    """Devuelve el zoom que iguala el tamaño de letra del resumen al del PDF completo.

    La edición completa contiene tablas más anchas que el papel, así que Chrome
    la encoge entera para que quepa. El resumen, sin figuras, ya no desborda y
    saldría a tamaño natural: la misma fuente daría dos libros con cuerpos de
    texto distintos. Se lee la escala del PDF completo recién generado y se
    reproduce, en vez de fijar un número que envejezca mal.
    """
    if not os.path.isfile(PDF_COMPLETO):
        print("  ⚠ no encuentro el PDF completo; el resumen sale a tamaño natural")
        return 1.0
    with open(PDF_COMPLETO, "rb") as f:
        datos = f.read()
    escalas = []
    for m in re.finditer(rb"stream\r?\n", datos):
        try:
            flujo = zlib.decompress(datos[m.end():datos.find(b"endstream", m.end())])
        except zlib.error:
            continue
        ctm = CTM_RE.search(flujo)
        if ctm and ctm.group(1) == ctm.group(2):
            escalas.append(float(ctm.group(1)))
        if len(escalas) >= 20:
            break
    if not escalas:
        print("  ⚠ no pude leer la escala del PDF completo; salgo a tamaño natural")
        return 1.0
    return max(set(escalas), key=escalas.count) / ESCALA_SIN_ENCOGER


def texto_visible(html):
    return re.sub(r"\s+", " ", TEXTO_RE.sub(" ", html)).strip()


def podar(block):
    """Saca los bloques de código y los gráficos, y limpia lo que quede huérfano."""
    block = quitar_divs(block, '<div class="bloque-codigo')

    # Gráficos: las figuras llevan dentro todo el SVG del libro (no hay <svg>,
    # <img> ni <canvas> sueltos en el cuerpo de los capítulos), y .triple es el
    # diagrama de una tripleta dibujado en línea.
    block = FIGURA_RE.sub("", block)
    block = quitar_divs(block, '<div class="triple')

    # Contenedores que existían sólo para maquetar código: si se quedaron sin
    # texto (o con un título suelto), sobran.
    for marcador in ('<div class="rejilla-2', '<div class="rejilla-3',
                     '<div class="columnas', '<div class="caja '):
        block = quitar_divs(block, marcador, minimo_texto=60)

    # Botones/enlaces a los anexos que ya no forman parte de esta edición.
    for excluido in EXCLUIR:
        block = re.sub(r'<a\b[^>]*class="[^"]*btn[^"]*"[^>]*href="%s"[^>]*>.*?</a>'
                       % re.escape(excluido), "", block, flags=re.DOTALL)
        block = re.sub(r'<a\b[^>]*href="%s"[^>]*class="[^"]*btn[^"]*"[^>]*>.*?</a>'
                       % re.escape(excluido), "", block, flags=re.DOTALL)

    # Párrafos y contenedores que quedaron vacíos (p. ej. la fila de botones
    # del índice, que sólo apuntaba a los anexos).
    block = re.sub(r"<p[^>]*>\s*</p>", "", block)
    while True:
        podado = re.sub(r"<(div|figure)\b[^>]*>\s*</\1>", "", block)
        if podado == block:
            return block
        block = podado


def extract_main(path):
    with open(path, encoding="utf-8") as f:
        html = f.read()
    m = MAIN_RE.search(html)
    block = m.group(1) if m else html
    block = AUDIO_RE.sub("", block)          # quita refs a .m4a
    return podar(block)


def main():
    with open(CSS_FILE, encoding="utf-8") as f:
        css = f.read()

    with open(PORTADA, "rb") as f:
        cov_b64 = base64.b64encode(f.read()).decode("ascii")

    zoom = zoom_de_la_edicion_completa()

    extra = f"""
    /* Mismo cuerpo de texto que la edición completa. */
    @media print {{ body.libro {{ zoom: {zoom:.4f}; }} }}
    """ + """
    /* --- ajustes del build PDF --- */
    .pdf-portada { width:100%; height:100vh; display:flex; align-items:center;
                   justify-content:center; background:#fff; break-after:page; }
    .pdf-portada img { max-width:100%; max-height:100%; object-fit:contain; }
    .pdf-pagina { break-before:page; }
    @media print { .audios, .cabecera, .barra-progreso, .drawer-indice,
                   .velo, .nav-cap { display:none !important; } }
    """

    secciones = []
    quitados = {"bloques de código": 0, "figuras": 0, "diagramas de tripleta": 0}
    for idx, name in enumerate(ordered_files()):
        with open(os.path.join(M2, name), encoding="utf-8") as f:
            crudo = f.read()
        quitados["bloques de código"] += len(re.findall(r'<div class="bloque-codigo', crudo))
        quitados["figuras"] += len(re.findall(r"<figure\b", crudo))
        quitados["diagramas de tripleta"] += len(re.findall(r'<div class="triple', crudo))
        cls = "pdf-pagina" if idx > 0 else ""
        secciones.append(f'<div class="{cls}">{extract_main(os.path.join(M2, name))}</div>')

    doc = f"""<!DOCTYPE html><html lang="es" data-tema="claro"><head>
<meta charset="utf-8">
<base href="file://{M2}/">
<style>{css}
{extra}</style></head><body class="libro">
<div class="pdf-portada"><img src="data:image/png;base64,{cov_b64}"></div>
{''.join(secciones)}
</body></html>"""

    with open(TMP_HTML, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"  HTML combinado: {len(secciones)} páginas + portada "
          f"({len(doc)//1024} KB)")
    for que, cuantos in quitados.items():
        print(f"  Eliminados — {que}: {cuantos}")
    print(f"  Anexos omitidos: {', '.join(sorted(EXCLUIR))}")
    print(f"  Zoom copiado de la edición completa: {zoom:.4f}")

    cmd = [
        CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
        "--no-first-run", "--no-default-browser-check",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=60000",
        f"--print-to-pdf={OUT_PDF}", f"file://{TMP_HTML}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if not os.path.isfile(OUT_PDF) or os.path.getsize(OUT_PDF) == 0:
        sys.stderr.write((r.stderr or "")[-2000:] + "\n")
        sys.exit("Chrome no generó el PDF.")
    os.remove(TMP_HTML)
    print(f"  ✓ {OUT_PDF}  ({os.path.getsize(OUT_PDF)//1024} KB)")


if __name__ == "__main__":
    main()
