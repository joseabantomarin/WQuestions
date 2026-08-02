"""Diagrama: anatomía de una situación reificada.
La consulta médica como nodo central con todos sus participantes y propiedades,
más las situaciones derivadas (prescripción, pago, control futuro) conectadas
por relaciones canónicas.

Salida: ../png/17_situacion_reificada.png
"""

import os
import math
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
O_FILL, O_EDGE = "#dcfce7", "#15803d"
Q_FILL, Q_EDGE = "#dbeafe", "#1d4ed8"
T_FILL, T_EDGE = "#fed7aa", "#c2410c"
L_FILL, L_EDGE = "#fef3c7", "#b45309"
K_FILL, K_EDGE = "#e0e7ff", "#4f46e5"

fig, ax = plt.subplots(figsize=(14, 9), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 8.55, "Anatomía de una situación reificada",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 8.15,
        "La consulta médica como punto articulador del grafo",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Situación central: la consulta
center_x, center_y = 7, 5.0
ev_box = FancyBboxPatch((center_x - 1.4, center_y - 0.55), 2.8, 1.1,
                        boxstyle="round,pad=0.06",
                        facecolor=O_FILL, edgecolor=O_EDGE, linewidth=2.5)
ax.add_patch(ev_box)
ax.text(center_x, center_y + 0.2, "consulta_2026_05_14",
        ha="center", va="center", fontsize=11, fontweight="bold",
        color=O_EDGE, family="monospace")
ax.text(center_x, center_y - 0.15, "∈ O  (situación reificada)",
        ha="center", va="center", fontsize=8.5, style="italic", color="#6b7280")

# Participantes y propiedades — distribución radial
nodes = [
    # (x, y, label, eje, fill, edge, relacion)
    (2.0, 7.0,  "accion_consultar",   "K", K_FILL, K_EDGE, "instancia_de"),
    (12.0,7.0,  "dra_torres",         "Q", Q_FILL, Q_EDGE, "agente"),
    (0.8, 5.0,  "maria_gonzales",     "Q", Q_FILL, Q_EDGE, "paciente"),
    (13.2,5.0,  "2026-05-14\n10:30 UTC","T", T_FILL, T_EDGE, "momento"),
    (2.0, 3.0,  "consultorio_03",     "L", L_FILL, L_EDGE, "lugar_de"),
    (12.0,3.0,  "control_rutinario",  "K", K_FILL, K_EDGE, "motivo"),
    (5.0, 1.4,  "hipertension_g1",    "K", K_FILL, K_EDGE, "diagnostico"),
    (9.0, 1.4,  "real",               "K", K_FILL, K_EDGE, "estatus_factual"),
]

for x, y, label, eje, fill, edge, rel in nodes:
    box = FancyBboxPatch((x - 1.0, y - 0.30), 2.0, 0.6,
                         boxstyle="round,pad=0.03",
                         facecolor=fill, edgecolor=edge, linewidth=1.3)
    ax.add_patch(box)
    ax.text(x, y + 0.05, label, ha="center", va="center",
            fontsize=8.5, fontweight="bold", color=edge, family="monospace")
    ax.text(x, y - 0.18, f"∈ {eje}", ha="center", va="center",
            fontsize=7.5, style="italic", color="#6b7280")

    # Flecha
    arr = FancyArrowPatch((center_x, center_y), (x, y),
                          arrowstyle="-|>", mutation_scale=10,
                          color="#6b7280", linewidth=0.9,
                          connectionstyle="arc3,rad=0.0")
    ax.add_patch(arr)
    # Etiqueta del predicado
    mx = (center_x + x) / 2
    my = (center_y + y) / 2
    ax.text(mx, my, rel, ha="center", va="center",
            fontsize=8, style="italic", color="#374151",
            bbox=dict(boxstyle="round,pad=0.10", facecolor="white",
                      edgecolor="none", alpha=0.95))

# Situaciones derivadas (abajo)
derived = [
    (3.0, 0.3, "prescripcion_017", "parte_de"),
    (7.0, 0.3, "pago_001",         "sobre_situacion"),
    (11.0, 0.3, "control_futuro_001", "prevista_por"),
]
for x, y, label, rel in derived:
    box = FancyBboxPatch((x - 1.2, y - 0.18), 2.4, 0.36,
                         boxstyle="round,pad=0.02",
                         facecolor=O_FILL, edgecolor=O_EDGE, linewidth=1.0)
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center",
            fontsize=8, fontweight="bold", color=O_EDGE, family="monospace")
    # Flecha hacia la consulta
    arr = FancyArrowPatch((x, y + 0.18), (center_x, center_y - 0.55),
                          arrowstyle="-|>", mutation_scale=10,
                          color=O_EDGE, linewidth=0.9,
                          connectionstyle="arc3,rad=0.15")
    ax.add_patch(arr)
    # Etiqueta
    mx = (x + center_x) / 2
    my = (y + center_y - 0.55) / 2 - 0.2
    ax.text(mx, my, rel, ha="center", va="center",
            fontsize=7.5, style="italic", color=O_EDGE,
            bbox=dict(boxstyle="round,pad=0.08", facecolor="white",
                      edgecolor="none", alpha=0.9))

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "17_situacion_reificada.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
