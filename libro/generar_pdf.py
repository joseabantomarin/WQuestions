#!/usr/bin/env python3
"""Genera el PDF del manuscrito WQuestions (con portada) desde los .md.

Pipeline sin dependencias pesadas:
  1. Lee manuscrito/*.md en orden.
  2. Convierte cada uno a HTML con la librería `markdown` (tablas + código).
  3. Embebe las imágenes (../diagrams/png/*.png) como data-URI base64
     y convierte el `alt` en pie de figura.
  4. Arma un HTML autocontenido con portada + CSS de impresión.
  5. Lo imprime a PDF con Google Chrome en modo headless.

Salida: libro/WQuestions.pdf
Uso:    python3 libro/generar_pdf.py
"""

import os
import re
import sys
import base64
import glob
import subprocess

import markdown

TITULO    = "WQuestions"
SUBTITULO = "Gramática Universal de la arquitectura de datos"
AUTOR     = "José Abanto Marín"

LIBRO_DIR      = os.path.dirname(os.path.abspath(__file__))
MANUSCRITO_DIR = os.path.join(LIBRO_DIR, "manuscrito")
OUT_PDF        = os.path.join(LIBRO_DIR, "WQuestions.pdf")
TMP_HTML       = os.path.join(LIBRO_DIR, ".pdf_build.html")

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 22mm 20mm; }
* { box-sizing: border-box; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 11.5pt;
       line-height: 1.5; color: #1f2937; margin: 0; }
.cover { height: 100vh; display: flex; flex-direction: column;
         justify-content: center; align-items: center; text-align: center;
         page-break-after: always; }
.cover .title { font-size: 52pt; font-weight: 700; letter-spacing: -1px;
                color: #1e3a8a; margin-bottom: 18px; }
.cover .subtitle { font-size: 19pt; font-style: italic; color: #374151;
                   max-width: 80%; margin-bottom: 60px; }
.cover .author { font-size: 15pt; color: #111827; }
.cover .rule { width: 90px; height: 3px; background: #1e3a8a; margin: 26px 0; }
.chapter { page-break-before: always; }
h1 { font-size: 22pt; color: #1e3a8a; line-height: 1.2;
     border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; margin-top: 0; }
h2 { font-size: 15pt; color: #1e40af; margin-top: 1.4em; }
h3 { font-size: 12.5pt; color: #374151; }
p { text-align: justify; }
code { font-family: 'SF Mono', Menlo, Consolas, monospace; font-size: 9.5pt;
       background: #f3f4f6; padding: 1px 4px; border-radius: 3px; }
pre { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 6px;
      padding: 10px 12px; overflow-x: auto; page-break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 9pt; line-height: 1.4; }
blockquote { border-left: 4px solid #93c5fd; background: #eff6ff; margin: 1em 0;
             padding: 8px 16px; color: #1e3a8a; border-radius: 0 6px 6px 0; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 1em 0;
        page-break-inside: avoid; }
th, td { border: 1px solid #d1d5db; padding: 5px 8px; text-align: left;
         vertical-align: top; }
th { background: #f1f5f9; }
figure { margin: 1.2em 0; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; max-height: 420px; }
figcaption { font-size: 9pt; font-style: italic; color: #6b7280;
             margin-top: 6px; padding: 0 8%; }
a { color: #1d4ed8; text-decoration: none; }
"""


def embed_images(html: str) -> str:
    """Reemplaza <img src="...png" alt="C"> por <figure> con base64 + pie."""
    def repl(m):
        attrs = m.group(1)
        src = re.search(r'src="([^"]+)"', attrs)
        alt = re.search(r'alt="([^"]*)"', attrs)
        if not src:
            return m.group(0)
        path = os.path.normpath(os.path.join(MANUSCRITO_DIR, src.group(1)))
        if not os.path.isfile(path):
            sys.stderr.write(f"  ! imagen no encontrada: {src.group(1)}\n")
            return m.group(0)
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        cap = alt.group(1) if alt else ""
        fig = f'<figure><img src="data:image/png;base64,{b64}">'
        if cap:
            fig += f'<figcaption>{cap}</figcaption>'
        return fig + '</figure>'
    return re.sub(r'<img\s+([^>]*?)/?>', repl, html)


def main():
    md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists"])
    files = sorted(glob.glob(os.path.join(MANUSCRITO_DIR, "*.md")))
    if not files:
        sys.exit("No hay .md en " + MANUSCRITO_DIR)

    cuerpo = []
    for f in files:
        md.reset()
        with open(f, encoding="utf-8") as fh:
            html = md.convert(fh.read())
        html = embed_images(html)
        cuerpo.append(f'<section class="chapter">{html}</section>')

    doc = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<style>{CSS}</style></head><body>
<div class="cover">
  <div class="title">{TITULO}</div>
  <div class="rule"></div>
  <div class="subtitle">{SUBTITULO}</div>
  <div class="author">{AUTOR}</div>
</div>
{''.join(cuerpo)}
</body></html>"""

    with open(TMP_HTML, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"  HTML armado: {len(files)} capítulos")

    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           "--run-all-compositor-stages-before-draw",
           "--virtual-time-budget=20000",
           f"--print-to-pdf={OUT_PDF}", f"file://{TMP_HTML}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not os.path.isfile(OUT_PDF) or os.path.getsize(OUT_PDF) == 0:
        sys.stderr.write(r.stderr[-2000:] + "\n")
        sys.exit("Chrome no generó el PDF.")
    os.remove(TMP_HTML)
    print(f"  ✓ {OUT_PDF}  ({os.path.getsize(OUT_PDF)//1024} KB)")


if __name__ == "__main__":
    main()
