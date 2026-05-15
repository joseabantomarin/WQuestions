"""Diagrama: los cuatro caminos por los que se intentó resolver la torre de Babel.

Salida: ../png/03_cuatro_intentos_previos.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK = "#1f2937"

approaches = [
    (0, 1, "#dbeafe", "#1d4ed8", "Ontologías de dominio",
     "Profundidad rica por dominio\n(CIDOC, Biolink, IFC, XBRL).",
     "Ningún piso compartido\nentre dominios."),
    (1, 1, "#fce7f3", "#9f1239", "Estándares de intercambio",
     "Formato común para transmitir\nentre sistemas (HL7 FHIR,\nEDI, ISO 20022).",
     "Cada sistema sigue guardando\nlos datos a su manera."),
    (0, 0, "#dcfce7", "#15803d", "Grafo abierto",
     "Sintaxis universal de tripletas\n(RDF, OWL, Wikidata).",
     "Inventario de predicados libre:\ncada uno inventa sus etiquetas."),
    (1, 0, "#fef3c7", "#b45309", "Canonicalización post-hoc",
     "Reconciliar vocabularios después\ndel hecho (OpenIE, mapeos).",
     "Trabajo de Sísifo con cada\nnueva fuente."),
]

# Geometría: dos columnas, dos filas
COL_W = 4.9
COL_H = 4.0
COL_X = [0.3, 5.4]
ROW_Y = [0.4, 4.5]  # bottom row, top row

fig, ax = plt.subplots(figsize=(11, 9.5), dpi=200)
ax.set_xlim(0, 10.5)
ax.set_ylim(0, 9.2)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

ax.text(5.25, 8.85, "Los cuatro caminos previos — ninguno cerró el problema",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)

for col, row, fill, edge, titulo, resuelve_txt, falta_txt in approaches:
    x = COL_X[col]
    y = ROW_Y[row]
    box = FancyBboxPatch((x, y), COL_W, COL_H, boxstyle="round,pad=0.08",
                         facecolor=fill, edgecolor=edge, linewidth=1.6)
    ax.add_patch(box)
    # Línea horizontal divisoria en el centro
    cy = y + COL_H / 2
    ax.plot([x + 0.3, x + COL_W - 0.3], [cy, cy],
            color=edge, linewidth=0.8, linestyle=":", alpha=0.5)

    # Título arriba
    ax.text(x + COL_W/2, y + COL_H - 0.4, titulo, ha="center", va="center",
            fontsize=13, fontweight="bold", color=edge)

    # Bloque superior: qué resuelve
    ax.text(x + 0.3, y + COL_H - 1.0, "✓  qué resuelve",
            ha="left", va="center", fontsize=10, fontweight="bold", color="#065f46")
    ax.text(x + 0.3, y + COL_H - 1.65, resuelve_txt,
            ha="left", va="top", fontsize=10, color=INK)

    # Bloque inferior: qué deja sin resolver
    ax.text(x + 0.3, y + COL_H/2 - 0.55, "✗  qué deja sin resolver",
            ha="left", va="center", fontsize=10, fontweight="bold", color="#991b1b")
    ax.text(x + 0.3, y + COL_H/2 - 1.15, falta_txt,
            ha="left", va="top", fontsize=10, color=INK)

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "03_cuatro_intentos_previos.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
