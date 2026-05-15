"""Diagrama: arquitectura en capas del lexicon (D8).
El usuario habla con vocabulario natural; el lexicon traduce a roles canónicos
(D7); el motor opera sobre identificadores internos. Cada capa cambia
independientemente.

Salida: ../png/23_lexicon_capas.png
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
ax.text(7, 8.55, "El lexicon como capa de traducción (D8)",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 8.15,
        "El catálogo canónico (D7) es invisible al usuario: el lexicon hace la traducción en ambas direcciones.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# ----- Capa 1: usuario / dominio -----
layer1_y = 6.7
ax.add_patch(FancyBboxPatch((0.5, layer1_y - 0.65), 13, 1.3,
                            boxstyle="round,pad=0.05",
                            facecolor="#fef3c7", edgecolor="#b45309",
                            linewidth=1.8))
ax.text(0.85, layer1_y + 0.40, "CAPA 1",
        ha="left", va="center", fontsize=9, fontweight="bold",
        color="#b45309", family="monospace")
ax.text(0.85, layer1_y + 0.10, "lenguaje natural del usuario",
        ha="left", va="center", fontsize=11, fontweight="bold",
        color="#b45309")
ax.text(0.85, layer1_y - 0.20, "(varía por persona, dialecto, dominio)",
        ha="left", va="center", fontsize=8.5, style="italic", color="#92400e")

# Ejemplos en la capa 1 (una columna por ejemplo, separación amplia)
examples_1 = [
    "\"el vendedor le facturó\nal cliente\"",
    "\"la doctora atendió\nal paciente\"",
    "\"Ana redimió su\nsesión gratis\"",
]
ex_xs = [6.7, 9.5, 12.3]
for ex_x, ex in zip(ex_xs, examples_1):
    ax.text(ex_x, layer1_y, ex,
            ha="center", va="center", fontsize=8.5,
            color="#92400e", style="italic", family="serif")

# Flechas entre capas
def vertical_arrows(y1, y2, label_left, label_right):
    # Flecha hacia abajo (compilación)
    ax.annotate("", xy=(4.5, y2 + 0.05), xytext=(4.5, y1 - 0.05),
                arrowprops=dict(arrowstyle="->", color="#15803d",
                                lw=1.8))
    ax.text(4.3, (y1 + y2) / 2, label_left,
            ha="right", va="center", fontsize=8.5,
            color="#15803d", style="italic", family="monospace")
    # Flecha hacia arriba (consulta / respuesta)
    ax.annotate("", xy=(9.5, y1 - 0.05), xytext=(9.5, y2 + 0.05),
                arrowprops=dict(arrowstyle="->", color="#1d4ed8",
                                lw=1.8))
    ax.text(9.7, (y1 + y2) / 2, label_right,
            ha="left", va="center", fontsize=8.5,
            color="#1d4ed8", style="italic", family="monospace")

vertical_arrows(layer1_y - 0.65, 5.0 + 0.65, "ingesta ↓", "respuesta ↑")

# ----- Capa 2: lexicon -----
layer2_y = 5.0
ax.add_patch(FancyBboxPatch((0.5, layer2_y - 0.65), 13, 1.3,
                            boxstyle="round,pad=0.05",
                            facecolor="#dbeafe", edgecolor="#1d4ed8",
                            linewidth=2.2))
ax.text(0.85, layer2_y + 0.40, "CAPA 2",
        ha="left", va="center", fontsize=9, fontweight="bold",
        color="#1d4ed8", family="monospace")
ax.text(0.85, layer2_y + 0.10, "lexicon",
        ha="left", va="center", fontsize=11, fontweight="bold",
        color="#1d4ed8")
ax.text(0.85, layer2_y - 0.20, "(verbo → tipo + roles + aliases + dialecto)",
        ha="left", va="center", fontsize=8.5, style="italic", color="#1e3a8a")

# Ejemplo de mapping en la capa 2
ax.text(5.5, layer2_y + 0.25, "vendedor → agente",
        ha="left", va="center", fontsize=9,
        color="#1d4ed8", family="monospace")
ax.text(5.5, layer2_y - 0.05, "doctora → agente",
        ha="left", va="center", fontsize=9,
        color="#1d4ed8", family="monospace")
ax.text(5.5, layer2_y - 0.35, "redimir → usar_beneficio",
        ha="left", va="center", fontsize=9,
        color="#1d4ed8", family="monospace")
ax.text(10.2, layer2_y + 0.25, "facturó → accion_emitir_factura",
        ha="left", va="center", fontsize=9,
        color="#1d4ed8", family="monospace")
ax.text(10.2, layer2_y - 0.05, "atendió → consulta_medica",
        ha="left", va="center", fontsize=9,
        color="#1d4ed8", family="monospace")
ax.text(10.2, layer2_y - 0.35, "sesión gratis → beneficio_fidelidad",
        ha="left", va="center", fontsize=9,
        color="#1d4ed8", family="monospace")

vertical_arrows(layer2_y - 0.65, 3.3 + 0.65, "tipa ↓", "instancia ↑")

# ----- Capa 3: catálogo canónico D7 -----
layer3_y = 3.3
ax.add_patch(FancyBboxPatch((0.5, layer3_y - 0.65), 13, 1.3,
                            boxstyle="round,pad=0.05",
                            facecolor="#dcfce7", edgecolor="#15803d",
                            linewidth=2.2))
ax.text(0.85, layer3_y + 0.40, "CAPA 3",
        ha="left", va="center", fontsize=9, fontweight="bold",
        color="#15803d", family="monospace")
ax.text(0.85, layer3_y + 0.10, "catálogo canónico (D7)",
        ha="left", va="center", fontsize=11, fontweight="bold",
        color="#15803d")
ax.text(0.85, layer3_y - 0.20, "(roles + ejes + signaturas, invisibles al usuario)",
        ha="left", va="center", fontsize=8.5, style="italic", color="#166534")

# Roles canónicos visibles: 4 chips por fila, 2 filas
canon_roles = ["agente", "tema", "beneficiario", "lugar_de",
               "momento", "instancia_de", "parte_de", "por_cuanto"]
chip_w = 1.55
chip_h = 0.30
col0_x = 5.5
gap_x = 1.75
row_ys = [layer3_y + 0.10, layer3_y - 0.30]
for i, r in enumerate(canon_roles):
    row = i // 4
    col = i % 4
    cx = col0_x + col * gap_x
    cy = row_ys[row]
    chip = FancyBboxPatch((cx, cy - chip_h/2), chip_w, chip_h,
                          boxstyle="round,pad=0.02",
                          facecolor="white", edgecolor="#15803d",
                          linewidth=0.9)
    ax.add_patch(chip)
    ax.text(cx + chip_w/2, cy, r,
            ha="center", va="center", fontsize=8,
            color="#15803d", family="monospace", fontweight="bold")

vertical_arrows(3.3 - 0.65, 1.6 + 0.65, "almacena ↓", "consulta ↑")

# ----- Capa 4: motor / almacenamiento -----
layer4_y = 1.6
ax.add_patch(FancyBboxPatch((0.5, layer4_y - 0.65), 13, 1.3,
                            boxstyle="round,pad=0.05",
                            facecolor="#e0e7ff", edgecolor="#4f46e5",
                            linewidth=1.8))
ax.text(0.85, layer4_y + 0.40, "CAPA 4",
        ha="left", va="center", fontsize=9, fontweight="bold",
        color="#4f46e5", family="monospace")
ax.text(0.85, layer4_y + 0.10, "motor / almacenamiento",
        ha="left", va="center", fontsize=11, fontweight="bold",
        color="#4f46e5")
ax.text(0.85, layer4_y - 0.20, "(UUIDs, índices, grafos, persistencia)",
        ha="left", va="center", fontsize=8.5, style="italic", color="#3730a3")

ax.text(5.5, layer4_y + 0.10,
        "(0193f8a2-... , agente, 0193f8a3-...)",
        ha="left", va="center", fontsize=8.5,
        color="#4f46e5", family="monospace")
ax.text(5.5, layer4_y - 0.20,
        "(0193f8a2-... , momento, 2026-05-15T18:30Z)",
        ha="left", va="center", fontsize=8.5,
        color="#4f46e5", family="monospace")

# Anotación lateral: D8
ax.annotate("", xy=(13.6, 5.6), xytext=(13.6, 7.0),
            arrowprops=dict(arrowstyle="-", color="#b45309",
                            lw=1.0, linestyle="dotted"))
ax.text(13.7, 6.3, "D8:\nel usuario\nsolo ve\nla CAPA 1",
        ha="left", va="center", fontsize=8.5,
        color="#b45309", style="italic")

# Pie
ax.text(7, 0.35,
        "Cualquier capa puede evolucionar sin romper las demás: el lexicon estabiliza la interfaz hacia el usuario\n"
        "y desacopla el catálogo interno del vocabulario externo.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "23_lexicon_capas.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
