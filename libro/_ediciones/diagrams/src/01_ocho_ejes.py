"""Diagrama: los siete ejes de WQuestions.

Representa los siete ejes (Q, O, L, T, N, K, M) como una estructura radial:
seis ejes de valor en torno a un centro (Q, O, L, T, N, K) y un eje
estructural (M, cómo) como anillo exterior que conecta a todos. La
cardinalidad (funcional o múltiple) es un atributo de cada predicado de M,
no un eje aparte.

Salida: ../png/01_ocho_ejes.png
"""

import os
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.lines import Line2D

# Configuración estética
FIG_SIZE = (10, 10)
DPI = 200
BG = "#ffffff"
INK = "#1f2937"          # gris-tinta
VALUE_FILL = "#e0e7ff"    # azul suave para ejes de valor
VALUE_EDGE = "#4f46e5"    # azul profundo
PRED_FILL = "#fef3c7"     # ámbar suave para predicados
PRED_EDGE = "#b45309"     # ámbar oscuro
CENTER_FILL = "#f3f4f6"
RING_COLOR = "#9ca3af"

# Definición de ejes
value_axes = [
    ("Q", "quién",   "agentes"),
    ("O", "qué",     "objetos, eventos, situaciones"),
    ("L", "dónde",   "lugares"),
    ("T", "cuándo",  "momentos"),
    ("N", "cuánto",  "magnitudes"),
    ("K", "cuál",    "tipos y categorías"),
]
predicate_axes = [
    ("M", "cómo", "predicados (cardinalidad 1..n)"),
]

fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
ax.set_xlim(-1.4, 1.4)
ax.set_ylim(-1.4, 1.4)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(BG)

# Anillo exterior — el eje de predicados (M, cómo) que conecta todo
ring = Circle((0, 0), 1.05, fill=False, edgecolor=RING_COLOR,
              linewidth=1, linestyle="--", zorder=1)
ax.add_patch(ring)

# Ejes de valor distribuidos en círculo
N = len(value_axes)
radius = 0.78
for i, (letra, pregunta, descripcion) in enumerate(value_axes):
    angle = math.pi / 2 - i * (2 * math.pi / N)
    x, y = radius * math.cos(angle), radius * math.sin(angle)
    circle = Circle((x, y), 0.20, facecolor=VALUE_FILL,
                    edgecolor=VALUE_EDGE, linewidth=2, zorder=3)
    ax.add_patch(circle)
    ax.text(x, y + 0.03, letra, ha="center", va="center",
            fontsize=22, fontweight="bold", color=VALUE_EDGE, zorder=4)
    ax.text(x, y - 0.08, pregunta, ha="center", va="center",
            fontsize=11, style="italic", color=INK, zorder=4)
    # Etiqueta descriptiva fuera del círculo
    lx, ly = 1.22 * math.cos(angle), 1.22 * math.sin(angle)
    ha = "center"
    if math.cos(angle) > 0.3: ha = "left"
    elif math.cos(angle) < -0.3: ha = "right"
    ax.text(lx, ly, descripcion, ha=ha, va="center",
            fontsize=9, color=INK, zorder=4)

# Centro: el universo V
center = Circle((0, 0), 0.18, facecolor=CENTER_FILL,
                edgecolor=INK, linewidth=1.2, zorder=2)
ax.add_patch(center)
ax.text(0, 0.02, "V", ha="center", va="center",
        fontsize=18, fontweight="bold", color=INK, zorder=4)
ax.text(0, -0.08, "universo", ha="center", va="center",
        fontsize=8, style="italic", color=INK, zorder=4)

# El eje de predicados M (cómo) como badge sobre el anillo exterior
for letra, pregunta, descripcion, pos_angle in [
    (predicate_axes[0][0], predicate_axes[0][1], predicate_axes[0][2], math.pi * 0.25),
]:
    x = 1.05 * math.cos(pos_angle)
    y = 1.05 * math.sin(pos_angle)
    # Pequeña etiqueta tipo "badge"
    box = plt.Rectangle((x - 0.13, y - 0.10), 0.26, 0.20,
                        facecolor=PRED_FILL, edgecolor=PRED_EDGE,
                        linewidth=1.5, zorder=3, alpha=0.95)
    ax.add_patch(box)
    ax.text(x, y + 0.02, letra, ha="center", va="center",
            fontsize=16, fontweight="bold", color=PRED_EDGE, zorder=4)
    ax.text(x, y - 0.07, pregunta, ha="center", va="center",
            fontsize=9, style="italic", color=INK, zorder=4)

# Título y leyenda
ax.text(0, 1.32, "Los siete ejes de WQuestions",
        ha="center", va="center", fontsize=15, fontweight="bold", color=INK)

# Leyenda visual abajo
legend_y = -1.32
ax.text(-1.30, legend_y, "●  ejes de valor (alojan individuos)",
        ha="left", va="center", fontsize=9, color=VALUE_EDGE)
ax.text(0.30, legend_y, "▭  eje estructural M (predicados; funcional o múltiple)",
        ha="left", va="center", fontsize=9, color=PRED_EDGE)

# Guardar
out_dir = os.path.join(os.path.dirname(__file__), "..", "png")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "01_ocho_ejes.png")
plt.savefig(out_path, dpi=DPI, bbox_inches="tight", facecolor=BG)
plt.close(fig)
print(f"  ✓ {out_path}")
