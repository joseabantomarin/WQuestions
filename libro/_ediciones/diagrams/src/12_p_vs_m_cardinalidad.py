"""Diagrama: P vs M — la única diferencia real es de cardinalidad.
Funcional (uno-a-uno) vs no funcional (uno-a-muchos).

Salida: ../png/12_p_vs_m_cardinalidad.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
P_FILL, P_EDGE = "#dbeafe", "#1d4ed8"
M_FILL, M_EDGE = "#fef3c7", "#b45309"

fig, ax = plt.subplots(figsize=(13, 7), dpi=200)
ax.set_xlim(0, 13)
ax.set_ylim(0, 7)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(6.5, 6.6, "Propiedades y relaciones: la única diferencia es la cardinalidad",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)

# Subtitle
ax.text(6.5, 6.2, "D3: misma forma sujeto-predicado-objeto; solo cambia cuántos objetos puede haber",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# IZQUIERDA — P (funcional)
LEFT_X = 0.5
LEFT_W = 5.7
left_box = FancyBboxPatch((LEFT_X, 0.8), LEFT_W, 4.9, boxstyle="round,pad=0.08",
                          facecolor=P_FILL, edgecolor=P_EDGE, linewidth=1.8)
ax.add_patch(left_box)
ax.text(LEFT_X + LEFT_W/2, 5.3, "Cable funcional (propiedad)",
        ha="center", va="center", fontsize=13, fontweight="bold", color=P_EDGE)
ax.text(LEFT_X + LEFT_W/2, 4.95, "un sujeto → un objeto",
        ha="center", va="center", fontsize=10, style="italic", color=INK)

# Sujeto a la izquierda
suj_x, suj_y = LEFT_X + 0.7, 3.0
suj_box = FancyBboxPatch((suj_x - 0.55, suj_y - 0.35), 1.1, 0.7,
                         boxstyle="round,pad=0.04",
                         facecolor="white", edgecolor=P_EDGE, linewidth=1.5)
ax.add_patch(suj_box)
ax.text(suj_x, suj_y + 0.05, "paciente_042", ha="center", va="center",
        fontsize=9, fontweight="bold", color=P_EDGE)
ax.text(suj_x, suj_y - 0.15, "∈ Q", ha="center", va="center",
        fontsize=7.5, style="italic", color="#6b7280")

# Objeto único a la derecha
obj_box = FancyBboxPatch((LEFT_X + 4.3, suj_y - 0.35), 1.0, 0.7,
                         boxstyle="round,pad=0.04",
                         facecolor="white", edgecolor=P_EDGE, linewidth=1.5)
ax.add_patch(obj_box)
ax.text(LEFT_X + 4.8, suj_y + 0.05, "42", ha="center", va="center",
        fontsize=14, fontweight="bold", color=P_EDGE)
ax.text(LEFT_X + 4.8, suj_y - 0.15, "∈ N", ha="center", va="center",
        fontsize=7.5, style="italic", color="#6b7280")

# Flecha
arrow = FancyArrowPatch((suj_x + 0.55, suj_y), (LEFT_X + 4.3, suj_y),
                        arrowstyle="-|>", mutation_scale=15,
                        color=P_EDGE, linewidth=1.6)
ax.add_patch(arrow)
ax.text((suj_x + LEFT_X + 4.8)/2, suj_y + 0.3, "edad",
        ha="center", va="center", fontsize=10, style="italic", color=P_EDGE,
        bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                  edgecolor="none", alpha=0.9))

# Regla de actualización
ax.text(LEFT_X + LEFT_W/2, 1.7,
        "Inserto (paciente_042, edad, 43)",
        ha="center", va="center", fontsize=9.5, family="monospace", color=INK)
ax.text(LEFT_X + LEFT_W/2, 1.30,
        "⇨  El nuevo valor reemplaza al anterior",
        ha="center", va="center", fontsize=10, fontweight="bold", color=P_EDGE)

# DERECHA — M (no funcional)
RIGHT_X = 6.8
RIGHT_W = 5.7
right_box = FancyBboxPatch((RIGHT_X, 0.8), RIGHT_W, 4.9, boxstyle="round,pad=0.08",
                           facecolor=M_FILL, edgecolor=M_EDGE, linewidth=1.8)
ax.add_patch(right_box)
ax.text(RIGHT_X + RIGHT_W/2, 5.3, "Cable múltiple (relación)",
        ha="center", va="center", fontsize=13, fontweight="bold", color=M_EDGE)
ax.text(RIGHT_X + RIGHT_W/2, 4.95, "un sujeto → varios objetos",
        ha="center", va="center", fontsize=10, style="italic", color=INK)

# Sujeto a la izquierda
suj_x2, suj_y2 = RIGHT_X + 0.7, 3.5
suj_box2 = FancyBboxPatch((suj_x2 - 0.55, suj_y2 - 0.35), 1.1, 0.7,
                          boxstyle="round,pad=0.04",
                          facecolor="white", edgecolor=M_EDGE, linewidth=1.5)
ax.add_patch(suj_box2)
ax.text(suj_x2, suj_y2 + 0.05, "modelo_gpt_x", ha="center", va="center",
        fontsize=8.5, fontweight="bold", color=M_EDGE)
ax.text(suj_x2, suj_y2 - 0.15, "∈ O", ha="center", va="center",
        fontsize=7.5, style="italic", color="#6b7280")

# Tres objetos
objetos = [("corpus_c4", 4.4), ("corpus_books3", 3.5), ("corpus_wiki", 2.6)]
for label, oy in objetos:
    o_box = FancyBboxPatch((RIGHT_X + 4.2, oy - 0.25), 1.3, 0.5,
                           boxstyle="round,pad=0.03",
                           facecolor="white", edgecolor=M_EDGE, linewidth=1.3)
    ax.add_patch(o_box)
    ax.text(RIGHT_X + 4.85, oy, label, ha="center", va="center",
            fontsize=8.5, fontweight="bold", color=M_EDGE)
    arr = FancyArrowPatch((suj_x2 + 0.55, suj_y2), (RIGHT_X + 4.2, oy),
                          arrowstyle="-|>", mutation_scale=12,
                          color=M_EDGE, linewidth=1.2,
                          connectionstyle="arc3,rad=0.0")
    ax.add_patch(arr)

ax.text(RIGHT_X + 2.8, 4.1, "entrenado_con",
        ha="center", va="center", fontsize=9.5, style="italic", color=M_EDGE,
        bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                  edgecolor="none", alpha=0.9))

# Regla de actualización
ax.text(RIGHT_X + RIGHT_W/2, 1.7,
        "Inserto (modelo_gpt_x, entrenado_con, corpus_new)",
        ha="center", va="center", fontsize=9, family="monospace", color=INK)
ax.text(RIGHT_X + RIGHT_W/2, 1.30,
        "⇨  El nuevo valor se acumula con los anteriores",
        ha="center", va="center", fontsize=10, fontweight="bold", color=M_EDGE)

# Pie
ax.text(6.5, 0.35,
        "La forma del hecho es idéntica: (sujeto, predicado, objeto). El motor de consulta es uno solo.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "12_p_vs_m_cardinalidad.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
