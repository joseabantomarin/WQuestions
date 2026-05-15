"""Diagrama: la asignación de un viaje con cuatro participantes.

Muestra el `asignar` con sus 4 roles: app (agente), solicitud (tema),
conductor (beneficiario), vehículo (instrumento). Tres participantes
en Q, uno en O.

Salida: ../png/30_asignacion_multi_agente.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
Q_FILL, Q_EDGE = "#dbeafe", "#1d4ed8"
O_FILL, O_EDGE = "#dcfce7", "#15803d"

fig, ax = plt.subplots(figsize=(14, 9), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 8.55, "Asignación de un viaje: agencia repartida (D5)",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 8.15,
        "Cuatro participantes con cuatro roles distintos. El app entra al eje Q como agente del verbo.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Situación central: la asignación
cx, cy = 7, 4.7
ev_box = FancyBboxPatch((cx - 1.7, cy - 0.65), 3.4, 1.3,
                        boxstyle="round,pad=0.06",
                        facecolor=O_FILL, edgecolor=O_EDGE, linewidth=2.6)
ax.add_patch(ev_box)
ax.text(cx, cy + 0.25, "asig_001",
        ha="center", va="center", fontsize=13, fontweight="bold",
        color=O_EDGE, family="monospace")
ax.text(cx, cy - 0.10, "∈ O", ha="center", va="center",
        fontsize=9, color="#6b7280")
ax.text(cx, cy - 0.40, "instancia_de: accion_asignar",
        ha="center", va="center", fontsize=8.5,
        style="italic", color="#374151", family="monospace")

# Cuatro participantes alrededor
participants = [
    {"label": "App RideEasy",   "axis": "Q", "role": "agente",
     "x": 2.0, "y": 7.2, "note": "agente software (D5)"},
    {"label": "sol_001",         "axis": "O", "role": "tema",
     "x": 12.0, "y": 7.2, "note": "la solicitud previa"},
    {"label": "Luis",            "axis": "Q", "role": "beneficiario",
     "x": 2.0, "y": 2.2, "note": "conductor humano"},
    {"label": "vehiculo_abc123", "axis": "O", "role": "instrumento",
     "x": 12.0, "y": 2.2, "note": "Toyota ABC-123"},
]

for p in participants:
    is_q = p["axis"] == "Q"
    fill = Q_FILL if is_q else O_FILL
    edge = Q_EDGE if is_q else O_EDGE
    box = FancyBboxPatch((p["x"] - 1.45, p["y"] - 0.50), 2.9, 1.0,
                         boxstyle="round,pad=0.05",
                         facecolor=fill, edgecolor=edge, linewidth=1.8)
    ax.add_patch(box)
    ax.text(p["x"], p["y"] + 0.20, p["label"],
            ha="center", va="center", fontsize=10.5, fontweight="bold",
            color=edge, family="monospace")
    ax.text(p["x"], p["y"] - 0.10, f"∈ {p['axis']}",
            ha="center", va="center", fontsize=9,
            style="italic", color="#6b7280")
    ax.text(p["x"], p["y"] - 0.32, p["note"],
            ha="center", va="center", fontsize=8,
            style="italic", color="#374151")

    # Flecha desde la situación al participante
    arr = FancyArrowPatch((cx, cy), (p["x"], p["y"]),
                          arrowstyle="-|>", mutation_scale=13,
                          color=edge, linewidth=1.4)
    ax.add_patch(arr)

    # Etiqueta del rol en la flecha
    mx = (cx + p["x"]) / 2
    my = (cy + p["y"]) / 2
    ax.text(mx, my, p["role"],
            ha="center", va="center", fontsize=9.5, fontweight="bold",
            color=edge, family="monospace",
            bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                      edgecolor=edge, linewidth=0.9, alpha=0.97))

# Caja inferior: el viaje articulador
viaje_box = FancyBboxPatch((5.0, 0.3), 4.0, 0.65,
                           boxstyle="round,pad=0.05",
                           facecolor="#dcfce7", edgecolor=O_EDGE,
                           linewidth=1.5)
ax.add_patch(viaje_box)
ax.text(7.0, 0.62, "viaje_001",
        ha="center", va="center", fontsize=10.5, fontweight="bold",
        color=O_EDGE, family="monospace")
ax.text(7.0, 0.40, "(entidad articuladora — asig_001 es parte_de viaje_001)",
        ha="center", va="center", fontsize=8.5,
        style="italic", color="#6b7280")
ax.annotate("", xy=(7.0, 0.95), xytext=(7.0, 4.05),
            arrowprops=dict(arrowstyle="-", color="#9ca3af",
                            lw=0.7, linestyle="dashed"))
ax.text(7.45, 2.5, "parte_de",
        ha="left", va="center", fontsize=8.5,
        style="italic", color="#9ca3af", family="monospace")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "30_asignacion_multi_agente.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
