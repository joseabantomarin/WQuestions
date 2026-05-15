"""Diagrama: la cadena de 6 situaciones que componen un viaje.

solicitar → asignar → aceptar → recoger → trasladar → completar,
con flechas `sigue_a` (temporal) y `motivado_por` (causal), y todo
parte_de un viaje_001 articulador.

Salida: ../png/29_cadena_viaje.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
O_FILL, O_EDGE = "#dcfce7", "#15803d"

fig, ax = plt.subplots(figsize=(16, 9), dpi=200)
ax.set_xlim(0, 16)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(8, 8.55, "Un viaje del taxi como cadena de 6 situaciones",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(8, 8.15,
        "Cada situación se sigue de la anterior (sigue_a) y todas pertenecen al viaje articulador (parte_de).",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# 6 cajas en línea, bien espaciadas
situations = [
    ("solicitar", "14:30", "Valeria"),
    ("asignar",   "14:31", "App"),
    ("aceptar",   "14:32", "Luis"),
    ("recoger",   "14:38", "Luis"),
    ("trasladar", "14:40", "Luis"),
    ("completar", "15:05", "Luis"),
]

# Distribución con buen aire
box_w = 1.8
xs = [1.3 + i * 2.45 for i in range(6)]  # 1.3, 3.75, 6.20, 8.65, 11.10, 13.55
chain_y = 5.0

for (verb, hora, agnt), x in zip(situations, xs):
    box = FancyBboxPatch((x - box_w/2, chain_y - 0.55), box_w, 1.1,
                         boxstyle="round,pad=0.05",
                         facecolor=O_FILL, edgecolor=O_EDGE, linewidth=1.8)
    ax.add_patch(box)
    ax.text(x, chain_y + 0.25, verb,
            ha="center", va="center", fontsize=11, fontweight="bold",
            color=O_EDGE, family="monospace")
    ax.text(x, chain_y - 0.08, hora,
            ha="center", va="center", fontsize=9.5,
            color="#6b7280", family="monospace")
    ax.text(x, chain_y - 0.35, f"agente: {agnt}",
            ha="center", va="center", fontsize=8.5,
            color="#374151", family="monospace")

# Flechas sigue_a (entre sucesivas)
for i in range(len(situations) - 1):
    x1 = xs[i] + box_w/2
    x2 = xs[i+1] - box_w/2
    arr = FancyArrowPatch((x1, chain_y), (x2, chain_y),
                          arrowstyle="-|>", mutation_scale=12,
                          color="#9ca3af", linewidth=1.4)
    ax.add_patch(arr)
    ax.text((x1 + x2) / 2, chain_y + 0.20, "sigue_a",
            ha="center", va="center", fontsize=7.5,
            color="#6b7280", style="italic", family="monospace")

# Flechas motivado_por en arco por encima
def curve_arrow(x1, x2, y_base, label, color="#b45309", rad=-0.35, lift=1.0):
    arr = FancyArrowPatch((x1, y_base), (x2, y_base),
                          arrowstyle="-|>", mutation_scale=13,
                          color=color, linewidth=1.4,
                          connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(arr)
    ax.text((x1 + x2) / 2, y_base + lift, label,
            ha="center", va="center", fontsize=8.5,
            color=color, fontweight="bold", family="monospace",
            bbox=dict(boxstyle="round,pad=0.16", facecolor="white",
                      edgecolor=color, linewidth=0.9, alpha=0.97))

# motivado_por: asignar (xs[1]) ← solicitar (xs[0])
curve_arrow(xs[1], xs[0], chain_y + 0.55, "motivado_por",
            color="#b45309", rad=-0.55, lift=0.8)
# motivado_por: recoger (xs[3]) ← solicitar (xs[0]) — arco grande
curve_arrow(xs[3], xs[0], chain_y + 0.55, "motivado_por (raíz)",
            color="#b45309", rad=-0.45, lift=1.2)

# Entidad articuladora superior
viaje_y = 1.8
viaje_box = FancyBboxPatch((5.5, viaje_y - 0.55), 5.0, 1.1,
                           boxstyle="round,pad=0.06",
                           facecolor="#dcfce7", edgecolor=O_EDGE,
                           linewidth=2.6)
ax.add_patch(viaje_box)
ax.text(8.0, viaje_y + 0.22, "viaje_001",
        ha="center", va="center", fontsize=14, fontweight="bold",
        color=O_EDGE, family="monospace")
ax.text(8.0, viaje_y - 0.13, "∈ O   (entidad articuladora del viaje)",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")
ax.text(8.0, viaje_y - 0.38, "estatus_factual: completado",
        ha="center", va="center", fontsize=8.5,
        color="#374151", family="monospace")

# Flechas parte_de
for x in xs:
    arr = FancyArrowPatch((x, chain_y - 0.55), (8.0, viaje_y + 0.55),
                          arrowstyle="-", color="#9ca3af",
                          linewidth=0.7, linestyle="dashed",
                          connectionstyle="arc3,rad=0.0")
    ax.add_patch(arr)
ax.text(12.5, 3.4, "todas parte_de  viaje_001",
        ha="left", va="center", fontsize=9, style="italic",
        color="#9ca3af", family="monospace")

# Pie
ax.text(8, 0.5,
        "Dos relaciones distintas: temporal (sigue_a) y motivacional (motivado_por).\n"
        "El viaje completo como nodo único permite facturar, refundir o auditar en una sola operación.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "29_cadena_viaje.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
