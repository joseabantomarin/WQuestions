"""Diagrama: comparación de WQuestions con otros espacios multidimensionales
(OLAP, Espacios Conceptuales, Embeddings).

Salida: ../png/16_comparacion_espacios.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK = "#1f2937"

# 4 espacios a comparar
spaces = [
    {"name": "Cubos OLAP",
     "subtitle": "BI / Data Warehouse",
     "fill": "#fed7aa", "edge": "#c2410c",
     "dims": "Dimensiones específicas\n(tiempo, geografía, producto,\ncliente, vendedor…).",
     "elem": "Hechos por celda con\nmedidas agregables.",
     "vs_wq": "Un cubo por dominio.\nWQ usa un único cubo\nuniversal de ocho ejes."},
    {"name": "Espacios Conceptuales",
     "subtitle": "Gärdenfors",
     "fill": "#dbeafe", "edge": "#1d4ed8",
     "dims": "Dimensiones continuas\nde cualidad (matiz, tono,\ntemperatura, intensidad).",
     "elem": "Conceptos = regiones\nconvexas; objetos = puntos.",
     "vs_wq": "Continuo y geométrico.\nWQ es discreto y simbólico:\nlos conceptos viven en K."},
    {"name": "Espacios de embeddings",
     "subtitle": "modelos de lenguaje",
     "fill": "#ede9fe", "edge": "#6d28d9",
     "dims": "Cientos o miles de\ndimensiones opacas, emergidas\ndel entrenamiento.",
     "elem": "Puntos densos con\ndistancia semántica\n(coseno).",
     "vs_wq": "Opaco — cada dimensión\nes desconocida. WQ es\ntransparente y se complementa."},
    {"name": "WQuestions",
     "subtitle": "este libro",
     "fill": "#dcfce7", "edge": "#15803d",
     "dims": "Ocho ejes universales\n(Q, O, L, T, N, K, P, M).",
     "elem": "Hechos atómicos\ncomo puntos parciales,\nmulti-valuados, tipados.",
     "vs_wq": "Pensado desde el inicio\npara consumo por LLMs\n+ federación de dominios."},
]

fig, ax = plt.subplots(figsize=(15, 8), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 8)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 7.65, "Espacios multidimensionales: cómo se diferencia WQuestions",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)

# 4 columnas
col_w = 3.5
gap = 0.08
total_w = 4 * col_w + 3 * gap
start_x = (15 - total_w) / 2

for i, s in enumerate(spaces):
    x = start_x + i * (col_w + gap)
    box = FancyBboxPatch((x, 0.9), col_w, 6.3, boxstyle="round,pad=0.08",
                         facecolor=s["fill"], edgecolor=s["edge"], linewidth=1.8)
    ax.add_patch(box)
    # Título
    ax.text(x + col_w/2, 6.85, s["name"], ha="center", va="center",
            fontsize=12.5, fontweight="bold", color=s["edge"])
    ax.text(x + col_w/2, 6.50, s["subtitle"], ha="center", va="center",
            fontsize=9, style="italic", color="#6b7280")

    # Sección: dimensiones
    ax.text(x + 0.2, 5.95, "Dimensiones",
            ha="left", va="center", fontsize=9.5, fontweight="bold", color=s["edge"])
    ax.text(x + 0.2, 5.30, s["dims"],
            ha="left", va="top", fontsize=9, color=INK)

    # Sección: elementos
    ax.text(x + 0.2, 4.10, "Elementos",
            ha="left", va="center", fontsize=9.5, fontweight="bold", color=s["edge"])
    ax.text(x + 0.2, 3.55, s["elem"],
            ha="left", va="top", fontsize=9, color=INK)

    # Sección: diferencia con WQ (excepto en la columna WQ)
    label = "WQ se distingue por" if i < 3 else "Lo distintivo"
    ax.text(x + 0.2, 2.40, label,
            ha="left", va="center", fontsize=9.5, fontweight="bold", color=s["edge"])
    ax.text(x + 0.2, 1.85, s["vs_wq"],
            ha="left", va="top", fontsize=9, color=INK)

# Pie
ax.text(7.5, 0.4,
        "No son competidores: cada espacio sirve para distintas operaciones.\nUn LLM razona internamente con embeddings y consulta hechos estructurados en WQuestions.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "16_comparacion_espacios.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
