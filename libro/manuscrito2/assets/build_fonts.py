#!/usr/bin/env python3
"""Descarga las tipografías de Google Fonts y las localiza (woff2) para uso offline.
Genera assets/fonts/fonts.css con @font-face apuntando a archivos locales."""
import re, os, hashlib, urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

FAMILIES = (
    "Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700"
    "&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,500;0,7..72,600;1,7..72,400;1,7..72,500"
    "&family=JetBrains+Mono:wght@400;500;700"
    "&family=Hanken+Grotesk:wght@400;500;600;700"
)
URL = "https://fonts.googleapis.com/css2?family=" + FAMILIES + "&display=swap"

here = os.path.dirname(os.path.abspath(__file__))
fonts_dir = os.path.join(here, "fonts")
os.makedirs(fonts_dir, exist_ok=True)

def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read() if binary else r.read().decode("utf-8")

css = fetch(URL)
urls = sorted(set(re.findall(r'https://fonts\.gstatic\.com[^)]+\.woff2', css)))
print(f"Encontradas {len(urls)} URLs de woff2")

total = 0
for u in urls:
    h = hashlib.md5(u.encode()).hexdigest()[:12]
    fname = f"g_{h}.woff2"
    dest = os.path.join(fonts_dir, fname)
    data = fetch(u, binary=True)
    with open(dest, "wb") as f:
        f.write(data)
    total += len(data)
    css = css.replace(u, fname)  # rutas relativas a fonts.css (mismo dir)

with open(os.path.join(fonts_dir, "fonts.css"), "w") as f:
    f.write("/* Tipografías localizadas (offline). Generado por build_fonts.py */\n")
    f.write(css)

print(f"Descargados {len(urls)} archivos, {total/1024:.0f} KB en total")
print("Escrito: fonts/fonts.css")
