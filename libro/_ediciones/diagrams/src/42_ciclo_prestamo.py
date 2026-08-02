"""Diagrama: ciclo de vida de un préstamo con D9.

Estado del préstamo cambia 4 veces a lo largo del año.
Reestructuración como préstamo nuevo con motivado_por / justificado_por / rectifica.

Salida: ../png/42_ciclo_prestamo.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

INK = "#1f2937"

fig, ax = plt.subplots(figsize=(15, 8.5), dpi=200)
ax.set_xlim(0, 15)
ax.set_ylim(0, 8.5)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

ax.text(7.5, 8.10, "Ciclo de vida de un préstamo: D9 + motivo + justificación + rectificación",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7.5, 7.70,
        "Cuatro estados se suceden con vigencia D9. La reestructuración es un préstamo nuevo que rectifica el original.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Línea temporal
TL_Y = 1.3
TL_LEFT = 1.0
TL_RIGHT = 14.0
ax.annotate("", xy=(TL_RIGHT, TL_Y), xytext=(TL_LEFT, TL_Y),
            arrowprops=dict(arrowstyle="->", color="#6b7280", lw=1.4))
ticks = [("Ene 2026", 1.5), ("Abr", 4.5), ("Jul", 7.5),
         ("Oct", 10.5), ("Ene 2027", 13.5)]
for lbl, x in ticks:
    ax.plot([x, x], [TL_Y - 0.08, TL_Y + 0.08], color="#9ca3af", lw=0.8)
    ax.text(x, TL_Y - 0.30, lbl,
            ha="center", va="center", fontsize=8.5, color="#6b7280")

# Bandas de estado con D9
bands = [
    {"x0": 1.5, "x1": 8.5, "label": "vigente",
        "fill": "#dcfce7", "edge": "#15803d",
        "dates": "from: 2026-01-15  to: 2026-08-10"},
    {"x0": 8.5, "x1": 9.5, "label": "mora_30",
        "fill": "#fef3c7", "edge": "#b45309",
        "dates": "Ago-10 → Sep-10"},
    {"x0": 9.5, "x1": 10.5, "label": "mora_60",
        "fill": "#fed7aa", "edge": "#c2410c",
        "dates": "Sep-10 → Oct-15"},
    {"x0": 10.5, "x1": 13.5, "label": "reestructurado",
        "fill": "#fee2e2", "edge": "#b91c1c",
        "dates": "Oct-15 → ∞"},
]
band_y = 3.0
for b in bands:
    box = Rectangle((b["x0"], band_y), b["x1"] - b["x0"], 0.85,
                    facecolor=b["fill"], edgecolor=b["edge"], lw=1.6)
    ax.add_patch(box)
    ax.text((b["x0"] + b["x1"]) / 2, band_y + 0.55, b["label"],
            ha="center", va="center", fontsize=10, fontweight="bold",
            color=b["edge"], family="monospace")
    ax.text((b["x0"] + b["x1"]) / 2, band_y + 0.22, b["dates"],
            ha="center", va="center", fontsize=7.5,
            color="#374151")

# Línea verticales puntiagudas de transiciones
for x in [8.5, 9.5, 10.5]:
    ax.plot([x, x], [TL_Y + 0.10, band_y], color="#9ca3af",
            lw=0.6, linestyle="dotted", alpha=0.6)

# Préstamo articulador (arriba izquierda)
prest_box = FancyBboxPatch((1.0, 5.5), 5.5, 1.6,
                           boxstyle="round,pad=0.06",
                           facecolor="#dcfce7", edgecolor="#15803d",
                           linewidth=2.0)
ax.add_patch(prest_box)
ax.text(3.75, 6.85, "prestamo_personal_017",
        ha="center", va="center", fontsize=11.5, fontweight="bold",
        color="#15803d", family="monospace")
ax.text(3.75, 6.55, "∈ O · otorgado 2026-01-15",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")
ax.text(3.75, 6.20, "cliente: Ana  ·  monto: 5000 USD",
        ha="center", va="center", fontsize=8.5,
        color="#374151", family="monospace")
ax.text(3.75, 5.95, "tasa: 18%  ·  plazo: 36 cuotas",
        ha="center", va="center", fontsize=8.5,
        color="#374151", family="monospace")
ax.text(3.75, 5.70, "tipo_producto: pp_tasa_fija_36m",
        ha="center", va="center", fontsize=8.5,
        color="#374151", family="monospace")

# Préstamo reestructurado (arriba derecha)
re_box = FancyBboxPatch((8.5, 5.5), 5.5, 1.6,
                        boxstyle="round,pad=0.06",
                        facecolor="#fee2e2", edgecolor="#b91c1c",
                        linewidth=2.0)
ax.add_patch(re_box)
ax.text(11.25, 6.85, "prestamo_017_re",
        ha="center", va="center", fontsize=11.5, fontweight="bold",
        color="#b91c1c", family="monospace")
ax.text(11.25, 6.55, "∈ O · 2026-10-15",
        ha="center", va="center", fontsize=9, style="italic", color="#6b7280")
ax.text(11.25, 6.20, "motivado_por: mora_017",
        ha="center", va="center", fontsize=8.5,
        color="#b91c1c", family="monospace")
ax.text(11.25, 5.95, "justificado_por: politica_v3",
        ha="center", va="center", fontsize=8.5,
        color="#b91c1c", family="monospace")
ax.text(11.25, 5.70, "rectifica: prestamo_017",
        ha="center", va="center", fontsize=8.5,
        color="#b91c1c", family="monospace")

# Flecha rectifica
arr = FancyArrowPatch((8.5, 6.3), (6.5, 6.3),
                      arrowstyle="-|>", mutation_scale=14,
                      color="#4f46e5", linewidth=1.5,
                      connectionstyle="arc3,rad=0.0")
ax.add_patch(arr)
ax.text(7.5, 6.55, "rectifica",
        ha="center", va="center", fontsize=9, fontweight="bold",
        color="#4f46e5", family="monospace",
        bbox=dict(boxstyle="round,pad=0.12", facecolor="white",
                  edgecolor="#4f46e5", lw=0.8, alpha=0.97))

# Pie
ax.text(7.5, 0.4,
        "Consulta al préstamo `at=2026-09-20` → mora_60. `at=2026-11-20` → reestructurado.",
        ha="center", va="center", fontsize=10, color="#374151")
ax.text(7.5, 0.05,
        "Cinco años después, una auditoría reconstruye toda la historia: estados, motivos, política aplicada.",
        ha="center", va="center", fontsize=9.5, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "42_ciclo_prestamo.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
