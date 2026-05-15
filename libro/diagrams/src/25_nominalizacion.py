"""Diagrama: nominalización y forma verbal producen la misma situación.
"El avión llegó tarde" y "La llegada tardía del avión" se reducen al mismo
grafo. El lexicon hace que ambos disparadores activen la misma entrada.

Salida: ../png/25_nominalizacion.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
O_FILL, O_EDGE = "#dcfce7", "#15803d"

fig, ax = plt.subplots(figsize=(14, 8.5), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 8.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 8.05, "Nominalización ≡ verbo: misma situación, distinta superficie",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 7.65,
        "Forma verbal y forma nominal disparan la misma entrada del lexicon y producen los mismos hechos.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Forma verbal (izquierda)
v_x = 3.5
v_y = 6.4
v_box = FancyBboxPatch((v_x - 2.7, v_y - 0.45), 5.4, 0.9,
                       boxstyle="round,pad=0.05",
                       facecolor="#dbeafe", edgecolor="#1d4ed8", linewidth=1.6)
ax.add_patch(v_box)
ax.text(v_x, v_y + 0.18, "El avión llegó tarde ayer.",
        ha="center", va="center", fontsize=11.5,
        color="#1d4ed8", family="serif")
ax.text(v_x, v_y - 0.22, "(forma verbal)",
        ha="center", va="center", fontsize=8.5,
        style="italic", color="#1e3a8a")

# Forma nominal (derecha)
n_x = 10.5
n_y = 6.4
n_box = FancyBboxPatch((n_x - 2.7, n_y - 0.45), 5.4, 0.9,
                       boxstyle="round,pad=0.05",
                       facecolor="#fef3c7", edgecolor="#b45309", linewidth=1.6)
ax.add_patch(n_box)
ax.text(n_x, n_y + 0.18, "La llegada tardía del avión de ayer.",
        ha="center", va="center", fontsize=11.5,
        color="#b45309", family="serif")
ax.text(n_x, n_y - 0.22, "(forma nominal)",
        ha="center", va="center", fontsize=8.5,
        style="italic", color="#92400e")

# Lexicon como mediador
lex_y = 4.6
lex_box = FancyBboxPatch((4.0, lex_y - 0.60), 6.0, 1.2,
                         boxstyle="round,pad=0.05",
                         facecolor="white", edgecolor="#9ca3af",
                         linewidth=1.4)
ax.add_patch(lex_box)
ax.text(7, lex_y + 0.32, "lexicon → entrada de  llegar",
        ha="center", va="center", fontsize=10.5, fontweight="bold",
        color=INK, family="monospace")
ax.text(7, lex_y + 0.02,
        "verbo: llegar",
        ha="center", va="center", fontsize=8.5,
        color="#374151", family="monospace")
ax.text(7, lex_y - 0.20,
        "formas_nominales: [\"llegada\", \"arribo\"]",
        ha="center", va="center", fontsize=8.5,
        color="#374151", family="monospace")
ax.text(7, lex_y - 0.42,
        "tipo_situacion: accion_llegar",
        ha="center", va="center", fontsize=8.5,
        color="#374151", family="monospace")

# Flechas desde ambas formas al lexicon
arr1 = FancyArrowPatch((v_x, v_y - 0.45), (5.4, lex_y + 0.6),
                       arrowstyle="-|>", mutation_scale=12,
                       color="#1d4ed8", linewidth=1.3)
ax.add_patch(arr1)
arr2 = FancyArrowPatch((n_x, n_y - 0.45), (8.6, lex_y + 0.6),
                       arrowstyle="-|>", mutation_scale=12,
                       color="#b45309", linewidth=1.3)
ax.add_patch(arr2)

# Situación reificada (única)
sit_y = 2.5
sit_box = FancyBboxPatch((5.0, sit_y - 0.6), 4.0, 1.2,
                         boxstyle="round,pad=0.06",
                         facecolor=O_FILL, edgecolor=O_EDGE, linewidth=2.5)
ax.add_patch(sit_box)
ax.text(7.0, sit_y + 0.22, "llegada_017",
        ha="center", va="center", fontsize=13, fontweight="bold",
        color=O_EDGE, family="monospace")
ax.text(7.0, sit_y - 0.18, "∈ O   (situación reificada — única)",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")

# Flecha desde el lexicon a la situación
arr3 = FancyArrowPatch((7.0, lex_y - 0.6), (7.0, sit_y + 0.6),
                       arrowstyle="-|>", mutation_scale=14,
                       color="#15803d", linewidth=1.6)
ax.add_patch(arr3)
ax.text(7.35, (lex_y + sit_y) / 2, "reifica",
        ha="left", va="center", fontsize=9, style="italic",
        color="#15803d", family="monospace")

# Hechos atómicos como pequeñas chips bajo la situación
facts = [
    "instancia_de: accion_llegar",
    "agente: avion_LP2226",
    "calificacion: tardia",
    "momento: 2026-05-14",
    "estatus_factual: real",
]
chip_w = 2.6
n = len(facts)
total_w = chip_w * n + 0.20 * (n - 1)
start_x = (14 - total_w) / 2 + chip_w / 2
for i, f in enumerate(facts):
    fx = start_x + i * (chip_w + 0.20)
    chip = FancyBboxPatch((fx - chip_w/2, 0.45), chip_w, 0.7,
                          boxstyle="round,pad=0.03",
                          facecolor="#f9fafb", edgecolor=O_EDGE,
                          linewidth=1.0)
    ax.add_patch(chip)
    ax.text(fx, 0.80, f,
            ha="center", va="center", fontsize=8,
            color="#15803d", family="monospace")

# Flecha desde la situación a los hechos
ax.annotate("", xy=(7.0, 1.18), xytext=(7.0, sit_y - 0.6),
            arrowprops=dict(arrowstyle="-", color="#9ca3af", lw=0.8))

# Pie
ax.text(7, 0.15,
        "Mismos hechos atómicos, sin importar si el texto fuente usa el verbo o el sustantivo derivado.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "25_nominalizacion.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
