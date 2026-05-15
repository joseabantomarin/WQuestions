"""Diagrama: el patrón plantilla-K + instancia-O con factor de escala.

Tres dominios distintos (química, música, clínica) usando el mismo patrón:
- una entidad genérica/atemporal vive en K (la plantilla)
- una manifestación concreta vive en O (la instancia)
- la instancia apunta a la plantilla por `instancia_de` + factor de escala

Salida: ../png/34_plantilla_instancia.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK = "#1f2937"
K_FILL, K_EDGE = "#e0e7ff", "#4f46e5"
O_FILL, O_EDGE = "#dcfce7", "#15803d"

fig, ax = plt.subplots(figsize=(14, 9), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 8.55, "El patrón \"plantilla-K + instancia-O\"",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 8.15,
        "Tres dominios distintos, el mismo patrón estructural: lo genérico vive en K, lo concreto en O.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# 3 filas, 1 plantilla + 1 instancia
domains = [
    {
        "label": "química",
        "y": 6.4,
        "plantilla": "combustion_metano",
        "p_details": "CH₄ + 2 O₂ → CO₂ + 2 H₂O\n(estequiometría atemporal)",
        "instancia": "reaccion_001",
        "i_details": "factor_escala: 0.5 mol\nlugar: cilindro_motor\nmomento: 14:32",
    },
    {
        "label": "música",
        "y": 4.4,
        "plantilla": "sonata_op27_no2",
        "p_details": "compositor: Beethoven\n3 movimientos\n(obra atemporal)",
        "instancia": "interpretacion_001",
        "i_details": "intérprete: Claudio Arrau\nlugar: teatro NYC\nfecha: 1985-03-10",
    },
    {
        "label": "clínica",
        "y": 2.4,
        "plantilla": "guia_hta_2025",
        "p_details": "protocolo de hipertensión\n(régimen estándar)",
        "instancia": "tratamiento_maria_001",
        "i_details": "paciente: María\nadaptaciones: dosis ajustada\ninicio: 2026-05-14",
    },
]

for d in domains:
    y = d["y"]
    # Etiqueta de dominio
    ax.text(0.6, y, d["label"],
            ha="left", va="center", fontsize=11.5, fontweight="bold",
            color=INK, family="monospace")

    # Plantilla K
    pbox = FancyBboxPatch((3.0, y - 0.65), 3.6, 1.3,
                          boxstyle="round,pad=0.05",
                          facecolor=K_FILL, edgecolor=K_EDGE, linewidth=1.6)
    ax.add_patch(pbox)
    ax.text(4.8, y + 0.40, d["plantilla"],
            ha="center", va="center", fontsize=10.5, fontweight="bold",
            color=K_EDGE, family="monospace")
    ax.text(4.8, y + 0.15, "∈ K   (plantilla)",
            ha="center", va="center", fontsize=8,
            style="italic", color="#6b7280")
    for j, line in enumerate(d["p_details"].split("\n")):
        ax.text(4.8, y - 0.10 - j * 0.18, line,
                ha="center", va="center", fontsize=7.5,
                color="#374151", family="monospace")

    # Instancia O
    ibox = FancyBboxPatch((8.4, y - 0.65), 3.6, 1.3,
                          boxstyle="round,pad=0.05",
                          facecolor=O_FILL, edgecolor=O_EDGE, linewidth=1.6)
    ax.add_patch(ibox)
    ax.text(10.2, y + 0.40, d["instancia"],
            ha="center", va="center", fontsize=10.5, fontweight="bold",
            color=O_EDGE, family="monospace")
    ax.text(10.2, y + 0.15, "∈ O   (instancia)",
            ha="center", va="center", fontsize=8,
            style="italic", color="#6b7280")
    for j, line in enumerate(d["i_details"].split("\n")):
        ax.text(10.2, y - 0.10 - j * 0.18, line,
                ha="center", va="center", fontsize=7.5,
                color="#374151", family="monospace")

    # Flecha instancia_de
    arr = FancyArrowPatch((8.4, y), (6.6, y),
                          arrowstyle="-|>", mutation_scale=14,
                          color="#6b7280", linewidth=1.4)
    ax.add_patch(arr)
    ax.text(7.5, y + 0.32, "instancia_de",
            ha="center", va="center", fontsize=9, fontweight="bold",
            color="#374151", family="monospace",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor="#9ca3af", lw=0.7, alpha=0.95))

# Pie
ax.text(7, 0.55,
        "La invariante (estequiometría, partitura, protocolo) vive en K.",
        ha="center", va="center", fontsize=10, color="#374151")
ax.text(7, 0.25,
        "La manifestación concreta — situada, contingente, con factor de escala — vive en O.",
        ha="center", va="center", fontsize=10, color="#374151")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "34_plantilla_instancia.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
