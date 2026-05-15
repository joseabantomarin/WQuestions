"""Diagrama: las tres puertas previas (5W1H, RDF, ontologías de dominio).
Compara qué resuelve y qué deja sin resolver cada enfoque.

Salida: ../png/06_tres_puertas.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

approaches = [
    {
        "x": 0.4, "fill": "#fef3c7", "edge": "#b45309",
        "title": "5W1H",
        "subtitle": "metodología periodística\n+ extracción NLP",
        "ejemplos": "Yang & Hu, Mahmood",
        "tiene": ["Identifica las dimensiones\ncorrectas (quién, qué,\ndónde, cuándo, por qué, cómo).",
                  "Heurística probada en\nun siglo de uso real."],
        "falta": ["Sin estructura de tipos\n— las respuestas son texto.",
                  "Sin vocabulario canónico\n— cada noticia inventa."],
    },
    {
        "x": 4.4, "fill": "#dcfce7", "edge": "#15803d",
        "title": "RDF / Web Semántica",
        "subtitle": "grafos abiertos\nde tripletas",
        "ejemplos": "RDF, OWL, Wikidata,\nDBpedia",
        "tiene": ["Sintaxis universal\nsujeto-predicado-objeto.",
                  "Escala a miles de\nmillones de tripletas."],
        "falta": ["Inventario de predicados\nlibre — cualquiera puede\ninventar etiquetas.",
                  "Sin signaturas tipadas:\n'compuso' y 'autor_de'\nno se reconocen."],
    },
    {
        "x": 8.4, "fill": "#dbeafe", "edge": "#1d4ed8",
        "title": "Ontologías de dominio",
        "subtitle": "vocabularios\nformalizados por área",
        "ejemplos": "CIDOC CRM, Biolink,\nSchema.org, FHIR",
        "tiene": ["Profundidad rica\ndentro de un dominio.",
                  "URIs estables, autoridad\nexterna, comunidad activa."],
        "falta": ["Ningún piso común\nentre dominios.",
                  "Cada nuevo dominio\nrequiere otra ontología\ny otro puente."],
    },
]

fig, ax = plt.subplots(figsize=(13, 8.5), dpi=200)
ax.set_xlim(0, 12.5)
ax.set_ylim(0, 8.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(6.25, 8.15, "Las tres puertas previas — ninguna terminó de cerrar",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)

BOX_W = 3.8
BOX_H = 7.4

for a in approaches:
    x = a["x"]
    y = 0.3
    box = FancyBboxPatch((x, y), BOX_W, BOX_H, boxstyle="round,pad=0.08",
                         facecolor=a["fill"], edgecolor=a["edge"], linewidth=1.6)
    ax.add_patch(box)

    # Título
    ax.text(x + BOX_W/2, y + BOX_H - 0.5, a["title"],
            ha="center", va="center", fontsize=15, fontweight="bold", color=a["edge"])
    ax.text(x + BOX_W/2, y + BOX_H - 1.1, a["subtitle"],
            ha="center", va="center", fontsize=10, style="italic", color=INK)
    ax.text(x + BOX_W/2, y + BOX_H - 1.7, a["ejemplos"],
            ha="center", va="center", fontsize=9, color="#6b7280")

    # Línea divisoria
    ax.plot([x + 0.3, x + BOX_W - 0.3], [y + BOX_H - 2.1, y + BOX_H - 2.1],
            color=a["edge"], linewidth=0.6, linestyle=":", alpha=0.5)

    # ✓ qué resuelve
    ax.text(x + 0.3, y + BOX_H - 2.5, "✓  qué resuelve",
            ha="left", va="center", fontsize=10, fontweight="bold", color="#065f46")
    cur_y = y + BOX_H - 3.05
    for txt in a["tiene"]:
        ax.text(x + 0.3, cur_y, txt, ha="left", va="top", fontsize=9, color=INK)
        cur_y -= (txt.count("\n") + 1) * 0.32 + 0.15

    # Línea divisoria
    ax.plot([x + 0.3, x + BOX_W - 0.3], [y + 2.7, y + 2.7],
            color=a["edge"], linewidth=0.6, linestyle=":", alpha=0.5)

    # ✗ qué falta
    ax.text(x + 0.3, y + 2.4, "✗  qué deja sin resolver",
            ha="left", va="center", fontsize=10, fontweight="bold", color="#991b1b")
    cur_y = y + 1.95
    for txt in a["falta"]:
        ax.text(x + 0.3, cur_y, txt, ha="left", va="top", fontsize=9, color=INK)
        cur_y -= (txt.count("\n") + 1) * 0.32 + 0.15

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "06_tres_puertas.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
