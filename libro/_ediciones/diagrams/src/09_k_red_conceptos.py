"""Diagrama: K como red de conceptos (no saco plano).
Muestra `instancia_de` y `subtipo_de` operando juntas, con un ejemplo concreto
de un jugador y sus categorías jerárquicas.

Salida: ../png/09_k_red_conceptos.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
K_FILL = "#e0e7ff"
K_EDGE = "#4f46e5"
Q_FILL = "#dbeafe"
Q_EDGE = "#1d4ed8"

fig, ax = plt.subplots(figsize=(11, 8), dpi=200)
ax.set_xlim(0, 11)
ax.set_ylim(0, 8)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(5.5, 7.65, "K no es un saco plano: es una red de conceptos",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)

# Nodos K (categorías) — jerarquía
k_nodes = [
    # (id, x, y, label, sub)
    ("persona", 5.5, 6.6, "persona_humana", "K"),
    ("atleta",  5.5, 5.4, "atleta_profesional", "K"),
    ("jugador", 3.3, 4.2, "jugador_de_futbol", "K"),
    ("capitan", 6.7, 4.2, "capitan_de_seleccion", "K"),
    ("ganador", 9.0, 5.4, "ganador_balon_de_oro", "K"),
]

# Dibujar nodos K
node_coords = {}
for id_, x, y, label, sub in k_nodes:
    box = FancyBboxPatch((x - 1.0, y - 0.30), 2.0, 0.6,
                         boxstyle="round,pad=0.04",
                         facecolor=K_FILL, edgecolor=K_EDGE, linewidth=1.5)
    ax.add_patch(box)
    ax.text(x, y + 0.05, label, ha="center", va="center",
            fontsize=9.5, fontweight="bold", color=K_EDGE)
    ax.text(x, y - 0.15, "∈ K", ha="center", va="center",
            fontsize=7.5, style="italic", color="#6b7280")
    node_coords[id_] = (x, y)

# Flechas de subtipo_de (entre categorías)
subtype_edges = [
    ("atleta", "persona"),
    ("jugador", "atleta"),
    ("capitan", "atleta"),
]
for src, tgt in subtype_edges:
    sx, sy = node_coords[src]
    tx, ty = node_coords[tgt]
    arrow = FancyArrowPatch((sx, sy + 0.30), (tx, ty - 0.30),
                            arrowstyle="-|>", mutation_scale=12,
                            color=K_EDGE, linewidth=1.2,
                            connectionstyle="arc3,rad=0.0")
    ax.add_patch(arrow)
    # Etiqueta
    mid_x = (sx + tx) / 2
    mid_y = (sy + ty) / 2
    ax.text(mid_x + 0.10, mid_y, "subtipo_de",
            ha="left", va="center", fontsize=7.5, style="italic", color=K_EDGE,
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor="none", alpha=0.85))

# Nodo de instancia (Messi en Q)
messi_x, messi_y = 5.5, 1.5
box = FancyBboxPatch((messi_x - 0.7, messi_y - 0.30), 1.4, 0.6,
                     boxstyle="round,pad=0.04",
                     facecolor=Q_FILL, edgecolor=Q_EDGE, linewidth=1.6)
ax.add_patch(box)
ax.text(messi_x, messi_y + 0.05, "messi",
        ha="center", va="center", fontsize=11, fontweight="bold", color=Q_EDGE)
ax.text(messi_x, messi_y - 0.15, "∈ Q", ha="center", va="center",
        fontsize=7.5, style="italic", color="#6b7280")

# Flechas instancia_de (Messi → varias categorías)
instance_edges = ["jugador", "capitan", "ganador"]
for tgt in instance_edges:
    tx, ty = node_coords[tgt]
    arrow = FancyArrowPatch((messi_x, messi_y + 0.30), (tx, ty - 0.30),
                            arrowstyle="-|>", mutation_scale=12,
                            color="#15803d", linewidth=1.2,
                            connectionstyle="arc3,rad=0.0")
    ax.add_patch(arrow)
    mid_x = (messi_x + tx) / 2
    mid_y = (messi_y + ty) / 2
    ax.text(mid_x, mid_y, "instancia_de",
            ha="center", va="center", fontsize=7.5, style="italic", color="#15803d",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor="none", alpha=0.85))

# Leyenda
legend_y = 0.55
ax.plot([0.8], [legend_y], "s", color=K_EDGE, markersize=11)
ax.text(1.0, legend_y, "categoría (en K)", ha="left", va="center",
        fontsize=9, color=INK)
ax.plot([3.5], [legend_y], "s", color=Q_EDGE, markersize=11)
ax.text(3.7, legend_y, "individuo (aquí, en Q)", ha="left", va="center",
        fontsize=9, color=INK)
ax.annotate("", xy=(6.5, legend_y), xytext=(6.0, legend_y),
            arrowprops=dict(arrowstyle="-|>", color=K_EDGE, lw=1.2))
ax.text(6.7, legend_y, "subtipo_de", ha="left", va="center",
        fontsize=9, color=K_EDGE)
ax.annotate("", xy=(9.0, legend_y), xytext=(8.5, legend_y),
            arrowprops=dict(arrowstyle="-|>", color="#15803d", lw=1.2))
ax.text(9.2, legend_y, "instancia_de", ha="left", va="center",
        fontsize=9, color="#15803d")

# Pie
ax.text(5.5, 0.10,
        "Con subtipo_de e instancia_de, el motor infiere transitivamente:\nsi Messi es jugador_de_futbol y eso es subtipo_de atleta_profesional, Messi es atleta_profesional.",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "09_k_red_conceptos.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
