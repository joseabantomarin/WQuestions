"""Diagrama: las cuatro relaciones canónicas del 'por qué'.
Una situación central conectada a cuatro situaciones de tipos distintos —
causa previa, intención del agente, estado futuro buscado, regla
que la autoriza — por relaciones canónicas distintas.

Salida: ../png/19_cuatro_por_que.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
O_FILL, O_EDGE = "#dcfce7", "#15803d"

# Colores por tipo de relación
CAUSA_FILL, CAUSA_EDGE = "#fee2e2", "#b91c1c"        # rojo — causa física
MOTIVO_FILL, MOTIVO_EDGE = "#fef3c7", "#b45309"      # ámbar — motivo intencional
FIN_FILL, FIN_EDGE = "#dbeafe", "#1d4ed8"            # azul — finalidad futura
NORMA_FILL, NORMA_EDGE = "#e0e7ff", "#4f46e5"        # índigo — regla normativa

fig, ax = plt.subplots(figsize=(14, 9), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 8.55, "Las cuatro relaciones canónicas del \"por qué\"",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 8.15,
        "Una misma situación puede tener simultáneamente causa, motivo, finalidad y justificación.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Situación central
cx, cy = 7, 4.6
ev_box = FancyBboxPatch((cx - 1.6, cy - 0.6), 3.2, 1.2,
                        boxstyle="round,pad=0.06",
                        facecolor=O_FILL, edgecolor=O_EDGE, linewidth=2.5)
ax.add_patch(ev_box)
ax.text(cx, cy + 0.20, "cirugia_023",
        ha="center", va="center", fontsize=12, fontweight="bold",
        color=O_EDGE, family="monospace")
ax.text(cx, cy - 0.20, "∈ O  (la acción a explicar)",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

# Cuatro nodos en cruz alrededor
nodes = [
    # (x, y, label, sub, rel_name, fill, edge, semantica)
    (2.3, 6.8,  "tumor_001",            "situación previa",
        "causado_por",     CAUSA_FILL, CAUSA_EDGE,
        "causalidad física"),
    (11.7, 6.8, "pedido_paciente_001",  "intención del agente",
        "motivado_por",    MOTIVO_FILL, MOTIVO_EDGE,
        "motivación humana"),
    (2.3, 2.3,  "extirpacion_tumor_001","estado futuro buscado",
        "con_finalidad",   FIN_FILL, FIN_EDGE,
        "propósito teleológico"),
    (11.7, 2.3, "protocolo_oncologico_2025", "regla previa",
        "justificado_por", NORMA_FILL, NORMA_EDGE,
        "autoridad normativa"),
]

for x, y, label, sub, rel, fill, edge, sem in nodes:
    box = FancyBboxPatch((x - 1.4, y - 0.45), 2.8, 0.9,
                         boxstyle="round,pad=0.05",
                         facecolor=fill, edgecolor=edge, linewidth=1.8)
    ax.add_patch(box)
    ax.text(x, y + 0.13, label, ha="center", va="center",
            fontsize=10, fontweight="bold", color=edge, family="monospace")
    ax.text(x, y - 0.20, sub, ha="center", va="center",
            fontsize=8.5, style="italic", color="#6b7280")

    # Flecha desde el centro hacia este nodo
    arr = FancyArrowPatch((cx, cy), (x, y),
                          arrowstyle="-|>", mutation_scale=14,
                          color=edge, linewidth=1.6,
                          connectionstyle="arc3,rad=0.0")
    ax.add_patch(arr)
    # Etiqueta del predicado en la flecha
    mx = (cx + x) / 2
    my = (cy + y) / 2
    ax.text(mx, my, rel, ha="center", va="center",
            fontsize=9, fontweight="bold", color=edge,
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                      edgecolor=edge, alpha=0.95, linewidth=0.8))
    # Semántica abajo del nodo
    ax.text(x, y - 0.70, sem, ha="center", va="center",
            fontsize=8, color=edge)

# Caja de pie: por qué cuatro y no una
ax.text(7, 0.55,
        "Las cuatro respuestas son del mismo \"porque\" superficial, pero ontológicamente distintas:\n"
        "una causa previa, una intención del agente, un estado futuro y una norma. Tratarlas como cuatro\n"
        "relaciones — y no un único eje — preserva la distinción que el lenguaje natural ya hace.",
        ha="center", va="center", fontsize=9.5, color="#374151")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "19_cuatro_por_que.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
