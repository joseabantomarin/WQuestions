"""Diagrama: D4 — plantilla en K + instancia en O con factor de escala.
Caso: receta abstracta vs preparación concreta.

Salida: ../png/10_plantilla_instancia.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

fig, ax = plt.subplots(figsize=(13, 7.5), dpi=200)
ax.set_xlim(0, 13)
ax.set_ylim(0, 7.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(6.5, 7.15, "D4 — plantilla atemporal en K, instancia situada en O",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)

# Panel izquierdo: PLANTILLA (en K)
K_FILL = "#e0e7ff"
K_EDGE = "#4f46e5"
LEFT_X = 0.5
LEFT_W = 5.5
left_box = FancyBboxPatch((LEFT_X, 0.7), LEFT_W, 6.0, boxstyle="round,pad=0.08",
                          facecolor=K_FILL, edgecolor=K_EDGE, linewidth=1.8)
ax.add_patch(left_box)
ax.text(LEFT_X + LEFT_W/2, 6.3, "PLANTILLA  (en K)",
        ha="center", va="center", fontsize=12, fontweight="bold", color=K_EDGE)
ax.text(LEFT_X + LEFT_W/2, 5.9, "atemporal, sin fecha, replicable",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

# Contenido de la plantilla
ax.text(LEFT_X + 0.3, 5.4, "receta_risotto_milanesa", ha="left", va="center",
        fontsize=12, fontweight="bold", color=K_EDGE, family="monospace")
ax.text(LEFT_X + 0.3, 5.0, "∈ K", ha="left", va="center",
        fontsize=9, style="italic", color="#6b7280", family="monospace")

# Atributos
attrs_K = [
    ("instancia_de:",     "tipo_receta"),
    ("ingrediente_base:", "arroz_arborio   (200 g)"),
    ("ingrediente_base:", "caldo_vegetal   (1 L)"),
    ("ingrediente_base:", "azafran         (1 g)"),
    ("tiempo_coccion:",   "45 min"),
    ("porciones_base:",   "2"),
    ("dificultad:",       "intermedia"),
]
y = 4.5
for k, v in attrs_K:
    ax.text(LEFT_X + 0.5, y, k, ha="left", va="center",
            fontsize=9.5, color=INK, family="monospace")
    ax.text(LEFT_X + 2.5, y, v, ha="left", va="center",
            fontsize=9.5, color=INK, family="monospace")
    y -= 0.4

# Panel derecho: INSTANCIA (en O)
O_FILL = "#dbeafe"
O_EDGE = "#1d4ed8"
RIGHT_X = 7.0
RIGHT_W = 5.5
right_box = FancyBboxPatch((RIGHT_X, 0.7), RIGHT_W, 6.0, boxstyle="round,pad=0.08",
                           facecolor=O_FILL, edgecolor=O_EDGE, linewidth=1.8)
ax.add_patch(right_box)
ax.text(RIGHT_X + RIGHT_W/2, 6.3, "INSTANCIA  (en O)",
        ha="center", va="center", fontsize=12, fontweight="bold", color=O_EDGE)
ax.text(RIGHT_X + RIGHT_W/2, 5.9, "situada en tiempo y lugar, con factor de escala",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

ax.text(RIGHT_X + 0.3, 5.4, "preparacion_2026_05_14", ha="left", va="center",
        fontsize=12, fontweight="bold", color=O_EDGE, family="monospace")
ax.text(RIGHT_X + 0.3, 5.0, "∈ O", ha="left", va="center",
        fontsize=9, style="italic", color="#6b7280", family="monospace")

attrs_O = [
    ("instancia_de:",   "receta_risotto_milanesa"),
    ("factor_escala:",  "2  (preparé para 4 en lugar de 2)"),
    ("cocinero:",       "juan"),
    ("cuando:",         "2026-05-14T20:30:00"),
    ("donde:",          "cocina_casa"),
    ("sustitucion:",    "queso_grana_padano"),
    ("resultado:",      "completada"),
]
y = 4.5
for k, v in attrs_O:
    ax.text(RIGHT_X + 0.5, y, k, ha="left", va="center",
            fontsize=9.5, color=INK, family="monospace")
    ax.text(RIGHT_X + 2.5, y, v, ha="left", va="center",
            fontsize=9.5, color=INK, family="monospace")
    y -= 0.4

# Flecha grande "instancia_de" entre los dos paneles
arrow = FancyArrowPatch((RIGHT_X, 4.5), (LEFT_X + LEFT_W, 4.5),
                        arrowstyle="-|>", mutation_scale=20,
                        color="#15803d", linewidth=2.5)
ax.add_patch(arrow)
ax.text(6.5, 4.8, "instancia_de", ha="center", va="center",
        fontsize=10, fontweight="bold", color="#15803d",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                  edgecolor="#15803d", alpha=0.95))

# Pie
ax.text(6.5, 0.30,
        "La plantilla atemporal vive en K y se reusa.\nCada preparación concreta vive en O con su contexto: fecha, lugar, cocinero, escala.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "10_plantilla_instancia.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
