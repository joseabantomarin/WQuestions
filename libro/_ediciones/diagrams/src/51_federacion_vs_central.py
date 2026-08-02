"""Diagrama 51: federación frente a base central.

Izquierda: el depósito único donde todos leen — la pesadilla de privacidad.
Derecha: cada tenedor guarda lo suyo y solo se une, bajo consentimiento,
un idioma común de preguntas.

Salida: ../png/51_federacion_vs_central.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse, Rectangle

INK = "#1f2937"
AZUL_BG, AZUL_BD = "#e0e7ff", "#4f46e5"
VERDE_BG, VERDE_BD = "#dcfce7", "#15803d"
ROJO = "#b91c1c"
GRIS = "#6b7280"

fig, ax = plt.subplots(figsize=(15, 8.5), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 8.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

ax.text(7.5, 8.15, "Un idioma compartido no es una base compartida",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)

tenedores = ["Clínica", "Banco", "Endocrinóloga"]

# ===== IZQUIERDA: base central (pesadilla) =====
lx = 3.7
ax.text(lx, 7.45, "Base central — la pesadilla",
        ha="center", va="center", fontsize=12, fontweight="bold", color=ROJO)

# cilindro central
cyl_x, cyl_y, cyl_w, cyl_h = lx - 1.1, 1.6, 2.2, 1.7
ax.add_patch(Rectangle((cyl_x, cyl_y), cyl_w, cyl_h,
                       facecolor="#fee2e2", edgecolor=ROJO, linewidth=1.6))
ax.add_patch(Ellipse((lx, cyl_y + cyl_h), cyl_w, 0.5,
                     facecolor="#fee2e2", edgecolor=ROJO, linewidth=1.6))
ax.add_patch(Ellipse((lx, cyl_y), cyl_w, 0.5,
                     facecolor="#fecaca", edgecolor=ROJO, linewidth=1.6))
ax.text(lx, cyl_y + cyl_h / 2, "TODO\nde todos",
        ha="center", va="center", fontsize=10, fontweight="bold", color=ROJO)

for i, t in enumerate(tenedores):
    tx = lx + (i - 1) * 2.4
    ty = 5.6
    ax.add_patch(FancyBboxPatch((tx - 1.0, ty - 0.4), 2.0, 0.8,
                                boxstyle="round,pad=0.04",
                                facecolor="#f3f4f6", edgecolor=GRIS, linewidth=1.2))
    ax.text(tx, ty, t, ha="center", va="center", fontsize=9.5, color=INK)
    ax.add_patch(FancyArrowPatch((tx, ty - 0.45), (lx, cyl_y + cyl_h + 0.45),
                                 arrowstyle="-|>", mutation_scale=12,
                                 color=ROJO, linewidth=1.3,
                                 connectionstyle="arc3,rad=0.05"))

ax.text(lx, 0.9, "Cualquiera que entra, lo ve todo.",
        ha="center", va="center", fontsize=9.5, style="italic", color=ROJO)

# divisoria
ax.plot([7.5, 7.5], [0.6, 7.0], color="#d1d5db", linewidth=1.0, linestyle="--")

# ===== DERECHA: federación =====
rx = 11.3
ax.text(rx, 7.45, "Federación — cada quien guarda lo suyo",
        ha="center", va="center", fontsize=12, fontweight="bold", color=VERDE_BD)

islas = [(rx - 1.9, 5.2), (rx + 1.9, 5.2), (rx, 2.4)]
for (ix, iy), t in zip(islas, tenedores):
    ax.add_patch(FancyBboxPatch((ix - 1.1, iy - 0.55), 2.2, 1.1,
                                boxstyle="round,pad=0.05",
                                facecolor=VERDE_BG, edgecolor=VERDE_BD, linewidth=1.5))
    ax.text(ix, iy + 0.18, t, ha="center", va="center",
            fontsize=9.5, fontweight="bold", color=VERDE_BD)
    ax.text(ix, iy - 0.20, "su grafo, su llave",
            ha="center", va="center", fontsize=7.5, style="italic", color=GRIS)

# puentes de consentimiento (líneas punteadas con candado/etiqueta)
pares = [(islas[0], islas[1]), (islas[0], islas[2]), (islas[1], islas[2])]
for (ax1, ay1), (ax2, ay2) in pares:
    ax.add_patch(FancyArrowPatch((ax1, ay1), (ax2, ay2),
                                 arrowstyle="-", linestyle=(0, (4, 3)),
                                 color=AZUL_BD, linewidth=1.3))
ax.text(rx, 4.05, "puentes de\nconsentimiento",
        ha="center", va="center", fontsize=8, color=AZUL_BD,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor=AZUL_BD, linewidth=0.8))

ax.text(rx, 0.9, "Hablan el mismo idioma de preguntas;\nsolo se unen con permiso.",
        ha="center", va="center", fontsize=9.5, style="italic", color=VERDE_BD)

out = os.path.join(os.path.dirname(__file__), "..", "png", "51_federacion_vs_central.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
