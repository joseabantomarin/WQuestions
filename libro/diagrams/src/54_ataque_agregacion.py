"""Diagrama 54: el ataque por agregación.

Tres hechos que por separado son inofensivos —un lugar, un horario, una
compra— convergen y reconstruyen una identidad que ninguno revelaba solo.
El frente que ningún modelo enlazable resuelve por completo.

Salida: ../png/54_ataque_agregacion.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
AZUL_BG, AZUL_BD = "#e0e7ff", "#4f46e5"
ROJO_BG, ROJO_BD = "#fee2e2", "#b91c1c"
GRIS = "#6b7280"

fig, ax = plt.subplots(figsize=(13, 8.5), dpi=200)
ax.set_xlim(0, 13)
ax.set_ylim(0, 8.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

ax.text(6.5, 8.05, "El ataque por agregación",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(6.5, 7.60, "ningún hecho es secreto; juntos, te identifican",
        ha="center", va="center", fontsize=10, style="italic", color=GRIS)

# tres hechos inocuos
hechos = [
    ("Lugar", "vive cerca de\nun código postal", 2.0),
    ("Horario", "sale del trabajo\na las 18:40", 6.5),
    ("Compra", "recoge receta en\ncierta farmacia", 11.0),
]
hy = 5.6
for titulo, detalle, hx in hechos:
    ax.add_patch(FancyBboxPatch((hx - 1.5, hy - 0.7), 3.0, 1.4,
                                boxstyle="round,pad=0.05",
                                facecolor=AZUL_BG, edgecolor=AZUL_BD, linewidth=1.5))
    ax.text(hx, hy + 0.30, titulo, ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=AZUL_BD)
    ax.text(hx, hy - 0.25, detalle, ha="center", va="center",
            fontsize=8.5, color=INK)
    ax.text(hx, hy - 1.05, "inofensivo por sí solo",
            ha="center", va="center", fontsize=8, style="italic", color=GRIS)

# nodo identidad reconstruida
ix, iy = 6.5, 1.8
ax.add_patch(FancyBboxPatch((ix - 2.0, iy - 0.65), 4.0, 1.3,
                            boxstyle="round,pad=0.06",
                            facecolor=ROJO_BG, edgecolor=ROJO_BD, linewidth=2.0))
ax.text(ix, iy + 0.18, "identidad reconstruida",
        ha="center", va="center", fontsize=11.5, fontweight="bold", color=ROJO_BD)
ax.text(ix, iy - 0.28, "una sola persona, re-identificada",
        ha="center", va="center", fontsize=8.5, style="italic", color=ROJO_BD)

# flechas convergentes
for _, _, hx in hechos:
    ax.add_patch(FancyArrowPatch((hx, hy - 1.25), (ix, iy + 0.75),
                                 arrowstyle="-|>", mutation_scale=14,
                                 color=ROJO_BD, linewidth=1.5,
                                 connectionstyle="arc3,rad=0.08"))

ax.text(6.5, 0.45,
        "k-anonimato y privacidad diferencial mitigan; no resuelven. Es parte de lo que falta.",
        ha="center", va="center", fontsize=9.5, color="#374151")

out = os.path.join(os.path.dirname(__file__), "..", "png", "54_ataque_agregacion.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
