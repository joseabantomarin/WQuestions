"""Diagrama: timeline de las cuatro tradiciones que convergen en las preguntas-W.

Aristóteles (s. IV a.C.) → Cicerón (s. I a.C.) → Quintiliano → Tomás de Aquino
→ Bleyer 1913 (5W1H periodismo) → Fillmore 1968 (roles temáticos).

Salida: ../png/04_convergencia_tradiciones.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

INK = "#1f2937"
TIMELINE_COLOR = "#9ca3af"

# Eventos: (x_position, year_label, autor, tradicion, color, height)
# x: -1 (lejos en el tiempo) ... 1 (presente)
events = [
    (0.05, "s. IV a.C.",  "Aristóteles",   "Ética a Nicómaco:\nlas circunstancias del acto",  "#dbeafe", "#1d4ed8", 1.4),
    (0.20, "s. I a.C.",   "Cicerón",       "De inventione:\nquis, quid, ubi, quando, cur,\nquomodo, quibus auxiliis", "#dbeafe", "#1d4ed8", -1.4),
    (0.30, "s. I d.C.",   "Quintiliano",   "Institutio Oratoria:\nrefinamiento retórico",  "#dbeafe", "#1d4ed8", 1.4),
    (0.45, "s. XIII",     "Tomás de Aquino","Suma Teológica:\ncircunstancias del acto moral", "#dbeafe", "#1d4ed8", -1.4),
    (0.68, "1913",        "Bleyer",        "Newspaper Writing and\nEditing: los 5W1H",     "#fef3c7", "#b45309", 1.4),
    (0.85, "1968",        "Fillmore",      "The Case for Case:\nroles temáticos",          "#dcfce7", "#15803d", -1.4),
    (0.95, "1972–96",     "Wierzbicka",    "Natural Semantic\nMetalanguage",               "#dcfce7", "#15803d", 1.4),
]

fig, ax = plt.subplots(figsize=(13, 6.5), dpi=200)
ax.set_xlim(0, 1.05)
ax.set_ylim(-3, 3)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Línea de tiempo principal
ax.plot([0, 1.0], [0, 0], color=TIMELINE_COLOR, linewidth=2.5, zorder=1)
# Punto inicial y final
ax.plot([0], [0], "o", color=TIMELINE_COLOR, markersize=8, zorder=2)
ax.plot([1.0], [0], ">", color=TIMELINE_COLOR, markersize=12, zorder=2)

# Eventos
for x, year, autor, desc, fill, edge, h in events:
    # Marca en el timeline
    ax.plot([x], [0], "o", color=edge, markersize=9, zorder=3)
    # Línea vertical fina hasta el cuadro
    ax.plot([x, x], [0, h * 0.5], color=edge, linewidth=0.8, alpha=0.6, zorder=2)
    # Cuadro de descripción
    box_y = h * 0.55 if h > 0 else h * 0.55 - 1.05
    box = FancyBboxPatch((x - 0.07, box_y), 0.14, 1.0,
                         boxstyle="round,pad=0.02",
                         facecolor=fill, edgecolor=edge, linewidth=1.3)
    ax.add_patch(box)
    # Año
    year_y = box_y + 0.85
    ax.text(x, year_y, year, ha="center", va="center",
            fontsize=8, fontweight="bold", color=edge)
    # Autor
    ax.text(x, year_y - 0.25, autor, ha="center", va="center",
            fontsize=9, fontweight="bold", color=INK)
    # Descripción
    ax.text(x, year_y - 0.65, desc, ha="center", va="center",
            fontsize=7.5, color=INK)

# Banderas de tradición (a la derecha)
ax.text(0.5, 2.65, "Cuatro tradiciones independientes, mismo descubrimiento",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)

# Leyenda inferior
legend_items = [
    ("#1d4ed8", "Filosofía moral y retórica clásica"),
    ("#b45309", "Periodismo profesional"),
    ("#15803d", "Lingüística formal y semántica"),
]
for i, (color, label) in enumerate(legend_items):
    x_legend = 0.05 + i * 0.30
    ax.plot([x_legend], [-2.65], "s", color=color, markersize=12)
    ax.text(x_legend + 0.02, -2.65, label, ha="left", va="center",
            fontsize=10, color=INK)

# Resumen abajo del todo
ax.text(0.5, -2.95,
        "Las preguntas reaparecen en contextos disímiles porque no son convención cultural,\nsino la descomposición que la mente humana hace ante un hecho del mundo.",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "04_convergencia_tradiciones.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
