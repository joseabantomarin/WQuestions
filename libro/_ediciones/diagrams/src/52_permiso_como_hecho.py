"""Diagrama 52: el permiso como situación reificada.

Un nodo-permiso descrito con los mismos ejes que cualquier otro hecho:
quién recibe el acceso, sobre qué situación, qué puede hacer, desde cuándo.
El control de acceso habla el mismo idioma que aquello que controla.

Salida: ../png/52_permiso_como_hecho.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
AZUL_BG, AZUL_BD = "#e0e7ff", "#4f46e5"
AMBAR_BG, AMBAR_BD = "#fef3c7", "#b45309"
VERDE_BG, VERDE_BD = "#dcfce7", "#15803d"
GRIS = "#6b7280"

fig, ax = plt.subplots(figsize=(13, 9), dpi=200)
ax.set_xlim(0, 13)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

ax.text(6.5, 8.55, "El permiso es un hecho más",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(6.5, 8.10, "descrito con las mismas siete preguntas que cualquier situación",
        ha="center", va="center", fontsize=10, style="italic", color=GRIS)

# nodo central: la situación-permiso (reificada -> verde)
cx, cy = 6.5, 4.6
ax.add_patch(FancyBboxPatch((cx - 1.6, cy - 0.8), 3.2, 1.6,
                            boxstyle="round,pad=0.06",
                            facecolor=VERDE_BG, edgecolor=VERDE_BD, linewidth=2.0))
ax.text(cx, cy + 0.30, "consentimiento_4471",
        ha="center", va="center", fontsize=11, fontweight="bold", color=VERDE_BD)
ax.text(cx, cy - 0.25, "(situación reificada)",
        ha="center", va="center", fontsize=8.5, style="italic", color=GRIS)

# ejes/participantes alrededor
ejes = [
    ("quién (Q)",   "María\ntitular del dato", AZUL_BG, AZUL_BD, 2.0, 7.2),
    ("permite (M)", "puede_ver",               AMBAR_BG, AMBAR_BD, 11.0, 7.2),
    ("qué (O)",     "situación\n«arritmia_dx_2026»", AZUL_BG, AZUL_BD, 1.4, 4.6),
    ("a quién (Q)", "cardiólogo\nRosales",      AZUL_BG, AZUL_BD, 11.6, 4.6),
    ("desde (T)",   "2026-03-12",              AZUL_BG, AZUL_BD, 2.0, 2.0),
    ("carácter",    "revocable",               AMBAR_BG, AMBAR_BD, 11.0, 2.0),
]

for rol, val, bg, bd, ex, ey in ejes:
    ax.add_patch(FancyBboxPatch((ex - 1.25, ey - 0.55), 2.5, 1.1,
                                boxstyle="round,pad=0.05",
                                facecolor=bg, edgecolor=bd, linewidth=1.4))
    ax.text(ex, ey + 0.22, rol, ha="center", va="center",
            fontsize=9, fontweight="bold", color=bd)
    ax.text(ex, ey - 0.22, val, ha="center", va="center",
            fontsize=8.5, color=INK)
    ax.add_patch(FancyArrowPatch((ex, ey), (cx, cy),
                                 arrowstyle="-|>", mutation_scale=12,
                                 color=GRIS, linewidth=1.1, shrinkA=22, shrinkB=42,
                                 connectionstyle="arc3,rad=0.0"))

ax.text(6.5, 0.55,
        "Por eso revocar es publicar un hecho nuevo (gana el último — D6),\ny cada acceso queda, también, como una situación auditable.",
        ha="center", va="center", fontsize=9.5, color="#374151")

out = os.path.join(os.path.dirname(__file__), "..", "png", "52_permiso_como_hecho.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
