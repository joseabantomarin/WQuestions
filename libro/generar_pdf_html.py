#!/usr/bin/env python3
"""Genera el PDF del libro WQuestions desde la edición HTML canónica (manuscrito2/).

A diferencia de generar_pdf.py (que parte del markdown desfasado), este builder
toma el contenido <main> de cada página de manuscrito2/, lo concatena en UN solo
documento con el CSS del sitio inline (incluido su @media print), antepone
portada.png a página completa, y lo imprime con UNA sola llamada a Chrome
headless. Las etiquetas <audio> (index.html) se eliminan del documento para que
Chrome no intente cargar los .m4a (~92 MB) — no hace falta mover archivos.

Orden: portada → index.html → 00..34 → referencias.html → anexo-reglas.html.

Uso: python3 libro/generar_pdf_html.py
Salida: libro/manuscrito2/WQuestions.pdf
"""

import os
import re
import base64
import subprocess
import sys

LIBRO_DIR = os.path.dirname(os.path.abspath(__file__))
M2 = os.path.join(LIBRO_DIR, "manuscrito2")
OUT_PDF = os.path.join(M2, "WQuestions.pdf")
TMP_HTML = os.path.join(M2, ".pdf_build_html.html")  # en M2 para que assets resuelvan
PORTADA = os.path.join(LIBRO_DIR, "portada.png")
CSS_FILE = os.path.join(M2, "assets", "estilo.css")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

MAIN_RE = re.compile(r"<main\b[^>]*>(.*?)</main>", re.DOTALL | re.IGNORECASE)
AUDIO_RE = re.compile(r"<audio\b.*?</audio>|<audio\b[^>]*/>", re.DOTALL | re.IGNORECASE)


def ordered_files():
    files = ["index.html"]
    for i in range(0, 35):
        n = f"{i:02d}"
        files += sorted(f for f in os.listdir(M2)
                        if f.startswith(n + "-") and f.endswith(".html"))
    files += ["referencias.html", "anexo-reglas.html"]
    return [f for f in files if os.path.isfile(os.path.join(M2, f))]


def extract_main(path):
    with open(path, encoding="utf-8") as f:
        html = f.read()
    m = MAIN_RE.search(html)
    block = m.group(1) if m else html
    block = AUDIO_RE.sub("", block)          # quita refs a .m4a
    return block


def main():
    with open(CSS_FILE, encoding="utf-8") as f:
        css = f.read()

    with open(PORTADA, "rb") as f:
        cov_b64 = base64.b64encode(f.read()).decode("ascii")

    extra = """
    /* --- ajustes del build PDF --- */
    .pdf-portada { width:100%; height:100vh; display:flex; align-items:center;
                   justify-content:center; background:#fff; break-after:page; }
    .pdf-portada img { max-width:100%; max-height:100%; object-fit:contain; }
    .pdf-pagina { break-before:page; }
    @media print { .audios, .cabecera, .barra-progreso, .drawer-indice,
                   .velo, .nav-cap { display:none !important; } }
    """

    secciones = []
    for idx, name in enumerate(ordered_files()):
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
