"""Diagrama: pipeline LLM ↔ WQuestions.

Usuario → LLM → función → grafo → respuesta.
Seis pasos numerados con cajas y flechas direccionales.

Salida: ../png/35_pipeline_llm.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

fig, ax = plt.subplots(figsize=(15, 9), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 8.55,
        "Pipeline LLM ↔ WQuestions: del lenguaje natural al grafo y de regreso",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 8.15,
        "Seis pasos. Dos lenguajes — natural y estructurado — comunicándose sin fricción.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Paso 1: Usuario
def step_box(x, y, w, h, num, title, body, fill, edge, body_color="#374151"):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.06",
                         facecolor=fill, edgecolor=edge, linewidth=1.8)
    ax.add_patch(box)
    # número en círculo
    circ = FancyBboxPatch((x - w/2 + 0.15, y + h/2 - 0.45), 0.45, 0.30,
                          boxstyle="round,pad=0.02",
                          facecolor=edge, edgecolor="none")
    ax.add_patch(circ)
    ax.text(x - w/2 + 0.375, y + h/2 - 0.30, str(num),
            ha="center", va="center", fontsize=10,
            color="white", fontweight="bold", family="monospace")
    # título
    ax.text(x, y + h/2 - 0.30, title,
            ha="center", va="center", fontsize=11, fontweight="bold",
            color=edge)
    # body
    for i, line in enumerate(body):
        ax.text(x, y + 0.15 - i * 0.25, line,
                ha="center", va="center", fontsize=8.5,
                color=body_color, family="monospace")


# Paso 1 — Usuario (izquierda arriba)
step_box(2.0, 6.4, 3.0, 1.7, 1, "USUARIO",
         ['"¿Qué medicación', 'venía tomando', 'María Gonzales',
          'y desde cuándo?"'],
         "#fef3c7", "#b45309")

# Paso 2 — LLM interpreta
step_box(7.5, 6.4, 4.0, 1.7, 2, "LLM (Claude / GPT / ...)",
         ['Interpreta intención',
          'Elige función del lexicon:',
          '→ consultar_tratamiento(',
          '     paciente: maria_g, ...)'],
         "#dbeafe", "#1d4ed8")

# Paso 3 — Function call (derecha arriba)
step_box(12.7, 6.4, 4.0, 1.7, 3, "FUNCTION CALL",
         ['JSON estructurado:',
          '{ "name": "consultar",',
          '  "args": { "paciente": …,',
          '            "periodo": "histórico" }}'],
         "#e0e7ff", "#4f46e5")

# Paso 4 — Evaluador / grafo (centro abajo)
step_box(7.5, 3.5, 6.0, 1.7, 4, "EVALUADOR + GRAFO WQUESTIONS",
         ['query(Pattern(fixed={"paciente": maria_g},',
          '              ask={"medicamento_prescrito": Var()},',
          '              type_constraint="accion_prescribir"),',
          '      at=hoy)  →  enalapril desde 2026-05-14'],
         "#dcfce7", "#15803d")

# Paso 5 — Respuesta estructurada
step_box(2.0, 1.6, 3.0, 1.4, 5, "RESPUESTA DE FUNCIÓN",
         ['{ "medicamento":', '   "enalapril 10mg",',
          '  "desde":', '   "2026-05-14" }'],
         "#e0e7ff", "#4f46e5")

# Paso 6 — Respuesta natural
step_box(12.7, 1.6, 4.0, 1.4, 6, "LLM GENERA RESPUESTA",
         ['"María Gonzales tomaba',
          'enalapril 10 mg cada',
          'mañana, desde el 14 de',
          'mayo de 2026..."'],
         "#fef3c7", "#b45309")

# Flechas (1→2, 2→3, 3→4, 4→5, 5→6)
def arrow(x1, y1, x2, y2, rad=0.0, color="#6b7280"):
    arr = FancyArrowPatch((x1, y1), (x2, y2),
                          arrowstyle="-|>", mutation_scale=15,
                          color=color, linewidth=1.5,
                          connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(arr)

# 1 → 2
arrow(3.5, 6.4, 5.5, 6.4)
# 2 → 3
arrow(9.5, 6.4, 10.7, 6.4)
# 3 → 4 (curva hacia abajo)
arrow(12.7, 5.55, 10.5, 4.35, rad=0.2, color="#4f46e5")
# 4 → 5 (hacia abajo izquierda)
arrow(4.5, 3.5, 3.5, 2.30, rad=-0.2, color="#15803d")
# 5 → 6 (hacia la derecha)
arrow(3.5, 1.6, 10.7, 1.6, rad=-0.15, color="#4f46e5")
# 6 → usuario implícito (pie)
ax.annotate("", xy=(2.5, 5.55), xytext=(11.4, 1.6),
            arrowprops=dict(arrowstyle="-", color="#fca5a5",
                            lw=0.7, linestyle="dashed"))
ax.text(7.5, 0.55,
        "El LLM se ocupa de la superficie lingüística. El grafo se ocupa de la profundidad estructural.\n"
        "Cada uno hace lo que hace mejor; ninguno carga con lo que no le sale bien.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "35_pipeline_llm.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
