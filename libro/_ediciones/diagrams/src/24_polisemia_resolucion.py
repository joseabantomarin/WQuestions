"""Diagrama: resolución de polisemia del verbo "dar".
Cuatro patrones léxicos del verbo "dar" que disparan cuatro tipos de
situación distintos. El parser elige el patrón más específico que coincida.

Salida: ../png/24_polisemia_resolucion.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

fig, ax = plt.subplots(figsize=(14, 9), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 8.55, "Resolución de polisemia: el verbo \"dar\"",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 8.15,
        "Cuatro unidades léxicas distintas; el parser elige por patrón de complemento, del más específico al más general.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Verbo central
verb_box = FancyBboxPatch((6.1, 6.6), 1.8, 0.8,
                          boxstyle="round,pad=0.06",
                          facecolor="#f9fafb", edgecolor=INK, linewidth=2.0)
ax.add_patch(verb_box)
ax.text(7.0, 7.0, "dar",
        ha="center", va="center", fontsize=18, fontweight="bold",
        color=INK, family="monospace")

# Cuatro patrones léxicos, distribuidos abajo
patterns = [
    {
        "x": 1.7,
        "pattern": "dar  [la mano]",
        "ejemplo": "\"le dio la mano al jefe\"",
        "tipo": "accion_saludar",
        "roles": "agente · paciente",
        "color_fill": "#fef3c7",
        "color_edge": "#b45309",
    },
    {
        "x": 5.4,
        "pattern": "dar  [conferencia | clase]",
        "ejemplo": "\"dio una conferencia el martes\"",
        "tipo": "evento_exposicion",
        "roles": "agente · tema · audiencia?",
        "color_fill": "#dbeafe",
        "color_edge": "#1d4ed8",
    },
    {
        "x": 9.1,
        "pattern": "dar  [asco | pena | miedo]",
        "ejemplo": "\"la noticia le dio asco\"",
        "tipo": "experiencia_sensorial",
        "roles": "tema · experimentador",
        "color_fill": "#fee2e2",
        "color_edge": "#b91c1c",
    },
    {
        "x": 12.4,
        "pattern": "dar   (genérico)",
        "ejemplo": "\"le dio un regalo a María\"",
        "tipo": "accion_dar",
        "roles": "agente · tema · beneficiario",
        "color_fill": "#dcfce7",
        "color_edge": "#15803d",
    },
]

# Etiquetas de especificidad
spec_y = 5.55
ax.annotate("", xy=(12.8, spec_y), xytext=(1.0, spec_y),
            arrowprops=dict(arrowstyle="->", color="#9ca3af", lw=1.0))
ax.text(0.4, spec_y, "más\nespecífico",
        ha="left", va="center", fontsize=8.5,
        style="italic", color="#6b7280")
ax.text(13.5, spec_y, "más\ngeneral",
        ha="right", va="center", fontsize=8.5,
        style="italic", color="#6b7280")
ax.text(7, spec_y + 0.20, "orden de prueba del parser",
        ha="center", va="center", fontsize=8.5,
        style="italic", color="#6b7280")

# Cada patrón como una caja
for p in patterns:
    x = p["x"]
    # Caja del patrón (arriba)
    box_pat = FancyBboxPatch((x - 1.4, 4.4), 2.8, 0.85,
                             boxstyle="round,pad=0.04",
                             facecolor="white", edgecolor=p["color_edge"],
                             linewidth=1.5)
    ax.add_patch(box_pat)
    ax.text(x, 4.95, p["pattern"],
            ha="center", va="center", fontsize=9.5,
            color=p["color_edge"], family="monospace", fontweight="bold")
    ax.text(x, 4.62, p["ejemplo"],
            ha="center", va="center", fontsize=8.5,
            color="#374151", style="italic", family="serif")

    # Flecha desde el verbo hacia la caja del patrón
    arr = FancyArrowPatch((7.0, 6.6), (x, 5.25),
                          arrowstyle="-|>", mutation_scale=10,
                          color="#9ca3af", linewidth=0.9,
                          connectionstyle="arc3,rad=0.0")
    ax.add_patch(arr)

    # Caja del tipo (abajo) — tipo_situacion en K
    box_tipo = FancyBboxPatch((x - 1.4, 2.4), 2.8, 1.1,
                              boxstyle="round,pad=0.04",
                              facecolor=p["color_fill"],
                              edgecolor=p["color_edge"], linewidth=1.8)
    ax.add_patch(box_tipo)
    ax.text(x, 3.20, p["tipo"],
            ha="center", va="center", fontsize=10.5, fontweight="bold",
            color=p["color_edge"], family="monospace")
    ax.text(x, 2.90, "∈ K  (tipo de situación)",
            ha="center", va="center", fontsize=8,
            style="italic", color="#6b7280")
    ax.text(x, 2.60, p["roles"],
            ha="center", va="center", fontsize=8.5,
            color="#374151", family="monospace")

    # Flecha del patrón al tipo
    arr2 = FancyArrowPatch((x, 4.4), (x, 3.50),
                           arrowstyle="-|>", mutation_scale=12,
                           color=p["color_edge"], linewidth=1.4)
    ax.add_patch(arr2)

# Pie
ax.text(7, 1.5,
        "El parser intenta los patrones específicos primero (\"dar la mano\", \"dar conferencia\")",
        ha="center", va="center", fontsize=10,
        color="#374151")
ax.text(7, 1.15,
        "y solo cae al patrón genérico \"dar\" si ninguno coincide.",
        ha="center", va="center", fontsize=10,
        color="#374151")
ax.text(7, 0.6,
        "Polisemia tratada como sobrecarga de funciones — declarativa, mecánica, extensible.",
        ha="center", va="center", fontsize=9.5,
        style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "24_polisemia_resolucion.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
