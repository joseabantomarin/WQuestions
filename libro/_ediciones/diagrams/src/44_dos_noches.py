"""Diagrama de cierre: las dos noches comparadas.

Antes (cap 1): cuatro sistemas con cuatro schemas bloquean la información.
Después (conclusión): los cuatro publican al grafo común y la historia
se reconstruye en segundos.

Salida: ../png/44_dos_noches.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"

fig, ax = plt.subplots(figsize=(15, 9.5), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 9.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7.5, 9.10,
        "Dos noches, la misma sala de emergencias",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 8.70,
        "La información existe en ambos casos. La diferencia está en si puede consultarse.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# ===== LADO IZQUIERDO: 2026 (antes) =====
left_x = 3.7
ax.text(left_x, 8.05, "2026 — la sala bloqueada",
        ha="center", va="center", fontsize=12, fontweight="bold",
        color="#b91c1c")

# Médico bloqueado
med_box = FancyBboxPatch((left_x - 1.8, 6.5), 3.6, 1.1,
                         boxstyle="round,pad=0.05",
                         facecolor="#fef3c7", edgecolor="#b45309",
                         linewidth=1.5)
ax.add_patch(med_box)
ax.text(left_x, 7.30, "Médico de guardia",
        ha="center", va="center", fontsize=11, fontweight="bold",
        color="#b45309")
ax.text(left_x, 6.95, "ve: 3 líneas, bronquitis 2022",
        ha="center", va="center", fontsize=8.5, style="italic",
        color="#374151")
ax.text(left_x, 6.70, "no ve: nada del resto",
        ha="center", va="center", fontsize=8.5, style="italic",
        color="#b91c1c")

# 4 sistemas separados, sin conexión
systems_2026 = [
    {"label": "Hospital A", "schema": "dx_p, med_act",
     "x": 0.9, "y": 4.5},
    {"label": "Hospital B", "schema": "diagnostico_principal,\nmedicacion_actual",
     "x": 3.2, "y": 4.5},
    {"label": "Endocrinóloga", "schema": "consultas.txt\n(propietario)",
     "x": 5.5, "y": 4.5},
    {"label": "Cardiólogo", "schema": "prescripciones,\nfarmaco_id",
     "x": 7.0, "y": 4.5},
]

for s in systems_2026:
    box = FancyBboxPatch((s["x"] - 0.85, s["y"] - 0.8), 1.7, 1.6,
                         boxstyle="round,pad=0.04",
                         facecolor="#fee2e2", edgecolor="#b91c1c",
                         linewidth=1.2)
    ax.add_patch(box)
    ax.text(s["x"], s["y"] + 0.45, s["label"],
            ha="center", va="center", fontsize=9, fontweight="bold",
            color="#b91c1c")
    for j, line in enumerate(s["schema"].split("\n")):
        ax.text(s["x"], s["y"] - 0.10 - j * 0.20, line,
                ha="center", va="center", fontsize=7,
                color="#374151", family="monospace")
    # X grande indicando "no se comunica"
    ax.text(s["x"], s["y"] - 0.60, "✗",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color="#b91c1c")

# Pie 2026
ax.text(left_x, 2.7,
        "La información existe pero los schemas\n"
        "no hablan entre sí. Cada cruce es\n"
        "un proyecto de integración bilateral.",
        ha="center", va="center", fontsize=9, style="italic",
        color="#7f1d1d")

# Decisión sin información
ax.text(left_x, 1.2,
        "Decisión clínica con datos parciales.",
        ha="center", va="center", fontsize=9.5, fontweight="bold",
        color="#b91c1c")

# Separador vertical
ax.plot([7.5, 7.5], [0.6, 8.4], color="#d1d5db", lw=1.0,
        linestyle="dashed")

# ===== LADO DERECHO: 2028 (después) =====
right_x = 11.3
ax.text(right_x, 8.05, "2028 — la sala conectada",
        ha="center", va="center", fontsize=12, fontweight="bold",
        color="#15803d")

# Médico con acceso completo
med_box = FancyBboxPatch((right_x - 1.8, 6.5), 3.6, 1.1,
                         boxstyle="round,pad=0.05",
                         facecolor="#dcfce7", edgecolor="#15803d",
                         linewidth=1.5)
ax.add_patch(med_box)
ax.text(right_x, 7.30, "Médico de guardia",
        ha="center", va="center", fontsize=11, fontweight="bold",
        color="#15803d")
ax.text(right_x, 6.95, "ve: historia completa",
        ha="center", va="center", fontsize=8.5, style="italic",
        color="#374151")
ax.text(right_x, 6.70, "(eco, controles, ajustes, recomendaciones)",
        ha="center", va="center", fontsize=8.5, style="italic",
        color="#15803d")

# Grafo común
grafo_y = 4.5
grafo_box = FancyBboxPatch((right_x - 2.2, grafo_y - 0.55), 4.4, 1.1,
                           boxstyle="round,pad=0.06",
                           facecolor="#dcfce7", edgecolor="#15803d",
                           linewidth=2.5)
ax.add_patch(grafo_box)
ax.text(right_x, grafo_y + 0.25, "Grafo común WQuestions",
        ha="center", va="center", fontsize=11, fontweight="bold",
        color="#15803d", family="monospace")
ax.text(right_x, grafo_y - 0.10, "catálogo D7 + dialectos",
        ha="center", va="center", fontsize=8.5, style="italic",
        color="#6b7280")
ax.text(right_x, grafo_y - 0.35, "consulta_medica · diagnostico · prescripcion",
        ha="center", va="center", fontsize=8,
        color="#15803d", family="monospace")

# Flecha grafo ↔ médico
arr = FancyArrowPatch((right_x, grafo_y + 0.6), (right_x, 6.5),
                      arrowstyle="<|-|>", mutation_scale=14,
                      color="#15803d", linewidth=1.5)
ax.add_patch(arr)

# Las 4 fuentes publican
sources_2028 = [
    {"label": "Hospital A",   "x": 8.7,  "y": 2.7},
    {"label": "Hospital B",   "x": 10.4, "y": 2.7},
    {"label": "Endocrinóloga", "x": 12.2, "y": 2.7},
    {"label": "Cardiólogo",   "x": 13.9, "y": 2.7},
]
for s in sources_2028:
    box = FancyBboxPatch((s["x"] - 0.65, s["y"] - 0.35), 1.3, 0.7,
                         boxstyle="round,pad=0.03",
                         facecolor="#dcfce7", edgecolor="#15803d",
                         linewidth=1.0)
    ax.add_patch(box)
    ax.text(s["x"], s["y"] + 0.10, s["label"],
            ha="center", va="center", fontsize=8, fontweight="bold",
            color="#15803d")
    ax.text(s["x"], s["y"] - 0.18, "publica",
            ha="center", va="center", fontsize=7,
            style="italic", color="#15803d")
    # flecha hacia el grafo
    arr = FancyArrowPatch((s["x"], s["y"] + 0.35),
                          (right_x, grafo_y - 0.55),
                          arrowstyle="-|>", mutation_scale=10,
                          color="#15803d", linewidth=1.0, alpha=0.6)
    ax.add_patch(arr)

# Pie 2028
ax.text(right_x, 1.2,
        "Decisión clínica con la historia completa.",
        ha="center", va="center", fontsize=9.5, fontweight="bold",
        color="#15803d")

# Footer común
ax.text(7.5, 0.30,
        "Misma información en ambas escenas. Lo que cambió fue la arquitectura.",
        ha="center", va="center", fontsize=10, color="#374151")
ax.text(7.5, 0.00,
        "Hablar en preguntas — el mismo modelo que Aristóteles, Cicerón y el periodismo del siglo XX — fue suficiente.",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "44_dos_noches.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
