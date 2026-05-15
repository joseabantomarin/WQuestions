"""Diagrama: las cinco islas del banco publicando al grafo común.

El patrón típico de una financiera mediana: core en Linux, agencias con
software propietario, contabilidad en Excel + sistemas a medida,
promotores con tablas planas, reporting que arma ETLs. WQuestions no
exige reemplazarlas — exige que cada una publique sus hechos al grafo
común con su dialecto.

Salida: ../png/43_cinco_islas_banco.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
GRAFO_FILL, GRAFO_EDGE = "#dcfce7", "#15803d"

islas = [
    {
        "name": "ISLA 1 — Central",
        "tech": "Servidor Linux\nBase relacional\nstored procedures",
        "vocab": "\"cuenta\", \"saldo\",\n\"asiento\", \"movimiento\"",
        "x": 1.7, "y": 7.0,
        "fill": "#dbeafe", "edge": "#1d4ed8",
    },
    {
        "name": "ISLA 2 — Agencias",
        "tech": "Software propietario\nSimuladores tasas\nAprobación express",
        "vocab": "\"línea_crédito\",\n\"simulación\", \"aprobación\"",
        "x": 5.5, "y": 7.0,
        "fill": "#fef3c7", "edge": "#b45309",
    },
    {
        "name": "ISLA 3 — Contabilidad",
        "tech": "Excel + macros\nSistemas a medida\nVB legacy",
        "vocab": "\"ajuste_mensual\",\n\"partida\", \"cierre\"",
        "x": 9.3, "y": 7.0,
        "fill": "#fed7aa", "edge": "#c2410c",
    },
    {
        "name": "ISLA 4 — Promotores",
        "tech": "Tablas planas\nPlanillas Excel\nFormularios PDF",
        "vocab": "\"prospecto\",\n\"promesa\", \"originación\"",
        "x": 13.1, "y": 7.0,
        "fill": "#fee2e2", "edge": "#b91c1c",
    },
    {
        "name": "ISLA 5 — Reporting",
        "tech": "ETLs ad-hoc\nData warehouse\nProyectos 1-3 meses",
        "vocab": "\"indicador\",\n\"snapshot\", \"KPI\"",
        "x": 7.5, "y": 4.0,
        "fill": "#e9d5ff", "edge": "#7c3aed",
    },
]

fig, ax = plt.subplots(figsize=(15, 9.5), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 9.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 9.10,
        "Las cinco islas del banco: vocabularios distintos, un grafo común",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 8.70,
        "Cada isla sigue siendo isla. Cada una publica sus hechos al grafo con su dialecto, mapeado al catálogo D7 una vez.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Las 4 islas superiores
box_w, box_h = 3.0, 1.9
for isla in islas[:4]:
    x, y = isla["x"], isla["y"]
    box = FancyBboxPatch((x - box_w/2, y - box_h/2), box_w, box_h,
                         boxstyle="round,pad=0.05",
                         facecolor=isla["fill"], edgecolor=isla["edge"],
                         linewidth=1.6)
    ax.add_patch(box)
    ax.text(x, y + box_h/2 - 0.25, isla["name"],
            ha="center", va="center", fontsize=10.5, fontweight="bold",
            color=isla["edge"])
    # Tecnología
    for i, line in enumerate(isla["tech"].split("\n")):
        ax.text(x, y + 0.20 - i * 0.22, line,
                ha="center", va="center", fontsize=8,
                color="#374151")
    # Vocabulario
    ax.text(x, y - 0.55, "vocabulario:",
            ha="center", va="center", fontsize=7.5, fontweight="bold",
            color="#6b7280")
    for i, line in enumerate(isla["vocab"].split("\n")):
        ax.text(x, y - 0.75 - i * 0.20, line,
                ha="center", va="center", fontsize=7.5,
                color=isla["edge"], style="italic", family="monospace")

# Isla 5 (reporting) — abajo, conectada hacia atrás al grafo
isla5 = islas[4]
x, y = isla5["x"], isla5["y"]
box = FancyBboxPatch((x - box_w/2, y - box_h/2), box_w, box_h,
                     boxstyle="round,pad=0.05",
                     facecolor=isla5["fill"], edgecolor=isla5["edge"],
                     linewidth=1.6)
ax.add_patch(box)
ax.text(x, y + box_h/2 - 0.25, isla5["name"],
        ha="center", va="center", fontsize=10.5, fontweight="bold",
        color=isla5["edge"])
for i, line in enumerate(isla5["tech"].split("\n")):
    ax.text(x, y + 0.20 - i * 0.22, line,
            ha="center", va="center", fontsize=8,
            color="#374151")
ax.text(x, y - 0.55, "vocabulario:",
        ha="center", va="center", fontsize=7.5, fontweight="bold",
        color="#6b7280")
for i, line in enumerate(isla5["vocab"].split("\n")):
    ax.text(x, y - 0.75 - i * 0.20, line,
            ha="center", va="center", fontsize=7.5,
            color=isla5["edge"], style="italic", family="monospace")

# Grafo común al centro inferior
grafo_y = 1.5
grafo_box = FancyBboxPatch((4.0, grafo_y - 0.65), 7.0, 1.3,
                           boxstyle="round,pad=0.06",
                           facecolor=GRAFO_FILL, edgecolor=GRAFO_EDGE,
                           linewidth=2.8)
ax.add_patch(grafo_box)
ax.text(7.5, grafo_y + 0.30, "GRAFO COMÚN WQUESTIONS",
        ha="center", va="center", fontsize=13, fontweight="bold",
        color=GRAFO_EDGE, family="monospace")
ax.text(7.5, grafo_y - 0.05, "catálogo D7 + dialectos por dominio",
        ha="center", va="center", fontsize=9, style="italic",
        color="#6b7280")
ax.text(7.5, grafo_y - 0.35,
        "una vista común, consultable por LLM o por código",
        ha="center", va="center", fontsize=8.5,
        color="#374151", style="italic")

# Flechas de cada isla al grafo (con etiqueta "mapeo D7")
def to_grafo(x_isla, y_isla, color):
    arr = FancyArrowPatch((x_isla, y_isla - box_h/2),
                          (7.5 + (x_isla - 7.5) * 0.15, grafo_y + 0.65),
                          arrowstyle="-|>", mutation_scale=12,
                          color=color, linewidth=1.4,
                          connectionstyle="arc3,rad=0.0")
    ax.add_patch(arr)

# Las 4 islas superiores
for isla in islas[:4]:
    to_grafo(isla["x"], isla["y"], isla["edge"])

# Isla 5 está más cerca, su flecha es vertical corta
arr = FancyArrowPatch((isla5["x"], isla5["y"] - box_h/2),
                      (7.5, grafo_y + 0.65),
                      arrowstyle="-|>", mutation_scale=12,
                      color=isla5["edge"], linewidth=1.4)
ax.add_patch(arr)

# Texto de las flechas
ax.text(7.5, 3.0, "cada isla publica con su dialecto · el mapeo a D7 se hace una vez por isla",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

# Pie
ax.text(7.5, 0.35,
        "Sin centralización ni reescritura. Las islas siguen existiendo; el grafo las vuelve consultables en conjunto.",
        ha="center", va="center", fontsize=10, color="#374151")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "43_cinco_islas_banco.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
