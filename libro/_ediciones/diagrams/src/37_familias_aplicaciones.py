"""Diagrama: las cinco familias de aplicaciones que abre WQuestions+LLM.

Un núcleo central (WQuestions+LLM) con 5 radios hacia las familias.

Salida: ../png/37_familias_aplicaciones.png
"""

import os
import math
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

fig, ax = plt.subplots(figsize=(14, 9.5), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 9.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 9.10,
        "Cinco familias de aplicaciones habilitadas por WQuestions + LLM",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 8.70,
        "Todas radian del mismo núcleo: grafo persistente con identidad estable + interface conversacional.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Núcleo central
cx, cy = 7, 4.5
core = FancyBboxPatch((cx - 1.85, cy - 0.75), 3.7, 1.5,
                      boxstyle="round,pad=0.06",
                      facecolor="#dcfce7", edgecolor="#15803d",
                      linewidth=2.5)
ax.add_patch(core)
ax.text(cx, cy + 0.30, "WQuestions",
        ha="center", va="center", fontsize=13.5, fontweight="bold",
        color="#15803d", family="monospace")
ax.text(cx, cy + 0.00, "+ LLM via MCP",
        ha="center", va="center", fontsize=10, fontweight="bold",
        color="#15803d", family="monospace")
ax.text(cx, cy - 0.30,
        "grafo persistente · interface conversacional",
        ha="center", va="center", fontsize=8.5, style="italic",
        color="#6b7280")

# Cinco familias en posiciones radiales
families = [
    {
        "title": "1. Búsqueda cross-dominio",
        "subtitle": "sin schema matching",
        "examples": ["• cruzar ventas + RRHH + finanzas",
                     "• preguntas que antes eran proyectos"],
        "x": 2.0, "y": 7.5,
        "fill": "#dbeafe", "edge": "#1d4ed8",
    },
    {
        "title": "2. Auditoría retrospectiva",
        "subtitle": "bitemporalidad",
        "examples": ["• \"¿qué sabíamos cuándo?\"",
                     "• cumplimiento bancario y clínico"],
        "x": 12.0, "y": 7.5,
        "fill": "#fef3c7", "edge": "#b45309",
    },
    {
        "title": "3. Razonamiento composicional",
        "subtitle": "LLM + grafo trazable",
        "examples": ["• simulación basada en reglas",
                     "• pattern matching cross-pacientes"],
        "x": 1.5, "y": 2.0,
        "fill": "#e9d5ff", "edge": "#7c3aed",
    },
    {
        "title": "4. Multi-agente",
        "subtitle": "modelo del mundo compartido",
        "examples": ["• varios LLMs co-anotando",
                     "• coordinación observable"],
        "x": 7.0, "y": 1.6,
        "fill": "#fee2e2", "edge": "#b91c1c",
    },
    {
        "title": "5. Educación + explicabilidad",
        "subtitle": "grafo como libro interactivo",
        "examples": ["• navegar dominios complejos",
                     "• explicar decisiones de IA"],
        "x": 12.5, "y": 2.0,
        "fill": "#e0e7ff", "edge": "#4f46e5",
    },
]

for f in families:
    box = FancyBboxPatch((f["x"] - 1.65, f["y"] - 0.85), 3.3, 1.7,
                         boxstyle="round,pad=0.05",
                         facecolor=f["fill"], edgecolor=f["edge"],
                         linewidth=1.6)
    ax.add_patch(box)
    ax.text(f["x"], f["y"] + 0.55, f["title"],
            ha="center", va="center", fontsize=10.5, fontweight="bold",
            color=f["edge"])
    ax.text(f["x"], f["y"] + 0.25, f["subtitle"],
            ha="center", va="center", fontsize=9, style="italic",
            color=f["edge"])
    for i, ex in enumerate(f["examples"]):
        ax.text(f["x"], f["y"] - 0.10 - i * 0.25, ex,
                ha="center", va="center", fontsize=8.5,
                color="#374151")

    # Flecha desde el núcleo
    arr = FancyArrowPatch((cx, cy), (f["x"], f["y"]),
                          arrowstyle="-|>", mutation_scale=14,
                          color=f["edge"], linewidth=1.4, alpha=0.7)
    ax.add_patch(arr)

# Pie
ax.text(7, 0.4,
        "El común denominador: identidad estable a través del tiempo + relaciones canónicas trazables.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "37_familias_aplicaciones.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
