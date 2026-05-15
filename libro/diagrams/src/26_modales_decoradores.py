"""Diagrama: los modales no crean situaciones, las decoran.
Cuatro oraciones modales que comparten el mismo verbo nuclear "viajar" y
producen la misma situación reificada, con distintas propiedades de
modalidad y estatus factual.

Salida: ../png/26_modales_decoradores.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
O_FILL, O_EDGE = "#dcfce7", "#15803d"

fig, ax = plt.subplots(figsize=(14, 9.5), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 9.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 9.10, "Los modales no crean situaciones: las decoran",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 8.70,
        "Cuatro modalidades sobre el mismo evento \"viajar\": una sola situación reificada, propiedades distintas.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Cuatro oraciones de entrada (arriba)
sentences = [
    {"x": 1.95, "text": "\"Juan viaja\nmañana.\"",
        "fill": "#dcfce7", "edge": "#15803d",
        "modalidad": "—",
        "factual": "real",
        "polaridad": "afirm."},
    {"x": 5.30, "text": "\"Juan quiere\nviajar mañana.\"",
        "fill": "#dbeafe", "edge": "#1d4ed8",
        "modalidad": "volitiva",
        "factual": "intencionado",
        "polaridad": "afirm."},
    {"x": 8.70, "text": "\"Juan debe\nviajar mañana.\"",
        "fill": "#fef3c7", "edge": "#b45309",
        "modalidad": "deóntica",
        "factual": "obligatorio",
        "polaridad": "afirm."},
    {"x": 12.05, "text": "\"Juan no puede\nviajar mañana.\"",
        "fill": "#fee2e2", "edge": "#b91c1c",
        "modalidad": "alética",
        "factual": "no_realizable",
        "polaridad": "neg."},
]

for s in sentences:
    box = FancyBboxPatch((s["x"] - 1.50, 7.30), 3.0, 1.0,
                         boxstyle="round,pad=0.05",
                         facecolor=s["fill"], edgecolor=s["edge"],
                         linewidth=1.6)
    ax.add_patch(box)
    ax.text(s["x"], 7.80, s["text"],
            ha="center", va="center", fontsize=10.5,
            color=s["edge"], family="serif")

# Situación reificada central — única
sit_y = 5.0
sit_box = FancyBboxPatch((5.0, sit_y - 0.6), 4.0, 1.2,
                         boxstyle="round,pad=0.06",
                         facecolor=O_FILL, edgecolor=O_EDGE, linewidth=2.6)
ax.add_patch(sit_box)
ax.text(7.0, sit_y + 0.20, "viajar_001",
        ha="center", va="center", fontsize=13, fontweight="bold",
        color=O_EDGE, family="monospace")
ax.text(7.0, sit_y - 0.20, "∈ O   (una sola situación)",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

# Flechas desde cada oración a la misma situación
for s in sentences:
    arr = FancyArrowPatch((s["x"], 7.30), (7.0, sit_y + 0.6),
                          arrowstyle="-|>", mutation_scale=12,
                          color=s["edge"], linewidth=1.1, alpha=0.7,
                          connectionstyle="arc3,rad=0.0")
    ax.add_patch(arr)

# Hechos atómicos compartidos (base del verbo, abajo izquierda)
shared_facts = [
    "instancia_de:    accion_viajar",
    "agente:          juan",
    "destino:         cusco",
    "momento:         2026-05-16",
]
sf_box = FancyBboxPatch((0.6, 2.4), 5.5, 1.7,
                        boxstyle="round,pad=0.05",
                        facecolor="#f9fafb", edgecolor=O_EDGE,
                        linewidth=1.2)
ax.add_patch(sf_box)
ax.text(3.35, 3.92, "hechos compartidos por las 4 lecturas",
        ha="center", va="center", fontsize=9, fontweight="bold",
        color=O_EDGE, style="italic")
for i, f in enumerate(shared_facts):
    ax.text(0.85, 3.50 - i * 0.28, f,
            ha="left", va="center", fontsize=9,
            color="#374151", family="monospace")

# Hechos diferenciadores (decoradores) — tabla
diff_box = FancyBboxPatch((6.4, 2.4), 7.0, 1.7,
                          boxstyle="round,pad=0.05",
                          facecolor="#f9fafb", edgecolor="#9ca3af",
                          linewidth=1.2)
ax.add_patch(diff_box)
ax.text(9.9, 3.92, "hechos que cambian según la modalidad (los \"decoradores\")",
        ha="center", va="center", fontsize=9, fontweight="bold",
        color="#374151", style="italic")
# Encabezado
ax.text(7.0, 3.55, "modalidad",
        ha="left", va="center", fontsize=8.5,
        color="#374151", family="monospace", fontweight="bold")
ax.text(9.4, 3.55, "estatus_factual",
        ha="left", va="center", fontsize=8.5,
        color="#374151", family="monospace", fontweight="bold")
ax.text(11.9, 3.55, "polaridad",
        ha="left", va="center", fontsize=8.5,
        color="#374151", family="monospace", fontweight="bold")
# Filas: una por lectura
for i, s in enumerate(sentences):
    rowy = 3.20 - i * 0.20
    # marcador de color
    chip = FancyBboxPatch((6.55, rowy - 0.05), 0.12, 0.12,
                          boxstyle="round,pad=0.005",
                          facecolor=s["edge"], edgecolor="none")
    ax.add_patch(chip)
    ax.text(7.0, rowy, s["modalidad"],
            ha="left", va="center", fontsize=8.3,
            color=s["edge"], family="monospace")
    ax.text(9.4, rowy, s["factual"],
            ha="left", va="center", fontsize=8.3,
            color=s["edge"], family="monospace")
    ax.text(11.9, rowy, s["polaridad"],
            ha="left", va="center", fontsize=8.3,
            color=s["edge"], family="monospace")

# Flecha desde la situación a las cajas de hechos
ax.annotate("", xy=(3.35, 4.10), xytext=(7.0, sit_y - 0.6),
            arrowprops=dict(arrowstyle="-", color="#9ca3af", lw=0.8))
ax.annotate("", xy=(9.9, 4.10), xytext=(7.0, sit_y - 0.6),
            arrowprops=dict(arrowstyle="-", color="#9ca3af", lw=0.8))

# Pie
ax.text(7, 1.4,
        "Querer / deber / poder no son situaciones del mundo: son cualidades del registro de viajar_001.",
        ha="center", va="center", fontsize=10, color="#374151")
ax.text(7, 1.0,
        "Una situación, varios estados modales. El grafo no se infla con verbos auxiliares reificados.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "26_modales_decoradores.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
