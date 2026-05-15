"""Diagrama: D9 sobre un diagnóstico clínico.

HTA grado 1 vigente desde mayo 2026 hasta enero 2027, reemplazado por
HTA grado 2 desde enero 2027 (abierto al futuro). Una consulta `at=`
recupera el correcto según el momento.

Salida: ../png/32_d9_diagnostico.png
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

INK = "#1f2937"

fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
ax.set_xlim(0, 14)
ax.set_ylim(0, 8)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Título
ax.text(7, 7.55,
        "D9 sobre un diagnóstico: dos rangos de vigencia, sin perder histórico",
        ha="center", va="center", fontsize=14, fontweight="bold", color=INK)
ax.text(7, 7.15,
        "El rediagnóstico rectifica el original. La consulta temporal recupera el correcto según el momento.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

# Línea temporal
TL_Y = 1.3
TL_LEFT = 1.0
TL_RIGHT = 13.0
ax.annotate("", xy=(TL_RIGHT, TL_Y), xytext=(TL_LEFT, TL_Y),
            arrowprops=dict(arrowstyle="->", color="#6b7280", lw=1.4))
months = [(2026, "May 2026", 1.5), (2026, "Sep 2026", 4.5),
          (2027, "Ene 2027", 7.5), (2027, "Jun 2027", 10.5),
          (2027, "Dic 2027", 12.7)]
for _, lbl, x in months:
    ax.plot([x, x], [TL_Y - 0.08, TL_Y + 0.08], color="#9ca3af", lw=0.8)
    ax.text(x, TL_Y - 0.25, lbl,
            ha="center", va="center", fontsize=8.5, color="#6b7280")

# Banda 1: HTA-g1 (mayo 2026 a enero 2027)
b1_x0, b1_x1 = 1.5, 7.5
b1_y = 3.2
band1 = Rectangle((b1_x0, b1_y), b1_x1 - b1_x0, 0.9,
                  facecolor="#fed7aa", edgecolor="#c2410c", lw=1.8)
ax.add_patch(band1)
ax.text((b1_x0 + b1_x1)/2, b1_y + 0.62, "diag_hta_001",
        ha="center", va="center", fontsize=11, fontweight="bold",
        color="#c2410c", family="monospace")
ax.text((b1_x0 + b1_x1)/2, b1_y + 0.28,
        "diagnosticado_como: hipertension_grado_1",
        ha="center", va="center", fontsize=9,
        color="#7c2d12", family="monospace")

# Banda 2: HTA-g2 (enero 2027 → ∞)
b2_x0, b2_x1 = 7.5, 12.8
b2_y = 3.2
band2 = Rectangle((b2_x0, b2_y), b2_x1 - b2_x0, 0.9,
                  facecolor="#fee2e2", edgecolor="#b91c1c", lw=1.8)
ax.add_patch(band2)
ax.text((b2_x0 + b2_x1)/2, b2_y + 0.62, "diag_hta_002",
        ha="center", va="center", fontsize=11, fontweight="bold",
        color="#b91c1c", family="monospace")
ax.text((b2_x0 + b2_x1)/2, b2_y + 0.28,
        "diagnosticado_como: hipertension_grado_2",
        ha="center", va="center", fontsize=9,
        color="#7f1d1d", family="monospace")
# flecha → ∞
ax.annotate("", xy=(b2_x1 + 0.3, b2_y + 0.45),
            xytext=(b2_x1, b2_y + 0.45),
            arrowprops=dict(arrowstyle="->", color="#b91c1c", lw=1.4))

# Etiquetas inicio/fin
ax.text(b1_x0, b1_y + 1.05, "from:\n2026-05-14",
        ha="center", va="bottom", fontsize=8, color="#c2410c")
ax.text(b1_x1, b1_y + 1.05, "to:\n2027-01-10",
        ha="center", va="bottom", fontsize=8, color="#c2410c")
ax.text(b2_x0, b2_y + 1.05, "from:\n2027-01-10",
        ha="center", va="bottom", fontsize=8, color="#b91c1c")
ax.text(b2_x1 + 0.5, b2_y + 0.45, "to: null",
        ha="left", va="center", fontsize=8, style="italic",
        color="#b91c1c")

# Relación rectifica
ax.annotate("", xy=(b1_x1 - 0.6, b1_y + 0.45),
            xytext=(b2_x0 + 0.6, b1_y + 0.45),
            arrowprops=dict(arrowstyle="-|>", color="#4f46e5", lw=1.5,
                            connectionstyle="arc3,rad=0.3"))
ax.text(b1_x1, b1_y - 0.30, "rectifica",
        ha="center", va="center", fontsize=9, fontweight="bold",
        color="#4f46e5", family="monospace",
        bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                  edgecolor="#4f46e5", lw=0.9, alpha=0.97))

# Consultas
def query_marker(year_label, x, color, answer_y, answer_text, answer_sub):
    ax.plot([x, x], [TL_Y, 6.0], color=color, lw=1.5, linestyle="--", alpha=0.85)
    ax.plot([x], [TL_Y], "v", color=color, markersize=10)
    ax.text(x, 6.25,
            f"Consulta: \n¿qué dx tenía María {year_label}?",
            ha="center", va="bottom", fontsize=9, fontweight="bold",
            color=color)
    ans = FancyBboxPatch((x - 1.7, answer_y), 3.4, 0.75,
                         boxstyle="round,pad=0.05",
                         facecolor="white", edgecolor=color, lw=1.4)
    ax.add_patch(ans)
    ax.text(x, answer_y + 0.50, answer_text,
            ha="center", va="center", fontsize=10, fontweight="bold",
            color=color, family="monospace")
    ax.text(x, answer_y + 0.18, answer_sub,
            ha="center", va="center", fontsize=8, style="italic",
            color=color)

query_marker("en agosto 2026", 4.0, "#c2410c", 5.0,
             "→ HTA grado 1",
             "(diag_hta_001 vigente)")
query_marker("en marzo 2027", 9.0, "#b91c1c", 5.0,
             "→ HTA grado 2",
             "(diag_hta_002 vigente)")

# Pie
ax.text(7, 0.30,
        "La misma consulta, parametrizada por `at=...`, devuelve el diagnóstico vigente en ese momento.",
        ha="center", va="center", fontsize=10, style="italic", color="#6b7280")

out = os.path.join(os.path.dirname(__file__), "..", "png",
                   "32_d9_diagnostico.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="#ffffff")
plt.close(fig)
print(f"  ✓ {out}")
