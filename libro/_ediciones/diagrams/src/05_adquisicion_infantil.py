"""Diagrama: orden de adquisición de las preguntas-W en el desarrollo infantil.
Basado en Brown (1973) y estudios comparados.

Salida: ../png/05_adquisicion_infantil.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

INK = "#1f2937"

stages = [
    # (orden, edad_aprox, pregunta, ejemplo, color)
    (1, "1.5-2 años",  "¿qué?",   "¿qué es eso?",         "#fee2e2", "#b91c1c"),
    (2, "2 años",      "¿dónde?", "¿dónde está mamá?",    "#fed7aa", "#c2410c"),
    (3, "2.5 años",    "¿quién?", "¿quién hizo esto?",    "#fef3c7", "#b45309"),
    (4, "3 años",      "¿cuándo?","¿cuándo viene papá?",  "#dcfce7", "#15803d"),
    (5, "3-4 años",    "¿por qué?","¿por qué llueve?",    "#dbeafe", "#1d4ed8"),
    (6, "4-5 años",    "¿cómo?",  "¿cómo se hace?",       "#ede9fe", "#6d28d9"),
]

fig, ax = plt.subplots(figsize=(11, 6.5), dpi=200)
ax.set_xlim(0, 11)
ax.set_ylim(0, 6.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Eje horizontal de complejidad cognitiva
ax.annotate("", xy=(10.5, 0.8), xytext=(0.5, 0.8),
            arrowprops=dict(arrowstyle="->", color="#9ca3af", lw=1.5))
ax.text(0.5, 0.5, "menos complejo", ha="left", va="center",
        fontsize=9, style="italic", color="#6b7280")
ax.text(10.5, 0.5, "más complejo", ha="right", va="center",
        fontsize=9, style="italic", color="#6b7280")

# Etapas
box_w = 1.55
total_w = box_w * len(stages) + 0.15 * (len(stages) - 1)
start_x = (11 - total_w) / 2

for i, (orden, edad, preg, ejemplo, fill, edge) in enumerate(stages):
    x = start_x + i * (box_w + 0.15)
    y = 1.6
    box = FancyBboxPatch((x, y), box_w, 3.3, boxstyle="round,pad=0.05",
                         facecolor=fill, edgecolor=edge, linewidth=1.8)
    ax.add_patch(box)
    # Número de orden (círculo)
    circle = plt.Circle((x + box_w/2, y + 3.0), 0.22,
                        facecolor=edge, edgecolor="white", linewidth=1.5, zorder=3)
    ax.add_patch(circle)
    ax.text(x + box_w/2, y + 3.0, str(orden), ha="center", va="center",
            fontsize=11, fontweight="bold", color="white", zorder=4)
    # Edad
    ax.text(x + box_w/2, y + 2.4, edad, ha="center", va="center",
            fontsize=8.5, color="#6b7280")
    # Pregunta
    ax.text(x + box_w/2, y + 1.65, preg, ha="center", va="center",
            fontsize=15, fontweight="bold", color=edge)
    # Ejemplo
    ax.text(x + box_w/2, y + 0.7, ejemplo, ha="center", va="center",
            fontsize=8.5, style="italic", color=INK)

    # Punto en el eje
    ax.plot([x + box_w/2], [0.8], "o", color=edge, markersize=8, zorder=5)
    # Línea desde punto hasta caja
    ax.plot([x + box_w/2, x + box_w/2], [0.8, y], color=edge,
            linewidth=0.7, alpha=0.4, zorder=1)

# Título
ax.text(5.5, 6.15, "Orden de adquisición de las preguntas-W en niños",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(5.5, 5.7,
        "Observado en hablantes de inglés, español, francés, mandarín, japonés, hebreo",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

# Pie con fuente
ax.text(5.5, 0.15,
        "fuente: Brown, R. (1973) y estudios comparados posteriores",
        ha="center", va="center", fontsize=8, color="#9ca3af")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "05_adquisicion_infantil.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
