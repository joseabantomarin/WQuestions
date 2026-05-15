"""Diagrama: evento reificado n-ario.
'Messi le pasó el balón a Di María en el minuto 87 con un toque de pierna izquierda.'

Salida: ../png/14_evento_reificado.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

fig, ax = plt.subplots(figsize=(12, 8), dpi=200)
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(6, 7.65, "Eventos n-arios: cuando una tripleta no alcanza",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)

# Quote
quote_box = FancyBboxPatch((1.5, 6.5), 9, 0.7, boxstyle="round,pad=0.04",
                           facecolor="#f9fafb", edgecolor="#9ca3af", linewidth=1)
ax.add_patch(quote_box)
ax.text(6, 6.85,
        '"Messi le pasó el balón a Di María en el minuto 87 con un toque de pierna izquierda."',
        ha="center", va="center", fontsize=11, style="italic", color=INK)

# Evento reificado en el centro
ev_x, ev_y = 6, 3.5
ev_box = FancyBboxPatch((ev_x - 1.0, ev_y - 0.5), 2.0, 1.0,
                        boxstyle="round,pad=0.06",
                        facecolor="#dcfce7", edgecolor="#15803d", linewidth=2.2)
ax.add_patch(ev_box)
ax.text(ev_x, ev_y + 0.15, "pase_001", ha="center", va="center",
        fontsize=12, fontweight="bold", color="#15803d", family="monospace")
ax.text(ev_x, ev_y - 0.20, "∈ O  (reificado)", ha="center", va="center",
        fontsize=8.5, style="italic", color="#6b7280")

# Participantes en torno al evento
participants = [
    # (x, y, label, eje, color_fill, color_edge, predicado, color_pred, conexion_angle)
    (1.5, 5.5, "accion_pasar",      "K", "#e0e7ff", "#4f46e5", "instancia_de", "#15803d"),
    (1.0, 3.5, "messi",             "Q", "#dbeafe", "#1d4ed8", "agente",       "#b45309"),
    (1.5, 1.5, "di_maria",          "Q", "#dbeafe", "#1d4ed8", "beneficiario", "#b45309"),
    (5.5, 1.0, "balon_partido_001", "O", "#e0e7ff", "#4f46e5", "objeto_pase",  "#b45309"),
    (9.0, 1.5, "87",                "N", "#fef3c7", "#b45309", "minuto",       "#1d4ed8"),
    (10.5,3.5, "pierna_izquierda",  "K", "#e0e7ff", "#4f46e5", "instrumento",  "#1d4ed8"),
    (9.0, 5.5, "minuto_87_partido", "T", "#fed7aa", "#c2410c", "momento",      "#1d4ed8"),
]

for x, y, label, eje, fill, edge, pred, pcolor in participants:
    # Caja del participante
    width = max(1.3, len(label) * 0.12 + 0.6)
    box = FancyBboxPatch((x - width/2, y - 0.30), width, 0.6,
                         boxstyle="round,pad=0.04",
                         facecolor=fill, edgecolor=edge, linewidth=1.3)
    ax.add_patch(box)
    ax.text(x, y + 0.05, label, ha="center", va="center",
            fontsize=9, fontweight="bold", color=edge, family="monospace")
    ax.text(x, y - 0.16, f"∈ {eje}", ha="center", va="center",
            fontsize=7.5, style="italic", color="#6b7280")

    # Flecha desde el evento al participante
    arrow = FancyArrowPatch((ev_x, ev_y), (x, y),
                            arrowstyle="-|>", mutation_scale=11,
                            color=pcolor, linewidth=1.1,
                            connectionstyle="arc3,rad=0.0")
    ax.add_patch(arrow)
    # Etiqueta del predicado en mitad del recorrido
    mx, my = (ev_x + x)/2, (ev_y + y)/2
    ax.text(mx, my, pred, ha="center", va="center",
            fontsize=8, style="italic", color=pcolor,
            bbox=dict(boxstyle="round,pad=0.10", facecolor="white",
                      edgecolor="none", alpha=0.95))

# Pie
ax.text(6, 0.4,
        "Una oración n-aria se descompone en seis hechos atómicos sobre el evento reificado.\nCada uno verificable, consultable y componible por separado.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "14_evento_reificado.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
