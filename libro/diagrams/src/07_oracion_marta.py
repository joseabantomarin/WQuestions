"""Diagrama: la oración 'Marta le regaló un libro a su sobrino ayer en su casa'
descompuesta en los cuatro pilares (Q, O, L, T).

Salida: ../png/07_oracion_marta.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

# Oración + segmentación
segments = [
    # (texto, x_inicio, x_fin, pilar, color_fill, color_edge)
    ("Marta",        0.4, 1.3, "Q",  "#dbeafe", "#1d4ed8"),
    ("le regaló",    1.3, 2.5, None, None, None),
    ("un libro",     2.5, 3.5, "O",  "#dbeafe", "#1d4ed8"),
    ("a su sobrino", 3.5, 4.8, "Q",  "#dbeafe", "#1d4ed8"),
    ("ayer",         4.8, 5.6, "T",  "#dbeafe", "#1d4ed8"),
    ("en su casa",   5.6, 6.9, "L",  "#dbeafe", "#1d4ed8"),
]

pilars = [
    ("Q", "quién",  "Marta\nel sobrino"),
    ("O", "qué",    "un libro"),
    ("L", "dónde",  "la casa"),
    ("T", "cuándo", "ayer"),
]

fig, ax = plt.subplots(figsize=(11, 7), dpi=200)
ax.set_xlim(0, 11)
ax.set_ylim(0, 7)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(5.5, 6.65, "Cuatro pilares en una oración",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)

# La oración misma (línea principal)
y_orac = 5.3
ax.text(5.5, y_orac + 0.55,
        '"Marta le regaló un libro a su sobrino ayer en su casa."',
        ha="center", va="center", fontsize=13, style="italic", color=INK)

# Subrayados por segmentos
for text, x0, x1, pilar, fill, edge in segments:
    if pilar is None:
        continue
    # Subrayado del segmento
    ax.plot([x0 + 1.5, x1 + 1.5], [y_orac + 0.30, y_orac + 0.30],
            color=edge, linewidth=2.5)
    # Etiqueta del pilar arriba
    ax.text((x0 + x1) / 2 + 1.5, y_orac + 0.85, pilar,
            ha="center", va="center", fontsize=10, fontweight="bold", color=edge)

# Cuatro pilares debajo, en columnas
y_pilar = 1.0
COL_W = 2.3
total = COL_W * 4 + 0.3 * 3
start_x = (11 - total) / 2

pilar_colors = {
    "Q": ("#dbeafe", "#1d4ed8"),
    "O": ("#dbeafe", "#1d4ed8"),
    "L": ("#dbeafe", "#1d4ed8"),
    "T": ("#dbeafe", "#1d4ed8"),
}

for i, (letra, preg, contenido) in enumerate(pilars):
    x = start_x + i * (COL_W + 0.3)
    fill, edge = pilar_colors[letra]
    box = FancyBboxPatch((x, y_pilar), COL_W, 2.6, boxstyle="round,pad=0.05",
                         facecolor=fill, edgecolor=edge, linewidth=1.6)
    ax.add_patch(box)
    # Letra grande
    ax.text(x + COL_W/2, y_pilar + 2.20, letra,
            ha="center", va="center", fontsize=26, fontweight="bold", color=edge)
    # Pregunta
    ax.text(x + COL_W/2, y_pilar + 1.65, "¿" + preg + "?",
            ha="center", va="center", fontsize=11, style="italic", color=INK)
    # Línea divisoria
    ax.plot([x + 0.2, x + COL_W - 0.2], [y_pilar + 1.30, y_pilar + 1.30],
            color=edge, linewidth=0.6, linestyle=":", alpha=0.5)
    # Contenido
    ax.text(x + COL_W/2, y_pilar + 0.75, contenido,
            ha="center", va="center", fontsize=10, color=INK)
    # Flecha desde el subrayado al pilar
    if letra == "Q":
        anchor_x = 1.5 + (0.4 + 1.3) / 2 + 1.5 - 1.5
        # En realidad usamos los segmentos
        for text, x0, x1, p, _, _ in segments:
            if p == letra:
                arrow = FancyArrowPatch((((x0 + x1)/2) + 1.5, y_orac + 0.25),
                                        (x + COL_W/2, y_pilar + 2.55),
                                        arrowstyle="-", color=edge,
                                        linewidth=0.7, alpha=0.4,
                                        connectionstyle="arc3,rad=0.05")
                ax.add_patch(arrow)
    else:
        for text, x0, x1, p, _, _ in segments:
            if p == letra:
                arrow = FancyArrowPatch((((x0 + x1)/2) + 1.5, y_orac + 0.25),
                                        (x + COL_W/2, y_pilar + 2.55),
                                        arrowstyle="-", color=edge,
                                        linewidth=0.7, alpha=0.4,
                                        connectionstyle="arc3,rad=0.05")
                ax.add_patch(arrow)

# Pie
ax.text(5.5, 0.4,
        "La mente identifica los pilares sin esfuerzo. El modelo solo los hace explícitos.",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "07_oracion_marta.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
