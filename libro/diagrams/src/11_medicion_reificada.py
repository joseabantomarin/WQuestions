"""Diagrama: medición reificada — un valor de N siempre va acompañado de unidad
en K, y cuando hace falta más detalle, se reifica como situación en O.

Salida: ../png/11_medicion_reificada.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
N_FILL, N_EDGE = "#fef3c7", "#b45309"
K_FILL, K_EDGE = "#e0e7ff", "#4f46e5"
O_FILL, O_EDGE = "#dbeafe", "#1d4ed8"

fig, ax = plt.subplots(figsize=(13, 7), dpi=200)
ax.set_xlim(0, 13)
ax.set_ylim(0, 7)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(6.5, 6.6, "Un número nunca viaja solo: cantidad + unidad (+ contexto)",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)

# IZQUIERDA — versión simple
ax.text(2.7, 5.9, "Versión simple", ha="center", va="center",
        fontsize=12, fontweight="bold", color=INK)
ax.text(2.7, 5.55, "(unidad como propiedad)", ha="center", va="center",
        fontsize=9, style="italic", color="#6b7280")

# Hecho 1: el número
n_box = FancyBboxPatch((0.5, 4.0), 1.4, 0.9, boxstyle="round,pad=0.04",
                       facecolor=N_FILL, edgecolor=N_EDGE, linewidth=1.5)
ax.add_patch(n_box)
ax.text(1.2, 4.55, "340", ha="center", va="center",
        fontsize=15, fontweight="bold", color=N_EDGE)
ax.text(1.2, 4.20, "∈ N", ha="center", va="center",
        fontsize=8, style="italic", color="#6b7280")

# Unidad en K
k_box = FancyBboxPatch((3.5, 4.0), 1.6, 0.9, boxstyle="round,pad=0.04",
                       facecolor=K_FILL, edgecolor=K_EDGE, linewidth=1.5)
ax.add_patch(k_box)
ax.text(4.3, 4.55, "milisegundo", ha="center", va="center",
        fontsize=11, fontweight="bold", color=K_EDGE)
ax.text(4.3, 4.20, "∈ K", ha="center", va="center",
        fontsize=8, style="italic", color="#6b7280")

# Sujeto (la situación a la que pertenece la medición)
sujeto_box = FancyBboxPatch((1.8, 2.3), 2.0, 0.8, boxstyle="round,pad=0.04",
                            facecolor=O_FILL, edgecolor=O_EDGE, linewidth=1.5)
ax.add_patch(sujeto_box)
ax.text(2.8, 2.7, "respuesta_017", ha="center", va="center",
        fontsize=10, fontweight="bold", color=O_EDGE)
ax.text(2.8, 2.4, "∈ O", ha="center", va="center",
        fontsize=8, style="italic", color="#6b7280")

# Flechas con predicados
arrow1 = FancyArrowPatch((2.8, 3.1), (1.2, 4.0),
                         arrowstyle="-|>", mutation_scale=12,
                         color="#15803d", linewidth=1.1,
                         connectionstyle="arc3,rad=-0.15")
ax.add_patch(arrow1)
ax.text(1.7, 3.55, "latencia", ha="center", va="center",
        fontsize=8.5, style="italic", color="#15803d",
        bbox=dict(boxstyle="round,pad=0.12", facecolor="white",
                  edgecolor="none", alpha=0.9))

arrow2 = FancyArrowPatch((2.8, 3.1), (4.3, 4.0),
                         arrowstyle="-|>", mutation_scale=12,
                         color="#15803d", linewidth=1.1,
                         connectionstyle="arc3,rad=0.15")
ax.add_patch(arrow2)
ax.text(4.0, 3.55, "unidad_latencia", ha="center", va="center",
        fontsize=8.5, style="italic", color="#15803d",
        bbox=dict(boxstyle="round,pad=0.12", facecolor="white",
                  edgecolor="none", alpha=0.9))

# DERECHA — versión reificada
ax.text(10.0, 5.9, "Versión reificada", ha="center", va="center",
        fontsize=12, fontweight="bold", color=INK)
ax.text(10.0, 5.55, "(medición como situación con propiedades)",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

# Sujeto-medición reificado
med_box = FancyBboxPatch((7.5, 1.0), 5.0, 4.0, boxstyle="round,pad=0.08",
                         facecolor="#dcfce7", edgecolor="#15803d", linewidth=1.8)
ax.add_patch(med_box)
ax.text(10.0, 4.55, "latencia_resp_017", ha="center", va="center",
        fontsize=12, fontweight="bold", color="#15803d", family="monospace")
ax.text(10.0, 4.20, "∈ O   (medición reificada)", ha="center", va="center",
        fontsize=8.5, style="italic", color="#6b7280")

# Propiedades del medición reificado
props = [
    ("cantidad:",   "340",                     N_FILL, N_EDGE),
    ("unidad:",     "milisegundo  (qudt:MilliSEC)", K_FILL, K_EDGE),
    ("contexto:",   "llamada_API_017",         O_FILL, O_EDGE),
    ("instrumento:","monitor_latencia_v3",     O_FILL, O_EDGE),
    ("medido_en:",  "2026-05-14T10:32:15Z",    "#fde68a", "#b45309"),
]
y = 3.7
for label, value, fill, edge in props:
    ax.text(7.8, y, label, ha="left", va="center",
            fontsize=10, family="monospace", color=INK)
    val_box = FancyBboxPatch((9.4, y - 0.18), 3.0, 0.36,
                             boxstyle="round,pad=0.02",
                             facecolor=fill, edgecolor=edge, linewidth=1.0)
    ax.add_patch(val_box)
    ax.text(9.55, y, value, ha="left", va="center",
            fontsize=9.5, family="monospace", color=INK)
    y -= 0.50

# Pie con regla de oro
ax.text(6.5, 0.45,
        "Regla: reificar la medición cuando la unidad no es obvia por contexto,\no cuando hace falta convertir, agregar o comparar entre unidades.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

# Leyenda
ax.plot([0.7], [0.30], "s", color=N_EDGE, markersize=9)
ax.text(0.9, 0.30, "N (número)", ha="left", va="center", fontsize=9, color=INK)
ax.plot([3.0], [0.30], "s", color=K_EDGE, markersize=9)
ax.text(3.2, 0.30, "K (clase/unidad)", ha="left", va="center", fontsize=9, color=INK)
ax.plot([5.6], [0.30], "s", color=O_EDGE, markersize=9)
ax.text(5.8, 0.30, "O (situación)", ha="left", va="center", fontsize=9, color=INK)

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "11_medicion_reificada.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
